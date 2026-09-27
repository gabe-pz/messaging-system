from dotenv import load_dotenv 
from upstash_redis import Redis
import json

load_dotenv() 

redis_client: Redis = Redis.from_env() 

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

#write
def write(key: str, value) -> None:

    #ensure staying within limit
    if(redis_client.llen(key) > 11):
        #to-do: summarize the conversation from 0 - 11, store it as summary of convo, then remove them
        redis_client.lpop(key) 


    if(isinstance(value, dict)):
        value_as_text: str = json.dumps(value, ensure_ascii=False) 
        redis_client.rpush(key, value_as_text) 

    else:
        redis_client.rpush(key, value) 

