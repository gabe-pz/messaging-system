# All memory for MAMS, every message and every saved fact lives in one sqlite file so an agent still remembers a person after the program is turned off and started again.

# IMPORTS
import sqlite3
import threading
import time
from pathlib import Path


# DATABASE
DB_PATH: Path = Path(__file__).resolve().parent / "mams_memory.sqlite"

# check_same_thread is off because the batch timer threads write here too
connection: sqlite3.Connection = sqlite3.connect(DB_PATH, check_same_thread=False)

lock: threading.RLock = threading.RLock()


# How many past messages an agent is allowed to read, so a long conversation never grows the prompt forever.
HISTORY_LIMIT: int = 16


#Builds the two tables the first time MAMS ever runs.
def setup_memory() -> None:
    with lock:
        connection.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, channel TEXT, role TEXT, text TEXT, created_at REAL)")

        connection.execute("CREATE TABLE IF NOT EXISTS facts (user_id TEXT, name TEXT, value TEXT, PRIMARY KEY (user_id, name))")

        connection.commit()


#Saves one message, role is "customer" for what came in and "agent" for what went out.
def save_message(user_id: str, channel: str, role: str, text: str) -> None:
    with lock:
        connection.execute("INSERT INTO messages (user_id, channel, role, text, created_at) VALUES (?, ?, ?, ?, ?)", (user_id, channel, role, text, time.time()))

        connection.commit()


#The last few turns as plain text, this is what gets pasted into an agent prompt.
def read_history(user_id: str, limit: int = HISTORY_LIMIT) -> str:
    with lock:
        rows: list = connection.execute("SELECT role, text FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit)).fetchall()

    rows.reverse()

    lines: list[str] = []

    for row in rows:
        lines.append(f"{row[0]}: {row[1]}")

    return "\n".join(lines)


#The newest message of one role
def read_last_message(user_id: str, role: str) -> str:
    with lock:
        row: tuple | None = connection.execute("SELECT text FROM messages WHERE user_id = ? AND role = ? ORDER BY id DESC LIMIT 1", (user_id, role)).fetchone()

    if row is None:
        return ""

    return str(row[0])


#Saves one thing worth remembering about a person, for example a name or a chosen option.
def save_fact(user_id: str, name: str, value: str) -> None:
    with lock:
        connection.execute("INSERT OR REPLACE INTO facts (user_id, name, value) VALUES (?, ?, ?)", (user_id, name, value))

        connection.commit()


#Reads one saved fact back, the default is returned when nothing was ever saved.
def read_fact(user_id: str, name: str, default: str = "") -> str:
    with lock:
        row: tuple | None = connection.execute("SELECT value FROM facts WHERE user_id = ? AND name = ?", (user_id, name)).fetchone()

    if row is None:
        return default

    return str(row[0])


#Wipes everything remembered about one person.
def forget_user(user_id: str) -> None:
    with lock:
        connection.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))

        connection.execute("DELETE FROM facts WHERE user_id = ?", (user_id,))

        connection.commit()


# START
setup_memory()
