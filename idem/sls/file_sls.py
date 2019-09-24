'''
This module is used to retrive files from a local source
'''
# Import python libs
import os
import shutil


__virtualname__ = 'file'


async def cache(hub, cache_dir, full):
    '''
    Take a file from a location definition and cache it in the target location
    '''
    if full.startswith('file://'):
        full = full[7:]
    c_tgt = os.path.join(cache_dir, full.lstrip(os.sep))
    c_dir = os.path.dirname(c_tgt)
    try:
        os.makedirs(c_dir)
    except FileExistsError:
        pass
    if not os.path.isfile(full):
        return None
    shutil.copy(full, c_tgt)
    return c_tgt
