from helpers.state_form import message_form, message_history_form
from helpers.car_model_analyze import car_model_analyze
from helpers.log import write, write_bs, has_id, RESTRICTED_KEY
from src import mams as m
from src.rage_functions import BOOKING_LINK
from datetime import datetime
from zoneinfo import ZoneInfo


# FALLBACK REPLY
FALLBACK_RESPONSE: str = "Got it, ill get right back to you real quick."


def core(current_message_batch: list, id: str, channel: str) -> None:
    #create the users message from message batch
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

    #analyzer user message for a car model and update state if exists 
    try:
        car_model: str = car_model_analyze(user_message) 

        if(car_model != ""):
            write_bs(f"{id}_bstate", {"car_model": car_model})

    #a failed car model call must not stop the message from being logged and answered
    except Exception as error:
        print("CAR MODEL ERROR: " + str(error))

    #assemble the message history for state
    message_history: dict = {}

    try:
        message_history = message_history_form(id) 

    #without history the message is still answered on its own
    except Exception as error:
        print("HISTORY ERROR: " + str(error))

    #write the users message after history assembled
    try:
        write(f"{id}_usermsg", user_message)

    except Exception as error:
        print("WRITE ERROR: " + str(error))

    #assemble the state
    shop_time: datetime = datetime.now(ZoneInfo("America/Chicago"))

    current_date_time: str = shop_time.strftime("%A, %B %d, %Y at %I:%M %p")

    state: dict = {"current_date_time": current_date_time, "current_user_message": user_message, "message_history": message_history}

    #agents response
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

            print(agent_response)
            if("$" in agent_response):
                write_bs(f"{id}_bstate", {"pricing_state": "SENT"}) 
            if(BOOKING_LINK in agent_response):
                write_bs(f"{id}_bstate", {"booking_link_state": "SENT"})


    except Exception as error:
        print("CORE ERROR: " + str(error))

    #a customer who is not restricted always gets a reply, so anything that failed above falls back and loops in a human
    if(not restricted and (agent_response is None or agent_response.strip() == "")):
        agent_response = FALLBACK_RESPONSE

        print("trigger hil")

    #write agent response to reddis w/ upstash
    try:
        write(f"{id}_agentres", agent_response)

    except Exception as error:
        print("WRITE ERROR: " + str(error))













