from src import rage_functions as rf
from helpers import log as lg


# S_P BRANCH
def service_and_pricing_branch(state: dict) -> str:
    s_and_p_result: list = rf.service_and_pricing_analyzer(state) 

    s_and_p_reply: str = rf.service_and_pricing_generator(state, s_and_p_result)

    #a failed check or regen still sends the first reply
    try:
        s_and_p_enforce: bool = rf.service_and_pricing_enforcer(f"AGENT_RESPONSE:\n{s_and_p_reply}")

        if(s_and_p_enforce):
            s_and_p_reply = rf.service_and_pricing_regen(state, s_and_p_result, s_and_p_reply)
            print("REGEN\n\n")
            return s_and_p_reply
        else: 
            print("FIRST TRY")
            return s_and_p_reply

    except Exception as error:
        print("S_P CHECK ERROR: " + str(error))

        return s_and_p_reply


# MAMS
def mams(state: dict, id: str) -> str: 
    #customer is answering the picture request, so acknowledge it and hand them to a human
    if(lg.has_id(lg.HIL_QUEUE_KEY, id)):
        ack_reply: str = rf.acknowledge_service_gen(state)

        print("trigger hil")

        lg.add_id(lg.RESTRICTED_KEY, id)

        lg.remove_id(lg.HIL_QUEUE_KEY, id)

        return ack_reply

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
            business_ops_enforce: bool = rf.business_operations_enforcer(business_ops_reply)

            if(business_ops_enforce):
                business_ops_reply = rf.business_operations_regen(state, business_ops_result, business_ops_reply)

                print("REGEN\n\n")
                return business_ops_reply 
            else: 
                print("FIRST TRY!\n\n")
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

                    print("REGEN\n\n")
                    return booking_reply
                else:
                    print("FIRST TRY!\n\n")
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

    #no branch for this route yet, so core sends the fallback reply
    return ""


