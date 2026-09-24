from helpers.state_form import message_form, message_history_form
from dotenv import load_dotenv 
from upstash_redis import Redis
import json, pprint

load_dotenv() 

redis_client: Redis = Redis.from_env() 

def log_dict(key: str, value: dict) -> None:
    value_as_text: str = json.dumps(value) 


    if(redis_client.llen(key) > 12):
        redis_client.lpop(key) 


    redis_client.rpush(key, value_as_text) 

def core(current_message_batch: list, id: str, channel: str) -> None:
    #create the users message from message batch
    user_message: dict = message_form(current_message_batch, channel)

    #log user message
    log_dict(f"{id}_usermsg", user_message)

    #assemble the message history for state
    message_history: dict = message_history_form(id) 

    state: dict = {
            "current_user_message": user_message,
            "message_history": message_history
    }

    #pass state into mams

    log_dict(f"{id}_agentres", "AGENT RESPONSESS!!")

    print()
    pprint.pp(state)











