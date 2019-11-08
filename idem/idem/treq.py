'''
This plugin is used to resolve transparent requisites adn apply them to
the lowstate
'''
# Import pop libs
import pop.loader
# TREQ = {func_D requires func_a, B, C}
#TREQ = {'func_D':
#            'require': [
#              'foo.bar.baz.func_A',
#              'test.func_B',
#              ],
#            'soft_require': [
#                'cheese.func_C',
#                ],
#            }


def gather(hub, subs, low):
    '''
    Given the runtime name and the chunk in question, determine what function
    on the hub that can be run
    '''
    ret = {}
    for chunk in low:
        s_ref = chunk['state']
        if s_ref in ret:
            continue
        for sub in subs:
            test = f'{sub}.{s_ref}'
            try:
                mod = getattr(hub, test)
            except AttributeError:
                continue
            if not isinstance(mod, pop.loader.LoadedMod):
                continue
            if mod is None:
                continue
            if hasattr(mod, 'TREQ'):
                ret.update({s_ref: mod.TREQ})
    return ret


def apply(hub, subs, low):
    '''
    Look up the transparetn requisites as defined in state modules and apply
    them to the respective low chunks
    '''
    treq = hub.idem.treq.gather(subs, low)
    refs = {}
    for ind, chunk in enumerate(low):
        path = f'{chunk["state"]}.{chunk["fun"]}'
        if path not in refs:
            refs[path] = []
        # I am using a list to maintain requisite ordering. if a set is used
        # The we will have no deterministic ordering, which would be BAD!!!
        if ind not in refs[path]:
            refs[path].append(ind)
    for chunk in low:
        if not chunk['state'] in treq:
            continue
        if not chunk['fun'] in treq[chunk['state']]:
            continue
        rule = treq[chunk['state']][chunk['fun']]
        for req, r_refs in rule.items():
            for ref in r_refs:
                if ref not in refs:
                    continue
                for rind in refs[path]:
                    req_chunk = low[rind]
                    if req not in chunk:
                        chunk[req] = []
                    chunk[req].append({req_chunk['state']: req_chunk['__id__']})
    return low
