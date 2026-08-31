"""
Settings GUI Plugin for JARVIS
Provides a proper settings window for configuring API keys, city, theme, and email.
"""
import os
import json
import tkinter as tk
from tkinter import messagebox

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'settings.json')


def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception:
        return {}


def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass


def encrypt_value(value):
    import base64
    return base64.b64encode(value.encode()).decode()


def decrypt_value(value):
    import base64
    try:
        return base64.b64decode(value.encode()).decode()
    except Exception:
        return value


def register(jarvis):
    """Register settings GUI command."""

    def settings_gui_handler(query, speak, log, **kwargs):
        """Open the settings configuration window."""
        settings = load_settings()

        # Decrypt sensitive fields for display
        api_key = settings.get('openai_api_key', '')
        if api_key and not api_key.startswith('http'):
            try:
                api_key = decrypt_value(api_key)
            except Exception:
                pass

        email_password = settings.get('email_password', '')
        if email_password and not email_password.startswith('http'):
            try:
                email_password = decrypt_value(email_password)
            except Exception:
                pass

        # Create settings window
        win = tk.Toplevel()
        win.title("Settings - JARVIS")
        win.geometry("520x520")
        win.configure(bg='#1a1a2e')
        win.resizable(False, False)

        # Title
        title = tk.Label(win, text="⚙️ Settings", font=("Segoe UI", 20, "bold"),
                         bg='#1a1a2e', fg='#4f8ef7')
        title.pack(pady=(15, 10))

        # Scrollable content
        canvas = tk.Canvas(win, bg='#1a1a2e', highlightthickness=0)
        scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg='#1a1a2e')

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(15, 0))
        scrollbar.pack(side="right", fill="y")

        # --- OpenAI Settings ---
        section1 = tk.Label(scroll_frame, text="🤖 OpenAI Configuration", font=("Segoe UI", 13, "bold"),
                           bg='#1a1a2e', fg='#ffd700', anchor='w')
        section1.pack(fill=tk.X, pady=(5, 3))

        api_frame = tk.Frame(scroll_frame, bg='#1a1a2e')
        api_frame.pack(fill=tk.X, pady=2)
        tk.Label(api_frame, text="API Key:", font=("Segoe UI", 11), bg='#1a1a2e', fg='#e0e0e0',
                 width=12, anchor='w').pack(side=tk.LEFT)
        api_entry = tk.Entry(api_frame, font=("Segoe UI", 11), show='*', width=35)
        api_entry.insert(0, api_key)
        api_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # --- Weather Settings ---
        section2 = tk.Label(scroll_frame, text="🌤️ Weather", font=("Segoe UI", 13, "bold"),
                           bg='#1a1a2e', fg='#ffd700', anchor='w')
        section2.pack(fill=tk.X, pady=(12, 3))

        city_frame = tk.Frame(scroll_frame, bg='#1a1a2e')
        city_frame.pack(fill=tk.X, pady=2)
        tk.Label(city_frame, text="City:", font=("Segoe UI", 11), bg='#1a1a2e', fg='#e0e0e0',
                 width=12, anchor='w').pack(side=tk.LEFT)
        city_entry = tk.Entry(city_frame, font=("Segoe UI", 11), width=35)
        city_entry.insert(0, settings.get('default_city', ''))
        city_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # --- Theme Settings ---
        section3 = tk.Label(scroll_frame, text="🎨 Theme", font=("Segoe UI", 13, "bold"),
                           bg='#1a1a2e', fg='#ffd700', anchor='w')
        section3.pack(fill=tk.X, pady=(12, 3))

        theme_frame = tk.Frame(scroll_frame, bg='#1a1a2e')
        theme_frame.pack(fill=tk.X, pady=2)
        tk.Label(theme_frame, text="Theme:", font=("Segoe UI", 11), bg='#1a1a2e', fg='#e0e0e0',
                 width=12, anchor='w').pack(side=tk.LEFT)
        theme_var = tk.StringVar(value=settings.get('theme', 'Dark'))
        theme_menu = tk.OptionMenu(theme_frame, theme_var, 'Dark', 'Light', 'Blue', 'Gold')
        theme_menu.config(font=("Segoe UI", 10))
        theme_menu.pack(side=tk.LEFT)

        # --- Voice Settings ---
        section4 = tk.Label(scroll_frame, text="🔊 Voice", font=("Segoe UI", 13, "bold"),
                           bg='#1a1a2e', fg='#ffd700', anchor='w')
        section4.pack(fill=tk.X, pady=(12, 3))

        rate_frame = tk.Frame(scroll_frame, bg='#1a1a2e')
        rate_frame.pack(fill=tk.X, pady=2)
        tk.Label(rate_frame, text="Speech Rate:", font=("Segoe UI", 11), bg='#1a1a2e', fg='#e0e0e0',
                 width=12, anchor='w').pack(side=tk.LEFT)
        rate_var = tk.IntVar(value=settings.get('speech_rate', 150))
        rate_scale = tk.Scale(rate_frame, from_=80, to=250, orient=tk.HORIZONTAL,
                              variable=rate_var, bg='#1a1a2e', fg='#e0e0e0',
                              highlightthickness=0, length=200)
        rate_scale.pack(side=tk.LEFT)

        # --- Email Settings ---
        section5 = tk.Label(scroll_frame, text="✉️ Email (Gmail)", font=("Segoe UI", 13, "bold"),
                           bg='#1a1a2e', fg='#ffd700', anchor='w')
        section5.pack(fill=tk.X, pady=(12, 3))

        email_frame = tk.Frame(scroll_frame, bg='#1a1a2e')
        email_frame.pack(fill=tk.X, pady=2)
        tk.Label(email_frame, text="Email:", font=("Segoe UI", 11), bg='#1a1a2e', fg='#e0e0e0',
                 width=12, anchor='w').pack(side=tk.LEFT)
        email_entry = tk.Entry(email_frame, font=("Segoe UI", 11), width=35)
        email_entry.insert(0, settings.get('email_address', ''))
        email_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        pwd_frame = tk.Frame(scroll_frame, bg='#1a1a2e')
        pwd_frame.pack(fill=tk.X, pady=2)
        tk.Label(pwd_frame, text="App Password:", font=("Segoe UI", 11), bg='#1a1a2e', fg='#e0e0e0',
                 width=12, anchor='w').pack(side=tk.LEFT)
        pwd_entry = tk.Entry(pwd_frame, font=("Segoe UI", 11), show='*', width=35)
        pwd_entry.insert(0, email_password)
        pwd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        email_hint = tk.Label(scroll_frame, text="Use a Gmail App Password, not your main password.",
                             font=("Segoe UI", 9, "italic"), bg='#1a1a2e', fg='#a0a0a0', anchor='w')
        email_hint.pack(fill=tk.X, pady=(0, 5))

        # --- Status ---
        status_label = tk.Label(scroll_frame, text="", font=("Segoe UI", 10),
                                bg='#1a1a2e', fg='#00c853')
        status_label.pack(pady=(5, 0))

        # --- Buttons ---
        btn_frame = tk.Frame(scroll_frame, bg='#1a1a2e')
        btn_frame.pack(fill=tk.X, pady=(10, 15))

        def save():
            new_settings = load_settings()
            new_settings['openai_api_key'] = encrypt_value(api_entry.get().strip())
            new_settings['default_city'] = city_entry.get().strip()
            new_settings['theme'] = theme_var.get()
            new_settings['speech_rate'] = rate_var.get()
            new_settings['email_address'] = email_entry.get().strip()
            new_settings['email_password'] = encrypt_value(pwd_entry.get().strip())
            save_settings(new_settings)
            status_label.config(text="✅ Settings saved!", fg='#00c853')
            log("Settings saved from GUI.")
            speak("Settings saved successfully.")

        def reset():
            if messagebox.askyesno("Reset", "Reset all settings to defaults?", parent=win):
                default_settings = {
                    'openai_api_key': '',
                    'dark_mode': False,
                    'theme': 'Dark',
                    'voice': 0,
                    'default_city': '',
                    'speech_rate': 150,
                    'email_address': '',
                    'email_password': '',
                }
                save_settings(default_settings)
                api_entry.delete(0, tk.END)
                city_entry.delete(0, tk.END)
                theme_var.set('Dark')
                rate_var.set(150)
                email_entry.delete(0, tk.END)
                pwd_entry.delete(0, tk.END)
                status_label.config(text="Settings reset to defaults.", fg='#ffc107')

        save_btn = tk.Button(btn_frame, text="💾 Save", font=("Segoe UI", 12, "bold"),
                             command=save, bg='#0f3460', fg='#ffffff',
                             activebackground='#4f8ef7', relief=tk.FLAT, cursor="hand2")
        save_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=15, ipady=3)

        reset_btn = tk.Button(btn_frame, text="🔄 Reset", font=("Segoe UI", 12),
                              command=reset, bg='#3d3d3d', fg='#e0e0e0',
                              activebackground='#555555', relief=tk.FLAT, cursor="hand2")
        reset_btn.pack(side=tk.LEFT, ipadx=15, ipady=3)

    jarvis['add_command'](
        trigger_words=['settings', 'open settings', 'configure', 'configuration', 'preferences'],
        handler=settings_gui_handler,
        description='Open the settings configuration window.'
    )
