#did no work but I just put it here to keep the file
import requests
import json
import vosk
import os
import pyaudio
from gtts import gTTS
import pygame

# Initialize Vosk model and recognizer
model = vosk.Model("vosk-model")  # Specify the path to your Vosk model
recognizer = vosk.KaldiRecognizer(model, 16000)

# Initialize Pygame mixer for audio playback
pygame.mixer.init()

url = "http://127.0.0.1:11434/api/chat"

# Initialize the conversation history
messages = [{"role": "user", "content": "Hello, how are you?"}]
audio_files = []  # List to keep track of audio files

def speak(text):
    global audio_files
    audio_count = len(audio_files) + 1
    filename = f"response{audio_count}.mp3"  # Unique filename

    tts = gTTS(text=text, lang='en')
    tts.save(filename)

    # Load and play the audio file
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    
    # Wait for the sound to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)  # Add a small delay to prevent high CPU usage
    
    audio_files.append(filename)  # Keep track of the audio file

def listen():
    # Initialize microphone stream
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    print("Listening...")
    while True:
        data = stream.read(4000)
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            return json.loads(result)["text"]
    stream.stop_stream()
    stream.close()
    p.terminate()

while True:
    # Listen for user input
    user_input = listen()

    if user_input:
        print(f"You: {user_input}")
        messages.append({"role": "user", "content": user_input})
    else:
        print("Sorry, I did not listen. Please try again.")
        continue

    # Prepare the payload with the current messages
    payload = {
        "model": "ben",
        "messages": messages
    }

    response = requests.post(url, json=payload, stream=True)

    if response.status_code == 200:
        print("Response from the server:")
        assistant_message = ""
        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    json_data = json.loads(line)
                    # Extract the assistant's message
                    if "message" in json_data and "content" in json_data["message"]:
                        assistant_message = json_data["message"]["content"]
                        print(assistant_message)
                except json.JSONDecodeError:
                    print("Error decoding JSON:", line)

        # Speak the assistant's message after collecting the entire response
        if assistant_message:
            speak(assistant_message)

    else:
        print(f"Error: {response.status_code}")
        print(response.text)

    # Optional: Break the loop if the user types 'exit'
    if user_input.lower() == 'exit':
        break

# Cleanup: Remove all generated audio files
for audio_file in audio_files:
    if os.path.exists(audio_file):
        os.remove(audio_file)
