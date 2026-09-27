from dotenv import load_dotenv 
from src.prompts import router_instructions as ri
import os, requests

#init jev model
load_dotenv() 
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
DECISIONS_URL: str = "https://openrouter.ai/api/alpha/decisions"
ROUTER_MODEL: str = "typesafe/jev-1.13"

#route function
def route(state: dict) -> dict:
    CONFIDENCE_THRESHOLD: int = 15

    #define the criteria for routing 
    route_criteria: dict[str, str] = {
            "service_and_pricing": ri.service_and_prices_instructions(), 
            "booking": ri.booking_instructions(), 
            "business_operations": ri.business_operations_instructions(), 
            "general_text": ri.general_text_instructions()
    }

    #define the instructions for routing and the main question 
    route_instructions: str = "Which category does the customer's current message belong to? Use the message history ONLY for context."
    route_question: dict = {"type": "choice", "instructions": route_instructions, "criteria": route_criteria}

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
