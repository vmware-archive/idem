def check(hub, condition, reqret, chunk):
    '''
    Check to see if the result is True
    '''
    if reqret['ret']['result'] is condition:
        return {}
    else:
        return {'errors': [f'Result of require {reqret["r_tag"]} is "{reqret["ret"]["result"]}", not "{condition}"']}