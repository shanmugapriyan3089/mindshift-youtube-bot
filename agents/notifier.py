"""
Notification helper — tries Gmail first, falls back to Telegram when available.
Gmail setup: add NOTIFY_EMAIL + GMAIL_APP_PASSWORD to GitHub Secrets.
"""
import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def _send_email(subject: str, body: str) -> bool:
    gmail_user = os.getenv("NOTIFY_EMAIL")
    gmail_pass = os.getenv("GMAIL_APP_PASSWORD")
    if not gmail_user or not gmail_pass:
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"MindShift Bot <{gmail_user}>"
        msg["To"] = gmail_user

        # Plain text version (strip HTML tags roughly)
        import re
        plain = re.sub(r'<[^>]+>', '', body).strip()
        msg.attach(MIMEText(plain, "plain", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, gmail_user, msg.as_string())
        print(f"[Notifier] Email sent to {gmail_user}")
        return True
    except Exception as e:
        print(f"[Notifier] Email error: {e}")
        return False


def _send_telegram(message: str) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(url, json={
            "chat_id": chat_id,
            "text": message[:4096],
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }, timeout=30)
        return resp.status_code == 200
    except Exception:
        return False


def send(message: str, subject: str = "MindShift Bot Update"):
    """Send notification — Gmail first, Telegram as fallback."""
    # Try Gmail (works everywhere)
    sent = _send_email(subject, message)
    # Also try Telegram if configured (for when ban lifts)
    _send_telegram(message)
    if not sent:
        print(f"[Notifier] No notification method configured.\n{message}")
