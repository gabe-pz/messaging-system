# RESTRICTED QUESTION
def restricted_instructions() -> str:
    return "A human from the shop took over this customer, so the shop only replies when `current_user_message` is clearly a service question or a booking request it can answer on its own. Which category does `current_user_message` belong to? Read `message_history` oldest to newest first, and use it to understand short replies like 'yes' or 'that one'. The human's replies are NOT in `message_history`, and an empty agent response means the shop stayed quiet while the human handled that message, so the customer may be answering the human. When the message could belong to the conversation with the human, or you are not sure, choose ignore."


# SERVICE CRITERIA
def service_and_pricing_instructions() -> str:
    return "The customer clearly asks about one of the shop's set services: window tint or tint removal, a full vinyl wrap or a factory hood only wrap, clear PPF, colored PPF, windshield PPF, ceramic coating, paint correction, caliper wraps, or a starlight headliner. That covers its price, a quote, what it includes, specs, shades, star counts, warranty, or turnaround time, asking for more details on one of these services, asking what services the shop offers, a shop post, reel, story, or ad about one of these services with a question like 'info on this', a short follow up like 'how much for that one' when the newest agent response in `message_history` was about that service, and giving their vehicle when the newest agent response in `message_history` asked for it to price a service. NOT a custom job and NOT a vague 'how much' or 'any update' that names no set service, since those are likely about the job the human is handling."


# BOOKING CRITERIA
def booking_instructions() -> str:
    return "The customer clearly wants to book one of the shop's set services. That covers saying yes in any form, like 'yes', 'yeah lets do it', or 'book me', when the newest agent response in `message_history` asked if they want to get booked or on the schedule, asking to book a set service, asking for the booking link, asking if they need an appointment or can walk in, asking to come in at a certain time for a set service the shop already priced in `message_history`, and giving their vehicle when the newest agent response in `message_history` asked for it before getting them on the books. NOT a bare 'yes', 'ok', or 'sounds good' when the newest agent response did not ask them to book, and NOT a visit for a custom job or a car already at the shop, since those belong to the human."


# IGNORE CRITERIA
def ignore_instructions() -> str:
    return "Anything the shop leaves to the human who took over. That covers a custom job that needs pictures, like a roof wrap, a partial wrap that is not the factory hood, a chrome delete, house tint, a motorcycle, boat, or RV, removing an old wrap or PPF, or their own design, a complaint about past work, a refund, financing or payment plans, a car already at the shop, the shop's social media, a phone call or a phone number, photos or videos of their car with no clear question about a set service, a reply to something the human asked, a vague 'how much' or 'any update', a bare 'yes', 'ok', or 'thanks' that is not a yes to the shop's booking question, hours, location, or anything else about the shop itself, greetings, closing statements, off topic messages, spam, and any message that mixes a service or booking question with one of these."
