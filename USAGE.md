# JARVIS Usage Guide

## 🎙️ Voice Commands

### Application Launch
| Command | Description |
|---------|-------------|
| "Open Chrome" | Launch Google Chrome |
| "Open Spotify" | Launch Spotify |
| "Open Notepad" | Launch Notepad |
| "Open Netflix" | Open Netflix in browser |
| "Open YouTube" | Open YouTube in browser |
| "Open Calculator" | Launch Calculator |
| "Open Explorer" | Launch File Explorer |

### Time & Weather
| Command | Description |
|---------|-------------|
| "What time is it" | Get current time |
| "Tell me the weather" | Get weather for your city |
| "What's the temperature" | Get temperature |

### AI Chat
| Command | Description |
|---------|-------------|
| "Ask AI [question]" | Chat with GPT |
| "ChatGPT [question]" | Alternative trigger |
| "Assistant [question]" | Alternative trigger |

### System Controls
| Command | Description |
|---------|-------------|
| "Volume up" | Increase volume |
| "Volume down" | Decrease volume |
| "Take screenshot" | Capture screen |

### Notes & Reminders
| Command | Description |
|---------|-------------|
| "Add note [text]" | Save a note |
| "Show notes" | View all notes |
| "Delete note [text]" | Remove a note |
| "Remind me" | Set a reminder |

### System Info (requires psutil)
| Command | Description |
|---------|-------------|
| "CPU usage" | Get CPU usage |
| "Memory usage" | Get RAM usage |
| "Battery status" | Get battery level |

### Web Search
| Command | Description |
|---------|-------------|
| "Search [query]" | Search the web |
| "Google [query]" | Search using Google |
| "Look up [topic]" | Look up information |
| "Open website [url]" | Open a website |

### Email
| Command | Description |
|---------|-------------|
| "Send email" | Open email composer |
| "Compose email" | Open email composer |
| "Email to [address]" | Compose to recipient |

### Settings
| Command | Description |
|---------|-------------|
| "Settings" | Open settings window |
| "Configure" | Open settings window |

### Exit
| Command | Description |
|---------|-------------|
| "Exit" | Close JARVIS |
| "Quit" | Close JARVIS |
| "Goodbye" | Close JARVIS |

---

## ⌨️ Text Input

### Main Input Field
Type any command and press **Enter** or click **Send**:
- "open chrome"
- "what time is it"
- "take screenshot"

### AI Input Field
Type questions for the AI assistant:
- "What is machine learning?"
- "Explain quantum computing"
- "Write a Python function to sort a list"

---

## 🎨 GUI Features

### Theme Selector
Choose from 4 built-in themes:
- **Dark** - Blue/white on dark background
- **Light** - Clean white theme
- **Blue** - Deep blue ocean theme
- **Gold** - Elegant gold theme

### Status Indicators
- 🟢 **Listening** - JARVIS is capturing audio
- 🟡 **Processing** - Analyzing your command
- 🔵 **Speaking** - JARVIS is responding
- ⚪ **Ready** - Waiting for input

### System Tray
- Click the minimize button to send JARVIS to system tray
- Right-click the tray icon to restore or quit

---

## 🔌 Plugin Commands

### File Search (file_search.py)
| Command | Description |
|---------|-------------|
| "Find file [name]" | Search for a file |
| "Search file [name]" | Search for a file |

### Example Plugin (example_plugin.py)
| Command | Description |
|---------|-------------|
| "Hello JARVIS" | Greet JARVIS |
| "Tell me a joke" | Hear a random joke |
| "What's the date" | Get today's date |
| "Calculate [expression]" | Do math (e.g., "calculate 2 plus 2") |

### Web Search (web_search.py)
| Command | Description |
|---------|-------------|
| "Search [query]" | Search DuckDuckGo |
| "Open website [url]" | Open a URL in browser |

### Email GUI (email_gui.py)
| Command | Description |
|---------|-------------|
| "Send email" | Open email composition window |
| "Compose email" | Open email composition window |

### Settings GUI (settings_gui.py)
| Command | Description |
|---------|-------------|
| "Settings" | Open settings configuration window |
| "Configure" | Open settings configuration window |

---

## ⚙️ Settings

### API Key
1. Click **API Key** button
2. Enter your OpenAI API key
3. Key is encrypted and stored locally

### Set City
1. Click **Set City** button
2. Enter your city name
3. Used for weather queries

---

## 🛡️ Safety Features

### Confirmation Prompts
JARVIS asks for confirmation before:
- Shutting down your PC
- Other destructive actions

### Encrypted Storage
- API keys and passwords are encrypted
- Encryption key stored separately
- Never stored in plain text

---

## 🐛 Troubleshooting

### No Microphone
- Check if microphone is connected
- Grant microphone permissions
- Check Windows sound settings

### No Audio Output
- Check speaker/headphone connection
- Verify pyttsx3 is working: `python -c "import pyttsx3; e=pyttsx3.init(); e.say('test'); e.runAndWait()"`

### AI Not Working
- Verify API key is set correctly
- Check internet connection
- Review `jarvis.log` for errors

### Plugin Errors
- Check plugin syntax
- View error in console/logs
- Ensure dependencies are installed

---

## 📝 Notes

- All commands work with both voice and text input
- Conversation history is maintained during the session
- Notes and settings are persisted between sessions
- Logs are saved to `jarvis.log` and `jarvis_session_log.txt`
