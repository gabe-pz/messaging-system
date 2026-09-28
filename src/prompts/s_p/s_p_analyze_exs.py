# WINDOW TINT
def window_tint_exs() -> str:
    return r"""Yes: film on the vehicle's glass. Side windows, rear glass, front windshield, windshield brow, sunroof, shade or percentage, heat or UV rejection, price, removal, warranty, or booking a tint. "ceramic" with no mention of coating or paint means ceramic window tint.
No: ceramic COATING or paint correction, PPF on the windshield, any other service, or a message that names no service ("can I book an appointment", "how much for my 2007 Tahoe").
Read `message_history` only to resolve a short follow up ("how much for front", "yeah lets do it") to the service already being discussed. Media in `current_user_message.user_media` counts when the customer's text points at it ("info on this"). `current_date_time` never changes the answer.
Examples:
state: {"current_user_message":{"user_media":{},"user_text":"how dark can you go?"},"message_history":{"user_message_0":{"user_media":{},"user_text":"do you guys do windows?"},"agent_response_to_user_message_0":"We do! We install ceramic window tint on all vehicles."}}
answer: True
state: {"current_user_message":{"user_media":{},"user_text":"do you do ceramic coating?"},"message_history":{}}
answer: False
state: {"current_user_message":{"user_media":{},"user_text":"wow nice tint, what it heat reject"},"message_history":{}}
answer: True
state: {"current_user_message":{"user_media":{},"user_text":"Hey what’s up I’m interested in the ceramic for a 2024 Toyota Camry how much would that look like"},"message_history":{}}
answer: True
state: {"current_user_message":{"user_media":{},"user_text":"How much to ceramic the whole suv.plus tint"},"message_history":{}}
answer: True
state: {"current_user_message":{"user_media":{},"user_text":"how much for front"},"message_history":{"user_message_0":{"user_media":{"media_element_0":{"media_description(if applicable)":"brief_description: A technician applying dark tint film to a car window.\nservice_ques: Nano ceramic window tint special.\ntext_overlays: Limited 299$ special nano ceramic tint","post_description(if applicable)":"Limited time 299$ nano ceramic tint special #filthywraps #tint"}},"user_text":"let me also grab some info on this"},"agent_response_to_user_message_0":"That special is our nano ceramic tint, we tint all the side windows and rear windshield with a high heat rejection film for 299$, and it comes with a lifetime warranty.\nWant to get on the schedule for that?"}}
answer: True
state: {"current_user_message":{"user_media":{},"user_text":"Can you throw in a bra on the front windshield?"},"message_history":{"user_message_0":{"user_media":{},"user_text":"Toyota Camry 26"},"agent_response_to_user_message_0":"Perfect, the tint on your Camry will be 299$ for all sides and the rear. You can check out what we have open and grab a spot here https://filthy-booking-website.vercel.app"}}
answer: True
state: {"current_user_message":{"user_media":{},"user_text":"Can you put PPF on my windshield?"},"message_history":{}}
answer: False
state: {"current_user_message":{"user_media":{},"user_text":"Can I book an appointment"},"message_history":{}}
answer: False
state: {"current_user_message":{"user_media":{},"user_text":"How much for a 2007 Chevy Tahoe just a estimate"},"message_history":{}}
answer: False
state: {"current_user_message":{"user_media":{"media_element_0":{"media_description(if applicable)":"brief_description: Promotional ad for the shop, a technician applying dark window tint film to a white car.\nservice_ques: Ceramic window tint, a limited 299$ nano ceramic tint special.\ntext_overlays: Block heat. Drive cooler. Limited 299$ special nano ceramic tint","post_description(if applicable)":"Block the heat. Drive cooler. Limited time 299$ nano ceramic tint special #filthywraps #tint"}},"user_text":"Can I get more info on this?"},"message_history":{}}
answer: True"""


# CLEAR PPF
def ppf_exs() -> str:
    return r"""Yes: clear PPF on the painted body. Any "PPF" or "paint protection film" with no color or windshield qualifier, "clear bra", "clear ppf", full body, full front, frontal, hood, or bumper protection, or a follow up about a PPF quote. The word "front" does NOT mean the windshield.
No: colored or color change PPF, PPF or film on the windshield glass, window tint (a "bra" or "brow" on the front windshield during a tint conversation is tint), any other service, or a message that names no service.
Read `message_history` only to resolve a short follow up ("I got a cheaper quote", "yeah lets do it") to the service already being discussed. Media in `current_user_message.user_media` counts when the customer's text points at it ("info on this"). `current_date_time` never changes the answer.
Examples:
state: {"current_user_message":{"user_media":{"media_element_0":{"media_description(if applicable)":"","post_description(if applicable)":"Houston’s Trusted PPF Shop 🛡️\n\n150+ ⭐️ 5-Star Reviews and counting!\n\nProtect your paint from rock chips, scratches & everyday damage with premium Paint Protection Film (PPF).\n\n📍 Serving Houston & Cypress\n• PPF | Ceramic Window Tint | Vinyl Wraps\n• Message us today for your FREE quote!\n\nProtect it. Preserve it. Filthy Wraps.\n#filthywraps #ppf #tint #houston #wrap"}},"user_text":"Can I get some info? "},"message_history":{}}
answer: True
state: {"current_user_message":{"user_media":{},"user_text":"How much is PPF for my car?"},"message_history":{}}
answer: True
state: {"current_user_message":{"user_media":{},"user_text":"I want paint protection film on the front of my car"},"message_history":{}}
answer: True
state: {"current_user_message":{"user_media":{},"user_text":"I got a cheaper quote for 1500$"},"message_history":{"user_message_0":{"user_media":{},"user_text":"I have a 2020 corvette c8 I’m looking for frontal ppf"},"agent_response_to_user_message_0":"For your C8 the full frontal package will include the front bumper, full hood, full fenders, headlights, mirrors, door guards, and door cups. The price would be 1800$ which includes a free ceramic coating applied to the areas where the ppf was applied and is backed by our 10 year warranty.\nWant to get on the schedule for this?"}}
answer: True
state: {"current_user_message":{"user_media":{},"user_text":"Do yall install colored PPF?"},"message_history":{}}
answer: False
state: {"current_user_message":{"user_media":{},"user_text":"Can you put PPF on my windshield?"},"message_history":{}}
answer: False
state: {"current_user_message":{"user_media":{},"user_text":"Can you throw in a bra on the front windshield?"},"message_history":{"user_message_0":{"user_media":{},"user_text":"Toyota Camry 26"},"agent_response_to_user_message_0":"Perfect, the tint on your Camry will be 299$ for all sides and the rear. You can check out what we have open and grab a spot here https://filthy-booking-website.vercel.app"}}
answer: False
state: {"current_user_message":{"user_media":{},"user_text":"Sounds good, can you also tint the windows?"},"message_history":{"user_message_0":{"user_media":{},"user_text":"How much for clear PPF on my Model 3?"},"agent_response_to_user_message_0":"For your Model 3 the full frontal package is 1500$, and that comes with a free ceramic coating on those areas and our 10 year warranty.\n\nWant to get on the schedule for this?"}}
answer: False"""
