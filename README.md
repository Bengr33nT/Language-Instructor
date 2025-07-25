Voice AI Assistant with Ollama and Vosk

This project is a voice-controlled AI assistant that:

    Listens to your voice using Vosk for speech recognition

    Sends text queries to Ollama for processing (supports custom models)

    Responds back with generated speech using gTTS

Perfect for hands-free AI conversations using your own trained model.
Features

    Voice input via microphone (Vosk)

    Conversational AI using Ollama (with support for custom models)

    Voice output via gTTS + pygame

Requirements

    Python 3.9+

    Pip

    Ollama (for local AI models)

    Vosk Speech Recognition model

Setup Instructions
1. Clone the repository

git clone https://github.com/your-username/your-repo.git
cd your-repo

2. Create & activate a virtual environment (recommended)

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

requirements.txt should include:

vosk
pyaudio
pygame
gTTS
requests

Install & Run Ollama
1. Install Ollama

Follow instructions for your OS: https://ollama.ai/download
2. Verify installation

ollama --version

3. Download the custom model (ben)

Your custom model (ben) is included in this repository as a .modelfile.

Load it into Ollama:

ollama create ben -f ./ben.modelfile

4. Run the Ollama server

ollama serve

Run the Assistant

    Ensure Ollama is running:

ollama serve

    Run the script:

python main.py

    Speak into your microphone, and the AI will respond via voice.

Exiting

Say "exit", "quit", or "bye" to stop the assistant.
