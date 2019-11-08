def stage(hub, name):
    '''
    Apply the exclude value
    '''
    low = hub.idem.treq.apply(
            hub.idem.RUNS[name]['subs'],
            hub.idem.RUNS[name]['low'],
            )
    hub.idem.RUNS[name]['low'] = low
