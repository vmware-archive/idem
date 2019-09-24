'''
This subsystem is used to manage the renderer process
'''

async def render(hub, default, cfn, sls_ref):
    '''
    '''
    #try:
    with open(cfn, 'r') as rfp:
        raw = rfp.read()
        if raw.startswith('#!'):
            default = raw[:raw.index('\n')]
            default = raw[2:]
        pcount = 0
        for pipe in default.split('|'):
            ref = f'render.{pipe}.render'
            if pcount == 0:
                data = await hub.pop.ref.last(ref)(raw)
            else:
                data = await hub.pop.ref.last(ref)(data)
            pcount += 1
    #except:  #TODO: Fix exception block
    #    return {}
    return data
