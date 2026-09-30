#examples for router

def route_exs() -> str: 
    return r"""
    #Context
    -Filthy Wraps is a car customization shop with two locations in Texas (Cypress and Houston). It offers window tint, vinyl wraps, clear PPF, colored PPF, windshield PPF, ceramic coating with paint correction, caliper wraps, and starlight headliners.
    -Signals of a service question: a service name (tint, tinted, windshield, windows, wrap, PPF, clear bra, ceramic, coating, paint correction, caliper, starlight, stars, headliner), or price, cost, quote, estimate, rate, turnaround, how long the job takes, or specs like "1000 stars".
    -Signals of a service that needs the owner to see pictures: a roof wrap, a partial wrap that is not only the hood (doors, one side, bumpers, half the car, stripes), a chrome delete or blacking out trim, badges, or emblems, removing an old wrap or PPF, their own custom design, house tint, or a motorcycle. A factory hood only wrap and tint removal are NOT custom jobs, they are priced services.
    -Signals of an escalation that needs the owner himself: a complaint about work the shop already did, a refund, financing or payment plans, the status of a car already at the shop, or the shop's social media.
    -`current_user_message.user_text` is every text the customer sent in this batch joined into ONE message. If any part of it asks about a service, booking, hours, or location, classify that part. A bare "Yes" or "Ok" next to a real question is filler.
    -`current_user_message.user_media` counts as service content when it shows a service, for example a shop post, reel, story, or ad about tint or wraps.

    #How To Use The Context
    -Classify ONLY `current_user_message`, but ALWAYS read it in light of `message_history`, never in isolation. The same words can be a different category depending on what came before.
    -Read `message_history` oldest to newest BEFORE classifying. Use it to resolve short replies and references ("yes", "that", "it", "that one", "same one", "the same car", "yeah lets do it", a bare vehicle or number) and to see what the shop's last response asked, since the customer is usually answering it.
    -An earlier turn never sets the category on its own. A topic already handled only counts when `current_user_message` continues it.
    -`current_date_time` never changes the category. A question about hours is business_operations whether the shop is open that day or not.

    #Priority When More Than One Category Fits
    1. escalation: a complaint, a refund, financing, a car already at the shop, or the shop's social media, even when the message also says yes to booking or asks something else.
    2. services_req_humans: any service that needs the owner to see pictures, even when the message also says yes to booking or asks something else.
    3. booking: the shop's last response asked if they want to get booked or on the schedule and the customer says yes, and the message does not change the job.
    4. service_and_pricing: any service content, service media, or a change to the job.
    5. booking: every other booking signal.
    6. business_operations
    7. phone_call
    8. closing_statements
    9. owner_conversation: only when message_history is empty
    10. off_topic: only off topic or spam, never a closing statement

    #Examples (ground truth, mirror them)
    Ex 1:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"I got a rq question u can tint my front glass ?"},"message_history":{"user_message_0":{"user_media":{},"user_text":"Hey good afternoon brother , I want to tint my Q50 s 2015. How much is cost"},"agent_response_to_user_message_0":"For tint on all your side windows and rear glass, that will be 299$ in our nano ceramic tint and this is all back by a lifetime warranty"}}
        answer: service_and_pricing
        reason: asking about a service

    Ex 2:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"Hey is this filthy wraps? Trying to get a tint done. What's it cost"},"message_history":{}}
        answer: service_and_pricing
        reason: asking about a service, which outranks confirming the business name

    Ex 3:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"Alright lets do it, but instead lets do 1000 stars instead"},"message_history":{"user_message_0":{"user_media":{},"user_text":"Sheesh thats the lowest price brother?"},"agent_response_to_user_message_0":"Yeah dawg thats the lowest we can do for all that work on the Urus. You getting top tier quality across the board with the wrap, tint, and starlight. You wanna lock in a time to bring it in?"}}
        answer: service_and_pricing
        reason: says yes to booking but changes the job to 1000 stars, so it must be priced again first

    Ex 4:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"How much"},"message_history":{}}
        answer: service_and_pricing
        reason: vague but asking the cost of something

    Ex 5:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"Okay, could I go on Saturday afternoon after 2 PM?"},"message_history":{}}
        answer: owner_conversation
        reason: message_history is empty but the message follows up on a conversation the shop has no record of

    Ex 6:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"Can I book an appointment"},"message_history":{}}
        answer: service_and_pricing
        reason: vague booking request with no service named yet

    Ex 7:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"Can I get on the schedule"},"message_history":{}}
        answer: service_and_pricing
        reason: vague booking request with no service named yet

    Ex 8:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"Ya'll Have time right now?"},"message_history":{}}
        answer: business_operations
        reason: an open status question

    Ex 9:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"Could you send me over the finance application. Thanks"},"message_history":{}}
        answer: owner_conversation
        reason: reads like a conversation with the owner the shop has no record of

    Ex 10:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"Can i get an estimate"},"message_history":{}}
        answer: service_and_pricing
        reason: vague request for an estimate

    Ex 11:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"Genesis 2025 SUV"},"message_history":{"user_message_0":{"user_media":{},"user_text":"yeah"},"agent_response_to_user_message_0":"Ok before we get you on the books what is the make, model, and year of your vehicle?"}}
        answer: booking
        reason: gives the vehicle the shop asked for before getting them on the books

    Ex 12:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"If I do drop of my car on the weekend how long till it gets done ? Like let’s say I drop it off Friday would it be done by the time Monday comes or how does that work?"},"message_history":{"user_message_0":{"user_media":{},"user_text":"How many u think would look good in a Mustang would u have some insight or no And definitely interested in shooting star as well"},"agent_response_to_user_message_0":"For a Mustang most folks go somewhere in the 600 to 800 star range to really fill out that night sky look, but it's totally up to how dense you want it. Minimum we do is 500 stars and there's no max."}}
        answer: service_and_pricing
        reason: turnaround time is a service question

    Ex 13:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"Get started"},"message_history":{"user_message_0":{"user_media":{},"user_text":""},"agent_response_to_user_message_0":"Before we get you on the books we just need to know what car you are bringing in. What kind of car is it?"}}
        answer: service_and_pricing
        reason: vague get started message inside a service flow

    Ex 14:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"Thank you!"},"message_history":{"user_message_0":{"user_media":{},"user_text":"Yes I would like to book"},"agent_response_to_user_message_0":"Ok you can go ahead and book here: https://bookinglink.com"}}
        answer: closing_statements
        reason: the conversation is over, they got the booking link

    Ex 15:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{"media_element_0":{"media_description(if applicable)":"brief_description: Photo of a bright pink Porsche 911 coupe, Porsche crest visible on the hood, parked in a shop with hexagon ceiling lights. A man in a black t-shirt stands near the back wall.\nservice_ques: none visible\ntext_overlays: none","post_description(if applicable)":"Houston’s #1 rated wrap & tint shop. Filthy Wraps is proud to have 100+ 5-star rating and provide top quality work on every vehicle. We offer full vehicle customization & protection services: Vinyl Wraps, Ceramic Window Tint, Paint Protection Film (PPF), Ceramic Coating, Paint Correction. Message us today to get a quote or schedule. #filthywraps #ppf #tint #houston"}},"user_text":""},"message_history":{}}
        answer: service_and_pricing
        reason: service media from the shop with no text

    Ex 16:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"I can drop the car in the morning How long do you think it’s gonna take"},"message_history":{}}
        answer: owner_conversation
        reason: message_history is empty but it reads like a conversation with the owner the shop has no record of

    Ex 17:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"Yes thank you so much. Where you guys located?"},"message_history":{"user_message_0":{"user_media":{},"user_text":"How much will be cost to do it polished from the rocks and ceramic coating?"},"agent_response_to_user_message_0":"Hello! For your Mercedes E 400, our paint correction/ceramic coating package includes\n- decontamination wash\n- clay bar\n- paint correction\n- 7 year ceramic coating\nThat would be 499$ for your car. This will help clean up the paint, bring the shine back, make it easier to maintain, and leave it with that showroom look.\n\nWould you like to get on the schedule for this?"}}
        answer: booking
        reason: yes to the booking question outranks the location question

    Ex 18:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"Yes Im intrested"},"message_history":{"user_message_0":{"user_media":{},"user_text":"Hello, can I get more info on window tints?"},"agent_response_to_user_message_0":"Hello! Our nano ceramic window tint is applied on all your side windows and rear windshield. It blocks 99% UV and 91% heat, and comes with a lifetime warranty.\n\nThe special is 299$ for all side and rear windows.\n\nWould you like to schedule an appointment?"}}
        answer: booking
        reason: yes to the booking question

    Ex 19:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"2015 infiniti q50"},"message_history":{"user_message_0":{"user_media":{},"user_text":"hey, i’m finally ready to come in for the tints can i get a final quote including windshield tint?"},"agent_response_to_user_message_0":"Hey, for sure. The side and rear windows with nano ceramic tint is 299$ and that comes with a lifetime warranty.\nThe front windshield price depends on the vehicle, so I just need the year, make, and model to get you the final total with windshield included?"}}
        answer: service_and_pricing
        reason: gives the vehicle the shop asked for to price a service

    Ex 20:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"Where are yall located at in texas"},"message_history":{}}
        answer: business_operations
        reason: only asking where the shop is

    Ex 21:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{"media_element_0":{"media_description(if applicable)":"brief_description: Photo inside a shop of a man applying dark film to the rear side window of a white sedan with a heat gun. Make and model not identifiable.\nservice_ques: window tint\ntext_overlays: Block heat. Drive cooler. | Limited 299$ special nano ceramic tint","post_description(if applicable)":"Block the heat. Drive cooler. Limited time 299$ nano ceramic tint special, high heat rejection, interior protection, and a cleaner look all around. Houston, TX. Message us to book your spot before it’s gone #filthywraps #tint #houston #ppf #wrap"}},"user_text":"where are yall located at?"},"message_history":{}}
        answer: service_and_pricing
        reason: service media from the shop outranks the location question

    Ex 22:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"Yes do you have a waiting area or would it need to be dropped off"},"message_history":{"user_message_0":{"user_media":{},"user_text":"Where are you guys located and what does the warranty cover"},"agent_response_to_user_message_0":"We’re located at 12015 Woodworth Dr, Cypress, TX 77429 and 6003 N Shepherd Dr, Houston, TX 77091.\n\nThe lifetime warranty covers bubbling, creasing, pulling, discoloration, essentially any failing of the tint application due to the installer.\n\nDid you want me to get you set up for an appointment?"}}
        answer: booking
        reason: yes to the booking question outranks everything else

    Ex 23:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"sounds great thanks!"},"message_history":{"user_message_0":{"user_media":{},"user_text":"Yes do you have a waiting area or would it need to be dropped off"},"agent_response_to_user_message_0":"You could do either, we have both a waiting area as well as the option to just drop it off and come back when its done. The turnaround is around 2 hours.\n\nYou can go ahead and book a time that works for you here:\nhttps://filthy-booking-website.vercel.app/"}}
        answer: closing_statements
        reason: a closing message with no request

    Ex 24:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"Sound good man I’m down to book with yall some time this week!"},"message_history":{"user_message_0":{"user_media":{},"user_text":"Tell me about the tint I get it it’s nano ceramic but is it good it won’t start pealing off within months?! Etc"},"agent_response_to_user_message_0":"Yeah so we use the STEK smart series, which STEK itself is a high qualtiy brand of tint, and cominbed with the smart series that is designed to keep your window tint looking good for years to come, there is no need to worry about pealing or anything like that. In the 0.01% chance that does happen we do offer a lifetime warranty so you can bring it by shop and we have you covered"}}
        answer: booking
        reason: wants to book this week, a specific time

    Ex 25:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"Nahh its okay man, I may have my buddy take care of that for me but I appreciate it for sure and I’ll look into making an appointment very soon Thanks for the help and quick response time"},"message_history":{"user_message_0":{"user_media":{},"user_text":"Any chance yall could throw on a new “H” for my honda? Its been off for a while now"},"agent_response_to_user_message_0":"Yessir purple would definitely go crazy on that Accord once the body stuff is cleaned up first.\nFor the full purple vinyl wrap it would still be 3000$, includes the free ceramic coating, and it’s backed by our 5 year warranty.\nOn the Honda “H” emblem, I’m not 100% sure if we can supply and install that or if you’d need to bring the emblem in. Let me double check on that real quick and ill get right back to you."}}
        answer: closing_statements
        reason: will book at a vague time, no specific timing, and a thank you

    Ex 26:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"Is there a number I can call? Easier to just talk it through"},"message_history":{}}
        answer: phone_call
        reason: asking for a number to talk on a phone call

    Ex 27:
        state: {"current_date_time":"Monday, June 08, 2026 at 02:30 PM","current_user_message":{"user_media":{},"user_text":"Yes Where are you located?"},"message_history":{}}
        answer: business_operations
        reason: the bare "Yes" is filler, the real question is the shop location

    Ex 28:
        state: {"current_date_time":"Monday, June 01, 2026 at 02:10 PM","current_user_message":{"user_media":{},"user_text":"2021 dodge charger scat pack Do I need an appointment or can I just walk in?"},"message_history":{"user_message_0":{"user_media":{},"user_text":"Are they all legal options where a cop can’t give me a ticket after testing my tint?"},"agent_response_to_user_message_0":"Good question. The short answer is yes, as long as we pick the right shade. Everything we install is street legal here in Texas, the front two windows just have to be a shade that lets in more light, and the back side windows plus rear glass can go as dark as you want, even limo.\n\nAll three tiers we carry come in the full range of shades, so whether you go with the 299$ nano ceramic, the 450$ nano ceramic plus, or the 600$ NEX+ series ceramic, we just match a legal shade on the front and you can run limo dark on the back if you want that look.\n\nTo get you that quote you asked about, whats the year, make, and model of your car?"}}
        answer: booking
        reason: asking about an appointment means they want to book

    Ex 29:
        state: {"current_date_time":"Monday, June 01, 2026 at 02:10 PM","current_user_message":{"user_media":{},"user_text":"any available spots today? at the shepherd location"},"message_history":{"user_message_0":{"user_media":{},"user_text":"when are you available? and where at?"},"agent_response_to_user_message_0":"We're open Monday through Saturday from 10AM to 5PM, closed Sundays.\n\nWe've got two locations for you:\n12015 Woodworth Dr, Cypress, TX 77429\n6003 N Shepherd Dr, Houston, TX 77091"}}
        answer: booking
        reason: asking for an available spot is booking

    Ex 30:
        state: {"current_date_time":"Friday, September 04, 2026 at 06:10 PM","current_user_message":{"user_media":{},"user_text":"Yes Do you do a veteran discount?"},"message_history":{"user_message_0":{"user_media":{},"user_text":"2026 F-150 Lariat"},"agent_response_to_user_message_0":"Appreciate it! For your 2026 F-150 Lariat, the full job in the NEX+ series ceramic, all side windows, rear glass, and the front windshield, runs 900$. That film is machine cut for a perfect fit with no scratches, gives you our highest heat rejection, and comes with a lifetime warranty.\n\nWant me to get you on the books for that?"}}
        answer: booking
        reason: yes to the booking question, and the discount question does not change the job

    Ex 31:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"How much to wrap just the roof gloss black on my camry"},"message_history":{}}
        answer: services_req_humans
        reason: a roof wrap is a custom job that needs a human

    Ex 32:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"Can yall do a chrome delete on a 2022 tahoe? window trim and the grille"},"message_history":{}}
        answer: services_req_humans
        reason: a chrome delete is a custom job that needs a human

    Ex 33:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"what would it cost to wrap only the front and rear bumpers matte black"},"message_history":{}}
        answer: services_req_humans
        reason: a partial wrap that is not the hood is a custom job that needs a human

    Ex 34:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"How much to wrap just the hood black"},"message_history":{}}
        answer: service_and_pricing
        reason: a hood only wrap is a priced service, not a custom job

    Ex 35:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"How much do yall charge to take off old tint on all my windows"},"message_history":{}}
        answer: service_and_pricing
        reason: tint removal is a priced service, not a custom job

    Ex 36:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"I got an old faded wrap on my mustang, can yall take it off?"},"message_history":{}}
        answer: services_req_humans
        reason: removing an old wrap depends on the car and the wrap, so it needs a human

    Ex 37:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"Yes, also could yall black out the badges and the window chrome while its in?"},"message_history":{"user_message_0":{"user_media":{},"user_text":"2021 Accord sport"},"agent_response_to_user_message_0":"For your 2021 Accord Sport, a full vinyl wrap runs 3000$, and that comes with a free ceramic coating and our 5 year warranty.\n\nWant to get on the schedule for this?"}}
        answer: services_req_humans
        reason: says yes to booking but adds a chrome delete, and a custom job that needs a human outranks booking

    Ex 38:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"Want to do the doors and the roof satin black on my charger, and the rest stays white"},"message_history":{}}
        answer: services_req_humans
        reason: a roof and door wrap is a partial wrap that is not the hood

    Ex 39:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"Let me think about it and ill get back to you"},"message_history":{"user_message_0":{"user_media":{},"user_text":"How much for tint on my 2020 camry"},"agent_response_to_user_message_0":"For your Camry we tint all the side windows and the rear windshield with our nano ceramic film, that blocks 99% of UV and 91% of heat. Price is 299$ and that comes with a lifetime warranty.\n\nWant to get on the schedule for that ?"}}
        answer: closing_statements
        reason: hesitation with no service question and no request

    Ex 40:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"Not sure yet, its for my brother in law let me see what he says."},"message_history":{"user_message_0":{"user_media":{},"user_text":"how much for front windshield tint on a model y"},"agent_response_to_user_message_0":"For the front windshield on a Model Y that runs 200$ in our nano ceramic film, and that comes with a lifetime warranty.\n\nWant to get on the schedule for this?"}}
        answer: closing_statements
        reason: on the fence, waiting on someone else

    Ex 41:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"can you just give me a call? 832-555-0142"},"message_history":{"user_message_0":{"user_media":{},"user_text":"how much for a full wrap on my tahoe"},"agent_response_to_user_message_0":"For your Tahoe a full vinyl wrap runs 4500$, and that comes with a free ceramic coating and our 5 year warranty.\n\nWant to get on the schedule for that?"}}
        answer: phone_call
        reason: asks the shop to call and shares a number

    Ex 42:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"whats the best number to call yall at"},"message_history":{}}
        answer: phone_call
        reason: asking for the shop's phone number

    Ex 43:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"Hi, I help businesses get more Google reviews and rank higher on maps, interested in a free audit?"},"message_history":{}}
        answer: off_topic
        reason: a sales pitch that has nothing to do with the shop's services

    Ex 44:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"who yall got winning the super bowl this year"},"message_history":{}}
        answer: off_topic
        reason: off topic, not about the shop or a car

    Ex 45:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"ok sounds good"},"message_history":{"user_message_0":{"user_media":{},"user_text":"do yall have a waiting area"},"agent_response_to_user_message_0":"Yeah we have a waiting area, or you can drop it off and come back when its done."}}
        answer: closing_statements
        reason: a closing statement is closing_statements, never off_topic

    Ex 46:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"Yes How much for tint on a 2020 camry"},"message_history":{}}
        answer: service_and_pricing
        reason: the bare "Yes" is filler and the real question is about a service, so never owner_conversation

    Ex 47:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"ill book once my car gets here next week"},"message_history":{"user_message_0":{"user_media":{},"user_text":"how much for tint on a 2024 civic"},"agent_response_to_user_message_0":"For your Civic we tint all the side windows and the rear windshield with our nano ceramic film for 299$, and that comes with a lifetime warranty.\n\nWant to get on the schedule for that ?"}}
        answer: booking
        reason: wants to book at a specific timing, when the car arrives next week

    Ex 48:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"whats yall tiktok"},"message_history":{}}
        answer: escalation
        reason: the shop's social media is not in the shop's info, so only the owner can answer it

    Ex 49:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"yall did my wrap last month and the corners are already lifting"},"message_history":{}}
        answer: escalation
        reason: a complaint about work the shop already did needs the owner himself

    Ex 50:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"can yall tint the windows on my house, its a 2 story"},"message_history":{}}
        answer: services_req_humans
        reason: house tint is priced by the owner from pictures

    Ex 51:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"how much for ppf on my motorcycle gas tank"},"message_history":{}}
        answer: services_req_humans
        reason: the shop has no set price for a motorcycle

    Ex 52:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"how much to wrap my aftermarket vented hood"},"message_history":{}}
        answer: services_req_humans
        reason: a hood that is not the factory hood is a custom job

    Ex 53:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"nah just the headlights and mirrors"},"message_history":{"user_message_0":{"user_media":{},"user_text":"how much for ppf on my 2023 tacoma"},"agent_response_to_user_message_0":"For your Tacoma the full frontal package runs 2200$, and that includes a free ceramic coating on the PPF areas and is backed by our 10 year warranty.\n\nWant to get on the schedule for this?"}}
        answer: services_req_humans
        reason: turned down the full package the shop offered for only certain panels

    Ex 54:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"do yall do payment plans on wraps"},"message_history":{}}
        answer: escalation
        reason: financing and payment plans need the owner himself

    Ex 55:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 03:40 PM","current_user_message":{"user_media":{},"user_text":"is my truck done yet? dropped it off this morning"},"message_history":{"user_message_0":{"user_media":{},"user_text":"yes lets do it"},"agent_response_to_user_message_0":"Bet, you can grab a spot here https://filthy-booking-website.vercel.app"}}
        answer: escalation
        reason: the status of a car already at the shop needs the owner himself

    Ex 56:
        state: {"current_date_time":"Tuesday, September 08, 2026 at 11:15 AM","current_user_message":{"user_media":{},"user_text":"I want my money back, the ppf yall put on is already turning yellow"},"message_history":{}}
        answer: escalation
        reason: a refund needs the owner himself
"""
