# doesnt fully work yet, but is a work in progress. I wanted this one to work completley offline, hence im trying to ue parler_tts instead of gtts or pyttsx3.
# I know that pyttsx3 is also offline, but I wanted to try something that is more expressive and has more control over the voice, like parler_tts.
# forgive the bad naming of program files :)
import os
import uuid
import time
import json
import requests
import vosk
import pyaudio
import pygame
import soundfile as sf
import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer

# --- Initialization ---

# Vosk Speech Recognition
model = vosk.Model("vosk-model")  # Set your path to vosk-model
recognizer = vosk.KaldiRecognizer(model, 16000)

# Audio playback
pygame.mixer.init()

# Ollama API
url = "http://127.0.0.1:11434/api/chat"

# Parler-TTS setup
device = "cuda:0" if torch.cuda.is_available() else "cpu"
parler_model = ParlerTTSForConditionalGeneration.from_pretrained(
    "parler-tts/parler-tts-mini-multilingual-v1.1"
).to(device)

parler_tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-mini-multilingual-v1.1")
desc_tokenizer = AutoTokenizer.from_pretrained(parler_model.config.text_encoder._name_or_path)

# Initial system prompt: personality
messages = [{
    "role": "system",
    "content": (
        "You are Blaze, a sarcastic, expressive AI with a bad attitude. "
        "You swear when you're pissed, you speak casually like a real person. "
        "Be funny, moody, rude if necessary, and don't hold back. Always write a short description of your emotional voice before each response, like 'description: A tired, angry male voice...'"
    )
}]


# --- Functions ---

def speak(text, voice_description):
    filename = f"response_{uuid.uuid4()}.wav"
    try:
        # Tokenize voice description and prompt
        desc_ids = desc_tokenizer(voice_description, return_tensors="pt").input_ids.to(device)
        prompt_ids = parler_tokenizer(text, return_tensors="pt").input_ids.to(device)

        # Generate audio
        output = parler_model.generate(input_ids=desc_ids, prompt_input_ids=prompt_ids)
        audio_arr = output.cpu().numpy().squeeze()
        sf.write(filename, audio_arr, parler_model.config.sampling_rate)

        # Play
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"❌ Parler-TTS error: {e}")
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
        print("Didn't catch that. Try again.")
        continue

    print(f"You: {user_input}")
    messages.append({"role": "user", "content": user_input})

    if user_input.lower() in ['exit', 'quit', 'bye']:
        print("Goodbye!")
        speak("Goodbye, jackass.", "A tired, annoyed male voice speaks with sarcasm.")
        break

    payload = {
        "model": "ben",  # Your uncensored model name
        "messages": messages
    }

    response = requests.post(url, json=payload, stream=True)

    if response.status_code == 200:
        assistant_raw = ""
        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    json_data = json.loads(line)
                    if "message" in json_data and "content" in json_data["message"]:
                        assistant_raw += json_data["message"]["content"]
                except json.JSONDecodeError:
                    print("⚠️ Error decoding JSON:", line)

        if assistant_raw:
            print(f"Assistant: {assistant_raw}")

            # Separate voice description from spoken message
            voice_description = "A neutral voice"
            if "description:" in assistant_raw.lower():
                parts = assistant_raw.split("description:")
                if len(parts) > 1:
                    desc_candidate = parts[1].strip().split("\n")[0]
                    voice_description = desc_candidate.strip().strip('"')
                    spoken_text = parts[0].strip()
                else:
                    spoken_text = assistant_raw.strip()
            else:
                spoken_text = assistant_raw.strip()

            messages.append({"role": "assistant", "content": assistant_raw})
            speak(spoken_text, voice_description)
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
