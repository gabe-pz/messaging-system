import os
from urllib.parse import quote

import requests

BLOOIO_API_KEY = os.environ["BLOOIO_API_KEY"]
IG_ACCESS_TOKEN = os.environ["IG_ACCESS_TOKEN"]

BLOOIO_BASE_URL = "https://backend.blooio.com/v2/api"
IG_SEND_URL = "https://graph.instagram.com/v25.0/me/messages"

def send_ig_message(recipient_id: str, text: str) -> bool:
    try:
        res = requests.post(
            IG_SEND_URL,
            headers={"Authorization": f"Bearer {IG_ACCESS_TOKEN}", "Content-Type": "application/json"},
            json={"recipient": {"id": recipient_id}, "message": {"text": text}},
            timeout=20,
        )
        if res.status_code >= 400:
            print(f"[IG] send to {recipient_id} failed {res.status_code}: {res.text[:300]}")
            return False
        return True
    except Exception as e:
        print(f"[IG] send to {recipient_id} errored: {e}")
        return False


def send_blooio_message(recipient: str, text: str) -> bool:
    try:
        res = requests.post(
            f"{BLOOIO_BASE_URL}/chats/{quote(recipient, safe='')}/messages",
            headers={"Authorization": f"Bearer {BLOOIO_API_KEY}", "Content-Type": "application/json"},
            json={"text": text},
            timeout=20,
        )
        if res.status_code >= 400:
            print(f"[BLOOIO] send to {recipient} failed {res.status_code}: {res.text[:300]}")
            return False
        return True
    except Exception as e:
        print(f"[BLOOIO] send to {recipient} errored: {e}")
        return False


