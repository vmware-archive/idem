# Import python libs
import asyncio


async def runtime(hub, name, ctx, seq, low, running):
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
    coros = []
    for ind in inds:
        coros.append(
                hub.idem.rules.init.run(
                    name,
                    ctx,
                    low,
                    seq[ind],
                    running,
                    hub.idem.RUNS[name]['run_num'],
                    )
                )
        hub.idem.RUNS[name]['run_num'] += 1
    for fut in asyncio.as_completed(coros):
        await fut
    if len(low) <= len(running):
        return
