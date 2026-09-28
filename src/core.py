from helpers.state_form import message_form, message_history_form
from helpers.log import write
from src import mams as m
from datetime import datetime
from zoneinfo import ZoneInfo

def core(current_message_batch: list, id: str, channel: str) -> None:
    #create the users message from message batch
    user_message: dict = message_form(current_message_batch, channel)

    #assemble the message history for state
    message_history: dict = message_history_form(id) 

    #write the users message after history assembled
    write(f"{id}_usermsg", user_message)

    #create the state with the shop's local time
    shop_time: datetime = datetime.now(ZoneInfo("America/Chicago"))

    current_date_time: str = shop_time.strftime("%A, %B %d, %Y at %I:%M %p")

    state: dict = {"current_date_time": current_date_time, "current_user_message": user_message, "message_history": message_history}

    #a failed run still stores an empty reply so user and agent turns stay paired
    agent_response: str = ""

    try:
        agent_response = m.mams(state)

    except Exception as error:
        print("CORE ERROR: " + str(error))

    print(agent_response)

    #write agent response to reddis w/ upstash
    write(f"{id}_agentres", agent_response)













