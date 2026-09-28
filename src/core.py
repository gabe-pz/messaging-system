from helpers.state_form import message_form, message_history_form
from helpers.car_model_analyze import car_model_analyze
from helpers.log import write, write_bs
from src import mams as m
from datetime import datetime
from zoneinfo import ZoneInfo

def core(current_message_batch: list, id: str, channel: str) -> None:
    #create the users message from message batch
    user_message: dict = message_form(current_message_batch, channel)

    #analyzer user message for a car model and update state if exists 
    car_model: str = car_model_analyze(user_message) 
    if(car_model != ""):
        write_bs(f"{id}_bstate", "car_model", car_model)

    #assemble the message history for state
    message_history: dict = message_history_form(id) 

    #write the users message after history assembled
    write(f"{id}_usermsg", user_message)

    #assemble the state
    shop_time: datetime = datetime.now(ZoneInfo("America/Chicago"))

    current_date_time: str = shop_time.strftime("%A, %B %d, %Y at %I:%M %p")

    state: dict = {"current_date_time": current_date_time, "current_user_message": user_message, "message_history": message_history}

    #agents response
    agent_response: str = ""

    try:
        agent_response = m.mams(state)

        if("$" in agent_response):
            write_bs(f"{id}_bstate", "pricing_state", "SENT")


    except Exception as error:
        print("CORE ERROR: " + str(error))


    #write agent response to reddis w/ upstash
    write(f"{id}_agentres", agent_response)













