from helpers.media_prep import prepare_image
from helpers.media_process import process_image
 
def state(current_message: list):
    attatchments: list[dict] = []

    for message in current_message:
        if(message[1] != []):
            attatchments.append(message[1])

    image_url: str = attatchments[0][0].get("url") 

    data_url: str = prepare_image(image_url) 

    image_decription: str = process_image(data_url)

    print(image_decription)
