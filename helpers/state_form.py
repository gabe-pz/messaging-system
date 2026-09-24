from helpers import media_process
from helpers.media_prep import prepare_media
from helpers.media_process import process_media
from helpers.log import read

#function to form  the media elements in state
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
                "media_description": media_description
                })

        return media_elements
    
    elif(channel == "ig"):
        media_processed: list[list] = []
        media_can_process: list[str] = ["ig_story", "ig_post", "image", "video"]

        for attatchment in attatchments:

            if(len(attatchment) > 1):
                for x in attatchment:
                    type_media: str = x.get("type")

                    if(type_media in media_can_process and type_media == "ig_post"):
                        data_url_and_type: tuple = prepare_media(x.get("payload").get("url"))

                        media_processed.append([data_url_and_type, x.get("payload").get("title")])

                    elif(type_media in media_can_process and type_media == "ig_story"):
                        data_url_and_type: tuple = prepare_media(x.get("payload").get("story_media_url"))

                        media_processed.append([data_url_and_type, ""])

                    elif(type_media in media_can_process and type_media != "ig_reel"):
                        data_url_and_type: tuple = prepare_media(x.get("payload").get("url"))

                        media_processed.append([data_url_and_type, ""])

                    elif(type_media == "ig_reel"):

                        media_processed.append(["", x.get("payload").get("title")])

                    else:
                        media_processed.append(["", ""])

            else:
                type_media: str = attatchment[0].get("type") 
                x = attatchment[0]

                if(type_media in media_can_process and type_media == "ig_post"):
                    data_url_and_type: tuple = prepare_media(x.get("payload").get("url"))

                    media_processed.append([data_url_and_type, x.get("payload").get("title")])

                elif(type_media in media_can_process and type_media == "ig_story"):
                    data_url_and_type: tuple = prepare_media(x.get("payload").get("story_media_url"))

                    media_processed.append([data_url_and_type, x.get("payload").get("title")])

                elif(type_media in media_can_process and type_media != "ig_reel"):
                    data_url_and_type: tuple = prepare_media(x.get("payload").get("url"))

                    media_processed.append([data_url_and_type, ""])

                elif(type_media == "ig_reel"):

                    media_processed.append(["", x.get("payload").get("title")])

                else:
                    media_processed.append(["", ""])

        for i, media_proccesing in enumerate(media_processed):
            if(media_proccesing[0] != ""):
                data_url: str = media_proccesing[0][0]
                type_media: str = media_proccesing[0][1]

                media_processed[i][0] = process_media(data_url, type_media)

        media_elements: list[dict] = []

        for media in media_processed:
            media_elements.append({
                "media_description(if applicable)": media[0],
                "post_description(if applicable)": media[1]
            }) 

        return media_elements


#function that forms the message in the state
def message_form(current_message_batch: list, channel: str) -> dict:
    current_attatchments: list = []
    current_text: list = []

    #extract content from message batch
    for message in current_message_batch:
        if(isinstance(message, list) and message != []):
            current_attatchments.append(message)
        
        elif(isinstance(message, str)):
            current_text.append(message) 

    media: dict = {}
    if(current_attatchments != []):
        media_elements: list[dict] = media_element_form(current_attatchments, channel)

        for i, media_element in enumerate(media_elements):
            media[f"media_element_{i}"] = media_element

    text: str = "" 
    if(current_text != []):
        for txt in current_text:
            text += f"{txt} "

    message: dict = {
            "user_media": media, 
            "user_text": text
    }

    return message

#function that forms the message history in state
def message_history_form(id: str):
    user_messages: list[str] = read(f"{id}_usermsg") 
    agent_response: list[str] = read(f"{id}_agentres") 

    msg_hist: dict = {} 

    for i in range(len(agent_response)):
        msg_hist[f"user_message_{i}"] = user_messages[i] 
        msg_hist[f"agent_response_to_user_message_{i}"] = agent_response[i]
        
    return msg_hist

