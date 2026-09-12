# All batching for MAMS, people send a few quick messages in a row so every new message restarts a short timer and the whole group is answered once

# IMPORTS
import threading
from collections.abc import Callable


# WAIT TIMES
# How long each channel waits for the person to stop typing before the batch is handed over.
WAIT_SECONDS: dict[str, int] = {"instagram": 150, "messenger": 150, "blooio": 150}

DEFAULT_WAIT_SECONDS: int = 150


# BUFFERS
# What each person has said so far in the batch they are still building, and the timer counting down for them.
buffers: dict[str, dict] = {}

timers: dict[str, threading.Timer] = {}

lock: threading.RLock = threading.RLock()


# KEY
def buffer_key(channel: str, user_id: str) -> str:
    return f"{channel}|{user_id}"


# WAIT TIME
def wait_seconds_for(channel: str) -> int:
    return WAIT_SECONDS.get(channel, DEFAULT_WAIT_SECONDS)


# MERGED TEXT
# Every message of the batch as one numbered block, this is the format the lc agents read.
def build_merged_text(texts: list[str]) -> str:
    lines: list[str] = ["User Text:"]

    number: int = 1

    for text in texts:
        lines.append(f"{number}) {text}")

        number = number + 1

    return "\n".join(lines)


# TIMER
# Starts the countdown for one person, the caller already holds the lock.
def start_timer(channel: str, user_id: str, on_ready: Callable[[str, str, str, list], None]) -> None:
    key: str = buffer_key(channel, user_id)

    old_timer: threading.Timer | None = timers.get(key)

    if old_timer is not None:
        old_timer.cancel()

    timer: threading.Timer = threading.Timer(wait_seconds_for(channel), flush_batch, [channel, user_id, on_ready])

    timer.daemon = True

    timers[key] = timer

    timer.start()


# FLUSH
# The timer ran out so the person stopped talking, hand the whole batch over to MAMS
def flush_batch(channel: str, user_id: str, on_ready: Callable[[str, str, str, list], None]) -> None:
    key: str = buffer_key(channel, user_id)

    with lock:
        buffer: dict = buffers.get(key, {})

        texts: list[str] = buffer.get("texts", [])

        attachments: list = buffer.get("attachments", [])

        waited_twice: bool = buffer.get("waited_twice", False)

        # media with no text waits one more window, the question about the photo almost always lands after the photo
        if attachments and not texts and not waited_twice:
            buffer["waited_twice"] = True

            start_timer(channel, user_id, on_ready)

            return

        buffers.pop(key, None)

        timers.pop(key, None)

    if not texts and not attachments:
        return

    merged_text: str = build_merged_text(texts)

    on_ready(channel, user_id, merged_text, attachments)


# ADD MESSAGE
# The one function MAMS calls for every incoming message on every channel
def add_message(channel: str, user_id: str, text: str, attachments: list, on_ready: Callable[[str, str, str, list], None]) -> None:
    key: str = buffer_key(channel, user_id)

    with lock:
        if key not in buffers:
            buffers[key] = {"texts": [], "attachments": [], "waited_twice": False}

        if text:
            buffers[key]["texts"].append(text)

        for attachment in attachments:
            buffers[key]["attachments"].append(attachment)

        start_timer(channel, user_id, on_ready)
