# Few shot examples for the business operations generator

# EXAMPLES
def business_operations_generator_examples() -> str:
    return """
    #Examples
    Ex 1:
    Current date and time: Monday, June 8, 2026 at 02:30 PM
    Conversation so far:
    Current message: "hey are you guys open saturday"
    Details: [{"Hours Of Operation":{"Mon, Tue, Wed, Thu, Fri":"PLACEHOLDER 9AM - 5PM","Sat":"PLACEHOLDER 10AM - 2PM","Sun":"PLACEHOLDER CLOSED"}}]
    Answer: <reply>Yeah we are, saturdays we run PLACEHOLDER 10AM - 2PM</reply>
    REASON: They asked about one day only, so only that day is answered

    Ex 2:
    Current date and time: Monday, June 8, 2026 at 02:30 PM
    Conversation so far:
    customer: whats the address
    agent: We are at PLACEHOLDER STREET, PLACEHOLDER CITY
    Current message: "and do you take card"
    Details: [{"Payments Accepted":"PLACEHOLDER payment methods"}]
    Answer: <reply>We take PLACEHOLDER payment methods</reply>
    REASON: The address was already given, so the reply only covers the new question

    Ex 3:
    Current date and time: Monday, June 8, 2026 at 02:30 PM
    Conversation so far:
    Current message: "do you guys deliver out of state"
    Details: []
    Answer: <reply>Let me double check on that and get right back to you</reply>
    REASON: Nothing in the details answers it, so the reply never invents one

"""
