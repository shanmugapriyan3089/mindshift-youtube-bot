"""Telegram notification helper — no bot server needed, just HTTP POST."""
import os
import requests


def send(message: str, parse_mode: str = "HTML"):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print(f"[Notifier] No Telegram config. Console output:\n{message}")
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(url, json={
            "chat_id": chat_id,
            "text": message[:4096],
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
        }, timeout=30)
        if resp.status_code != 200:
            print(f"[Notifier] Telegram error {resp.status_code}: {resp.text}")
            return False
        return True
    except Exception as e:
        print(f"[Notifier] Error: {e}")
        return False
