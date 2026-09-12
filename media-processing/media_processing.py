# All media processing for MAMS, it pulls the media out of an incoming message on any channel and turns every image or video into a short written description such that the agents can read 

# IMPORTS
import base64
import io
import os
from typing import Any
from urllib.parse import urlparse

import cv2
import requests
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from PIL import Image


# MODEL
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

VISION_MODEL_NAME: str = os.getenv("MAMS_VISION_MODEL", "moonshotai/kimi-k3")

vision_model: ChatOpenAI = ChatOpenAI(model=VISION_MODEL_NAME, base_url=OPENROUTER_BASE_URL, api_key=os.environ["OPENROUTER_API_KEY"], timeout=90)


# VISION PROMPT
# The vision agent always answers in these four labeled lines, so every description has the same shape.
VISION_PROMPT: str = """Describe this media for the person answering the customer. Answer with exactly these four labeled lines and nothing else. 
    Subject: what is in the media. 
    Details: the details that matter for a customer question. 
    Text In Media: any words visible in the media, or none. 
    Confidence: high, medium or low.
    """

media_analyzer_agent: Any = create_agent(model=vision_model)


# MARKERS
# Sent to the agents when a media exists but could not be described, they must read the same marker every time.
NOT_ANALYZABLE: str = "NOT ANALYZABLE: this media could not be described, rely on the text of the message."

MAX_IMAGE_SIDE: int = 1024

JPEG_QUALITY: int = 85


# INSTAGRAM MEDIA
def gather_instagram_media(attachments: list) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []

    for attachment in attachments:
        media_type: str = attachment.get("type", "")

        url: str = attachment.get("payload", {}).get("url", "")

        if url:
            found.append((f"instagram {media_type} the user sent", url))

    return found


# MESSENGER MEDIA
def gather_messenger_media(attachments: list) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []

    for attachment in attachments:
        media_type: str = attachment.get("type", "")

        url: str = attachment.get("payload", {}).get("url", "")

        if url:
            found.append((f"messenger {media_type} the user sent", url))

    return found


# BLOOIO MEDIA
def gather_blooio_media(attachments: list) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []

    for attachment in attachments:
        url: str = attachment.get("payload", {}).get("url", "")

        if url:
            found.append(("photo the customer texted", url))

    return found


# CHANNEL PICK
def gather_media(channel: str, attachments: list) -> list[tuple[str, str]]:
    match channel:
        case "instagram":
            return gather_instagram_media(attachments)

        case "messenger":
            return gather_messenger_media(attachments)

        case "blooio":
            return gather_blooio_media(attachments)

        case _:
            return []


# MEDIA TYPE
def check_media_type(url: str) -> str:
    path: str = urlparse(url).path.lower()

    image_endings: tuple = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic")

    video_endings: tuple = (".mp4", ".mov", ".m4v", ".webm", ".avi")

    if path.endswith(image_endings):
        return "image"

    if path.endswith(video_endings):
        return "video"

    return "unknown"


# IMAGE TO BASE64
def image_to_base64(url: str) -> str:
    headers: dict = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=30)

    response.raise_for_status()

    image = Image.open(io.BytesIO(response.content))

    image = image.convert("RGB")

    image.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))

    buffer = io.BytesIO()

    image.save(buffer, format="JPEG", quality=JPEG_QUALITY)

    encoded: str = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:image/jpeg;base64,{encoded}"


# VIDEO TO BASE64
def video_to_base64(url: str) -> str:
    capture = cv2.VideoCapture(url)

    got_frame, frame = capture.read()

    capture.release()

    if not got_frame:
        raise ValueError("no frame could be read from this video")

    worked, encoded_frame = cv2.imencode(".jpg", frame)

    if not worked:
        raise ValueError("the frame could not be encoded")

    encoded: str = base64.b64encode(encoded_frame.tobytes()).decode("utf-8")

    return f"data:image/jpeg;base64,{encoded}"


# REPLY TEXT
def read_text(content: object) -> str:
    if isinstance(content, list):
        parts: list[str] = []

        for block in content:
            if isinstance(block, dict):
                parts.append(str(block.get("text", "")))

        return "".join(parts)

    return str(content)


# DESCRIBE
def describe_media(url: str) -> str:
    media_type: str = check_media_type(url)

    try:
        if media_type == "video":
            data_uri: str = video_to_base64(url)
        else:
            data_uri = image_to_base64(url)

        prompt = HumanMessage(content=[{"type": "text", "text": VISION_PROMPT}, {"type": "image_url", "image_url": {"url": data_uri}}])

        result = media_analyzer_agent.invoke({"messages": [prompt]})

        description: str = read_text(result["messages"][-1].content).strip()

        if not description:
            return NOT_ANALYZABLE

        return description
    except Exception as error:
        print(f"[MEDIA] could not describe {url}: {error}")

        return NOT_ANALYZABLE


# PROCESS MEDIA
#The one function MAMS calls, it returns the media block that gets tagged onto the message, or an empty string when there is no media.
def process_media(channel: str, attachments: list) -> str:
    media_list: list[tuple[str, str]] = gather_media(channel, attachments)

    if not media_list:
        return ""

    blocks: list[str] = []

    number: int = 1

    for source, url in media_list:
        print(f"[MEDIA] describing media {number} on {channel}")

        description: str = describe_media(url)

        blocks.append(f"media {number} ({source})\nMedia Description: {description}")

        number = number + 1

    return "\n\n".join(blocks)
