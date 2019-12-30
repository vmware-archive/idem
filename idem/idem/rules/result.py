def check(hub, condition, reqret, chunk):
    '''
    Check to see if the result is True
    '''
    if isinstance(condition, list):
        if reqret['ret']['result'] in condition:
            return {}
    if reqret['ret']['result'] is condition:
        return {}
    else:
        return {'errors': [f'Result of require {reqret["r_tag"]} is "{reqret["ret"]["result"]}", not "{condition}"']}
