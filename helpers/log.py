from dotenv import load_dotenv 
from upstash_redis import Redis
import json

load_dotenv() 

redis_client: Redis = Redis.from_env() 

#read 
def read(key: str) -> list[str]:
    values_as_text: list[str] = redis_client.lrange(key, 0, -1)

    return values_as_text

#write
def write(key: str, value) -> None:

    #ensure staying within limit
    if(redis_client.llen(key) > 12):
        redis_client.lpop(key) 


    if(isinstance(value, dict)):
        value_as_text: str = json.dumps(value) 
        redis_client.rpush(key, value_as_text) 

    else:
        redis_client.rpush(key, value) 

