from dotenv import load_dotenv
import os, requests

load_dotenv() 

api_url: str = "https://openrouter.ai/api/v1/chat/completions"

api_key: str = os.environ["OPENROUTER_API_KEY"]

model_name: str = "z-ai/glm-5.3-flash" 

def process_image(data_url: str) -> str: 
    process_image_prompt: str = "Describe this image in 2-3 sentences" 

    text_block: dict = {"type": "text", "text": process_image_prompt}

    image_info: dict = {"url": data_url} 

    image_block: dict = {"type": "image_url", "image_url": image_info}

    content: list = [text_block, image_block] 
    
    message: dict = {"role": "user", "content": content} 

    body: dict = {"model": model_name, "messages": [message]}

    headers: dict = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}

    http_response: requests.Response = requests.post(api_url, headers=headers, json=body)

    result: dict = http_response.json()

    if("choices" not in result):
        print(result)
        return "ERROR: IMAGE COULD NOT BE PROCESSED"

    description: str = result["choices"][0]["message"]["content"]

    return description

