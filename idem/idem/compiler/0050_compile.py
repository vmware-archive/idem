def stage(hub, name):
    '''
    Apply the exclude value
    '''
    low = hub.idem.low.compile(hub.idem.RUNS[name]['high'])
    hub.idem.RUNS[name]['low'] = low