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
        prompt = """
        # Prompt
        process this image, the output should be in the following format

        brief_description: 
        service_ques: 
        text_overlays:

        # Note
            brief_description is a 1-2 sentence description for an LLM to understand fully the image 

            service_ques is a 1-2 sentece description about any and all services it could be talking about 
            for a car customzation shop that is

            text_overlays is any overlays of text that was on the image, just as they were

        """
        media_block: dict = {"type": "image_url", "image_url": media_info}


    elif(media_type == "v"):
        prompt = """
        # Prompt
        process this video, the output should be in the following format

        brief_description: 
        service_ques: 
        text_overlays:

        # Note
            - brief_description is a 1-2 sentence description for an LLM to understand fully the video

            - service_ques is a 1-2 sentece description about any and all services it could be talking about 
            for a car customzation shop that is

            - text_overlays is any overlays of text that was on the video, just as they were
        """

        media_block: dict = {"type": "video_url", "video_url": media_info}

    else:
        return "ERROR: MEDIA COULT NOT BE PROCESSED"

    text_block: dict = {"type": "text", "text": prompt}

    content: list = [text_block, media_block] 

    message: dict = {"role": "user", "content": content} 

    body: dict = {"model": model_name, "messages": [message]}

    headers: dict = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}

    try:
        http_response: requests.Response = requests.post(api_url, headers=headers, json=body, timeout=120)
        result: dict = http_response.json()
    except (requests.RequestException, ValueError) as error:
        print("MEDIA PROCESS ERROR: " + str(error))
        return "ERROR: MEDIA COULT NOT BE PROCESSED"

    if("choices" not in result):
        print(result)
        return "ERROR: MEDIA COULT NOT BE PROCESSED"

    description: str = result["choices"][0]["message"]["content"]

    return description

