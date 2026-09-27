#functions to return strings for examples such that JEV can classify service accuratley 

def window_tint_exs() -> str:
    return """
    # Examples 
    Ex 1: 
        state: {'current_user_message': {'user_media': {}, 'user_text': 'how dark can you go?'}, 'message_history': {'user_message_0': {'user_media': {}, 'user_text': 'do you guys do windows?'}, 'agent_response_to_user_message_0': 'We do! We install ceramic window tint on all vehicles.'}}
        answer: True
    Ex 2: 
        state: {'current_user_message': {'user_media': {}, 'user_text': 'do you do ceramic coating?'}, 'message_history': {}}
        answer: False
    Ex 3: 
        state: {'current_user_message': {'user_media': {}, 'user_text': 'wow nice tint, what it heat reject'}, 'message_history': {}}
        answer: True
"""

def ppf_exs() -> str:
    return """
    # Examples
    Ex 1: 
        state: {'current_user_message': {'user_media': {'media_element_0': {'media_description(if applicable)': '', 'post_description(if applicable)': 'Houston’s Trusted PPF Shop 🛡️\n\n150+ ⭐️ 5-Star Reviews and counting!\n\nProtect your paint
        from rock chips, scratches & everyday damage with premium Paint Protection Film (PPF).\n\n📍 Serving Houston & Cypress\n• PPF | Ceramic Window Tint | Vinyl Wraps\n• Message us today for your FREE quote!\n\nProtect it. Preserve 
        it. Filthy Wraps.\n#filthywraps #ppf #tint #houston #wrap'}}, 'user_text': 'Can I get some info? '}, 'message_history': {}}
        answer: True
    """

