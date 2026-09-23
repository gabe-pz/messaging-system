from helpers.media_prep import prepare_media
from helpers.media_process import process_media

def media_element_form(attatchments: list, channel: str):

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

def state(current_message: list):
    current_attatchments: list = []
    current_text: list = []

    #extract content from message batch
    for message in current_message:
        if(isinstance(message, list) and message != []):
            current_attatchments.append(message)
        
        elif(isinstance(message, str)):
            current_text.append(message) 

    if(current_attatchments != []):
        media_element_form(current_attatchments, "blooio")
