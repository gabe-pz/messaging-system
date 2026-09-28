from dotenv import load_dotenv

from src.prompts.car_model import car_model_sys_prompt as cmSP

import os, requests, json

#API key
load_dotenv()
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")

#GLM model for car model analysis
GENERATORS_URL: str = "https://openrouter.ai/api/v1/chat/completions"
CAR_MODEL_MODEL: str = "z-ai/glm-5.3-flash"

def car_model_analyze(user_message: dict) -> str:
    #system prompt goes first and never changes, so it can be cached
    system_block: dict = {"type": "text", "text": cmSP.car_model_system_prompt(), "cache_control": {"type": "ephemeral"}}
    system_message: dict = {"role": "system", "content": [system_block]}

    #compact json with no extra spaces or escaped unicode
    user_message_as_text: str = json.dumps(user_message, ensure_ascii=False, separators=(",", ":"))

    #create the text to pass
    user_text: str = f"USER_MESSAGE: {user_message_as_text}"
    message: dict = {"role": "user", "content": user_text}

    #prepare the request
    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    provider_settings: dict = {"order": ["z-ai"], "allow_fallbacks": True}
    reasoning_settings: dict = {"effort": "low"}
    payload: dict = {"model": CAR_MODEL_MODEL, "messages": [system_message, message], "provider": provider_settings, "reasoning": reasoning_settings, "max_tokens": 2000}

    #send request
    response = requests.post(GENERATORS_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()

    #grab car model
    result: dict = response.json()
    car_model: str = result["choices"][0]["message"]["content"].strip()

    #no car model given
    if(car_model.lower() == "none"):
        return ""

    return car_model
