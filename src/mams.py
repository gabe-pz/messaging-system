from src import rage_functions as rf
from helpers import log as lg
from helpers import senders as send
from dotenv import load_dotenv
import os

#HIL 
load_dotenv() 
HIL_RECIPENT: str = os.getenv("HIL_RECIPENT")

#S_P BRANCH
def service_and_pricing_branch(state: dict) -> str:
    s_and_p_result: list = rf.service_and_pricing_analyzer(state) 

    s_and_p_reply: str = rf.service_and_pricing_generator(state, s_and_p_result)

    try:
        s_and_p_enforce: bool = rf.service_and_pricing_enforcer(state, s_and_p_reply)

        if(s_and_p_enforce):
            s_and_p_reply = rf.service_and_pricing_regen(state, s_and_p_result, s_and_p_reply)
            return s_and_p_reply
        else: 
            return s_and_p_reply

    except Exception as error:
        print("S_P CHECK ERROR: " + str(error))

        return s_and_p_reply


#MAMS
def mams(state: dict, id: str) -> str: 

    #customer is answering the picture request, so acknowledge it and hand them to a human
    if(lg.has_id(lg.HIL_QUEUE_KEY, id)):
        ack_reply: str = rf.acknowledge_service_gen(state)

        send.send_blooio_message(HIL_RECIPENT, "HIL TRIGERED, due to HUMAN NEEDED FOR SERVICE")

        lg.add_id(lg.RESTRICTED_KEY, id)

        lg.remove_id(lg.HIL_QUEUE_KEY, id)

        return ack_reply

    #ROUTE
    route_result: str = rf.route(state)

    #s_p branch
    if(route_result == "service_and_pricing"):
        return service_and_pricing_branch(state)

    #business_ops branch 
    elif(route_result == "business_operations"):
        business_ops_result: list = rf.business_operations_analyzer(state) 

        business_ops_reply: str = rf.business_operations_generator(state, business_ops_result) 

        #a failed check or regen still sends the first reply
        try:
            business_ops_enforce: bool = rf.business_operations_enforcer(state, business_ops_reply)

            if(business_ops_enforce):
                business_ops_reply = rf.business_operations_regen(state, business_ops_result, business_ops_reply)

                return business_ops_reply 
            else: 
                return business_ops_reply

        except Exception as error:
            print("B_O CHECK ERROR: " + str(error))

            return business_ops_reply

    #booking branch
    elif(route_result == "booking"):
        booking_state: dict = lg.read_bs(f"{id}_bstate")

        car_model: str = booking_state.get("car_model", "")

        pricing_sent: str = booking_state.get("pricing_state", "")

        if(car_model != "" and pricing_sent != ""):
            booking_link_sent: bool = booking_state.get("booking_link_state", "") != ""

            booking_details: dict = {"booking_link": rf.BOOKING_LINK, "booking_link_sent": booking_link_sent, "car_model": car_model}

            booking_reply: str = rf.booking_generator(state, booking_details)

            #a failed check or regen still sends the first reply
            try:
                booking_enforce: bool = rf.booking_enforcer(state, booking_details, booking_reply)

                if(booking_enforce):
                    booking_reply = rf.booking_regen(state, booking_details, booking_reply)

                    return booking_reply

                else:
                    return booking_reply

            except Exception as error:
                print("BOOKING CHECK ERROR: " + str(error))

                return booking_reply
        else: 
            #no car yet, so ask for it before booking
            if(car_model == ""):
                car_model_reply: str = rf.car_model_integrator_gen(state)

                return car_model_reply
            #car known but never priced, so price it first
            else: 
                return service_and_pricing_branch(state)


    #services_req_humans branch
    elif(route_result == "services_req_humans"):
        s_rh_reply: str = rf.services_rh_gen(state)

        #wait on the pictures before handing off to a human
        lg.add_id(lg.HIL_QUEUE_KEY, id)

        return s_rh_reply

    #closing_statements branch
    elif(route_result == "closing_statements"):
        closing_reply: str = rf.closing_statements_gen(state)

        #a failed check or regen still sends the first reply
        try:
            closing_enforce: bool = rf.closing_statements_enforcer(state, closing_reply)

            if(closing_enforce):
                closing_reply = rf.closing_statements_regen(state, closing_reply)

                return closing_reply
            else:
                return closing_reply

        except Exception as error:
            print("CLOSING CHECK ERROR: " + str(error))

            return closing_reply

    #phone_call branch
    elif(route_result == "phone_call"):
        phone_reply: str = rf.phone_call_gen(state)

        #trigger hil
        send.send_blooio_message(HIL_RECIPENT, "HIL TRIGERED, due to PHONE CALL")
        lg.add_id(lg.RESTRICTED_KEY, id)

        return phone_reply

    elif(route_result == "escalation"):
        esclation_reply: str = rf.escalation_gen(state)

        #trigger hil
        send.send_blooio_message(HIL_RECIPENT, "HIL TRIGERED, due to ESCLATION")
        lg.add_id(lg.RESTRICTED_KEY, id)

        return esclation_reply

    #covers off_topic and owner_convo
    else:
        lg.add_id(lg.RESTRICTED_KEY, id)
        return ""


