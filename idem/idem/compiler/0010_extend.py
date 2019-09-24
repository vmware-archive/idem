def stage(hub, name):
    '''
    Take the highdata and reconcoile the extend keyword
    '''
    high, errors = hub.idem.extend.reconcile(hub.idem.RUNS[name]['high'])
    hub.idem.RUNS[name]['high'] = high
    hub.idem.RUNS[name]['errors'] = errors