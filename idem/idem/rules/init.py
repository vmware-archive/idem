# Import python libs
import asyncio


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


async def run(hub, name, low, seq_comp, running, run_num):
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
    if '.' in chunk['state']:
        root_sub = chunk['state'].split('.')[0]
        if not root_sub in hub.idem.RUNS[name]['subs']:
            ret = {
                'name': chunk['name'],
                'comment': f'State not available: chunk["state"]',
                'changes': {},
                'result': False}
            ret['__run_num'] = run_num
            running[tag] = ret
            return
        s_ref = f"{chunk['state']}.{chunk['fun']}"
    else:
        s_ref = f"states.{chunk['state']}.{chunk['fun']}"
    func = getattr(hub, s_ref)
    call = hub.idem.tools.format_call(func, chunk, expected_extra_kws=STATE_INTERNAL_KEYWORDS)
    for rdat in rdats:
        if 'pre' in rdat:
            ret = rdat['pre'](*call['args'], **call['kwargs'])
            if asyncio.iscoroutine(ret):
                ret = await ret
    if '__run_name' in call['avail_kwargs'] or '__run_name' in call['avail_args']:
        call['kwargs']['__run_name'] = name
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
