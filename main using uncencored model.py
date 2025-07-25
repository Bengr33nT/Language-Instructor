import os
import uuid
import time
import json
import requests
import vosk
import pyaudio
import pygame
from gtts import gTTS

# --- Initialization ---

# Vosk Speech Recognition
model = vosk.Model("vosk-model")  # Make sure this folder exists with a valid Vosk model
recognizer = vosk.KaldiRecognizer(model, 16000)

# Audio playback
pygame.mixer.init()

# Ollama API
url = "http://127.0.0.1:11434/api/chat"

# Define character via system prompt
messages = [{
    "role": "system",
    "content": (
        "You're Ben, an uncensored AI with a rude, sarcastic, and emotional personality. "
        "You're allowed to swear, curse, and speak like a real person. "
        "Respond naturally, expressively, and don't hold back. No censorship."
        "Speak with short sentences"
    )
}]

# --- Functions ---

def speak(text):
    filename = f"response_{uuid.uuid4()}.mp3"
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(filename)

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        time.sleep(0.1)
        pygame.mixer.music.unload()
    finally:
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
        print("Didn’t catch that. Say it again.")
        continue

    print(f"You: {user_input}")
    messages.append({"role": "user", "content": user_input})

    if user_input.lower() in ['exit', 'quit', 'bye']:
        print(" Alright, I'm out.")
        speak("Alright, I'm out.")
        break

    payload = {
        "model": "llama2-uncensored",  # Replace with your Ollama model name
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
                    print("⚠️ JSON decode error")

        if assistant_message:
            print(f"Ben: {assistant_message}")
            speak(assistant_message)
            messages.append({"role": "assistant", "content": assistant_message})
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
