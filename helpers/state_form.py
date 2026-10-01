from helpers.media_prep import prepare_media
from helpers.media_process import process_media
from helpers.log import read

#function to form  the media elements in state
def media_element_form(attatchments: list, referrals: list, channel: str) -> list[dict]:

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
        media_can_process: list[str] = ["ig_story", "story", "story_mention", "ig_post", "image", "video"]

        story_types: list[str] = ["ig_story", "story", "story_mention"]

        #prepare attatchments for processing
        for attatchment in attatchments:

            if(len(attatchment) > 1):
                for x in attatchment:
                    type_media: str = x.get("type")

                    if(type_media in media_can_process and type_media == "ig_post"):
                        data_url_and_type: tuple = prepare_media(x.get("payload").get("url"))

                        media_processed.append([data_url_and_type, x.get("payload").get("title")])

                    elif(type_media in media_can_process and type_media in story_types):
                        story_url: str = x.get("payload").get("url")

                        #meta sends the story link in url, fall back to story_media_url if it is missing
                        if(not story_url):
                            story_url = x.get("payload").get("story_media_url")

                        data_url_and_type: tuple = prepare_media(story_url)

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

                elif(type_media in media_can_process and type_media in story_types):
                    story_url: str = x.get("payload").get("url")

                    #meta sends the story link in url, fall back to story_media_url if it is missing
                    if(not story_url):
                        story_url = x.get("payload").get("story_media_url")

                    data_url_and_type: tuple = prepare_media(story_url)

                    media_processed.append([data_url_and_type, x.get("payload").get("title")])

                elif(type_media in media_can_process and type_media != "ig_reel"):
                    data_url_and_type: tuple = prepare_media(x.get("payload").get("url"))

                    media_processed.append([data_url_and_type, ""])

                elif(type_media == "ig_reel"):

                    media_processed.append(["", x.get("payload").get("title")])

                else:
                    media_processed.append(["", ""])

        #prepare referrals(ads) for processing
        for referral in referrals:
            data = referral.get("ads_context_data", {})

            if(data.get("photo_url")):
                data_url_and_type: tuple = prepare_media(data.get("photo_url"))

                media_processed.append([data_url_and_type, data.get("ad_title")])

            elif(data.get("video_url")): 
                data_url_and_type: tuple = prepare_media(data.get("video_url"))

                media_processed.append([data_url_and_type, data.get("ad_title")])

            else:
                media_processed.append(["", ""])

        #process all media
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

    elif(channel == "messenger"):
        media_processed: list[list] = []

        #prepare attatchments for processing
        for attatchment in attatchments:
            for x in attatchment:
                type_media: str = x.get("type")
                payload: dict = x.get("payload") or {}
                title: str = payload.get("title") or ""

                #photos, videos, and shared posts are downloaded, a shared post keeps its caption
                if(type_media in ["image", "video", "post", "ig_post"]):
                    data_url_and_type: tuple = prepare_media(payload.get("url"))

                    media_processed.append([data_url_and_type, title])

                #shared links and reels are not downloaded, their title is the caption
                elif(type_media in ["fallback", "reel", "ig_reel"]):
                    media_processed.append(["", title])

                #audio, files, and anything else cannot be described
                else:
                    media_processed.append(["", ""])

        #prepare referrals(ads) for processing, video_url is the thumbnail of the ad video so both are images
        for referral in referrals:
            data: dict = referral.get("ads_context_data") or {}
            ad_url: str = data.get("photo_url") or data.get("video_url") or ""
            ad_title: str = data.get("ad_title") or ""

            if(ad_url):
                data_url_and_type: tuple = prepare_media(ad_url)

                media_processed.append([data_url_and_type, ad_title])

            else:
                media_processed.append(["", ad_title])

        #process all media
        for i, media_proccesing in enumerate(media_processed):
            if(media_proccesing[0] != ""):
                data_url: str = media_proccesing[0][0]
                type_media: str = media_proccesing[0][1]

                media_processed[i][0] = process_media(data_url, type_media)

        #same two fields as instagram, so the prompts read a shop post or ad the same way on both
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
    current_referrals: list = []
    current_text: list = []

    #extract content from message batch
    for message in current_message_batch:
        if(isinstance(message, list) and message != []):
            current_attatchments.append(message)
        
        elif(isinstance(message, str)):
            current_text.append(message) 

        elif(isinstance(message, dict) and message != {}):
            current_referrals.append(message)

    media: dict = {}
    if(current_attatchments != [] or current_referrals != []):
        media_elements: list[dict] = media_element_form(current_attatchments, current_referrals, channel)

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
    agent_responses: list[str] = read(f"{id}_agentres") 

    msg_hist: dict = {} 

    if(len(user_messages) == len(agent_responses)):
        for i in range(len(user_messages)):
            msg_hist[f"user_message_{i}"] = user_messages[i]
            msg_hist[f"agent_response_to_user_message_{i}"] = agent_responses[i]
    else:
        if(len(user_messages) > len(agent_responses)):
           for i in range(len(user_messages)):
               if(i < len(agent_responses)):
                    msg_hist[f"user_message_{i}"] = user_messages[i]
                    msg_hist[f"agent_response_to_user_message_{i}"] = agent_responses[i]
               else:
                    msg_hist[f"user_message_{i}"] = user_messages[i]
        else: 
           for i in range(len(agent_responses)):
               if(i < len(user_messages)):
                    msg_hist[f"user_message_{i}"] = user_messages[i]
                    msg_hist[f"agent_response_to_user_message_{i}"] = agent_responses[i]

               else:
                    msg_hist[f"agent_response_to_user_message_{i}"] = agent_responses[i]


    return msg_hist

