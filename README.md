# JARVIS - Just A Rather Very Intelligent System

A modern, voice-controlled AI assistant for Windows with a sleek GUI, smart command routing, and extensible plugin system.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

### 🎨 Modern GUI
- Clean, professional interface with multiple color themes (Dark, Light, Blue, Gold)
- Real-time status indicators (Listening, Processing, Speaking)
- Split-panel layout with conversation log and controls
- Responsive design that adapts to window size

### 🎙️ Voice Control
- Natural speech recognition with Google's speech API
- Text-to-speech responses using pyttsx3
- Wake word detection support

### 🤖 AI Integration
- GPT-powered conversational AI
- Context-aware responses with conversation memory
- Persistent chat history

### 🧠 Smart Command Routing
- Intent-based command classification
- Synonym matching for flexible commands
- Plugin system for extensibility

### 🔌 Plugin Architecture
- Modular plugin system
- Easy-to-create plugins
- Hot-loadable plugins from `plugins/` directory

### 🛡️ Safety Features
- Confirmation prompts for destructive actions (shutdown, etc.)
- Encrypted storage for sensitive settings (API keys, passwords)
- Graceful error handling and recovery

### 📱 System Tray
- Minimize to system tray for background operation
- Quick access from notification area
- Restore window from tray

### 🔍 Web Search
- Search the web from voice or text
- DuckDuckGo integration (no API key needed)
- Read top search results aloud

### ✉️ Email
- Compose and send emails via Gmail
- GUI email composer with all fields
- App password authentication (secure)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows 10/11
- Microphone for voice commands

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/jarvis.git
   cd jarvis
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download spaCy model (optional, for NLP):**
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Run JARVIS:**
   ```bash
   python jarvis.py
   ```

---

## 📖 Usage

### Voice Commands

| Command | Description |
|---------|-------------|
| "Open [app]" | Launch applications (Chrome, Spotify, Notepad, etc.) |
| "What time is it" | Get current time |
| "Weather" | Get weather for your city |
| "Ask AI [question]" | Chat with GPT |
| "Volume up/down" | Adjust system volume |
| "Take screenshot" | Capture screen |
| "Add note [text]" | Save a note |
| "Show notes" | View saved notes |
| "Shutdown" | Shut down PC (with confirmation) |

### Text Input
- Use the main input field for commands
- Use the AI input field for conversational queries

### GUI Controls
- **Speak** - Activate voice input
- **Theme Selector** - Switch between color themes
- **API Key** - Set your OpenAI API key
- **Set City** - Configure default city for weather

---

## 🔌 Creating Plugins

Plugins are Python files in the `plugins/` directory. Each plugin must have a `register()` function:

```python
def register(jarvis):
    def my_handler(query, speak, log, **kwargs):
        speak("Hello from my plugin!")
        log("My plugin executed")
    
    jarvis['add_command'](
        trigger_words=['my command', 'do something'],
        handler=my_handler,
        description='Description of my command'
    )
```

### Plugin Parameters
- `query` - The user's input text
- `speak` - Function to convert text to speech
- `log` - Function to log messages
- `**kwargs` - Additional context (can be extended)

### Example Plugins
- `file_search.py` - Search for files by name
- `example_plugin.py` - Demonstrates plugin capabilities

---

## 🛠️ Configuration

### Settings File (`settings.json`)
```json
{
  "openai_api_key": "your-api-key",
  "dark_mode": true,
  "theme": "Dark",
  "voice": 0,
  "default_city": "New York",
  "email_address": "your-email@gmail.com",
  "email_password": "your-app-password"
}
```

### Sensitive Data
API keys and passwords are automatically encrypted using the `cryptography` library. The encryption key is stored in `settings.key`.

---

## 📁 Project Structure

```
jarvis/
├── jarvis.py              # Main application entry point
├── requirements.txt       # Python dependencies
├── settings.json          # User settings (auto-created)
├── settings.key           # Encryption key (auto-created)
├── notes.json             # Saved notes (auto-created)
├── calendar.json          # Calendar events (auto-created)
├── jarvis.log             # Application logs
├── plugins/               # Plugin directory
│   ├── __init__.py
│   ├── file_search.py     # File search plugin
│   └── example_plugin.py  # Example plugin
└── screenshots/           # Screenshots directory (auto-created)
```

---

## 🧪 Development

### Adding New Features
1. Create a new plugin in `plugins/`
2. Or extend `CommandRouter` in `jarvis.py`

### Running Tests
```bash
# Test the application
python jarvis.py

# Check logs
cat jarvis.log
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Sarthak** - Initial work
- **Meet** - Initial work

## 🙏 Acknowledgments

- [pyttsx3](https://github.com/nateshmbhat/pyttsx3) - Text-to-speech
- [SpeechRecognition](https://github.com/Uberi/speech_recognition) - Speech recognition
- [OpenAI](https://openai.com/) - GPT API
- [spaCy](https://spacy.io/) - NLP processing
- [pystray](https://github.com/moses-palmer/pystray) - System tray support
