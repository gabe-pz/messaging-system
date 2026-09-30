from json import load
from helpers.state_form import message_form, message_history_form
from helpers.car_model_analyze import car_model_analyze
from helpers.log import write, write_bs, read_bs, has_id, RESTRICTED_KEY
from src import mams as m
from src.rage_functions import BOOKING_LINK
from datetime import datetime
from zoneinfo import ZoneInfo
from helpers import senders as send


#core function that handles states and calls mams()
def core(current_message_batch: list, id: str, channel: str) -> None:

    #CREATE USER MESSAGE FROM MESSAGE BATCH
    try:
        user_message: dict = message_form(current_message_batch, channel)

    #media that breaks is dropped, so the text still gets answered
    except Exception as error:
        print("MESSAGE FORM ERROR: " + str(error))

        text_batch: list = []

        for message in current_message_batch:
            if(isinstance(message, str)):
                text_batch.append(message)

        user_message = message_form(text_batch, channel)

    #ASSEMBLE THE MESSAGE HISTORY
    message_history: dict = {}
    try:
        message_history = message_history_form(id) 

    #without history message can stil be answered on its own
    except Exception as error:
        print("HISTORY ERROR: " + str(error))


    #ANALYZE THE USER_MESSAGE FOR A CAR MODEL
    try:
        book_state: dict = read_bs(f"{id}_bstate")

        #runs every message with the history, so a car switch or a car finished over a few messages still gets saved
        car_model: str = car_model_analyze(user_message, message_history) 

        if(car_model != "" and car_model != book_state.get("car_model", "")):
            write_bs(f"{id}_bstate", {"car_model": car_model})

    #a failed car model call must not stop the message from being answered
    except Exception as error:
        print("CAR MODEL ERROR: " + str(error))


    #WRITE USER_MESSAGE 
    try:
        write(f"{id}_usermsg", user_message)

    except Exception as error:
        print("WRITE ERROR: " + str(error))

    
    #ASSEMBLE THE STATE
    shop_time: datetime = datetime.now(ZoneInfo("America/Chicago"))

    current_date_time: str = shop_time.strftime("%A, %B %d, %Y at %I:%M %p")

    state: dict = {"current_date_time": current_date_time, "current_user_message": user_message, "message_history": message_history}


    #RESPONSE OF "AGENT"
    agent_response: str = ""

    restricted: bool = False

    try:

        #restricted customers are handled by a human, so the system does not respond to them
        restricted = has_id(RESTRICTED_KEY, id)

        if(restricted):
            print("RESTRICTED: " + id)

        else:

            #one retry so a timed out or busy model still gets a real reply out
            try:
                agent_response = m.mams(state, id)

            except Exception as error:
                print("MAMS ERROR, RETRYING: " + str(error))

                agent_response = m.mams(state, id)

            #examples wrap replies in quotes, so a stray quote the model copies over is cut off
            agent_response = agent_response.strip().strip('"')

            #pricing and booking link states updated 
            if("$" in agent_response):
                write_bs(f"{id}_bstate", {"pricing_state": "SENT"}) 
            if(BOOKING_LINK in agent_response):
                write_bs(f"{id}_bstate", {"booking_link_state": "SENT"})


    except Exception as error:
        print("CORE ERROR: " + str(error))

    
    #SEND RESPONSE FOR PARICULAR CHANNEL 
    if(agent_response != "" and not restricted): 
        if(channel == "ig"):
            send.send_ig_message(id, agent_response)
        elif(channel == "blooio"):
            send.send_blooio_message(id, agent_response)




    #WRITE AGENT RESPONSE 
    try:
        write(f"{id}_agentres", agent_response)

    except Exception as error:
        print("WRITE ERROR: " + str(error))













