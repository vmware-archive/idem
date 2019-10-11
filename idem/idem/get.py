'''
This file contains routines to get sls files from references
'''
# Import python libs
import os


async def ref(hub, name, sls):
    '''
    Cache the given file from the named reference point
    '''
    for source in hub.idem.RUNS[name]['sls_sources']:
        proto = source[:source.index(':')]
        path = sls.replace('.', '/')
        locs = [f'{path}.sls', f'{path}/init.sls']
        for loc in locs:
            full = os.path.join(source, loc)
            cfn = await hub.pop.ref.last(f'sls.{proto}.cache')(hub.idem.RUNS[name]['cache_dir'], full)
            if cfn:
                return cfn
