from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv 
import uvicorn, asyncio
from src.core import core

app = FastAPI()

load_dotenv()

#dicts for message batching
state_dict: dict[str, str] = {}
message_batch_dict: dict[str, list] = {}

#main batch function
async def batch(id: str):
    
    await asyncio.sleep(30) 

    print(message_batch_dict[id]) 

    current_message_batch: list = message_batch_dict[id] 
    
    #call mams with await asyncio.to_thread(mams_fn, mams_args), to create a worker thread for current id to process without stopping program ever
    await asyncio.to_thread(core, current_message_batch, id, "ig")

    del state_dict[id]
    del message_batch_dict[id]

#process GET data to verify webhook
@app.get("/ig/webhook")
async def ig_verify(request: Request) -> PlainTextResponse:
    challenge: str = request.query_params.get("hub.challenge")

    return PlainTextResponse(challenge)

#process POST data
@app.post("/ig/webhook")
async def ig_hook(request: Request) -> dict:
    data: dict = await request.json()

    #grab the event
    event: dict = data.get("entry")[0].get("messaging")[0] 

    #check if its an incoming message from a user 
    if("message" in event and "is_echo" not in event["message"]):
        id: str = event.get("sender").get("id") 
        text: str = event.get("message").get("text")
        attachments: list = event.get("message").get("attachments") 
        referral: dict = event.get("message").get("referral")

        if(id not in state_dict): 
            #create the list of messages and add the initial message(where a message is text + attachments)
            message_batch_dict[id] = [text, attachments, referral]

            #start the clock for the current id
            state_dict[id] = asyncio.create_task(batch(id))

        else: 
            #append the new message that came in for user that was in countdown
            message_batch_dict[id].append(text)
            message_batch_dict[id].append(attachments)
            message_batch_dict[id].append(referral)

            #cancel timer for current id
            state_dict[id].cancel()

            #start timer again for curretn id
            state_dict[id] = asyncio.create_task(batch(id))

    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
