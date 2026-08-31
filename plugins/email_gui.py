"""
Email GUI Plugin for JARVIS
Provides a window to compose and send emails via Gmail.
"""
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tkinter as tk
from tkinter import messagebox


SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'settings.json')

SENSITIVE_KEYS = ['email_password']


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
    """Simple base64 obfuscation (not real encryption)."""
    import base64
    return base64.b64encode(value.encode()).decode()


def decrypt_value(value):
    import base64
    try:
        return base64.b64decode(value.encode()).decode()
    except Exception:
        return value


def register(jarvis):
    """Register email GUI commands."""

    def email_gui_handler(query, speak, log, **kwargs):
        """Open the email composition window."""
        settings = load_settings()

        # Try to decrypt password if encrypted
        email_password = settings.get('email_password', '')
        if email_password and not email_password.startswith('http'):
            try:
                email_password = decrypt_value(email_password)
            except Exception:
                pass

        email_address = settings.get('email_address', '')

        # Create email window
        win = tk.Toplevel()
        win.title("Send Email - JARVIS")
        win.geometry("500x450")
        win.configure(bg='#1a1a2e')
        win.resizable(False, False)

        # Title
        title = tk.Label(win, text="✉️ Send Email", font=("Segoe UI", 18, "bold"),
                         bg='#1a1a2e', fg='#4f8ef7')
        title.pack(pady=(15, 10))

        # From (pre-filled if configured)
        from_frame = tk.Frame(win, bg='#1a1a2e')
        from_frame.pack(fill=tk.X, padx=30, pady=3)
        tk.Label(from_frame, text="From:", font=("Segoe UI", 11), bg='#1a1a2e', fg='#e0e0e0',
                 width=8, anchor='w').pack(side=tk.LEFT)
        from_entry = tk.Entry(from_frame, font=("Segoe UI", 11), width=40)
        from_entry.insert(0, email_address)
        from_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # To
        to_frame = tk.Frame(win, bg='#1a1a2e')
        to_frame.pack(fill=tk.X, padx=30, pady=3)
        tk.Label(to_frame, text="To:", font=("Segoe UI", 11), bg='#1a1a2e', fg='#e0e0e0',
                 width=8, anchor='w').pack(side=tk.LEFT)
        to_entry = tk.Entry(to_frame, font=("Segoe UI", 11), width=40)
        to_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Subject
        subj_frame = tk.Frame(win, bg='#1a1b2e')
        subj_frame.pack(fill=tk.X, padx=30, pady=3)
        tk.Label(subj_frame, text="Subject:", font=("Segoe UI", 11), bg='#1a1a2e', fg='#e0e0e0',
                 width=8, anchor='w').pack(side=tk.LEFT)
        subj_entry = tk.Entry(subj_frame, font=("Segoe UI", 11), width=40)
        subj_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Message body
        body_frame = tk.Frame(win, bg='#1a1a2e')
        body_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(8, 3))
        tk.Label(body_frame, text="Message:", font=("Segoe UI", 11), bg='#1a1a2e', fg='#e0e0e0',
                 anchor='w').pack(anchor='w')
        body_text = tk.Text(body_frame, font=("Segoe UI", 11), height=8, width=50,
                            bg='#16213e', fg='#e0e0e0', insertbackground='#e0e0e0', relief=tk.FLAT)
        body_text.pack(fill=tk.BOTH, expand=True)

        # Status label
        status = tk.Label(win, text="", font=("Segoe UI", 10), bg='#1a1a2e', fg='#a0a0a0')
        status.pack(pady=(2, 0))

        # Buttons
        btn_frame = tk.Frame(win, bg='#1a1a2e')
        btn_frame.pack(fill=tk.X, padx=30, pady=(5, 15))

        def send_email():
            from_addr = from_entry.get().strip()
            to_addr = to_entry.get().strip()
            subject = subj_entry.get().strip()
            msg_body = body_text.get("1.0", tk.END).strip()

            if not from_addr or not to_addr or not subject or not msg_body:
                messagebox.showerror("Error", "All fields are required.", parent=win)
                return

            if not email_password:
                messagebox.showerror(
                    "Email Not Configured",
                    "Please set your email and app password in Settings first.",
                    parent=win
                )
                return

            status.config(text="Sending...", fg='#ffc107')
            win.update_idletasks()

            try:
                msg = MIMEMultipart()
                msg['From'] = from_addr
                msg['To'] = to_addr
                msg['Subject'] = subject
                msg.attach(MIMEText(msg_body, 'plain'))

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(from_addr, email_password)
                server.sendmail(from_addr, to_addr, msg.as_string())
                server.quit()

                status.config(text="✅ Email sent successfully!", fg='#00c853')
                log(f"Email sent to {to_addr} with subject '{subject}'")
                speak(f"Email sent to {to_addr}")
                win.after(1500, win.destroy)

            except smtplib.SMTPAuthenticationError:
                status.config(text="❌ Authentication failed. Check credentials.", fg='#ff5252')
                speak("Email authentication failed. Check your credentials.")
            except smtplib.SMTPRecipientsRefused:
                status.config(text="❌ Invalid recipient email.", fg='#ff5252')
            except Exception as e:
                status.config(text=f"❌ Failed: {str(e)[:50]}", fg='#ff5252')
                speak("Failed to send email.")

        def cancel():
            win.destroy()

        send_btn = tk.Button(btn_frame, text="📨 Send", font=("Segoe UI", 12, "bold"),
                             command=send_email, bg='#0f3460', fg='#ffffff',
                             activebackground='#4f8ef7', relief=tk.FLAT, cursor="hand2")
        send_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=15, ipady=3)

        cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 12),
                               command=cancel, bg='#3d3d3d', fg='#e0e0e0',
                               activebackground='#555555', relief=tk.FLAT, cursor="hand2")
        cancel_btn.pack(side=tk.LEFT, ipadx=15, ipady=3)

    jarvis['add_command'](
        trigger_words=['send email', 'email to', 'mail to', 'compose email', 'write email'],
        handler=email_gui_handler,
        description='Open email composition window.'
    )
