# JARVIS

A voice-controlled AI co-pilot for Windows that automates everyday system tasks using speech recognition and natural language processing.

---

## 🧠 Overview

JARVIS (Just A Rather Very Intelligent System) brings hands-free computing to life. Using voice commands, it can:

- Open applications like Chrome, Spotify, Notepad, and more
- Search the internet or get weather info
- Send emails
- Set alarms
- Take notes and screenshots
- Provide spoken responses using TTS (pyttsx3)
- Act as a GPT-powered assistant using OpenAI API

Built for developers, students, and productivity enthusiasts looking for a futuristic desktop companion.

---

## 🚀 Features

- 🎙️ **Voice Recognition** via `SpeechRecognition`
- 🤖 **GPT Integration** using OpenAI's Chat API
- 📢 **Text-to-Speech Engine** (TTS) with customizable voice/rate
- 🧾 **GUI Interface** built with `tkinter`
- 🧠 **Wake Word Detection** with Vosk (offline support)
- ⏰ **Alarms, Reminders & Clipboard Reading**
- 📝 **Note Taking + Screenshot Capture**
- 💡 **System Commands** (Volume, Shutdown, Open Apps)

---

## 🛠️ Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/jarvis.git
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python jarvis.py
   ```

> ✅ Vosk model should be downloaded and placed in your working directory.

---

## 🧭 Project Roadmap

### ✅ Step 1: Core Voice Recognition
- Real-time transcription using `SpeechRecognition`
- Wake word detection using Vosk ("Hey Jarvis")

### ✅ Step 2: Intent Classification
- Rule-based parsing using keywords
- Future: SpaCy/HuggingFace integration

### ✅ Step 3: Command Execution
- Handles system automation (apps, volume, browser, etc.)
- Integrated voice feedback with `pyttsx3`

### ✅ Step 4: GUI + Background Support
- Tkinter-based dashboard
- Dark mode toggle, TTS settings, About panel
- Future: Add system tray support

### 🔄 Step 5: Post-MVP Enhancements
- GPT memory/contextual conversation
- Integration with smart devices/IoT
- Multi-language voice input/output

---

## 💻 Technologies Used

- Python
- `SpeechRecognition` + `PyAudio`
- `pyttsx3` (TTS)
- `pyautogui`, `os`, `subprocess`, `requests`, `bs4`
- `tkinter`, `plyer`, `pyperclip`
- OpenAI GPT-3.5-Turbo API
- Vosk (Wake word engine)

---

## 📸 Screenshots / Demo

> _Coming soon..._

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repo and submit pull requests.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🧑‍💻 Developed by

Meet Jadhav & Sarthak (Team JARVIS)

> Special thanks to open-source contributors and the Python community.

