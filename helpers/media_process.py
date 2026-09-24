from dotenv import load_dotenv
import os, requests

load_dotenv() 

#API init for model call
api_url: str = "https://openrouter.ai/api/v1/chat/completions"
api_key: str = os.environ["OPENROUTER_API_KEY"]
model_name: str = "z-ai/glm-5.3-flash" 

#function to process media 
def process_media(data_url: str, media_type: str) -> str: 
    
    media_info: dict = {"url": data_url} 

    media_block: dict = {}

    prompt: str = ""

    if(media_type == "i"):
        prompt = "process this image in 2-3 sentences "
        media_block: dict = {"type": "image_url", "image_url": media_info}


    elif(media_type == "v"):
        prompt = "process this video in 2-3 sentences"
        media_block: dict = {"type": "video_url", "video_url": media_info}

    else:
        raise ValueError("Unsupported Media Type: " + media_type)

    text_block: dict = {"type": "text", "text": prompt}

    content: list = [text_block, media_block] 

    message: dict = {"role": "user", "content": content} 

    body: dict = {"model": model_name, "messages": [message]}

    headers: dict = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}

    http_response: requests.Response = requests.post(api_url, headers=headers, json=body)

    result: dict = http_response.json()

    if("choices" not in result):
        print(result)
        return "ERROR: MEDIA COULT NOT BE PROCESSED"

    description: str = result["choices"][0]["message"]["content"]

    return description

