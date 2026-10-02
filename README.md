# Messaging System 
The goal of this project was to create a messaging system that could receive messages on behalf of a business, process them in an intelligent manner, and submit a reply that is grounded in the business's details. In particular the system was designed to handle potential customers that message the business first incoming from an advertisement on a meta platform, a website quote request form, or directly to the businesses meta accounts. 

A variation of this system was built and deployed into production for the business Filthy Wraps LLC and in a span of 3 months has booked 830 service based jobs to the businesses calendar. During this time the output tokens per month was around 8M with an average cost per month of $17. 

## Core overview
The system uses two main major types of Natural Language Processing models for answering a message, of which serve two distinct purposes in the system, which are 
1. Multi-Modal Large Language Models for generating a response given some details 
2. System one models for analyzing a users message to determine information about an incoming message

These two types of NLP models are then used in a programmatic manor in order to properly answer a message. They both take in a defined state, and processes it based on some rules given. An overview of a state is given below.  

### State Formulation
Firstly, a customer message is defined as the total text and media sent to the servers from the customer, in some allocated amount of time. Then a state is simply the customer message, plus message history(customer messages and system response) and the current time. 

- A customer message is formed from a complete batch of information sent by a user to one of the servers, that is text and media. The code constructs this batch by capturing new POST requests from a user as they reach the server, restarting a counter each time, such that when the counter completes, the batch is considered completed. This message batch is then sent into a customer message formulation function that extracts all the information from it, process any media present, and assembles it into a defined form. 

- The code will assemble the message history that will be used for context, by reading previous customer messages and system responses. 

- And the time is simple formed from datetime and zoneinfo modules  

### Mams  
After the state is formed at the beginning of the core function, it will then be passed into the mams function, where it returns a string that is the systems response. 

The mams function processes a message by first determining what particular category of operations the message pertains to, then based upon that, will send the message to a set of NLP models that are meant to processes messages for that exact category, and finally a message will be returned. 

For example, in this code the categories used were

 - service and pricing 
 - business operations
 - booking
 - services requiring humans 
 - escalations
 -  closing statements 
 - other

And in the most general case, the set of NLP models consist of, 
- System one analyzer model to further break down exactly what sub-categories the message pertains to. This model will output a list of details about the sub-categories that the message pertains to
- Multi-modal large language model to generate a response given the list of details and the current state, where this model will output a string that is a response
- System one analyzer model to check the response against hard rules given by the shop and tuned by me. The type of question asked in this case is a noul
- If the previous output of the system one model is above some confidence threshold then it will trigger a 2nd call to a multi-modal large language model that will take in the details, state, and flagged response, and regenerate a response based on some rules and output a string that is the response


Some categories do not require this entire set of NLP models to process the message due to their simplicity. Also a few categories will put the user into some particular state, and thus a few checks happen at the top of mams for these states as well as even in core before mams is processed. 

The name mams for the function was picked due to historical reasons, and thus there is no real meaning of it in relation to this codebase.
