import requests
import json
import vosk
import os
import pyaudio
import pygame
from gtts import gTTS
import time

# --- Setup ---

# Initialize Vosk model
model = vosk.Model("vosk-model")  # Replace with your model path
recognizer = vosk.KaldiRecognizer(model, 16000)

# Initialize Pygame for audio playback
pygame.mixer.init()

# API endpoint for Ollama
url = "http://127.0.0.1:11434/api/chat"

# Initial conversation message
messages = [{"role": "user", "content": "Hello, how are you?"}]


# --- Functions ---

import uuid  # Add this at the top if not already there

def speak(text):
    filename = f"response_{uuid.uuid4()}.mp3"
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(filename)

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        time.sleep(0.2)  # Ensure OS releases the file

    finally:
        # Try to delete the file even if something failed
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except PermissionError:
            print(f"Warning: Could not delete {filename}. File may still be in use.")



def listen():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    print("Listening...")
    while True:
        data = stream.read(4000)
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            text = json.loads(result).get("text", "")
            if text:
                stream.stop_stream()
                stream.close()
                p.terminate()
                return text


# --- Main Loop ---

while True:
    user_input = listen()

    if not user_input:
        print("Sorry, I didn't catch that. Please try again.")
        continue

    print(f"You: {user_input}")
    messages.append({"role": "user", "content": user_input})

    if user_input.lower() in ['exit', 'quit', 'bye']:
        print("Goodbye!")
        break

    payload = {
        "model": "ben",  # Change if you're using a different Ollama model
        "messages": messages
    }

    response = requests.post(url, json=payload, stream=True)

    if response.status_code == 200:
        assistant_message = ""

        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    json_data = json.loads(line)
                    if "message" in json_data and "content" in json_data["message"]:
                        assistant_message += json_data["message"]["content"]
                except json.JSONDecodeError:
                    print("Error decoding JSON:", line)

        if assistant_message:
            print(f"Assistant: {assistant_message}")
            speak(assistant_message)
            messages.append({"role": "assistant", "content": assistant_message})
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

# finnaly worked yayyy