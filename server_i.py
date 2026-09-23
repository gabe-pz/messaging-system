from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv 
import uvicorn, asyncio
from src.mams import core

app = FastAPI()

load_dotenv()

#dicts for batching messages
state_dict: dict[str, str] = {}
message_batch_dict: dict[str, list] = {}

#main batch function
async def batch(id: str):
    await asyncio.sleep(30) 

    print(message_batch_dict[id]) 

    current_message: list = message_batch_dict[id] 

    #call mams with await asyncio.to_thread(mams_fn, mams_args), to create a worker thread for current id to process without stopping program ever
    await asyncio.to_thread(core, current_message, id)

    del state_dict[id]
    del message_batch_dict[id]

#process get data to verify webhook
@app.get("/ig/webhook")
async def ig_verify(request: Request) -> PlainTextResponse:
    challenge: str = request.query_params.get("hub.challenge", "")

    return PlainTextResponse(challenge)

#process post data
@app.post("/ig/webhook")
async def ig_hook(request: Request) -> dict:
    data: dict = await request.json()

    print(data)

    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
