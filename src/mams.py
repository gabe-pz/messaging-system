from src import rage_functions as rf


def mams(state: dict) -> str: 
    route_result: str = rf.route(state)
    print(route_result) 

    if(route_result == "service_and_pricing"):
        s_and_p_result: list = rf.service_and_pricing_analyzer(state) 

        s_and_p_reply: str = rf.service_and_pricing_generator(state, s_and_p_result)
    
        return s_and_p_reply

