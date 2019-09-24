def check(hub, condition, reqret, chunk):
    '''
    Check to see if the result is True
    '''
    run = False
    if isinstance(condition, bool):
        if bool(reqret['ret']['changes']) is condition:
            return {}
    # TODO: Add the ability to make more granular changes condition definitions
    elif reqret['ret']['changes'] == condition:
        return {}
    return {'errors': [f'Changes from {reqret["r_tag"]} is "{reqret["ret"]["result"]}", not "{condition}"']}
