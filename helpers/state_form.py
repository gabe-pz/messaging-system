from helpers.media_prep import prepare_media
from helpers.media_process import process_media

def media_element_form(attatchments: list, channel: str) -> list[dict]:

    if(channel == "blooio"):
        #prepare media
        data_urls_types: list[tuple] = []

        for attatchment in attatchments:

            if(len(attatchment) > 1):
                for x in attatchment:
                    media_url: str = x.get("url")
                    data_urls_types.append(prepare_media(media_url))

            else:
                media_url: str = attatchment[0].get("url")
                data_urls_types.append(prepare_media(media_url))

        #process media
        media_descriptions: list[str] = [] 

        for data_url_type in data_urls_types:
            data_url: str = data_url_type[0] 
            media_type: str = data_url_type[1]

            media_descriptions.append(process_media(data_url, media_type))

        media_elements: list[dict] = []

        for media_description in media_descriptions: 
            media_elements.append({
                "media_description": media_description,
                "channel": channel,
                "is_ad": False
                })

        return media_elements

def message_form(current_message_batch: list, channel: str) -> dict:
    current_attatchments: list = []
    current_text: list = []

    #extract content from message batch
    for message in current_message_batch:
        if(isinstance(message, list) and message != []):
            current_attatchments.append(message)
        
        elif(isinstance(message, str)):
            current_text.append(message) 

    message: dict = {} 

    media: dict = {}
    if(current_attatchments != []):
        media_elements: list[dict] = media_element_form(current_attatchments, channel)

        for i, media_element in enumerate(media_elements):
            media[f"media_element_{i}"] = media_element

    text: str = "" 
    if(current_text != []):
        for txt in current_text:
            if(text != ""):
                text += f" {txt}\n "
            else: 
                text += f"{txt}\n "


    message["user_media"] = media
    message["user_text"] =  text


    return message


def message_history_form(id: str):
    pass

