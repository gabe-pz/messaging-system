from helpers.state_form import message_form
from dotenv import load_dotenv 
from upstash_redis import Redis
import json

load_dotenv() 

redis_client: Redis = Redis.from_env() 

def log_dict(key: str, value: dict) -> None:
    value_as_text: str = json.dumps(value) 

    redis_client.rpush(key, value_as_text) 

def core(current_message_batch: list, id: str, channel: str) -> None:
    #create the users message from message batch
    user_message: dict = message_form(current_message_batch, channel)

    #log user message
    log_dict(f"{id}_usermsg", user_message)











