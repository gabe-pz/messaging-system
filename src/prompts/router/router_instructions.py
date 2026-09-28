#instructions for the router as well as examples 

def service_and_prices_instructions() -> str: 
    return """
    The customer is asking about information on a serive or pricing for a service 
    """

def booking_instructions() -> str:
    return """
    The customer is asking to book a service, get on the schedule, or expressing general concern to go into the shop for some service
    """

def business_operations_instructions() -> str:
    return """
    The customer is asking about the operations of the business
    """

def general_text_instructions() -> str:
    return """
    The customer is asking about non of the other instructions listed and is not spam or asking about anything harmful
    """
