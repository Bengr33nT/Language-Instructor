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

def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    
    # Load and play the audio file
    pygame.mixer.music.load("response.mp3")
    pygame.mixer.music.play()
    
    # Wait for the sound to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)  # Add a small delay to prevent high CPU usage
    
    pygame.mixer.music.stop()  # Stop the music
    pygame.mixer.quit()  # Quit the mixer
    pygame.mixer.init()  # Reinitialize the mixer

    os.remove("response.mp3")  # Clean up the audio file
    
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
        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    json_data = json.loads(line)
                    # Extract and print the assistant's message
                    if "message" in json_data and "content" in json_data["message"]:
                        assistant_message = json_data["message"]["content"]
                        print(assistant_message, end="")
                        speak(assistant_message)  # Speak the assistant's message
                        # Append the assistant's message to the conversation history
                        messages.append({"role": "assistant", "content": assistant_message})

                except json.JSONDecodeError:
                    print("Error decoding JSON:", line)
        print()  # ensure the final output is on a new line

    else:
        print(f"Error: {response.status_code}")
        print(response.text)

    # Optional: Break the loop if the user types 'exit'
    if user_input.lower() == 'exit':
        break
    