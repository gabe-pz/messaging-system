
#instructions for the router
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

#examples for router
def route_exs() -> str: 
    return """
    # EXAMPLES:
    Ex 1: 
        state: {'current_user_message': {'user_media': {'media_element_0': {'media_description(if applicable)': '', 'post_description(if applicable)': 'Houston’s Trusted PPF Shop 🛡️\n\n150+ ⭐️ 5-Star Reviews and counting!\n\nProtect your paint
        from rock chips, scratches & everyday damage with premium Paint Protection Film (PPF).\n\n📍 Serving Houston & Cypress\n• PPF | Ceramic Window Tint | Vinyl Wraps\n• Message us today for your FREE quote!\n\nProtect it. Preserve 
        it. Filthy Wraps.\n#filthywraps #ppf #tint #houston #wrap'}}, 'user_text': 'Can I get some info? '}, 'message_history': {}}
        answer: service_and_pricing
"""
