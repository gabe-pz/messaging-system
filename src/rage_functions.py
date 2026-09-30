from dotenv import load_dotenv 

from src.prompts.router import router_instructions as ri 
from src.prompts.router import router_exs as re

from src.prompts.s_p import s_p_analyze_exs as spaEX
from src.prompts.s_p import s_p_gen_sys_prompt as spgSP
from src.prompts.s_p import s_p_enforce as spE
from src.prompts.s_p import s_p_regen_sys_prompt as spRE

from src.prompts.business_ops import b_o_analyze_exs as boaEX
from src.prompts.business_ops import b_o_gen_sys_prompt as bogSP
from src.prompts.business_ops import b_o_enforce as boE
from src.prompts.business_ops import b_o_regen_sys_prompt as boRE

from src.prompts.hil import s_rh_gen_sys_prompt as srhSP
from src.prompts.hil import ack_gen_sys_prompt as ackSP
from src.prompts.hil import escalation_gen_sys_prompt as escSP

from src.prompts.booking import b_gen_sys_prompt as bgSP
from src.prompts.booking import b_enforce as bE
from src.prompts.booking import b_regen_sys_prompt as bRE

from src.prompts.car_model import car_model_int_sys_prompt as cmiSP

from src.prompts.general import closing_gen_sys_prompt as closingSP
from src.prompts.general import closing_enforce as closingE
from src.prompts.general import closing_regen_sys_prompt as closingRE
from src.prompts.general import phone_gen_sys_prompt as phoneSP

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

with open("details-json/business_operations_details.json", "r") as file: 
    b_o_details_dict: dict = json.load(file)


# BOOKING LINK
BOOKING_LINK: str = "https://filthy-booking-website.vercel.app"


#main route function
def route(state: dict) -> str:
    CONFIDENCE_THRESHOLD: float = 0.1

    #define the criteria for routing 
    route_criteria: dict[str, str] = {
            "service_and_pricing": ri.service_and_prices_instructions(), 
            "booking": ri.booking_instructions(), 
            "business_operations": ri.business_operations_instructions(), 
            "services_req_humans": ri.services_req_humans_instructions(), 
            "escalation": ri.escalation_instructions(), 
            "phone_call": ri.phone_call_instructions(), 
            "closing_statements": ri.closing_statements_instructions(), 
            "owner_conversation": ri.owner_conversation_instructions(), 
            "off_topic": ri.off_topic_instructions()
    }

    #define the instructions for routing and the main question 
    route_instructions: str = "Which category does the customers current message belong to? Read the message history first and interpret the current message in light of it (short replies like 'yes' or 'that one' continue the prior topic); classify the current message, using the history for context."
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

#analyzer function for service and pricing
def service_and_pricing_analyzer(state: dict) -> list[str]:
    SERVICE_CONFIDENCE_THRESHOLD: float = 0.1

    #questions
    tint_question: dict = {"type": "noul", "instructions": "Is the customer asking about window tint in `current_user_message`?"+"\n"+spaEX.window_tint_exs()}
    ppf_question: dict = {"type": "noul", "instructions": "Is the customer asking about clear paint protection film (PPF) in `current_user_message`?"+"\n"+spaEX.ppf_exs()}
    starlight_question: dict = {"type": "noul", "instructions": "Is the customer asking about a starlight headliner in `current_user_message`?"+"\n"+spaEX.starlight_exs()}
    wrap_question: dict = {"type": "noul", "instructions": "Is the customer asking about a vinyl wrap in `current_user_message`?"+"\n"+spaEX.vinyl_wrap_exs()}
    colored_ppf_question: dict = {"type": "noul", "instructions": "Is the customer asking about colored paint protection film (PPF) in `current_user_message`?"+"\n"+spaEX.colored_ppf_exs()}
    ceramic_question: dict = {"type": "noul", "instructions": "Is the customer asking about ceramic coating or paint correction in `current_user_message`?"+"\n"+spaEX.ceramic_coating_exs()}
    caliper_question: dict = {"type": "noul", "instructions": "Is the customer asking about caliper wraps in `current_user_message`?"+"\n"+spaEX.caliper_wrap_exs()}
    windshield_ppf_question: dict = {"type": "noul", "instructions": "Is the customer asking about paint protection film (PPF) on the windshield in `current_user_message`?"+"\n"+spaEX.windshield_ppf_exs()}

    #assemble questions and setup request
    service_questions: dict = {"s1": starlight_question, "s2": wrap_question, "s3": tint_question, "s4": colored_ppf_question, "s5": ceramic_question, "s6": caliper_question, "s7": windshield_ppf_question, "s8": ppf_question}
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

#generator functions for service and pricing
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

#enforcment function for service and pricing
def service_and_pricing_enforcer(state: dict, response: str) -> bool:
    ENFORCE_CONFIDENCE_THREASHOLD: float = 0.65 

    enforce_question: dict = {"type": "noul", "instructions": f"Is the agents response currenty going against any of the rules defined here\n{spE.s_p_enforce()}\n?"}
    enforce_q: dict = {"enforce_A": enforce_question}

    state_as_text: str = json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    #the checker needs the conversation to catch repeats, re-asks, and the ad car
    enforce_state: str = f"STATE: {state_as_text}\nAGENT_RESPONSE:\n{response}"

    #prepare request
    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload: dict = {"model": ROUTER_MODEL, "state": enforce_state, "questions": enforce_q}

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

#regeneration functions for service and pricing
def service_and_pricing_regen(state: dict, service_details: list, response: str) -> str: 

    #system prompt goes first and never changes, so it can be cached
    system_block: dict = {"type": "text", "text": spRE.s_p_regenerator_sys_prompt(), "cache_control": {"type": "ephemeral"}}
    system_message: dict = {"role": "system", "content": [system_block]}

    #compact json with no extra spaces or escaped unicode
    state_as_text: str = json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    #assemble the details
    details: str = ""
    for service_detail in service_details:
        details += json.dumps(service_detail) + "\n"

    #create the text to pass
    user_text: str = f"SERVICE_DETAILS: {details}\n STATE: {state_as_text}\n FLAGGED_RESPONSE: {response}"
    user_message: dict = {"role": "user", "content": user_text}

    #prepare the request
    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    provider_settings: dict = {"order": ["z-ai"], "allow_fallbacks": True}
    reasoning_settings: dict = {"effort": "medium"}
    payload: dict = {"model": GENERATOR_MODEL, "messages": [system_message, user_message], "provider": provider_settings, "reasoning": reasoning_settings, "max_tokens": 8000}

    #send request
    http_response = requests.post(GENERATORS_URL, headers=headers, json=payload, timeout=60)
    http_response.raise_for_status()

    #grab reply
    result: dict = http_response.json()
    reply: str = result["choices"][0]["message"]["content"]

    return reply

#analyzer functions for business operations
def business_operations_analyzer(state: dict) -> list[dict]:
    BUSINESS_CONFIDENCE_THRESHOLD: float = 0.5

    #questions
    hours_question: dict = {"type": "noul", "instructions": "Is the customer asking about the shop's hours or whether it is open in `current_user_message`?"+"\n"+boaEX.hours_exs()}
    years_question: dict = {"type": "noul", "instructions": "Is the customer asking how long the shop has been in business in `current_user_message`?"+"\n"+boaEX.years_in_business_exs()}
    name_question: dict = {"type": "noul", "instructions": "Is the customer asking about or confirming the name of the shop in `current_user_message`?"+"\n"+boaEX.business_name_exs()}
    owner_question: dict = {"type": "noul", "instructions": "Is the customer asking who owns or runs the shop in `current_user_message`?"+"\n"+boaEX.owner_exs()}
    address_question: dict = {"type": "noul", "instructions": "Is the customer asking where the shop is located in `current_user_message`?"+"\n"+boaEX.address_exs()}
    phone_question: dict = {"type": "noul", "instructions": "Is the customer asking for the shop's phone number in `current_user_message`?"+"\n"+boaEX.phone_exs()}
    email_question: dict = {"type": "noul", "instructions": "Is the customer asking for the shop's email address in `current_user_message`?"+"\n"+boaEX.email_exs()}
    website_question: dict = {"type": "noul", "instructions": "Is the customer asking for the shop's website in `current_user_message`?"+"\n"+boaEX.website_exs()}
    employees_question: dict = {"type": "noul", "instructions": "Is the customer asking how many people work at the shop in `current_user_message`?"+"\n"+boaEX.employees_exs()}
    license_question: dict = {"type": "noul", "instructions": "Is the customer asking whether the shop is licensed or registered in `current_user_message`?"+"\n"+boaEX.license_exs()}
    person_question: dict = {"type": "noul", "instructions": "Is the customer asking who they are talking to in `current_user_message`?"+"\n"+boaEX.person_talking_to_exs()}
    payments_question: dict = {"type": "noul", "instructions": "Is the customer asking which payment methods the shop accepts in `current_user_message`?"+"\n"+boaEX.payments_exs()}

    #assemble questions and setup request
    business_questions: dict = {"b1": hours_question, "b2": years_question, "b3": name_question, "b4": owner_question, "b5": address_question, "b6": phone_question, "b7": email_question, "b8": website_question, "b9": employees_question, "b10": license_question, "b11": person_question, "b12": payments_question}
    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload: dict = {"model": ROUTER_MODEL, "state": state, "questions": business_questions}

    #send the request with error handling
    response = requests.post(DECISIONS_URL, headers=headers, json=payload, timeout=10)
    response.raise_for_status()

    #extract response
    result: dict = response.json()

    #list of business fields
    fields: list[str] = []

    for field_name in business_questions:
        probability_yes: float = result["answers"][field_name]["noul"]

        if(probability_yes > BUSINESS_CONFIDENCE_THRESHOLD):
            fields.append(field_name)

    #fetch details for analyzed fields
    business_details: list = []
    for field in fields:
        business_details.append(b_o_details_dict[field])

    return business_details

#generator functions for business operations
def business_operations_generator(state: dict, business_details: list) -> str:
    #system prompt goes first and never changes, so it can be cached
    system_block: dict = {"type": "text", "text": bogSP.b_o_generator_sys_prompt(), "cache_control": {"type": "ephemeral"}}
    system_message: dict = {"role": "system", "content": [system_block]}

    #compact json with no extra spaces or escaped unicode
    state_as_text: str = json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    #assemble the details
    details: str = ""
    for business_detail in business_details:
        details += json.dumps(business_detail) + "\n"

    #create the text to pass
    user_text: str = f"BUSINESS_DETAILS: {details}\n STATE: {state_as_text}"
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

#enforcment functions for business operations
def business_operations_enforcer(state: dict, response: str) -> bool:
    ENFORCE_CONFIDENCE_THREASHOLD: float = 0.65 

    enforce_question: dict = {"type": "noul", "instructions": f"Is the agents response currenty going against any of the rules defined here\n{boE.b_o_enforce()}\n?"}
    enforce_q: dict = {"enforce_A": enforce_question}

    state_as_text: str = json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    #the checker needs the conversation to catch repeats and re-asks
    enforce_state: str = f"STATE: {state_as_text}\nAGENT_RESPONSE:\n{response}"

    #prepare request
    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload: dict = {"model": ROUTER_MODEL, "state": enforce_state, "questions": enforce_q}

    #send request
    http_response = requests.post(DECISIONS_URL, headers=headers, json=payload, timeout=10)
    http_response.raise_for_status()

    #extract response
    result: dict = http_response.json()

    probability_yes: float = result["answers"]["enforce_A"]["noul"]

    if(probability_yes > ENFORCE_CONFIDENCE_THREASHOLD):
        return True 
    else: 
        return False

#regeneration functions for business operations
def business_operations_regen(state: dict, business_details: list, response: str) -> str: 

    #system prompt goes first and never changes, so it can be cached
    system_block: dict = {"type": "text", "text": boRE.b_o_regenerator_sys_prompt(), "cache_control": {"type": "ephemeral"}}
    system_message: dict = {"role": "system", "content": [system_block]}

    #compact json with no extra spaces or escaped unicode
    state_as_text: str = json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    #assemble the details
    details: str = ""
    for business_detail in business_details:
        details += json.dumps(business_detail) + "\n"

    #create the text to pass
    user_text: str = f"BUSINESS_DETAILS: {details}\n STATE: {state_as_text}\n FLAGGED_RESPONSE: {response}"
    user_message: dict = {"role": "user", "content": user_text}

    #prepare the request
    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    provider_settings: dict = {"order": ["z-ai"], "allow_fallbacks": True}
    reasoning_settings: dict = {"effort": "medium"}
    payload: dict = {"model": GENERATOR_MODEL, "messages": [system_message, user_message], "provider": provider_settings, "reasoning": reasoning_settings, "max_tokens": 8000}

    #send request
    http_response = requests.post(GENERATORS_URL, headers=headers, json=payload, timeout=60)
    http_response.raise_for_status()

    #grab reply
    result: dict = http_response.json()
    reply: str = result["choices"][0]["message"]["content"]

    return reply



#generator function for services requiring humans
def services_rh_gen(state: dict) -> str: 
    #system prompt goes first and never changes, so it can be cached
    system_block: dict = {"type": "text", "text": srhSP.s_rh_system_prompt(), "cache_control": {"type": "ephemeral"}}
    system_message: dict = {"role": "system", "content": [system_block]}

    #compact json with no extra spaces or escaped unicode
    state_as_text: str = json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    #create the text to pass
    user_text: str = f"STATE: {state_as_text}"
    user_message: dict = {"role": "user", "content": user_text}

    #prepare the request
    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    provider_settings: dict = {"order": ["z-ai"], "allow_fallbacks": True}
    reasoning_settings: dict = {"effort": "medium"}
    payload: dict = {"model": GENERATOR_MODEL, "messages": [system_message, user_message], "provider": provider_settings, "reasoning": reasoning_settings, "max_tokens": 8000}

    #send request
    http_response = requests.post(GENERATORS_URL, headers=headers, json=payload, timeout=60)
    http_response.raise_for_status()

    #grab reply
    result: dict = http_response.json()
    reply: str = result["choices"][0]["message"]["content"]

    return reply


# ACKNOWLEDGE GENERATOR
def acknowledge_service_gen(state: dict) -> str:
    #system prompt goes first and never changes, so it can be cached
    system_block: dict = {"type": "text", "text": ackSP.ack_system_prompt(), "cache_control": {"type": "ephemeral"}}

    system_message: dict = {"role": "system", "content": [system_block]}

    state_as_text: str = json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    user_text: str = f"STATE: {state_as_text}"

    user_message: dict = {"role": "user", "content": user_text}

    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}

    provider_settings: dict = {"order": ["z-ai"], "allow_fallbacks": True}

    reasoning_settings: dict = {"effort": "low"}

    payload: dict = {"model": GENERATOR_MODEL, "messages": [system_message, user_message], "provider": provider_settings, "reasoning": reasoning_settings, "max_tokens": 4000}

    http_response: requests.Response = requests.post(GENERATORS_URL, headers=headers, json=payload, timeout=60)

    http_response.raise_for_status()

    result: dict = http_response.json()

    reply: str = result["choices"][0]["message"]["content"]

    return reply


# ESCALATION GENERATOR
def escalation_gen(state: dict) -> str:
    #system prompt goes first and never changes, so it can be cached
    system_block: dict = {"type": "text", "text": escSP.escalation_system_prompt(), "cache_control": {"type": "ephemeral"}}

    system_message: dict = {"role": "system", "content": [system_block]}

    state_as_text: str = json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    user_text: str = f"STATE: {state_as_text}"

    user_message: dict = {"role": "user", "content": user_text}

    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}

    provider_settings: dict = {"order": ["z-ai"], "allow_fallbacks": True}

    reasoning_settings: dict = {"effort": "low"}

    payload: dict = {"model": GENERATOR_MODEL, "messages": [system_message, user_message], "provider": provider_settings, "reasoning": reasoning_settings, "max_tokens": 4000}

    http_response: requests.Response = requests.post(GENERATORS_URL, headers=headers, json=payload, timeout=60)

    http_response.raise_for_status()

    result: dict = http_response.json()

    reply: str = result["choices"][0]["message"]["content"]

    return reply


# BOOKING GENERATOR
def booking_generator(state: dict, booking_details: dict) -> str:
    #system prompt goes first and never changes, so it can be cached
    system_block: dict = {"type": "text", "text": bgSP.b_generator_sys_prompt(), "cache_control": {"type": "ephemeral"}}

    system_message: dict = {"role": "system", "content": [system_block]}

    state_as_text: str = json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    details_as_text: str = json.dumps(booking_details, ensure_ascii=False)

    user_text: str = f"BOOKING_DETAILS: {details_as_text}\n STATE: {state_as_text}"

    user_message: dict = {"role": "user", "content": user_text}

    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}

    provider_settings: dict = {"order": ["z-ai"], "allow_fallbacks": True}

    reasoning_settings: dict = {"effort": "medium"}

    payload: dict = {"model": GENERATOR_MODEL, "messages": [system_message, user_message], "provider": provider_settings, "reasoning": reasoning_settings, "max_tokens": 8000}

    http_response: requests.Response = requests.post(GENERATORS_URL, headers=headers, json=payload, timeout=60)

    http_response.raise_for_status()

    result: dict = http_response.json()

    reply: str = result["choices"][0]["message"]["content"]

    return reply


# BOOKING ENFORCER
def booking_enforcer(state: dict, booking_details: dict, response: str) -> bool:
    ENFORCE_CONFIDENCE_THRESHOLD: float = 0.65

    enforce_question: dict = {"type": "noul", "instructions": f"Is the agents response currently going against any of the rules defined here\n{bE.b_enforce()}\n?"}

    enforce_q: dict = {"enforce_A": enforce_question}

    state_as_text: str = json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    details_as_text: str = json.dumps(booking_details, ensure_ascii=False)

    #the checker needs the booking details and conversation to judge the link and deposit rules
    enforce_state: str = f"BOOKING_DETAILS: {details_as_text}\nSTATE: {state_as_text}\nAGENT_RESPONSE:\n{response}"

    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}

    payload: dict = {"model": ROUTER_MODEL, "state": enforce_state, "questions": enforce_q}

    http_response: requests.Response = requests.post(DECISIONS_URL, headers=headers, json=payload, timeout=10)

    http_response.raise_for_status()

    result: dict = http_response.json()

    probability_yes: float = result["answers"]["enforce_A"]["noul"]

    if(probability_yes > ENFORCE_CONFIDENCE_THRESHOLD):
        return True
    else:
        return False


# BOOKING REGEN
def booking_regen(state: dict, booking_details: dict, response: str) -> str:
    #system prompt goes first and never changes, so it can be cached
    system_block: dict = {"type": "text", "text": bRE.b_regenerator_sys_prompt(), "cache_control": {"type": "ephemeral"}}

    system_message: dict = {"role": "system", "content": [system_block]}

    state_as_text: str = json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    details_as_text: str = json.dumps(booking_details, ensure_ascii=False)

    user_text: str = f"BOOKING_DETAILS: {details_as_text}\n STATE: {state_as_text}\n FLAGGED_RESPONSE: {response}"

    user_message: dict = {"role": "user", "content": user_text}

    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}

    provider_settings: dict = {"order": ["z-ai"], "allow_fallbacks": True}

    reasoning_settings: dict = {"effort": "medium"}

    payload: dict = {"model": GENERATOR_MODEL, "messages": [system_message, user_message], "provider": provider_settings, "reasoning": reasoning_settings, "max_tokens": 8000}

    http_response: requests.Response = requests.post(GENERATORS_URL, headers=headers, json=payload, timeout=60)

    http_response.raise_for_status()

    result: dict = http_response.json()

    reply: str = result["choices"][0]["message"]["content"]

    return reply


# CAR MODEL GENERATOR
def car_model_integrator_gen(state: dict) -> str:
    #system prompt goes first and never changes, so it can be cached
    system_block: dict = {"type": "text", "text": cmiSP.car_model_int_system_prompt(), "cache_control": {"type": "ephemeral"}}

    system_message: dict = {"role": "system", "content": [system_block]}

    state_as_text: str = json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    user_text: str = f"STATE: {state_as_text}"

    user_message: dict = {"role": "user", "content": user_text}

    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}

    provider_settings: dict = {"order": ["z-ai"], "allow_fallbacks": True}

    reasoning_settings: dict = {"effort": "low"}

    payload: dict = {"model": GENERATOR_MODEL, "messages": [system_message, user_message], "provider": provider_settings, "reasoning": reasoning_settings, "max_tokens": 4000}

    http_response: requests.Response = requests.post(GENERATORS_URL, headers=headers, json=payload, timeout=60)

    http_response.raise_for_status()

    result: dict = http_response.json()

    reply: str = result["choices"][0]["message"]["content"]

    return reply


# CLOSING STATEMENTS GENERATOR
def closing_statements_gen(state: dict) -> str:
    #system prompt goes first and never changes, so it can be cached
    system_block: dict = {"type": "text", "text": closingSP.closing_statements_system_prompt(), "cache_control": {"type": "ephemeral"}}

    system_message: dict = {"role": "system", "content": [system_block]}

    state_as_text: str = json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    user_text: str = f"STATE: {state_as_text}"

    user_message: dict = {"role": "user", "content": user_text}

    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}

    provider_settings: dict = {"order": ["z-ai"], "allow_fallbacks": True}

    reasoning_settings: dict = {"effort": "low"}

    payload: dict = {"model": GENERATOR_MODEL, "messages": [system_message, user_message], "provider": provider_settings, "reasoning": reasoning_settings, "max_tokens": 4000}

    http_response: requests.Response = requests.post(GENERATORS_URL, headers=headers, json=payload, timeout=60)

    http_response.raise_for_status()

    result: dict = http_response.json()

    reply: str = result["choices"][0]["message"]["content"]

    return reply


# CLOSING STATEMENTS ENFORCER
def closing_statements_enforcer(state: dict, response: str) -> bool:
    ENFORCE_CONFIDENCE_THRESHOLD: float = 0.65

    enforce_question: dict = {"type": "noul", "instructions": f"Is the agents response currently going against any of the rules defined here\n{closingE.closing_enforce()}\n?"}

    enforce_q: dict = {"enforce_A": enforce_question}

    state_as_text: str = json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    #the checker needs the conversation to judge if a detail or price was made up
    enforce_state: str = f"STATE: {state_as_text}\nAGENT_RESPONSE:\n{response}"

    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}

    payload: dict = {"model": ROUTER_MODEL, "state": enforce_state, "questions": enforce_q}

    http_response: requests.Response = requests.post(DECISIONS_URL, headers=headers, json=payload, timeout=10)

    http_response.raise_for_status()

    result: dict = http_response.json()

    probability_yes: float = result["answers"]["enforce_A"]["noul"]

    if(probability_yes > ENFORCE_CONFIDENCE_THRESHOLD):
        return True
    else:
        return False


# CLOSING STATEMENTS REGEN
def closing_statements_regen(state: dict, response: str) -> str:
    #system prompt goes first and never changes, so it can be cached
    system_block: dict = {"type": "text", "text": closingRE.closing_statements_regen_sys_prompt(), "cache_control": {"type": "ephemeral"}}

    system_message: dict = {"role": "system", "content": [system_block]}

    state_as_text: str = json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    user_text: str = f"STATE: {state_as_text}\n FLAGGED_RESPONSE: {response}"

    user_message: dict = {"role": "user", "content": user_text}

    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}

    provider_settings: dict = {"order": ["z-ai"], "allow_fallbacks": True}

    reasoning_settings: dict = {"effort": "medium"}

    payload: dict = {"model": GENERATOR_MODEL, "messages": [system_message, user_message], "provider": provider_settings, "reasoning": reasoning_settings, "max_tokens": 8000}

    http_response: requests.Response = requests.post(GENERATORS_URL, headers=headers, json=payload, timeout=60)

    http_response.raise_for_status()

    result: dict = http_response.json()

    reply: str = result["choices"][0]["message"]["content"]

    return reply


# PHONE CALL GENERATOR
def phone_call_gen(state: dict) -> str:
    #system prompt goes first and never changes, so it can be cached
    system_block: dict = {"type": "text", "text": phoneSP.phone_call_system_prompt(), "cache_control": {"type": "ephemeral"}}

    system_message: dict = {"role": "system", "content": [system_block]}

    state_as_text: str = json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    user_text: str = f"STATE: {state_as_text}"

    user_message: dict = {"role": "user", "content": user_text}

    headers: dict = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}

    provider_settings: dict = {"order": ["z-ai"], "allow_fallbacks": True}

    reasoning_settings: dict = {"effort": "low"}

    payload: dict = {"model": GENERATOR_MODEL, "messages": [system_message, user_message], "provider": provider_settings, "reasoning": reasoning_settings, "max_tokens": 4000}

    http_response: requests.Response = requests.post(GENERATORS_URL, headers=headers, json=payload, timeout=60)

    http_response.raise_for_status()

    result: dict = http_response.json()

    reply: str = result["choices"][0]["message"]["content"]

    return reply

