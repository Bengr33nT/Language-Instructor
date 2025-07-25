# Voice AI Assistant (Ollama + Vosk + gTTS)

This project is a voice-controlled AI assistant that:
- Listens to your voice using [Vosk](https://alphacephei.com/vosk/) for speech recognition.
- Sends your query to [Ollama](https://ollama.ai) for processing (supports custom AI models).
- Responds back with generated speech using [gTTS](https://pypi.org/project/gTTS/).

---

## Features
- **Voice Input:** Speech recognition using Vosk.
- **AI Responses:** Powered by Ollama (with support for custom models like `ben`).
- **Voice Output:** Converts AI text responses to speech via gTTS and plays them using Pygame.

---

## Requirements
- Python 3.9 or newer  
- [Ollama](https://ollama.ai) installed and running locally  
- [Vosk Speech Recognition model](https://alphacephei.com/vosk/models)

---

# Create and Activate a Virtual Enviroment

- for Windows use:
    venv\Scripts\activate

- for Linux/Mac:
    source venv/bin/activate

---

# Install Dependencies using pip

vosk
pyaudio
pygame
gTTS
requests

---

# Installing Ollama, for offline LLM use
## Download and install Ollama
Follow instructions for your OS:
https//ollama.ai/download

## Verify Installation
ollama --version

## Run one of the programs, preferably in your code editor
run one of these:
- main using uncencored model.py
- main.py
# Exit Command:
Hit ctrl C or
say:
- exit
- quit
- bye

to close it.


