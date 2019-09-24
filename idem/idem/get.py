'''
This file contains routines to get sls files from references
'''
# Import python libs
import os


async def ref(hub, name, sls):
    '''
    Cache the given file from the named reference point
    '''
    opts = hub.idem.RUNS[name]['opts']
    for source in opts.get('sls_sources', ['file://']):
        proto = source[:source.index(':')]
        path = sls.replace('.', '/')
        locs = [f'{path}.sls', f'{path}/init.sls']
        for loc in locs:
            full = os.path.join(source, loc)
            cfn = await hub.pop.ref.last(f'sls.{proto}.cache')(opts['cache_dir'], full)
            if cfn:
                return cfn
