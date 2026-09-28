from dotenv import load_dotenv 

from src.prompts.router import router_instructions as ri 
from src.prompts.router import router_exs as re

from src.prompts.s_p import s_p_analyze_exs as spaEX
from src.prompts.s_p import s_p_gen_sys_prompt as spgSP
from src.prompts.s_p import s_p_enforce as spE
from src.prompts.s_p import s_p_regen_sys_prompt as spRE
import os, requests, json

#API key
load_dotenv() 
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")

#JEV model for R, A, and E
DECISIONS_URL: str = "https://openrouter.ai/api/alpha/decisions"
ROUTER_MODEL: str = "typesafe/jev-1.13"

#GLM model for G and Potentially E
GENERATORS_URL: str = "https://openrouter.ai/api/v1/chat/completions"
GENERATOR_MODEL: str = "z-ai/glm-5.3"

#open up files
with open("details-json/service_pricing_details.json", "r") as file: 
    s_p_details_dict: dict = json.load(file)

#main route function
def route(state: dict) -> str:
    CONFIDENCE_THRESHOLD: float = 0.1

    #define the criteria for routing 
    route_criteria: dict[str, str] = {
            "service_and_pricing": ri.service_and_prices_instructions(), 
            "booking": ri.booking_instructions(), 
            "business_operations": ri.business_operations_instructions(), 
            "general_text": ri.general_text_instructions()
    }

    #define the instructions for routing and the main question 
    route_instructions: str = "Which category does the customers current message belong to? Use the message history ONLY for context."
    route_question: dict = {"type": "choice", "instructions": route_instructions+"\n"+re.route_exs(), "criteria": route_criteria}

    #setup the request
    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    questions: dict = {"route": route_question}
    payload: dict = {"model": ROUTER_MODEL, "state": state, "questions": questions}

    #send the request with error handling
    response = requests.post(DECISIONS_URL, headers=headers, json=payload, timeout=10)
    response.raise_for_status()

    #extract response
    result: dict = response.json()
    route_answer: dict = result["answers"]["route"]
    category: str = route_answer["choice"]
    confidence: float = route_answer["confidence"]

    if(confidence < CONFIDENCE_THRESHOLD):
        return "general_text"

    return category

#analyzer functions for each category
def service_and_pricing_analyzer(state: dict) -> list[str]:
    SERVICE_CONFIDENCE_THRESHOLD: float = 0.5

    #questions
    tint_question: dict = {"type": "noul", "instructions": "Is the customer asking about window tint in `current_user_message`?"+"\n"+spaEX.window_tint_exs()}
    ppf_question: dict = {"type": "noul", "instructions": "Is the customer asking about clear paint protection film (PPF) in `current_user_message`?"+"\n"+spaEX.ppf_exs()}

    #assemble questions and setup request
    service_questions: dict = {"s8": ppf_question, "s3": tint_question}
    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload: dict = {"model": ROUTER_MODEL, "state": state, "questions": service_questions}

    #send the request with error handling
    response = requests.post(DECISIONS_URL, headers=headers, json=payload, timeout=10)
    response.raise_for_status()

    #extract response
    result: dict = response.json()

    #list of services
    services: list[str] = []

    for service_name in service_questions:
        probability_yes: float = result["answers"][service_name]["noul"]

        if(probability_yes > SERVICE_CONFIDENCE_THRESHOLD):
            services.append(service_name)

    #fetch details for analyzed services
    service_details: list = []
    for service in services:
        service_details.append(s_p_details_dict[service])


    return service_details

#generator functions for each category
def service_and_pricing_generator(state: dict, service_details: list) -> str:
    #system prompt goes first and never changes, so it can be cached
    system_block: dict = {"type": "text", "text": spgSP.s_p_generator_system_prompt(), "cache_control": {"type": "ephemeral"}}
    system_message: dict = {"role": "system", "content": [system_block]}

    #compact json with no extra spaces or escaped unicode
    state_as_text: str = json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    #assemble the details
    details: str = ""
    for service_detail in service_details:
        details += json.dumps(service_detail) + "\n"

    #create the text to pass
    user_text: str = f"SERVICE_DETAILS: {details}\n STATE: {state_as_text}"
    user_message: dict = {"role": "user", "content": user_text}

    #prepare the request
    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    provider_settings: dict = {"order": ["z-ai"], "allow_fallbacks": True}
    reasoning_settings: dict = {"effort": "medium"}
    payload: dict = {"model": GENERATOR_MODEL, "messages": [system_message, user_message], "provider": provider_settings, "reasoning": reasoning_settings, "max_tokens": 8000}

    #send request
    response = requests.post(GENERATORS_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    #grab reply
    result: dict = response.json()
    reply: str = result["choices"][0]["message"]["content"]

    return reply

#enforcment functions 
def service_and_pricing_enforcer(response: str) -> bool:
    ENFORCE_CONFIDENCE_THREASHOLD: float = 0.65 

    enforce_question: dict = {"type": "noul", "instructions": f"Is the agents response currenty going against any of the rules defined here\n{spE.s_p_enforce()}\n?"}
    enforce_q: dict = {"enforce_A": enforce_question}
    #prepare request
    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload: dict = {"model": ROUTER_MODEL, "state": response, "questions": enforce_q}

    #send request
    response = requests.post(DECISIONS_URL, headers=headers, json=payload, timeout=10)
    response.raise_for_status()

    #extract response
    result: dict = response.json()

    probability_yes: float = result["answers"]["enforce_A"]["noul"]

    if(probability_yes > ENFORCE_CONFIDENCE_THREASHOLD):
        return True 
    else: 
        return False

#regeneration functions
def service_and_pricing_regen(state: dict, service_details: list, response: str) -> str: 

    #system prompt goes first and never changes, so it can be cached
    system_block: dict = {"type": "text", "text": spRE.s_p_regen_sys_prompt(), "cache_control": {"type": "ephemeral"}}
    system_message: dict = {"role": "system", "content": [system_block]}

    #compact json with no extra spaces or escaped unicode
    state_as_text: str = json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    #assemble the details
    details: str = ""
    for service_detail in service_details:
        details += json.dumps(service_detail) + "\n"

    #create the text to pass
    user_text: str = f"SERVICE_DETAILS: {details}\n STATE: {state_as_text}"
    user_message: dict = {"role": "user", "content": user_text}

    #prepare the request
    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    provider_settings: dict = {"order": ["z-ai"], "allow_fallbacks": True}
    reasoning_settings: dict = {"effort": "medium"}
    payload: dict = {"model": GENERATOR_MODEL, "messages": [system_message, user_message], "provider": provider_settings, "reasoning": reasoning_settings, "max_tokens": 8000}

    #send request
    response = requests.post(GENERATORS_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    #grab reply
    result: dict = response.json()
    reply: str = result["choices"][0]["message"]["content"]

    return reply
