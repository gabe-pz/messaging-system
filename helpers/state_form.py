

def state(current_message: list):
    attatchments: list = []

    for message in current_message:
        if(message[1] != []):
            attatchments.append(message[1])

    print(attatchments)


