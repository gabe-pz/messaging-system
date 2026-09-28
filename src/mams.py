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

