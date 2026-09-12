# Messaging System 
The goal of this project was to create a messaging system that could receive user messages on behalf of a business, process them in an intelligent manner, and submit a reply that is grounded in 
the business's details. 

## The path a message takes

```
POST /webhook/<channel>  ->  batching  ->  media processing  ->  router  ->  category agents (A G E)  ->  send reply
                                                                                  memory
```

## Setup

1. Install the dependencies:

```
pip install -r requirements.txt
```

2. Make a `.env` file inside the MAMS folder 
- Use .env.example for how to structure and fill in your actual values
- Set a channel to `0` to turn it off, it still answers its webhook but never runs the agents.

3. Run it:

```
python3 mams.py
```

4. Open the tunnel in a second terminal:

```
ngrok http [PORT]
```

5. Give each platform its webhook url, using the ngrok address:

| Channel | Webhook url |
|---|---|
| Instagram | `https://<your-ngrok>.ngrok-free.app/webhook/instagram` |
| Messenger | `https://<your-ngrok>.ngrok-free.app/webhook/messenger` |
| Blooio | `https://<your-ngrok>.ngrok-free.app/webhook/blooio` |


## Adding a category

1. Add the new letter and one line describing it to the Categories list in the router system prompt 
2. Make a `prompts/<category>/prompts.py` and `prompts/<category>/examples.py`, for that category
3. Make a `details/<category>_details.json` and load it in `agents.py` with `load_details`
4. Create the three agents for it in `agents.py` 
5. Write a `run_<category>_agent` function in `agents.py`
6. Add one `case` for the letter that correspond to the new category `mams.py` switch statement

