def check(hub, condition, req_ret, chunk):
    '''
    If changes are made then run the configured post command
    '''
    ret = {}
    if req_ret['ret']['changes']:
        func = getattr(hub, f'states.{chunk["state"]}.{condition}')
        if func:
            ret['post'] = func
    return ret
