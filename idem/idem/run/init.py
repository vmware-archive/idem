async def start(hub, name):
    '''
    Called only after the named run has compiled low data. If no low data
    is present an exception will be raised
    '''
    if not hub.idem.RUNS[name].get('low'):
        raise ValueError()
    ctx = {'run_name': name, 'test': hub.idem.RUNS[name]['test']}
    rtime = hub.idem.RUNS[name]['runtime']
    low = hub.idem.RUNS[name].get('low')
    ref = f'idem.run.{rtime}.runtime'
    old_seq = {}
    old_low_len = -1
    while True:
        # TODO: make the errors float up
        seq = hub.idem.req.init.seq(low, hub.idem.RUNS[name]['running'])
        if seq == old_seq:
            raise Exception()
        await getattr(hub, ref)(name, ctx, seq, low, hub.idem.RUNS[name]['running'])
        await hub.idem.resolve.render(name)
        await hub.idem.init.compile(name)
        low = hub.idem.RUNS[name].get('low')
        if len(low) <= len(hub.idem.RUNS[name]['running']):
            break
        if len(low) == old_low_len:
            # We made no progress! Recursive requisite!
            raise Exception()
        old_seq = seq
        old_low_len = len(low)
        # Check for any new, available blocks to render
