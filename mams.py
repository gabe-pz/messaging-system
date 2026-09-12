#MAMS is the whole system in one file, a message comes in on a channel, it is batched, its media is described, it goes through the agents and the reply goes back out on the same channel.

# IMPORTS
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
from dotenv import load_dotenv
from flask import Flask, request


# PATHS
MAMS_DIR: Path = Path(__file__).resolve().parent

sys.path.insert(0, str(MAMS_DIR))

#the media-processing folder has a dash in its name so it cannot be imported as a package, its folder goes on the path instead
sys.path.insert(0, str(MAMS_DIR / "media-processing"))

#the keys are loaded before the agents are imported, because building an agent needs the model key
load_dotenv(MAMS_DIR / ".env")

import agents
import media_processing
from batching.batching import add_message
from memory.memory import read_history, save_message


#Turn a channel on or off 
ENABLE_INSTAGRAM: bool = os.getenv("ENABLE_INSTAGRAM", "1") == "1"

ENABLE_MESSENGER: bool = os.getenv("ENABLE_MESSENGER", "1") == "1"

ENABLE_BLOOIO: bool = os.getenv("ENABLE_BLOOIO", "1") == "1"

# KEYS
VERIFY_TOKEN: str = os.getenv("VERIFY_TOKEN", "")

INSTAGRAM_ACCESS_TOKEN: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")

PAGE_ACCESS_TOKEN: str = os.getenv("PAGE_ACCESS_TOKEN", "")

BLOOIO_API_KEY: str = os.getenv("BLOOIO_API_KEY", "")

BLOOIO_BASE_URL: str = os.getenv("BLOOIO_BASE_URL", "https://api.blooio.com/v2")

PORT: int = 5000


# INSTAGRAM SEND
def send_instagram_message(user_id: str, text: str) -> None:
    url: str = "https://graph.instagram.com/v25.0/me/messages"

    headers: dict = {"Authorization": f"Bearer {INSTAGRAM_ACCESS_TOKEN}", "Content-Type": "application/json"}

    payload: dict = {"recipient": {"id": user_id}, "message": {"text": text}}

    response = requests.post(url, headers=headers, json=payload, timeout=20)

    print(f"[SENT instagram] {response.status_code} {response.text}")


# MESSENGER SEND
def send_messenger_message(user_id: str, text: str) -> None:
    url: str = "https://graph.facebook.com/v25.0/me/messages"

    headers: dict = {"Authorization": f"Bearer {PAGE_ACCESS_TOKEN}", "Content-Type": "application/json"}

    payload: dict = {"recipient": {"id": user_id}, "message": {"text": text}}

    response = requests.post(url, headers=headers, json=payload, timeout=20)

    print(f"[SENT messenger] {response.status_code} {response.text}")


# BLOOIO SEND
def send_blooio_message(user_id: str, text: str) -> None:
    chat_id: str = quote(user_id, safe="")

    url: str = f"{BLOOIO_BASE_URL}/chats/{chat_id}/messages"

    headers: dict = {"Authorization": f"Bearer {BLOOIO_API_KEY}", "Content-Type": "application/json"}

    response = requests.post(url, headers=headers, json={"text": text}, timeout=20)

    print(f"[SENT blooio] {response.status_code} {response.text}")


#Sends the finished reply back out on the channel the message arrived on.
def send_reply(channel: str, user_id: str, text: str) -> None:
    match channel:
        case "instagram":
            send_instagram_message(user_id, text)

        case "messenger":
            send_messenger_message(user_id, text)

        case "blooio":
            send_blooio_message(user_id, text)

        case _:
            print(f"[SEND] unknown channel {channel}, nothing sent")


#One finished batch from one person, this is the whole MAMS path from batched message to sent reply.
def handle_batch(channel: str, user_id: str, merged_text: str, attachments: list) -> None:
    print(f"[MAMS] batch ready from {user_id} on {channel}")

    # media becomes text and is tagged onto the message, so the agents read one single message
    media_text: str = media_processing.process_media(channel, attachments)

    full_message: str = merged_text

    if media_text:
        full_message = f"{merged_text}\n\n{media_text}"

    history_text: str = read_history(user_id)

    code: str = agents.run_router(full_message, history_text)

    reply: str = ""

    # every category is one case here, adding a category is adding one more case
    match code:
        case "A":
            reply = agents.run_business_operations_agent(full_message, history_text)

        case _:
            reply = ""

    save_message(user_id, channel, "customer", full_message)

    if not reply:
        print(f"[MAMS] no reply for {user_id} on {channel}")

        return

    save_message(user_id, channel, "agent", reply)

    send_reply(channel, user_id, reply)


# Every incoming message goes here first, the batcher holds it until the person stops yapping
def handle_incoming(channel: str, user_id: str, text: str, attachments: list) -> None:
    print(f"[MAMS] incoming on {channel} from {user_id}: {text}")

    add_message(channel, user_id, text, attachments, handle_batch)

#Every real message inside one Meta webhook body, to drop things like echos 
def read_meta_messages(body: dict) -> list[dict]:
    found: list[dict] = []

    for entry in body.get("entry", []):
        for event in entry.get("messaging", []):
            message: dict = event.get("message", {})

            if not message:
                continue

            if message.get("is_echo"):
                continue

            user_id: str = event.get("sender", {}).get("id", "")

            if not user_id:
                continue

            found.append({"user_id": user_id, "text": message.get("text", ""), "attachments": message.get("attachments", [])})

    return found


#The one message inside a Blooio webhook body, where the phone number is the id of the conversation.
def read_blooio_message(body: dict) -> dict:
    data: dict = body.get("data", body)

    user_id: str = str(data.get("from", "") or data.get("chat_id", ""))

    return {"user_id": user_id, "text": data.get("text", ""), "attachments": data.get("attachments", [])}


#Meta calls the webhook with a GET once, and it only accepts the challenge back when the token matches
def meta_verify() -> Any:
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return (request.args.get("hub.challenge", ""), 200)

    return ("wrong verify token", 403)


# APP
app: Flask = Flask(__name__)


# INSTAGRAM WEBHOOK
@app.route("/webhook/instagram", methods=["GET", "POST"])
def instagram_webhook() -> Any:
    if request.method == "GET":
        return meta_verify()

    body: dict = request.get_json(force=True, silent=True) or {}

    if ENABLE_INSTAGRAM:
        for message in read_meta_messages(body):
            handle_incoming("instagram", message["user_id"], message["text"], message["attachments"])

    return ("EVENT_RECEIVED", 200)


# MESSENGER WEBHOOK
@app.route("/webhook/messenger", methods=["GET", "POST"])
def messenger_webhook() -> Any:
    if request.method == "GET":
        return meta_verify()

    body: dict = request.get_json(force=True, silent=True) or {}

    if ENABLE_MESSENGER:
        for message in read_meta_messages(body):
            handle_incoming("messenger", message["user_id"], message["text"], message["attachments"])

    return ("EVENT_RECEIVED", 200)


# BLOOIO WEBHOOK
@app.route("/webhook/blooio", methods=["GET", "POST"])
def blooio_webhook() -> Any:
    if request.method == "GET":
        return ("blooio webhook is up", 200)

    body: dict = request.get_json(force=True, silent=True) or {}

    message: dict = read_blooio_message(body)

    if ENABLE_BLOOIO and message["user_id"]:
        handle_incoming("blooio", message["user_id"], message["text"], message["attachments"])

    return ("EVENT_RECEIVED", 200)


# MAIN
if __name__ == "__main__":
    print(f"MAMS running on port {PORT}")

    print(f"instagram: {ENABLE_INSTAGRAM} | messenger: {ENABLE_MESSENGER} | blooio: {ENABLE_BLOOIO}")

    app.run(port=PORT)
