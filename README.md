# JARVIS  
A voice-controlled AI co-pilot for Windows that automates everyday system tasks using speech recognition and natural language processing.

---

## Overview

JARVIS (Just A Rather Very Intelligent System) is designed to bring futuristic, hands-free computing to life. Using your voice, JARVIS can launch applications, search the internet, manage files, control system settings, and more — making it the perfect productivity assistant for developers, students, and professionals.

---

## Project Roadmap

###  Step 1: Build the Core Voice Recognition Pipeline  
- **Speech-to-Text**:  
  - Leverages `SpeechRecognition` and `PyAudio` to capture and convert user speech to text.  
  - Real-time transcription with basic noise handling.  
  - Live feedback display during speech capture.

- **Wake Word Detection (optional)**:  
  - Exploring integration of `Porcupine`, `Snowboy`, or `Vosk` for always-on listening with a trigger phrase like “Hey JARVIS”.

>  **Status**: Functional voice-to-text pipeline with real-time input capture.

---

### Step 2: Build the Intent Classification Module  
- **Basic NLP Model**:  
  - Starts with rule-based command detection using keywords and regex.  
  - Plans to integrate lightweight NLP models using `spaCy` or transformer-based classification.

- **Command Mapping**:  
  - Intent-to-function mapping (e.g., “open browser” → `open_chrome()`).  
  - Dynamic parsing of variables like app names or search terms.

>  **In Progress**: Basic rule engine working. ML-based parsing under development.

---

### Step 3: Develop the Command Execution Engine  
- **Windows Automation**:  
  - Automates real system tasks using `os`, `subprocess`, `pyautogui`, and `psutil`.  
  - Handles application control, volume adjustment, file navigation, etc.

- **Voice Feedback**:  
  - Uses `pyttsx3` for spoken confirmations and interaction.

>  **Pending**: Command mapping implemented; feedback system being fine-tuned.

---

### Step 4: Enable Autostart and Background Operation  
- Configure JARVIS to run at Windows startup.  
- Implement silent tray icon mode with wake-word activation.  
- Allow user-initiated shutdown or wake functions.

>  **Planned**: Background listening and autostart features in testing phase.

---

### Step 5: Optional Enhancements (Post-MVP)  
- **GUI Dashboard**:  
  - A frontend panel to view logs, toggle features, and customize settings.  

- **Contextual Memory**:  
  - Add context tracking for conversational continuity.

- **Cloud NLP APIs (Optional)**:  
  - Integrate OpenAI/Bedrock for more advanced understanding and responses.  

- **IoT/Smart Home Support**:  
  - Connect to smart home devices via IFTTT, MQTT, or API integrations.

---

## Technologies Used

- Python  
- SpeechRecognition + PyAudio  
- pyttsx3 for Text-to-Speech  
- spaCy / HuggingFace Transformers  
- pyautogui, psutil, subprocess, os  
- Optional: OpenAI GPT API / Vosk / Porcupine

---

## Directory Structure

