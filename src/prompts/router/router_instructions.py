#instructions for the router as well as examples 

def service_and_prices_instructions() -> str: 
    return """
    The customer is asking about a service or its price. That covers:
    - any service the shop offers (window tint, vinyl wrap, clear PPF, colored PPF, windshield PPF, ceramic coating, paint correction, caliper wraps, starlight headliner), including its price, a quote, an estimate, specs, coverage, shades, star counts, warranty, turnaround time, or how long the job takes
    - any vague request for a price or a start, like "how much", "can I get an estimate", "get started", or a booking request that names no service yet, like "can I book an appointment" or "can I get on the schedule"
    - media from the shop about a service, like "how much is this" or "info on this" with a post, reel, story, or ad attached, even if the text also asks where the shop is
    - the customer giving their vehicle because the shop's last response in `message_history` asked for it to price a service
    - a short follow up that only makes sense with `message_history`, like "what about the windshield", "how much for that one", or "same for my other car", when the shop was just discussing a service
    - the customer changing the job (a different service, quantity, or vehicle), even while saying yes to booking
    - a hood only wrap or tint removal, those are priced services
    - NOT a roof wrap, a partial wrap that is not the hood, a chrome delete, house tint, a motorcycle, or any other custom job, those are services_req_humans
    - NOT a complaint about past work, a refund, financing, or a car already at the shop, those are escalation
    """

def booking_instructions() -> str:
    return """
    The customer wants to book. That covers:
    - the shop's last response in `message_history` asked if they want to get booked or on the schedule, and the customer answers yes in any form ("yes", "yeah lets do it", "ok book me", "sure"). This wins even when the same message also asks a side question that does not change the job, like a discount, a waiting area, or where the shop is
    - the customer says they want to book at a specific time, like "this week", "Friday", or "any spots today at the shepherd location"
    - the customer asks if they need an appointment or can walk in
    - the customer gives their vehicle because the shop's last response in `message_history` said it needs it before getting them on the books
    - the customer gives booking details the shop asked for
    """

def business_operations_instructions() -> str:
    return """
    The customer is asking about the shop itself, not a service. That covers hours, open or closed status ("yall open today", "yall have time right now"), where the shop is located or its address, email, website, who owns the shop, who they are talking to, how long the shop has been in business, how many employees it has, whether it is licensed or registered, and which payment methods it accepts. NOT the phone number or a phone call, that is phone_call. NOT financing, payment plans, or the shop's social media, those are escalation.
    Only when the message has no service question, no service media from the shop, and no yes to a booking question.
    """

def services_req_humans_instructions() -> str:
    return """
    The customer is asking about a service the owner can only price after seeing pictures. That covers:
    - a roof wrap, including the roof with the pillars or mirrors
    - a partial wrap that is NOT only the hood, like the doors, one side, the bumpers, half the car, or stripes
    - a chrome delete, blacking out chrome trim, window trim, badges, or emblems
    - any other custom service that is not one of the shop's set services and depends on the car or the job, like removing an old wrap or PPF, a hood that is not the factory hood, or their own custom design or graphics
    - PPF or a wrap on only certain panels, after they turn down the full package the shop already offered
    - window tint for a house, office, or any building
    - a vehicle the shop has no set price for, like a motorcycle, boat, or RV
    NOT a factory hood only wrap and NOT tint removal, those are service_and_pricing. NOT a complaint, refund, financing, social media, or a car already at the shop, those are escalation.
    """

def escalation_instructions() -> str:
    return """
    The customer needs the owner himself for something that is not a new service. That covers:
    - a problem or complaint about work the shop already did, like tint bubbling or a wrap peeling
    - asking for a refund
    - financing or payment plans
    - the status of a car that is already at the shop, like "is my car ready yet"
    - the shop's social media, like its instagram or tiktok, since only the owner has it
    """

def owner_conversation_instructions() -> str:
    return """
    The customer seems to be continuing a conversation the shop has no record of, like one they had with the owner by phone or in person. That covers:
    - ONLY when `message_history` is empty
    - AND the message is not clearly service_and_pricing, booking, business_operations, escalation, services_req_humans, closing_statements, or phone_call
    - AND the message reads like a follow up to a missing earlier conversation or an informal inbound, like "could I go on Saturday afternoon after 2" or "could you send me over the finance application"
    - `current_user_message.user_text` can hold several texts joined into ONE message: if ANY part clearly asks about a service, booking, hours, or location, classify THAT and never owner_conversation. A bare "Yes" or "Ok" next to a real question is filler, not a follow up to a missing conversation
    """

def closing_statements_instructions() -> str:
    return """
    The customer is on the fence, or is just ending the conversation. That covers:
    - hesitation or uncertainty, like "let me think about it", "not sure yet", or "its for my brother in law, let me see what he says"
    - a closing statement with no request, like "thanks will do", "ok sounds good", "sounds great thanks", or "alright lets do it" when the shop's last response in `message_history` did NOT ask them to book
    - saying they want to book at some vague time in the future with no specific timing, like "ill look into making an appointment soon". A specific timing, like "this week", "a week from now", or "when my car arrives", is booking
    - it MUST have NO service content and NO actionable request, and it is a STATEMENT, not a question
    - a closing statement is always closing_statements, NEVER off_topic
    """

def phone_call_instructions() -> str:
    return """
    The customer wants to talk on the phone. That covers:
    - asking the shop to call them, or asking to talk it through on a call
    - sharing their phone number
    - asking for the shop's phone or contact number
    """

def off_topic_instructions() -> str:
    return """
    The message is off topic or spam and has nothing to do with the shop. That covers:
    - requests that are not about the shop or a car, like sports, weather, or random questions
    - spam, sales pitches, promotions, giveaways, or links sent to the shop
    - ONLY off topic or spam. A closing statement ("thanks", "ok sounds good") is NEVER off_topic, it is closing_statements
    """
