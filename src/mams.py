from src import rage_functions as rf


def mams(state: dict) -> str: 
    route_result: str = rf.route(state)

    #s_p branch
    if(route_result == "service_and_pricing"):
        s_and_p_result: list = rf.service_and_pricing_analyzer(state) 

        s_and_p_reply: str = rf.service_and_pricing_generator(state, s_and_p_result)

        s_and_p_enforce: bool = rf.service_and_pricing_enforcer(f"AGENT_RESPONSE:\n{s_and_p_reply}")

        if(s_and_p_enforce):
            s_and_p_reply = rf.service_and_pricing_regen(state, s_and_p_result, s_and_p_reply)
            print("REGEN\n\n")
            return s_and_p_reply
        else: 
            print("FIRST TRY")
            return s_and_p_reply

    #business_ops branch 
    elif(route_result == "business_operations"):
        business_ops_result: list = rf.business_operations_analyzer(state) 

        business_ops_reply: str = rf.business_operations_generator(state, business_ops_result) 

        business_ops_enforce: bool = rf.business_operations_enforcer(business_ops_reply)

        if(business_ops_enforce):
            business_ops_reply = rf.business_operations_regen(state, business_ops_result, business_ops_reply)

            print("REGEN\n\n")
            return business_ops_reply 
        else: 
            print("FIRST TRY!\n\n")
            return business_ops_reply

