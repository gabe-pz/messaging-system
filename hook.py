from fastapi import FastAPI, Request
import uvicorn, asyncio

app = FastAPI()

state_dict: dict = {}
message_batch_dict: dict[str, list[str | list]] = {}

async def batch(id: str):
    await asyncio.sleep(30) 

    print(message_batch_dict[id]) 

    current_message: list = message_batch_dict[id] 

    #call mams with await asyncio.to_thread(mams_fn, mams_args), to create a worker thread for current id to process without stopping program ever

    del state_dict[id]
    del message_batch_dict[id]





@app.post("/blooio/webhook")
async def blooio_hook(request: Request):
    #use await because the data from request does not come all at once, thus wait for it all to come and while still listing for more post
    data: dict = await request.json() 

    if(data.get("type") == "message.received"):
        id: str = data.get("data").get("sender")
        text: str = data.get("data").get("text") 
        attachments: list = data.get("data").get("attachments")


        if(id not in state_dict): 
            #create the list of messages and add the initial message(where a message is text + attachments)
            message_batch_dict[id] = [[text, attachments]]

            #start the clock for the current id
            state_dict[id] = asyncio.create_task(batch(id))

        else: 
            #append the new message that came in for user that was in countdown
            message_batch_dict[id].append([text, attachments])

            #cancel timer for current id
            state_dict[id].cancel()

            #start timer again for curretn id
            state_dict[id] = asyncio.create_task(batch(id))

    return {"status" : "ok"}




if(__name__ == "__main__"):
    uvicorn.run(app, port=8000)

    
