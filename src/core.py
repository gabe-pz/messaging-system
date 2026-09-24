from helpers.state_form import message_form, message_history_form
from helpers.log import write


def core(current_message_batch: list, id: str, channel: str) -> None:
    #create the users message from message batch
    user_message: dict = message_form(current_message_batch, channel)

    print()
    print(user_message)

    # #write user message to reddis w/ upstash
    # write(f"{id}_usermsg", user_message)
    #
    # #assemble the message history for state
    # message_history: dict = message_history_form(id) 
    # print()
    # print(message_history) 
    #
    # #create the state
    # state: dict = {
    #         "current_user_message": user_message,
    #         "message_history": message_history
    # }
    # print()
    # print(state)
    # #pass state into mams
    # #mams(state)
    #
    # #write agent response to reddis w/ upstash
    # write(f"{id}_agentres", "AGENT RESPONSESS!!")












