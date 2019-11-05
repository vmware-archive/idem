# Import python libs
import asyncio

# import local libs
import pop.loader


# These are keywords passed to state module functions which are to be used
# by salt in this state module and not on the actual state module function
STATE_REQUISITE_KEYWORDS = frozenset([
    'onchanges',
    'onchanges_any',
    'onfail',
    'onfail_any',
    'onfail_all',
    'onfail_stop',
    'prereq',
    'prerequired',
    'watch',
    'watch_any',
    'require',
    'require_any',
    'listen',
    ])
STATE_REQUISITE_IN_KEYWORDS = frozenset([
    'onchanges_in',
    'onfail_in',
    'prereq_in',
    'watch_in',
    'require_in',
    'listen_in',
    ])
STATE_RUNTIME_KEYWORDS = frozenset([
    'fun',
    'state',
    'check_cmd',
    'failhard',
    'onlyif',
    'unless',
    'retry',
    'order',
    'parallel',
    'prereq',
    'prereq_in',
    'prerequired',
    'reload_modules',
    'reload_grains',
    'reload_pillar',
    'runas',
    'runas_password',
    'fire_event',
    'saltenv',
    'use',
    'use_in',
    '__run_name',
    '__env__',
    '__sls__',
    '__id__',
    '__orchestration_jid__',
    '__pub_user',
    '__pub_arg',
    '__pub_jid',
    '__pub_fun',
    '__pub_tgt',
    '__pub_ret',
    '__pub_pid',
    '__pub_tgt_type',
    '__prereq__',
    ])

STATE_INTERNAL_KEYWORDS = STATE_REQUISITE_KEYWORDS.union(STATE_REQUISITE_IN_KEYWORDS).union(STATE_RUNTIME_KEYWORDS)


def get_func(hub, name, chunk):
    '''
    Given the runtime name and the chunk in question, determine what function
    on the hub that can be run
    '''
    s_ref = chunk['state']
    for sub in hub.idem.RUNS[name]['subs']:
        test = f'{sub}.{s_ref}.{chunk["fun"]}'
        try:
            func = getattr(hub, test)
        except AttributeError:
            continue
        if isinstance(func, pop.loader.LoadedMod):
            continue
        if func is None:
            continue
        return func
    return None


async def run(hub, name, ctx, low, seq_comp, running, run_num):
    '''
    All requisites have been met for this low chunk.
    '''
    chunk = seq_comp['chunk']
    tag = hub.idem.tools.gen_tag(chunk)
    rdats = []
    errors = []
    for reqret in seq_comp.get('reqrets', []):
        req = reqret['req']
        rules = hub.idem.RMAP[req]
        for rule in rules:
            if hasattr(hub.idem.rules, rule):
                rdat = (getattr(hub.idem.rules, rule).check(rules[rule], reqret, chunk))
                if rdat.get('errors'):
                    errors.extend(rdat['errors'])
                rdats.append(rdat)
    if errors:
        running[tag] = {
            'name': chunk['name'],
            'changes': {},
            'comment': '\n'.join(errors),
            'result': False,
            '__run_num': run_num}
        return
    func = hub.idem.rules.init.get_func(name, chunk)
    if func is None:
        running[tag] = {
            'name': chunk['name'],
            'changes': {},
            'comment': f'The named state {chunk["state"]} is not available',
            'result': False,
            '__run_num': run_num}
        return
    chunk['ctx'] = ctx
    call = hub.idem.tools.format_call(func, chunk, expected_extra_kws=STATE_INTERNAL_KEYWORDS)
    for rdat in rdats:
        if 'pre' in rdat:
            ret = rdat['pre'](*call['args'], **call['kwargs'])
            if asyncio.iscoroutine(ret):
                ret = await ret
    ret = func(*call['args'], **call['kwargs'])
    if asyncio.iscoroutine(ret):
        ret = await ret
    for rdat in rdats:
        if 'post' in rdat:
            ret = rdat['post'](*call['args'], **call['kwargs'])
            if asyncio.iscoroutine(ret):
                ret = await ret
    ret['__run_num'] = run_num
    running[tag] = ret
