from dotenv import load_dotenv 
from upstash_redis import Redis
from upstash_redis.client import Pipeline
import json, os, requests

load_dotenv() 

redis_client: Redis = Redis.from_env() 


# MEMORY LIMITS
MAX_ENTRIES: int = 12

#once a list is full, every turn except the last KEEP_RECENT is folded into one summary entry
KEEP_RECENT: int = 4


# SUMMARY MODEL
SUMMARY_URL: str = "https://openrouter.ai/api/v1/chat/completions"

SUMMARY_MODEL: str = "z-ai/glm-5.3-flash"

OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")


# HIL LISTS
#ids waiting to send pictures after asking about a custom service
HIL_QUEUE_KEY: str = "hil_queue"

#ids handed to a human, the system never responds to them
RESTRICTED_KEY: str = "hil_restricted"


# SUMMARY PROMPT
SUMMARY_PROMPT: str = """
Summarize this text conversation between Filthy Wraps, a car customization shop, and one customer, so the shop's agent can keep going without the full history.
The input is JSON, oldest first: user_message_N is the customer and agent_response_to_user_message_N is the shop's reply to it. A conversation_summary entry already covers even earlier messages, merge it in.
Write one short plain text paragraph, under 120 words, that keeps:
- the customer's vehicle (year, make, model) exactly as they typed it
- every service discussed and every price the shop quoted, with the exact numbers written like the shop does (299$, not $299)
- what the customer decided, asked for, or is still waiting on (booking, the shop checking on something, a hand off to the owner)
- what any media they sent or replied to showed, if it matters
Only use facts from the conversation. No greeting, no advice, no markdown, no em dashes.
"""


#read, turns json strings into dicts, and leaves plain text as is 
def read(key: str) -> list:
    values_as_text: list[str] = redis_client.lrange(key, 0, -1)
    values: list = []

    for value_as_text in values_as_text:
        try:
            value: dict = json.loads(value_as_text)
            values.append(value)
        except json.JSONDecodeError:
            values.append(value_as_text)

    return values


# SUMMARIZE
def summarize(id: str) -> None:
    user_key: str = f"{id}_usermsg"

    agent_key: str = f"{id}_agentres"

    lock_key: str = f"{id}_summarizing"

    #only one summary per conversation at a time, the lock removes itself after 120 seconds
    if(not redis_client.set(lock_key, "1", nx=True, ex=120)):
        return

    try:
        user_messages: list = read(user_key)

        agent_responses: list = read(agent_key)

        #only fold complete turns so user and agent turns stay paired
        complete_turns: int = min(len(user_messages), len(agent_responses))

        fold_count: int = complete_turns - KEEP_RECENT

        if(fold_count < 2):
            return

        conversation: dict = {}

        for i in range(fold_count):
            conversation[f"user_message_{i}"] = user_messages[i]

            conversation[f"agent_response_to_user_message_{i}"] = agent_responses[i]

        headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}

        system_message: dict = {"role": "system", "content": SUMMARY_PROMPT}

        user_message: dict = {"role": "user", "content": json.dumps(conversation, ensure_ascii=False)}

        payload: dict = {"model": SUMMARY_MODEL, "messages": [system_message, user_message], "reasoning": {"effort": "low"}}

        response: requests.Response = requests.post(SUMMARY_URL, headers=headers, json=payload, timeout=30)

        response.raise_for_status()

        result: dict = response.json()

        summary: str = result["choices"][0]["message"]["content"]

        if(summary is None or summary.strip() == ""):
            raise ValueError("empty summary")

        summary_entry: str = json.dumps({"conversation_summary": summary.strip()}, ensure_ascii=False)

        #swap the folded turns for the summary in one transaction, anything pushed meanwhile stays at the end
        transaction: Pipeline = redis_client.multi()

        transaction.ltrim(user_key, fold_count, -1)

        transaction.lpush(user_key, summary_entry)

        transaction.ltrim(agent_key, fold_count, -1)

        transaction.lpush(agent_key, "")

        transaction.exec()

    #on any failure every message is kept as is and the next agent reply tries again
    except Exception as error:
        print("SUMMARY ERROR: " + str(error))

    finally:
        redis_client.delete(lock_key)


#write
def write(key: str, value) -> None:

    #ensure staying within limit, folded when the agent reply is stored so a summary never delays a reply
    if(key.endswith("_agentres") and redis_client.llen(key) >= MAX_ENTRIES):
        id: str = key.removesuffix("_agentres")

        summarize(id)


    if(isinstance(value, dict)):
        value_as_text: str = json.dumps(value, ensure_ascii=False) 
        redis_client.rpush(key, value_as_text) 

    else:
        redis_client.rpush(key, value) 

#BOOK STATE
#overwrites only the fields given, like {"car_model": "..."}, the other fields stay
def write_bs(key: str, value: dict) -> None:
    redis_client.hset(key, values=value)

#every field as one dict, {} when nothing was written yet
def read_bs(key: str) -> dict:
    book_state: dict = redis_client.hgetall(key)

    return book_state


# ID LISTS
def add_id(key: str, id: str) -> None:
    redis_client.rpush(key, id)


def has_id(key: str, id: str) -> bool:
    ids: list[str] = redis_client.lrange(key, 0, -1)

    return id in ids


def remove_id(key: str, id: str) -> None:
    redis_client.lrem(key, 0, id)


