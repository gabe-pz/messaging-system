#instructions for the router as well as examples 

def service_and_prices_instructions() -> str: 
    return """
    The customer is asking about a service or its price. That covers:
    - any service the shop offers (window tint, vinyl wrap, clear PPF, colored PPF, windshield PPF, ceramic coating, paint correction, caliper wraps, starlight headliner), including its price, a quote, an estimate, specs, coverage, shades, star counts, warranty, turnaround time, or how long the job takes
    - any vague request for a price or a start, like "how much", "can I get an estimate", "get started", or a booking request that names no service yet, like "can I book an appointment" or "can I get on the schedule"
    - media from the shop about a service, like "how much is this" or "info on this" with a post, reel, story, or ad attached, even if the text also asks where the shop is
    - the customer giving their vehicle because the shop's last response asked for it to price a service
    - the customer changing the job (a different service, quantity, or vehicle), even while saying yes to booking
    """

def booking_instructions() -> str:
    return """
    The customer wants to book. That covers:
    - the shop's last response in `message_history` asked if they want to get booked or on the schedule, and the customer answers yes in any form ("yes", "yeah lets do it", "ok book me", "sure"). This wins even when the same message also asks a side question that does not change the job, like a discount, a waiting area, or where the shop is
    - the customer says they want to book at a specific time, like "this week", "Friday", or "any spots today at the shepherd location"
    - the customer asks if they need an appointment or can walk in
    - the customer gives their vehicle because the shop's last response said it needs it before getting them on the books
    - the customer gives booking details the shop asked for
    """

def business_operations_instructions() -> str:
    return """
    The customer is asking about the shop itself, not a service. That covers hours, open or closed status ("yall open today", "yall have time right now"), where the shop is located or its address, the phone number, email, website, who owns the shop, who they are talking to, how long the shop has been in business, how many employees it has, whether it is licensed or registered, and which payment methods it accepts.
    Only when the message has no service question, no service media from the shop, and no yes to a booking question.
    """

def general_text_instructions() -> str:
    return """
    None of the other categories fit. That covers:
    - a closing or thank you message with no request, like "thanks", "sounds great thanks", "ok sounds good", or "I'll think about it"
    - hesitation, or saying they will book at some vague time with no specific timing, and no service question
    - asking to talk on a phone call
    - a message that seems to continue a conversation the shop has no record of: `message_history` is empty but the message reads like a follow up, like "could I go on Saturday afternoon after 2" or "could you send me over the finance application"
    - off topic messages or spam
    """
