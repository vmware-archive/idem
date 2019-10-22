# Import python libs
import asyncio


async def runtime(hub, name, seq, low, running, run_num):
    '''
    Execute the runtime in parallel mode
    '''
    inds = []
    for ind in seq:
        if seq[ind].get('unmet'):
            # Requisites are unmet, skip this one
            continue
        inds.append(ind)
    if not inds:
        # Nothing can be run, we have hit recursive requisite,
        # or we are done
        pass
    for ind in inds:
        await hub.idem.rules.init.run(name, low, seq[ind], running, run_num)
    if len(low) <= len(running):
        return
