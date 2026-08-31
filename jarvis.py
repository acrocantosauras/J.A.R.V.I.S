"""
JARVIS AI Assistant - Just A Rather Very Intelligent System
A voice-controlled AI co-pilot for Windows.

Developed by Sarthak & Meet
"""

import sys
import os
import json
import time
import logging
import threading
import datetime
import webbrowser
import smtplib
import importlib.util
import glob
import re
import traceback

import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog

import pyttsx3
import speech_recognition as sr
import pyautogui
import requests
from bs4 import BeautifulSoup
import openai
from PIL import Image, ImageTk
import pyperclip
from plyer import notification

try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None

try:
    import pystray
    HAS_PYSTRAY = True
except ImportError:
    HAS_PYSTRAY = False

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# =============================================================================
# LOGGING SETUP
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jarvis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('JARVIS')

# =============================================================================
# CONFIGURATION & SETTINGS
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, 'settings.json')
NOTES_FILE = os.path.join(BASE_DIR, 'notes.json')
CALENDAR_FILE = os.path.join(BASE_DIR, 'calendar.json')
MEMORY_FILE = os.path.join(BASE_DIR, 'conversation_memory.json')
ENCRYPTION_KEY_FILE = os.path.join(BASE_DIR, 'settings.key')
LOG_FILE = os.path.join(BASE_DIR, 'jarvis_session_log.txt')
PLUGINS_DIR = os.path.join(BASE_DIR, 'plugins')

SENSITIVE_KEYS = ['openai_api_key', 'email_password']

# Timer/Stopwatch state
TIMER_RUNNING = False
TIMER_END = None
STOPWATCH_RUNNING = False
STOPWATCH_START = None
STOPWATCH_ELAPSED = 0

# Conversation memory
CONVERSATION_MEMORY = []
MAX_MEMORY_SIZE = 10

# =============================================================================
# ENCRYPTION & SETTINGS
# =============================================================================
def get_encryption_key():
    """Get or generate encryption key for sensitive settings."""
    if Fernet is None:
        return None
    if not os.path.exists(ENCRYPTION_KEY_FILE):
        key = Fernet.generate_key()
        with open(ENCRYPTION_KEY_FILE, 'wb') as f:
            f.write(key)
    else:
        with open(ENCRYPTION_KEY_FILE, 'rb') as f:
            key = f.read()
    return key


def encrypt_value(value):
    """Encrypt a sensitive value."""
    key = get_encryption_key()
    if key is None:
        return value
    f = Fernet(key)
    return f.encrypt(value.encode()).decode()


def decrypt_value(value):
    """Decrypt a sensitive value."""
    key = get_encryption_key()
    if key is None:
        return value
    f = Fernet(key)
    try:
        return f.decrypt(value.encode()).decode()
    except Exception:
        return value


def load_settings():
    """Load settings from JSON file with decryption of sensitive fields."""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
            for k in SENSITIVE_KEYS:
                if k in data and data[k]:
                    if data[k].startswith('gAAAA'):
                        data[k] = decrypt_value(data[k])
            return data
        return {}
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return {}


def save_settings(settings):
    """Save settings to JSON file with encryption of sensitive fields."""
    try:
        data = settings.copy()
        for k in SENSITIVE_KEYS:
            if k in data and data[k] and not data[k].startswith('gAAAA'):
                data[k] = encrypt_value(data[k])
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving settings: {e}")


def update_setting(key, value):
    """Update a single setting."""
    settings = load_settings()
    settings[key] = value
    save_settings(settings)


# =============================================================================
# DATA PERSISTENCE
# =============================================================================
def load_notes():
    """Load notes from JSON file."""
    try:
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception:
        return []


def save_notes(notes):
    """Save notes to JSON file."""
    try:
        with open(NOTES_FILE, 'w') as f:
            json.dump(notes, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving notes: {e}")


def load_calendar():
    """Load calendar events from JSON file."""
    try:
        if os.path.exists(CALENDAR_FILE):
            with open(CALENDAR_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception:
        return []


def save_calendar(events):
    """Save calendar events to JSON file."""
    try:
        with open(CALENDAR_FILE, 'w') as f:
            json.dump(events, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving calendar: {e}")


def load_conversation_memory():
    """Load conversation memory from disk."""
    global CONVERSATION_MEMORY
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r') as f:
                CONVERSATION_MEMORY = json.load(f)
        # Keep only recent entries
        if len(CONVERSATION_MEMORY) > MAX_MEMORY_SIZE:
            CONVERSATION_MEMORY = CONVERSATION_MEMORY[-MAX_MEMORY_SIZE:]
    except Exception as e:
        logger.error(f"Error loading conversation memory: {e}")
        CONVERSATION_MEMORY = []


def save_conversation_memory():
    """Persist conversation memory to disk."""
    try:
        with open(MEMORY_FILE, 'w') as f:
            json.dump(CONVERSATION_MEMORY[-MAX_MEMORY_SIZE:], f, indent=2)
    except Exception as e:
        logger.error(f"Error saving conversation memory: {e}")


# =============================================================================
# TTS & SPEECH RECOGNITION
# =============================================================================
class SpeechEngine:
    """Manages text-to-speech and speech recognition."""

    def __init__(self):
        try:
            self.engine = pyttsx3.init('sapi5')
            self.engine.setProperty('rate', 150)
        except Exception as e:
            logger.error(f"TTS init error: {e}")
            self.engine = None
        self.recognizer = sr.Recognizer()
        try:
            self.voices = self.engine.getProperty('voices') if self.engine else []
        except Exception:
            self.voices = []

    def speak(self, text):
        """Convert text to speech."""
        if not self.engine:
            logger.warning("TTS engine not available")
            return
        logger.info(f"Speaking: {text[:80]}...")
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS error: {e}")

    def listen(self, callback=None, timeout=10, phrase_time_limit=7):
        """Listen for voice input and return transcribed text."""
        try:
            with sr.Microphone() as source:
                if callback:
                    callback('listening')
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                if callback:
                    callback('processing')
                query = self.recognizer.recognize_google(audio, language='en-in')
                logger.info(f"User said: {query}")
                return query.lower()
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.WaitTimeoutError:
            logger.warning("Listening timed out")
            return None
        except OSError as e:
            logger.error(f"Microphone error: {e}")
            return None
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            return None

    def listen_for_confirmation(self, timeout=8):
        """Listen for a yes/no confirmation from the user."""
        query = self.listen(timeout=timeout, phrase_time_limit=3)
        if query is None:
            return None
        if any(w in query for w in ['yes', 'yeah', 'yep', 'confirm', 'do it', 'go ahead']):
            return True
        if any(w in query for w in ['no', 'nope', 'cancel', 'stop', 'nevermind']):
            return False
        return None


# =============================================================================
# AI CHAT
# =============================================================================
class AIChat:
    """Manages conversation with GPT."""

    def __init__(self, api_key):
        self.api_key = api_key
        self.history = []

    def chat(self, prompt):
        """Send prompt to GPT and get response."""
        if not self.api_key:
            return "No API key configured. Please set your OpenAI API key in settings."

        try:
            openai.api_key = self.api_key
            self.history.append({"role": "user", "content": prompt})

            # Build context: system prompt + conversation memory + recent history
            messages = [
                {"role": "system", "content": (
                    "You are JARVIS, a helpful AI assistant. You are concise, friendly, "
                    "and helpful. Keep responses short unless asked for detail."
                )}
            ]

            # Add persistent conversation memory for context
            for entry in CONVERSATION_MEMORY[-5:]:
                messages.append({"role": "user", "content": entry['user']})
                messages.append({"role": "assistant", "content": entry['ai']})

            # Add current session history
            messages.extend(self.history[-MAX_MEMORY_SIZE:])

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )

            ai_response = response["choices"][0]["message"]["content"]
            self.history.append({"role": "assistant", "content": ai_response})

            # Store in persistent conversation memory
            CONVERSATION_MEMORY.append({
                'user': prompt,
                'ai': ai_response,
                'timestamp': datetime.datetime.now().isoformat()
            })
            save_conversation_memory()

            logger.info("AI response generated")
            return ai_response

        except openai.error.AuthenticationError:
            return "Invalid API key. Please check your OpenAI API key in settings."
        except openai.error.RateLimitError:
            return "Rate limit exceeded. Please wait a moment and try again."
        except openai.error.APIConnectionError:
            return "Cannot connect to OpenAI. Please check your internet connection."
        except Exception as e:
            logger.error(f"AI chat error: {e}")
            return f"AI Error: {str(e)}"

    def get_context_summary(self):
        """Get a summary of recent conversation context."""
        if not CONVERSATION_MEMORY:
            return "No previous conversation context."
        recent = CONVERSATION_MEMORY[-3:]
        lines = []
        for entry in recent:
            lines.append(f"  You: {entry['user'][:60]}")
            lines.append(f"  AI:  {entry['ai'][:60]}")
        return "\n".join(lines)


# =============================================================================
# COMMAND ROUTER
# =============================================================================
class CommandRouter:
    """Routes commands to appropriate handlers using intent classification."""

    # Intent categories and their trigger patterns
    INTENT_MAP = {
        'open_app': {
            'triggers': ['open', 'start', 'launch', 'run'],
            'patterns': ['open {app}', 'start {app}', 'launch {app}'],
        },
        'time': {
            'triggers': ['the time', 'current time', 'what time', 'time is it', 'what is the time'],
        },
        'weather': {
            'triggers': ['weather', 'temperature', 'forecast', 'how hot', 'how cold'],
        },
        'ai_chat': {
            'triggers': ['ask ai', 'chatgpt', 'gpt', 'assistant', 'ask jarvis', 'jarvis'],
        },
        'volume': {
            'triggers': ['volume up', 'volume down', 'increase volume', 'louder',
                         'decrease volume', 'quieter', 'mute'],
        },
        'shutdown': {
            'triggers': ['shutdown', 'shut down', 'turn off', 'power off'],
        },
        'restart': {
            'triggers': ['restart', 'reboot'],
        },
        'clipboard': {
            'triggers': ['clipboard', 'read my clipboard', 'paste from clipboard'],
        },
        'reminder': {
            'triggers': ['reminder', 'remind me', 'notify', 'notification'],
        },
        'note': {
            'triggers': ['add note', 'show notes', 'delete note', 'list notes',
                         'save note', 'my notes'],
        },
        'email': {
            'triggers': ['send email', 'email to', 'mail to', 'send mail'],
        },
        'screenshot': {
            'triggers': ['screenshot', 'take screenshot', 'capture screen', 'screen shot'],
        },
        'system_info': {
            'triggers': ['cpu usage', 'memory usage', 'ram usage', 'battery status',
                         'system info', 'system status'],
        },
        'timer': {
            'triggers': ['set timer', 'start timer', 'timer for', 'countdown',
                         'stop timer', 'cancel timer', 'timer status'],
        },
        'stopwatch': {
            'triggers': ['start stopwatch', 'stop stopwatch', 'reset stopwatch',
                         'show stopwatch', 'stopwatch time'],
        },
        'calendar': {
            'triggers': ['add event', 'show calendar', 'my calendar', 'list events',
                         'delete event', 'show events'],
        },
        'exit': {
            'triggers': ['exit', 'quit', 'close', 'bye', 'goodbye', 'see you'],
        },
        'help': {
            'triggers': ['help', 'what can you do', 'commands', 'usage'],
        },
    }

    # App name synonyms
    APP_SYNONYMS = {
        'chrome': ['chrome', 'browser', 'google chrome', 'web browser', 'internet'],
        'notepad': ['notepad', 'editor', 'text editor', 'write'],
        'explorer': ['explorer', 'file explorer', 'files', 'my computer', 'folders'],
        'spotify': ['spotify', 'music', 'music player', 'play music', 'songs'],
        'calculator': ['calculator', 'calc', 'calculation', 'math', 'calculate'],
        'vlc': ['vlc', 'media player', 'video player', 'play video'],
        'netflix': ['netflix', 'movies', 'tv shows', 'watch netflix'],
        'youtube': ['youtube', 'videos', 'watch youtube'],
    }

    # App launch targets
    APP_TARGETS = {
        'spotify': 'spotify',
        'chrome': 'chrome',
        'notepad': 'notepad',
        'explorer': 'explorer',
        'netflix': 'https://www.netflix.com',
        'youtube': 'https://www.youtube.com',
        'calculator': 'calc',
        'vlc': 'vlc',
    }

    def __init__(self, speech_engine, ai_chat, settings):
        self.speech = speech_engine
        self.ai = ai_chat
        self.settings = settings
        self.plugin_commands = []
        self._log_callback = None

        # Register built-in command handlers
        self.handlers = {
            'open_app': self._handle_open_app,
            'time': self._handle_time,
            'weather': self._handle_weather,
            'ai_chat': self._handle_ai_chat,
            'volume': self._handle_volume,
            'shutdown': self._handle_shutdown,
            'restart': self._handle_restart,
            'clipboard': self._handle_clipboard,
            'reminder': self._handle_reminder,
            'note': self._handle_note,
            'email': self._handle_email,
            'screenshot': self._handle_screenshot,
            'system_info': self._handle_system_info,
            'timer': self._handle_timer,
            'stopwatch': self._handle_stopwatch,
            'calendar': self._handle_calendar,
            'exit': self._handle_exit,
            'help': self._handle_help,
        }

    def set_log_callback(self, callback):
        """Set the callback function for logging messages to the GUI."""
        self._log_callback = callback

    def log_to_gui(self, text, tag='system'):
        """Send a log message to the GUI if available."""
        if self._log_callback:
            self._log_callback(text, tag)

    def register_plugin_commands(self, commands):
        """Register commands from the plugin manager."""
        self.plugin_commands = commands
        logger.info(f"Registered {len(commands)} plugin commands")

    def classify_intent(self, query):
        """Classify the intent of a user query. Returns (intent, confidence)."""
        query_lower = query.lower().strip()

        # Check plugin commands first (highest priority)
        for cmd in self.plugin_commands:
            if any(trigger in query_lower for trigger in cmd.get('triggers', [])):
                return 'plugin', cmd

        # Check each intent
        best_intent = None
        best_score = 0

        for intent, config in self.INTENT_MAP.items():
            triggers = config.get('triggers', [])
            score = 0
            for trigger in triggers:
                if trigger in query_lower:
                    # Longer matches = higher confidence
                    score = max(score, len(trigger) / len(query_lower))
            if score > best_score:
                best_score = score
                best_intent = intent

        return best_intent, best_score

    def match_app_name(self, query):
        """Match an app name from the query using synonyms."""
        query_lower = query.lower()
        for app_name, synonyms in self.APP_SYNONYMS.items():
            for synonym in synonyms:
                if synonym in query_lower:
                    return app_name
        return None

    def route(self, query):
        """Route a query to the appropriate handler. Returns 'exit' to signal quit."""
        query = query.strip()
        if not query:
            return False

        intent, match = self.classify_intent(query)

        if intent is None:
            self.speech.speak("I didn't recognize that command. Say 'help' for available commands.")
            return False

        # Plugin command
        if intent == 'plugin':
            try:
                match['handler'](query, self.speech.speak, self._log_to_file)
                return True
            except Exception as e:
                logger.error(f"Plugin error: {e}")
                self.speech.speak("A plugin encountered an error.")
                return True

        # Built-in command
        handler = self.handlers.get(intent)
        if handler:
            try:
                result = handler(query)
                if result == 'exit':
                    return 'exit'
                return True
            except Exception as e:
                logger.error(f"Command handler error ({intent}): {e}")
                self.speech.speak(f"Error executing {intent} command.")
                return True

        return False

    def _log_to_file(self, text):
        """Log text to the session log file."""
        try:
            with open(LOG_FILE, 'a') as f:
                f.write(f"{datetime.datetime.now()}: {text}\n")
        except Exception:
            pass

    # =========================================================================
    # COMMAND HANDLERS
    # =========================================================================

    def _handle_open_app(self, query):
        """Open an application."""
        app_name = self.match_app_name(query)
        if app_name and app_name in self.APP_TARGETS:
            target = self.APP_TARGETS[app_name]
            if target.startswith('http'):
                webbrowser.open(target)
            else:
                os.system(f'start {target}')
            self.speech.speak(f"Opening {app_name}")
        else:
            self.speech.speak("Sorry, I don't know how to open that app.")

    def _handle_time(self, query):
        """Get current time."""
        str_time = datetime.datetime.now().strftime("%I:%M %p")
        self.speech.speak(f"Sir, the time is {str_time}")

    def _handle_weather(self, query):
        """Get weather information."""
        city = self.settings.get('default_city', '')
        if not city:
            city = simpledialog.askstring("Set City", "Please enter your city:")
            if city:
                update_setting('default_city', city)
                self.settings['default_city'] = city
            else:
                self.speech.speak("City not set. Please try again.")
                return

        search = f"temperature in {city}"
        url = f"https://www.google.com/search?q={search}"
        try:
            r = requests.get(url, timeout=10)
            data = BeautifulSoup(r.text, "html.parser")
            temp_element = data.find("div", class_="BNeawe")
            if temp_element:
                temp = temp_element.text
                self.speech.speak(f"Current temperature in {city} is {temp}")
            else:
                self.speech.speak("Sorry, I couldn't fetch the temperature.")
        except requests.RequestException as e:
            logger.error(f"Weather fetch error: {e}")
            self.speech.speak("Sorry, I couldn't fetch the weather. Check your internet connection.")

    def _handle_ai_chat(self, query):
        """Chat with GPT."""
        prompt = query
        for keyword in ['ask ai', 'chatgpt', 'gpt', 'assistant', 'jarvis']:
            prompt = prompt.replace(keyword, '')
        prompt = prompt.strip()
        if not prompt:
            self.speech.speak("What would you like to ask?")
            return
        response = self.ai.chat(prompt)
        self.speech.speak(response)

    def _handle_volume(self, query):
        """Adjust system volume."""
        if any(w in query for w in ['volume up', 'increase volume', 'louder']):
            pyautogui.press("volumeup")
            self.speech.speak("Volume increased")
        elif any(w in query for w in ['volume down', 'decrease volume', 'quieter']):
            pyautogui.press("volumedown")
            self.speech.speak("Volume decreased")
        elif 'mute' in query:
            pyautogui.press("volumemute")
            self.speech.speak("Volume muted")

    def _handle_shutdown(self, query):
        """Shut down the PC with confirmation."""
        self.speech.speak("Are you sure you want to shut down your PC?")
        self.log_to_gui("Confirming shutdown...", 'system')
        confirmed = self.speech.listen_for_confirmation(timeout=8)
        if confirmed is True:
            self.speech.speak("Shutting down your PC. Goodbye!")
            os.system("shutdown /s /t 1")
        elif confirmed is False:
            self.speech.speak("Shutdown cancelled.")
        else:
            self.speech.speak("I didn't hear a confirmation. Shutdown cancelled.")

    def _handle_restart(self, query):
        """Restart the PC with confirmation."""
        self.speech.speak("Are you sure you want to restart your PC?")
        self.log_to_gui("Confirming restart...", 'system')
        confirmed = self.speech.listen_for_confirmation(timeout=8)
        if confirmed is True:
            self.speech.speak("Restarting your PC. Goodbye!")
            os.system("shutdown /r /t 1")
        elif confirmed is False:
            self.speech.speak("Restart cancelled.")
        else:
            self.speech.speak("I didn't hear a confirmation. Restart cancelled.")

    def _handle_clipboard(self, query):
        """Read clipboard contents."""
        content = pyperclip.paste()
        if content:
            self.speech.speak(f"Clipboard content: {content}")
        else:
            self.speech.speak("Clipboard is empty.")

    def _handle_reminder(self, query):
        """Send a reminder notification."""
        notification.notify(
            title="JARVIS Reminder",
            message="This is a reminder from JARVIS AI Assistant.",
            timeout=5
        )
        self.speech.speak("Reminder notification sent.")

    def _handle_note(self, query):
        """Manage notes."""
        notes = load_notes()
        query_lower = query.lower()

        if 'add note' in query_lower or 'save note' in query_lower:
            note = query.split('note', 1)[-1].strip()
            if not note:
                note = simpledialog.askstring("Add Note", "What should I remember?")
            if note:
                notes.append(note)
                save_notes(notes)
                self.speech.speak("Note added.")
            else:
                self.speech.speak("Note cancelled.")

        elif 'show notes' in query_lower or 'list notes' in query_lower or 'my notes' in query_lower:
            if notes:
                self.speech.speak(f"You have {len(notes)} notes.")
                for i, note in enumerate(notes[:5], 1):
                    self.log_to_gui(f"{i}. {note}", 'system')
                if len(notes) > 5:
                    self.log_to_gui(f"...and {len(notes) - 5} more", 'system')
            else:
                self.speech.speak("You have no notes.")

        elif 'delete note' in query_lower:
            # Try to match note text in query
            idx = None
            for i, n in enumerate(notes):
                if n.lower() in query_lower:
                    idx = i
                    break
            if idx is None and notes:
                idx = simpledialog.askinteger("Delete Note", f"Enter note number to delete (1-{len(notes)}):")
                if idx:
                    idx -= 1
            if idx is not None and 0 <= idx < len(notes):
                removed = notes.pop(idx)
                save_notes(notes)
                self.speech.speak("Note deleted.")
                self.log_to_gui(f"Deleted: {removed}", 'system')
            else:
                self.speech.speak("Could not find that note.")

    def _handle_email(self, query):
        """Send email (requires configuration)."""
        settings = load_settings()
        from_addr = settings.get('email_address', '')
        password = settings.get('email_password', '')
        if not from_addr or not password:
            self.speech.speak("Email not configured. Please add your email and app password to settings.")
            return

        # Try to extract recipient from query
        to_match = re.search(r'(?:to|email to|mail to)\s+(\S+@\S+)', query)
        to_addr = to_match.group(1) if to_match else simpledialog.askstring("Recipient", "Recipient email:")
        subject = simpledialog.askstring("Subject", "Email subject:")
        msg_body = simpledialog.askstring("Message", "Email message:")

        if not to_addr or not subject or not msg_body:
            self.speech.speak("Email cancelled.")
            return

        try:
            msg = smtplib.MIMEMultipart()
            msg['From'] = from_addr
            msg['To'] = to_addr
            msg['Subject'] = subject
            msg.attach(smtplib.MIMEText(msg_body, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_addr, password)
            server.sendmail(from_addr, to_addr, msg.as_string())
            server.quit()
            self.speech.speak("Email sent successfully.")
            self.log_to_gui(f"Email sent to {to_addr}", 'system')
        except smtplib.SMTPAuthenticationError:
            self.speech.speak("Email authentication failed. Check your credentials.")
        except Exception as e:
            logger.error(f"Email error: {e}")
            self.speech.speak("Failed to send email.")

    def _handle_screenshot(self, query):
        """Take a screenshot."""
        try:
            from PIL import ImageGrab
            screenshots_dir = os.path.join(BASE_DIR, 'screenshots')
            os.makedirs(screenshots_dir, exist_ok=True)
            filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(screenshots_dir, filename)
            img = ImageGrab.grab()
            img.save(filepath)
            self.speech.speak(f"Screenshot saved.")
            self.log_to_gui(f"Screenshot: {filepath}", 'system')
        except ImportError:
            self.speech.speak("Screenshot feature requires Pillow with ImageGrab support.")
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            self.speech.speak("Failed to take screenshot.")

    def _handle_system_info(self, query):
        """Get system information."""
        if not HAS_PSUTIL:
            self.speech.speak("System monitoring requires psutil. Install it with pip install psutil.")
            return

        query_lower = query.lower()
        if 'cpu' in query_lower:
            cpu = psutil.cpu_percent(interval=1)
            self.speech.speak(f"CPU usage is {cpu} percent")
        elif 'memory' in query_lower or 'ram' in query_lower:
            mem = psutil.virtual_memory()
            self.speech.speak(f"Memory usage is {mem.percent} percent")
        elif 'battery' in query_lower:
            battery = psutil.sensors_battery()
            if battery:
                self.speech.speak(f"Battery is at {battery.percent} percent")
            else:
                self.speech.speak("Battery status not available")

    def _handle_timer(self, query):
        """Set or manage a timer."""
        global TIMER_RUNNING, TIMER_END
        query_lower = query.lower()

        if 'stop timer' in query_lower or 'cancel timer' in query_lower:
            if TIMER_RUNNING:
                TIMER_RUNNING = False
                self.speech.speak("Timer cancelled.")
            else:
                self.speech.speak("No timer running.")
            return

        if 'timer status' in query_lower or 'time left' in query_lower:
            if TIMER_RUNNING and TIMER_END:
                left = int(TIMER_END - time.time())
                if left > 0:
                    self.speech.speak(f"{left} seconds left on the timer.")
                else:
                    self.speech.speak("Timer is about to finish.")
            else:
                self.speech.speak("No timer running.")
            return

        # Set new timer
        time_match = re.search(r'(\d+)\s*(second|minute|hour)s?', query_lower)
        if not time_match:
            self.speech.speak("Please specify timer duration, like 'set timer for 5 minutes'.")
            return

        amount = int(time_match.group(1))
        unit = time_match.group(2)
        seconds = amount * (1 if 'second' in unit else 60 if 'minute' in unit else 3600)

        TIMER_RUNNING = True
        TIMER_END = time.time() + seconds

        def timer_thread():
            global TIMER_RUNNING
            while TIMER_RUNNING and time.time() < TIMER_END:
                time.sleep(1)
            if TIMER_RUNNING:
                TIMER_RUNNING = False
                self.speech.speak("Timer finished!")
                notification.notify(title="JARVIS Timer", message="Timer finished!", timeout=5)

        threading.Thread(target=timer_thread, daemon=True).start()
        self.speech.speak(f"Timer set for {amount} {unit}{'s' if amount > 1 else ''}.")

    def _handle_stopwatch(self, query):
        """Manage stopwatch."""
        global STOPWATCH_RUNNING, STOPWATCH_START, STOPWATCH_ELAPSED
        query_lower = query.lower()

        if 'start' in query_lower:
            if not STOPWATCH_RUNNING:
                STOPWATCH_RUNNING = True
                STOPWATCH_START = time.time() - STOPWATCH_ELAPSED
                self.speech.speak("Stopwatch started.")
            else:
                self.speech.speak("Stopwatch already running.")
        elif 'stop' in query_lower or 'pause' in query_lower:
            if STOPWATCH_RUNNING:
                STOPWATCH_ELAPSED = time.time() - STOPWATCH_START
                STOPWATCH_RUNNING = False
                self.speech.speak(f"Stopwatch stopped at {int(STOPWATCH_ELAPSED)} seconds.")
            else:
                self.speech.speak("Stopwatch is not running.")
        elif 'reset' in query_lower:
            STOPWATCH_RUNNING = False
            STOPWATCH_ELAPSED = 0
            self.speech.speak("Stopwatch reset.")
        else:
            # Show current time
            elapsed = time.time() - STOPWATCH_START if STOPWATCH_RUNNING else STOPWATCH_ELAPSED
            self.speech.speak(f"Stopwatch time is {int(elapsed)} seconds.")

    def _handle_calendar(self, query):
        """Manage calendar events."""
        events = load_calendar()
        query_lower = query.lower()

        if 'add event' in query_lower or 'add meeting' in query_lower:
            title_match = re.search(r'(?:add event|add meeting|add appointment)\s+(.+?)(?:\s+at\s+|\s+on\s+|$)', query)
            time_match = re.search(r'\s+(?:at|on)\s+(.+)', query)
            title = title_match.group(1).strip() if title_match else simpledialog.askstring("Event Title", "Event title:")
            time_str = time_match.group(1).strip() if time_match else simpledialog.askstring("Event Time", "When is the event?")

            if not title or not time_str:
                self.speech.speak("Event cancelled.")
                return

            events.append({'title': title, 'time': time_str})
            save_calendar(events)
            self.speech.speak(f"Event '{title}' added for {time_str}.")

        elif 'show' in query_lower or 'list' in query_lower:
            if events:
                self.speech.speak(f"You have {len(events)} events.")
                for i, e in enumerate(events[:5], 1):
                    self.log_to_gui(f"{i}. {e['title']} at {e['time']}", 'system')
            else:
                self.speech.speak("You have no events.")

        elif 'delete' in query_lower or 'remove' in query_lower:
            idx = None
            for i, e in enumerate(events):
                if e['title'].lower() in query_lower:
                    idx = i
                    break
            if idx is None and events:
                idx = simpledialog.askinteger("Delete Event", f"Enter event number (1-{len(events)}):")
                if idx:
                    idx -= 1
            if idx is not None and 0 <= idx < len(events):
                removed = events.pop(idx)
                save_calendar(events)
                self.speech.speak("Event deleted.")
            else:
                self.speech.speak("Could not find that event.")

    def _handle_exit(self, query):
        """Exit JARVIS."""
        self.speech.speak("Goodbye!")
        return 'exit'

    def _handle_help(self, query):
        """Show help information."""
        help_text = (
            "Available commands: "
            "Open apps, tell time, check weather, ask AI, "
            "volume control, take screenshot, manage notes, "
            "set timers, system info, and more. "
            "Say 'help' anytime for this list."
        )
        self.speech.speak(help_text)
        self.log_to_gui("JARVIS Help - Say any command or type it in the input field.", 'system')
        self.log_to_gui("Examples: 'open chrome', 'what time is it', 'ask AI what is Python'", 'system')


# =============================================================================
# PLUGIN SYSTEM
# =============================================================================
class PluginManager:
    """Manages loading and registration of plugins."""

    def __init__(self, plugins_dir):
        self.plugins_dir = plugins_dir
        self.plugin_commands = []

    def load_plugins(self):
        """Load all plugins from the plugins directory."""
        if not os.path.isdir(self.plugins_dir):
            os.makedirs(self.plugins_dir, exist_ok=True)
            return

        for plugin_path in glob.glob(os.path.join(self.plugins_dir, '*.py')):
            name = os.path.splitext(os.path.basename(plugin_path))[0]
            if name.startswith('_'):
                continue

            spec = importlib.util.spec_from_file_location(name, plugin_path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(mod)
                    if hasattr(mod, 'register'):
                        commands = []

                        def add_command_handler(trigger_words, handler, description=None):
                            commands.append({
                                'triggers': trigger_words,
                                'handler': handler,
                                'description': description
                            })

                        mod.register({'add_command': add_command_handler})
                        self.plugin_commands.extend(commands)
                        logger.info(f"Loaded plugin: {name} ({len(commands)} commands)")
                except Exception as e:
                    logger.error(f"Error loading plugin {name}: {e}")

    def get_commands(self):
        """Return all loaded plugin commands."""
        return self.plugin_commands


# =============================================================================
# MODERN GUI
# =============================================================================
class JarvisGUI:
    """Modern GUI for JARVIS AI Assistant."""

    THEMES = {
        'Dark': {
            'bg': '#1a1a2e', 'bg_secondary': '#16213e', 'accent': '#0f3460',
            'accent_light': '#4f8ef7', 'text': '#e0e0e0', 'text_secondary': '#a0a0a0',
            'success': '#00c853', 'warning': '#ffc107', 'error': '#ff5252',
            'button_bg': '#0f3460', 'button_hover': '#4f8ef7',
        },
        'Light': {
            'bg': '#f5f5f5', 'bg_secondary': '#ffffff', 'accent': '#1a237e',
            'accent_light': '#4f8ef7', 'text': '#212121', 'text_secondary': '#757575',
            'success': '#00c853', 'warning': '#ffc107', 'error': '#ff5252',
            'button_bg': '#1a237e', 'button_hover': '#4f8ef7',
        },
        'Blue': {
            'bg': '#0d1b2a', 'bg_secondary': '#1b2838', 'accent': '#1b4965',
            'accent_light': '#62b6cb', 'text': '#e0e0e0', 'text_secondary': '#a0a0a0',
            'success': '#00c853', 'warning': '#ffc107', 'error': '#ff5252',
            'button_bg': '#1b4965', 'button_hover': '#62b6cb',
        },
        'Gold': {
            'bg': '#2d2d2d', 'bg_secondary': '#3d3d3d', 'accent': '#b8860b',
            'accent_light': '#ffd700', 'text': '#f0f0f0', 'text_secondary': '#b0b0b0',
            'success': '#00c853', 'warning': '#ffc107', 'error': '#ff5252',
            'button_bg': '#b8860b', 'button_hover': '#ffd700',
        }
    }

    STATUS_COLORS = {
        'idle': '#757575', 'listening': '#00c853', 'processing': '#ffc107',
        'speaking': '#4f8ef7', 'error': '#ff5252',
    }

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JARVIS AI Assistant")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Load persistent data
        self.settings = load_settings()
        self.current_theme = self.settings.get('theme', 'Dark')
        load_conversation_memory()

        # Initialize engines
        self.speech_engine = SpeechEngine()
        self.ai_chat = AIChat(self.settings.get('openai_api_key', ''))
        self.command_router = CommandRouter(self.speech_engine, self.ai_chat, self.settings)
        self.command_router.set_log_callback(self._log_message)

        # Load plugins and wire them to the router
        self.plugin_manager = PluginManager(PLUGINS_DIR)
        self.plugin_manager.load_plugins()
        self.command_router.register_plugin_commands(self.plugin_manager.get_commands())

        # State
        self.listening = False
        self.status = 'idle'
        self._tray_thread = None

        # Build GUI
        self._build_gui()
        self._apply_theme(self.current_theme)

        # System tray
        self.tray_icon = None
        if HAS_PYSTRAY:
            self._setup_system_tray()

        # Window protocol
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_gui(self):
        """Build the modern GUI layout."""
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._build_header()
        self._build_status_bar()

        self.content_frame = tk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self._build_chat_panel()
        self._build_control_panel()
        self._build_input_area()

    def _build_header(self):
        """Build the header with title and theme selector."""
        header = tk.Frame(self.main_frame)
        header.pack(fill=tk.X, pady=(0, 10))

        self.title_label = tk.Label(header, text="J.A.R.V.I.S", font=("Segoe UI", 28, "bold"))
        self.title_label.pack(side=tk.LEFT)

        self.subtitle_label = tk.Label(header, text="AI Assistant", font=("Segoe UI", 12))
        self.subtitle_label.pack(side=tk.LEFT, padx=(10, 0), pady=(10, 0))

        theme_frame = tk.Frame(header)
        theme_frame.pack(side=tk.RIGHT)

        self.theme_label = tk.Label(theme_frame, text="Theme:", font=("Segoe UI", 10))
        self.theme_label.pack(side=tk.LEFT, padx=(0, 5))

        self.theme_var = tk.StringVar(value=self.current_theme)
        self.theme_menu = tk.OptionMenu(
            theme_frame, self.theme_var, *self.THEMES.keys(),
            command=self._on_theme_change
        )
        self.theme_menu.config(font=("Segoe UI", 10))
        self.theme_menu.pack(side=tk.LEFT)

    def _build_status_bar(self):
        """Build the status indicator bar."""
        self.status_frame = tk.Frame(self.main_frame, height=40)
        self.status_frame.pack(fill=tk.X, pady=(0, 10))
        self.status_frame.pack_propagate(False)

        self.status_canvas = tk.Canvas(self.status_frame, width=20, height=20, highlightthickness=0)
        self.status_canvas.pack(side=tk.LEFT, padx=(0, 10))

        self.status_label = tk.Label(self.status_frame, text="Ready", font=("Segoe UI", 12, "bold"))
        self.status_label.pack(side=tk.LEFT)

        self.status_detail = tk.Label(
            self.status_frame,
            text="Click Speak or type a command to begin",
            font=("Segoe UI", 10)
        )
        self.status_detail.pack(side=tk.LEFT, padx=(10, 0))

        self._update_status('idle')

    def _build_chat_panel(self):
        """Build the chat/log display panel."""
        left_panel = tk.Frame(self.content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        log_header = tk.Label(left_panel, text="Conversation", font=("Segoe UI", 12, "bold"))
        log_header.pack(anchor=tk.W, pady=(0, 5))

        self.chat_display = tk.Text(
            left_panel, font=("Consolas", 11), wrap=tk.WORD,
            state=tk.DISABLED, padx=10, pady=10, height=15
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        chat_scroll = tk.Scrollbar(self.chat_display, command=self.chat_display.yview)
        chat_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_display.config(yscrollcommand=chat_scroll.set)

        # Text tags for styling
        self.chat_display.tag_config('user', foreground='#4f8ef7', font=("Consolas", 11, "bold"))
        self.chat_display.tag_config('ai', foreground='#00c853', font=("Consolas", 11))
        self.chat_display.tag_config('system', foreground='#ffc107', font=("Consolas", 10, "italic"))
        self.chat_display.tag_config('error', foreground='#ff5252', font=("Consolas", 10))

    def _build_control_panel(self):
        """Build the control panel with buttons."""
        right_panel = tk.Frame(self.content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        controls_label = tk.Label(right_panel, text="Controls", font=("Segoe UI", 12, "bold"))
        controls_label.pack(anchor=tk.W, pady=(0, 10))

        # Voice button (prominent)
        self.speak_btn = tk.Button(
            right_panel, text="🎙️ Speak", font=("Segoe UI", 14, "bold"),
            command=self._on_speak, relief=tk.FLAT, cursor="hand2", height=2
        )
        self.speak_btn.pack(fill=tk.X, pady=(0, 10))

        # Quick actions
        quick_label = tk.Label(right_panel, text="Quick Actions", font=("Segoe UI", 10, "bold"))
        quick_label.pack(anchor=tk.W, pady=(5, 5))

        self._make_btn(right_panel, "⏰ Time", self._get_time).pack(fill=tk.X, pady=2)
        self._make_btn(right_panel, "🌤️ Weather", self._get_weather).pack(fill=tk.X, pady=2)
        self._make_btn(right_panel, "📸 Screenshot", self._take_screenshot).pack(fill=tk.X, pady=2)
        self._make_btn(right_panel, "🔍 Web Search", self._web_search).pack(fill=tk.X, pady=2)
        self._make_btn(right_panel, "✉️ Email", self._open_email).pack(fill=tk.X, pady=2)

        # Settings
        settings_label = tk.Label(right_panel, text="Settings", font=("Segoe UI", 10, "bold"))
        settings_label.pack(anchor=tk.W, pady=(15, 5))

        self._make_btn(right_panel, "⚙️ Settings", self._open_settings).pack(fill=tk.X, pady=2)

        # Help & Exit
        self._make_btn(right_panel, "❓ Help", self._show_help).pack(fill=tk.X, pady=(15, 2))
        self._make_btn(right_panel, "❌ Quit", self._on_close).pack(fill=tk.X, pady=2)

    def _build_input_area(self):
        """Build the input area at the bottom."""
        # Command input
        input_frame = tk.Frame(self.main_frame)
        input_frame.pack(fill=tk.X, pady=(10, 0))

        cmd_label = tk.Label(input_frame, text="Command:", font=("Segoe UI", 10))
        cmd_label.pack(side=tk.LEFT, padx=(0, 5))

        self.input_entry = tk.Entry(input_frame, font=("Segoe UI", 12), relief=tk.FLAT, bd=2)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_entry.bind('<Return>', self._on_send_command)

        self._make_btn(input_frame, "Send", self._on_send_command).pack(side=tk.RIGHT)

        # AI input
        ai_frame = tk.Frame(self.main_frame)
        ai_frame.pack(fill=tk.X, pady=(5, 0))

        ai_label = tk.Label(ai_frame, text="Ask AI:", font=("Segoe UI", 10))
        ai_label.pack(side=tk.LEFT, padx=(0, 5))

        self.ai_input = tk.Entry(ai_frame, font=("Segoe UI", 12), relief=tk.FLAT, bd=2)
        self.ai_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.ai_input.bind('<Return>', self._on_ask_ai)

        self._make_btn(ai_frame, "Ask AI", self._on_ask_ai).pack(side=tk.RIGHT)

    def _make_btn(self, parent, text, command):
        """Create a styled button."""
        return tk.Button(
            parent, text=text, font=("Segoe UI", 11),
            command=command, relief=tk.FLAT, cursor="hand2", height=1
        )

    # =========================================================================
    # THEME & STATUS
    # =========================================================================

    def _apply_theme(self, theme_name):
        """Apply the selected theme."""
        theme = self.THEMES.get(theme_name, self.THEMES['Dark'])
        self.current_theme = theme_name

        self.root.configure(bg=theme['bg'])
        self.main_frame.configure(bg=theme['bg'])
        self.title_label.configure(bg=theme['bg'], fg=theme['accent_light'])
        self.subtitle_label.configure(bg=theme['bg'], fg=theme['text_secondary'])
        self.theme_label.configure(bg=theme['bg'], fg=theme['text'])
        self.status_frame.configure(bg=theme['bg_secondary'])
        self.status_label.configure(bg=theme['bg_secondary'], fg=theme['text'])
        self.status_detail.configure(bg=theme['bg_secondary'], fg=theme['text_secondary'])
        self.chat_display.configure(bg=theme['bg_secondary'], fg=theme['text'], insertbackground=theme['text'])
        self.input_entry.configure(bg=theme['bg_secondary'], fg=theme['text'])
        self.ai_input.configure(bg=theme['bg_secondary'], fg=theme['text'])

        self._update_status(self.status)
        update_setting('theme', theme_name)

    def _update_status(self, status):
        """Update the status indicator."""
        self.status = status
        color = self.STATUS_COLORS.get(status, '#757575')
        self.status_canvas.delete('all')
        self.status_canvas.create_oval(2, 2, 18, 18, fill=color, outline=color)

        texts = {
            'idle': 'Ready', 'listening': 'Listening...',
            'processing': 'Processing...', 'speaking': 'Speaking...', 'error': 'Error'
        }
        self.status_label.config(text=texts.get(status, 'Ready'))

    # =========================================================================
    # LOGGING
    # =========================================================================

    def _log_message(self, text, tag='system'):
        """Add a message to the chat display (thread-safe)."""
        def _insert():
            self.chat_display.config(state=tk.NORMAL)
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            prefix = {
                'user': f"[{timestamp}] You: ",
                'ai': f"[{timestamp}] JARVIS: ",
                'system': f"[{timestamp}] ",
                'error': f"[{timestamp}] ⚠ ",
            }.get(tag, f"[{timestamp}] ")

            self.chat_display.insert(tk.END, prefix, tag)
            self.chat_display.insert(tk.END, f"{text}\n")
            self.chat_display.config(state=tk.DISABLED)
            self.chat_display.see(tk.END)

            try:
                with open(LOG_FILE, 'a') as f:
                    f.write(f"{timestamp} [{tag}] {text}\n")
            except Exception:
                pass

        # Always schedule on main thread
        if threading.current_thread() is threading.main_thread():
            _insert()
        else:
            self.root.after(0, _insert)

    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================

    def _on_speak(self):
        """Handle speak button click."""
        if self.listening:
            return
        self.listening = True
        self._update_status('listening')
        self._log_message('Listening...', 'system')

        def listen_thread():
            query = self.speech_engine.listen(callback=self._update_status)
            self.listening = False

            if query:
                self._log_message(query, 'user')
                self._update_status('processing')

                result = self.command_router.route(query)
                if result == 'exit':
                    self.root.after(0, self._on_close)
                else:
                    self._update_status('idle')
            else:
                self._log_message('Could not understand. Please try again.', 'error')
                self._update_status('idle')

        threading.Thread(target=listen_thread, daemon=True).start()

    def _on_send_command(self, event=None):
        """Handle send command."""
        query = self.input_entry.get().strip()
        if not query:
            return
        self.input_entry.delete(0, tk.END)
        self._log_message(query, 'user')
        self._update_status('processing')

        def process():
            result = self.command_router.route(query)
            if result == 'exit':
                self.root.after(0, self._on_close)
            else:
                self._update_status('idle')

        threading.Thread(target=process, daemon=True).start()

    def _on_ask_ai(self, event=None):
        """Handle ask AI."""
        query = self.ai_input.get().strip()
        if not query:
            return
        self.ai_input.delete(0, tk.END)
        self._log_message(query, 'user')
        self._update_status('processing')

        def ai_chat():
            response = self.ai_chat.chat(query)
            self._log_message(response, 'ai')
            self.speech_engine.speak(response)
            self._update_status('idle')

        threading.Thread(target=ai_chat, daemon=True).start()

    def _get_time(self):
        str_time = datetime.datetime.now().strftime("%I:%M %p")
        self._log_message(f"The time is {str_time}", 'ai')
        threading.Thread(target=self.speech_engine.speak, args=(f"The time is {str_time}",), daemon=True).start()

    def _get_weather(self):
        def fetch():
            self._update_status('processing')
            self.command_router._handle_weather("weather")
            self._update_status('idle')
        threading.Thread(target=fetch, daemon=True).start()

    def _take_screenshot(self):
        self.command_router._handle_screenshot("screenshot")

    def _set_api_key(self):
        key = simpledialog.askstring("API Key", "Enter your OpenAI API key:", show='*')
        if key:
            update_setting('openai_api_key', key)
            self.settings['openai_api_key'] = key
            self.ai_chat.api_key = key
            self._log_message('API key updated successfully', 'system')

    def _set_city(self):
        city = simpledialog.askstring("Set City", "Enter your city:")
        if city:
            update_setting('default_city', city)
            self.settings['default_city'] = city
            self._log_message(f'City set to {city}', 'system')

    def _open_settings(self):
        """Open the settings GUI window."""
        self._log_message('Opening settings...', 'system')
        self.command_router.route('open settings')

    def _open_email(self):
        """Open the email composition window."""
        self._log_message('Opening email...', 'system')
        self.command_router.route('compose email')

    def _web_search(self):
        """Prompt for a web search."""
        query = simpledialog.askstring("Web Search", "What would you like to search for?")
        if query:
            self._log_message(f'Searching: {query}', 'user')
            self._update_status('processing')

            def do_search():
                self.command_router.route(f'search {query}')
                self._update_status('idle')

            threading.Thread(target=do_search, daemon=True).start()

    def _show_help(self):
        help_text = """JARVIS AI Assistant - Commands

Voice & Text Commands:
  Open [app]        Launch applications
  What time is it   Get current time
  Weather           Get weather info
  Search [query]    Search the web
  Ask AI [question] Chat with GPT
  Volume up/down    Adjust volume
  Take screenshot   Capture screen
  Add note [text]   Save a note
  Show notes        View saved notes
  Set timer for X   Set a countdown timer
  Send email        Open email window
  Settings          Open settings window
  Shutdown          Shut down PC (with confirmation)
  Help              Show this help

Tips:
  • Click Speak or type in the Command field
  • Use Ask AI field for conversational queries
  • Click Settings to configure API key, city, theme, email
  • Click Email to compose and send emails
  • Click Web Search to search the internet

Developed by Sarthak & Meet"""
        messagebox.showinfo("JARVIS Help", help_text)

    def _on_theme_change(self, theme_name):
        self._apply_theme(theme_name)

    # =========================================================================
    # SYSTEM TRAY
    # =========================================================================

    def _setup_system_tray(self):
        """Setup system tray icon."""
        try:
            icon_image = Image.new('RGB', (64, 64), color='#4f8ef7')
            menu = pystray.Menu(
                pystray.MenuItem("Show", self._show_window),
                pystray.MenuItem("Speak", self._tray_speak),
                pystray.MenuItem("Quit", self._quit_from_tray)
            )
            self.tray_icon = pystray.Icon("JARVIS", icon_image, "JARVIS AI Assistant", menu)
        except Exception as e:
            logger.error(f"Failed to setup system tray: {e}")
            self.tray_icon = None

    def _show_window(self, icon=None, item=None):
        self.root.after(0, self._do_show_window)

    def _do_show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _tray_speak(self, icon=None, item=None):
        self.root.after(0, self._on_speak)

    def _quit_from_tray(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self._force_quit)

    def _minimize_to_tray(self):
        """Minimize window to system tray."""
        if self.tray_icon:
            self.root.withdraw()
            self._tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            self._tray_thread.start()
        else:
            self.root.iconify()

    # =========================================================================
    # WINDOW CLOSE
    # =========================================================================

    def _on_close(self):
        """Handle window close - minimize to tray instead of quitting."""
        if self.tray_icon:
            self._minimize_to_tray()
        else:
            if messagebox.askokcancel("Quit", "Are you sure you want to quit JARVIS?"):
                self._force_quit()

    def _force_quit(self):
        """Force quit the application."""
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        save_conversation_memory()
        self.root.quit()
        self.root.destroy()

    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
def main():
    """Main entry point for JARVIS AI Assistant."""
    logger.info("Starting JARVIS AI Assistant...")

    try:
        gui = JarvisGUI()
        gui.run()
    except Exception as e:
        logger.error(f"JARVIS startup error: {e}", exc_info=True)
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("JARVIS Error", f"Failed to start JARVIS:\n\n{traceback.format_exc()}")
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
