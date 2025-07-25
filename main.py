import os
import uuid
import time
import json
import requests
import vosk
import pyaudio
import pygame
from gtts import gTTS  # Switched back to gTTS

# --- Initialization ---

# Vosk Speech Recognition
model = vosk.Model("vosk-model")  # Update with your actual path
recognizer = vosk.KaldiRecognizer(model, 16000)

# Audio playback
pygame.mixer.init()

# Ollama API
url = "http://127.0.0.1:11434/api/chat"
messages = [{"role": "user", "content": "Hello, how are you?"}]


# --- Functions ---

def speak(text):
    filename = f"response_{uuid.uuid4()}.mp3"
    try:
        # Generate voice
        tts = gTTS(text=text, lang='en')
        tts.save(filename)

        # Play voice
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        time.sleep(0.1)  # Ensure it's done
        pygame.mixer.music.unload()
    finally:
        # Clean up
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except PermissionError:
                print(f"⚠️ Could not delete: {filename}")


def listen():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                    input=True, frames_per_buffer=8000)
    stream.start_stream()

    print("🎙️ Listening...")
    while True:
        data = stream.read(4000, exception_on_overflow=False)
    
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
        speak("Goodbye!")
        break

    # Send to Ollama
    payload = {
        "model": "ben",  # Replace with your model name if different
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
                    print("⚠️ Error decoding JSON:", line)

        if assistant_message:
            print(f"Assistant: {assistant_message}")
            speak(assistant_message)
            messages.append({"role": "assistant", "content": assistant_message})
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
