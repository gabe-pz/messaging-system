from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv 
from helpers import username as un
import uvicorn, asyncio, os
from src.core import core

app = FastAPI()

#load env
load_dotenv()

#the verify token typed into the meta app dashboard when the webhook is subscribed
MESSENGER_VERIFY_TOKEN: str = os.environ["MESSENGER_VERIFY_TOKEN"]

#dicts for message batching
state_dict: dict[str, asyncio.Task] = {}
message_batch_dict: dict[str, list] = {}

#CONSTANTS
MESSENGER_BATCH_TIME: int = 20

#main batch function
async def batch(id: str):
    await asyncio.sleep(MESSENGER_BATCH_TIME) 

    current_message_batch: list = message_batch_dict[id] 

    del state_dict[id]
    del message_batch_dict[id]

    #the name lookup is a blocking call, so it runs off the event loop
    user_name: str = await asyncio.to_thread(un.username_messenger, id)

    print(f"INCOMING MESSAGE BATCH FROM on MESSENGER from: {user_name}")
    print(f"Message batch: {current_message_batch}")
    print()

    #call mams with await asyncio.to_thread(mams_fn, mams_args), to create a worker thread for current id to process without stopping program ever
    await asyncio.to_thread(core, current_message_batch, id, "messenger")


#pulls [text, attachments, referral] out of one messaging event, None when there is nothing to answer
def event_message(event: dict) -> list | None:
    message: dict = event.get("message") or {}
    postback: dict = event.get("postback") or {}

    #echoes are the page's own sends, from this system or the owner replying in the inbox
    if(message.get("is_echo")):
        return None

    #a postback is a get started, icebreaker, or menu tap, its title is what the customer tapped
    text: str | None = message.get("text") or postback.get("title") or None

    #stickers like the thumbs up have nothing to describe or answer
    attachments: list = [attachment for attachment in message.get("attachments") or [] if attachment.get("type") != "sticker"]

    #an ad click comes inside the message, on its own for an existing thread, or with a get started tap
    referral: dict = message.get("referral") or event.get("referral") or postback.get("referral") or {}

    #only ad referrals carry context, m.me links and shop products do not
    if(referral.get("source") != "ADS"):
        referral = {}

    if(not text and not attachments and not referral):
        return None

    return [text, attachments, referral]


#process GET data to verify webhook
@app.get("/messenger/webhook")
async def messenger_verify(request: Request) -> PlainTextResponse:
    mode: str = request.query_params.get("hub.mode", "")
    token: str = request.query_params.get("hub.verify_token", "")
    challenge: str = request.query_params.get("hub.challenge", "")

    #meta only gets its challenge back when the token matches the one set in the app dashboard
    if(mode == "subscribe" and token == MESSENGER_VERIFY_TOKEN):
        return PlainTextResponse(challenge)

    print("MESSENGER WEBHOOK VERIFY FAILED: mode or verify token did not match")

    return PlainTextResponse("Forbidden", status_code=403)

#process POST data
@app.post("/messenger/webhook")
async def messenger_hook(request: Request) -> dict:
    data: dict = await request.json()

    #messenger events always come as a page object
    if(data.get("object") != "page"):
        return {"status": "ok"}

    #meta can group several entries and events into one POST
    for entry in data.get("entry") or []:
        for event in entry.get("messaging") or []:
            id: str = (event.get("sender") or {}).get("id")
            message: list | None = event_message(event)

            #reads, deliveries, reactions, echoes, and sticker only messages have nothing to answer
            if(not id or message is None):
                continue

            if(id not in state_dict): 
                #create the list of messages and add the initial message(where a message is text + attachments + referral)
                message_batch_dict[id] = message

                #start the clock for the current id
                state_dict[id] = asyncio.create_task(batch(id))

            else: 
                #append the new message that came in for user that was in countdown
                message_batch_dict[id].extend(message)

                #cancel timer for current id
                state_dict[id].cancel()

                #start timer again for current id
                state_dict[id] = asyncio.create_task(batch(id))

    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
