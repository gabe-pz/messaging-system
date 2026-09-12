# Every agent in MAMS is created here, one router plus one AGE set per category, where AGE is the Analyzer then the Generator then the Enforcer.

# IMPORTS
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

from prompts import shared
from prompts.business_operations import prompts as business_operations_prompts


#MODEL
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

MODEL_NAME: str = os.getenv("MAMS_MODEL", "z-ai/glm-5.3-flash")

model: ChatOpenAI = ChatOpenAI(model=MODEL_NAME, base_url=OPENROUTER_BASE_URL, api_key=os.environ["OPENROUTER_API_KEY"], timeout=90)


#Only the generator agents get the search tool, an analyzer or an enforcer never searches.
web_search_tool: TavilySearch = TavilySearch(max_results=5, topic="general")


#Every category reads its facts out of its own json file in the details folder.
DETAILS_DIR: Path = Path(__file__).resolve().parent / "details"


#Reads one details file, MAMS should not boot at all when a category has no details to answer from.
def load_details(file_name: str) -> dict:
    path: Path = DETAILS_DIR / file_name

    with open(path, encoding="utf-8") as file:
        return json.load(file)


business_operations_details: dict = load_details("business_operations_details.json")


# AGENT CREATION
#Each agent is built once here so its system prompt is fixed and every turn reuses the same agent.

router_agent: Any = create_agent(model=model, system_prompt=shared.router_system_prompt())


# BUSINESS OPERATIONS
business_operations_analyzer_agent: Any = create_agent(model=model, system_prompt=business_operations_prompts.business_operations_analyzer_system_prompt())

business_operations_generator_agent: Any = create_agent(model=model, system_prompt=business_operations_prompts.business_operations_generator_system_prompt(), tools=[web_search_tool])

business_operations_enforcer_agent: Any = create_agent(model=model, system_prompt=business_operations_prompts.business_operations_enforcer_system_prompt())


#ROUTER CODES
#Every letter the router is allowed to answer with, anything else is treated as Z and gets no reply.
ROUTER_CODES: tuple = ("A", "Z")


#DATE TIME
def current_date_time() -> str:
    return datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")

#Function such that can read agents reply
def read_text(content: object) -> str:
    if isinstance(content, list):
        parts: list[str] = []

        for block in content:
            if isinstance(block, dict):
                parts.append(str(block.get("text", "")))

        return "".join(parts)

    return str(content)


#Runs one agent on one prompt and gives back what it wrote.
def run_agent(agent: Any, prompt_text: str) -> str:
    prompt = HumanMessage(content=prompt_text)

    result = agent.invoke({"messages": [prompt]})

    return read_text(result["messages"][-1].content).strip()


#Pulls the message out of the <reply> tags, the last opening tag wins since an enforcer sometimes thinks out loud first.
def extract_reply(text: str) -> str:
    match = re.search(r".*<reply>(.*?)</reply>", text, re.DOTALL)

    if match:
        return match.group(1).strip()

    return ""


#The enforced message when there is one
def final_reply(enforcer_output: str, draft: str) -> str:
    enforced: str = extract_reply(enforcer_output)

    if enforced:
        return enforced

    return extract_reply(draft)


#The details behind the codes the analyzer picked, given to the generator and the enforcer as JSON
def details_for_codes(codes: str, details: dict) -> str:
    picked: list = []

    for code in codes.split():
        if code in details:
            picked.append(details[code])

    return json.dumps(picked, separators=(",", ":"), ensure_ascii=False)


#Reads one incoming message and says which category answers it.
def run_router(user_message: str, history_text: str) -> str:
    print("--- [AGENT] Router ---")

    prompt_text: str = f"Current date and time: {current_date_time()}\nConversation so far:\n{history_text}\nCurrent message:\n{user_message}"

    code: str = run_agent(router_agent, prompt_text).upper()

    if code not in ROUTER_CODES:
        print(f"[ROUTER] unknown code {code}, treating it as Z")

        code = "Z"

    print(f"[ROUTER] code: {code}")

    return code


#BUSINESS OPERATIONS AGENT
#The full AGE run of this category, the analyzer picks the details, the generator writes the draft, the enforcer returns what is sent

def run_business_operations_agent(user_message: str, history_text: str) -> str:
    print("--- [AGENT] Business Operations Analyzer ---")

    analyzer_prompt: str = f"Current date and time: {current_date_time()}\nConversation so far:\n{history_text}\nCurrent message:\n{user_message}"

    codes: str = run_agent(business_operations_analyzer_agent, analyzer_prompt)

    details_text: str = details_for_codes(codes, business_operations_details)

    print(f"[BUSINESS OPERATIONS] codes: {codes}")

    print("--- [AGENT] Business Operations Generator ---")

    generator_prompt: str = f"Current date and time: {current_date_time()}\nConversation so far:\n{history_text}\nCurrent message:\n{user_message}\nDetails: {details_text}"

    draft: str = run_agent(business_operations_generator_agent, generator_prompt)

    print("--- [AGENT] Business Operations Enforcer ---")

    enforcer_prompt: str = f"Current message:\n{user_message}\nDetails: {details_text}\nDraft reply: {draft}"

    enforcer_output: str = run_agent(business_operations_enforcer_agent, enforcer_prompt)

    return final_reply(enforcer_output, draft)
