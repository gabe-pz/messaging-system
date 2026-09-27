from dotenv import load_dotenv 
from src.prompts import router_instructions_and_exs as rie
from src.prompts import s_and_p_analyzer_examples as spe
import os, requests

#init jev model
load_dotenv() 
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
DECISIONS_URL: str = "https://openrouter.ai/api/alpha/decisions"
ROUTER_MODEL: str = "typesafe/jev-1.13"

#main route function
def route(state: dict) -> str:
    CONFIDENCE_THRESHOLD: float = 0.1

    #define the criteria for routing 
    route_criteria: dict[str, str] = {
            "service_and_pricing": rie.service_and_prices_instructions(), 
            "booking": rie.booking_instructions(), 
            "business_operations": rie.business_operations_instructions(), 
            "general_text": rie.general_text_instructions()
    }

    #define the instructions for routing and the main question 
    route_instructions: str = "Which category does the customers current message belong to? Use the message history ONLY for context."
    route_question: dict = {"type": "choice", "instructions": route_instructions+"\n"+rie.route_exs(), "criteria": route_criteria}

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
    tint_question: dict = {"type": "noul", "instructions": "Is the customer asking about window tint?"+"\n"+spe.window_tint_exs()}
    ppf_question: dict = {"type": "noul", "instructions": "Is the customer asking about paint protection film?"+"\n"+spe.ppf_exs()}

    #assemble questions and setup request
    service_questions: dict = {"ppf": ppf_question, "tint": tint_question}
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

    return services


