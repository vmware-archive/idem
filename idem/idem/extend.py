def reconcile(hub, high):
    '''
    Take the extend statement and reconcile it back into the highdata
    '''
    errors = []
    if '__extend__' not in high:
        return high, errors
    ext = high.pop('__extend__')
    for ext_chunk in ext:
        for id_, body in ext_chunk:
            if id_ not in high:
                state_type = next(
                    x for x in body if not x.startswith('__')
                )
                # Check for a matching 'name' override in high data
                ids = hub.idem.tools.find_id(id_, state_type, high)
                if len(ids) != 1:
                    errors.append(
                        'Cannot extend ID \'{0}\' in \'{1}:{2}\'. It is not '
                        'part of the high state.\n'
                        'This is likely due to a missing include statement '
                        'or an incorrectly typed ID.\nEnsure that a '
                        'state with an ID of \'{0}\' is available\nin '
                        'environment \'{1}\' and to SLS \'{2}\''.format(
                            id_,
                            body.get('__env__', 'base'),
                            body.get('__sls__', 'base'))
                        )
                    continue
                else:
                    id_ = ids[0][0]

            for state, run in body.items():
                if state.startswith('__'):
                    continue
                if state not in high[id_]:
                    high[id_][state] = run
                    continue
                for arg in run:
                    update = False
                    for hind in range(len(high[id_][state])):
                        if isinstance(arg, str) and isinstance(high[id_][state][hind], str):
                            # replacing the function, replace the index
                            high[id_][state].pop(hind)
                            high[id_][state].insert(hind, arg)
                            update = True
                            continue
                        if isinstance(arg, dict) and isinstance(high[id_][state][hind], dict):
                            # It is an option, make sure the options match
                            argfirst = next(iter(arg))
                            if argfirst == next(iter(high[id_][state][hind])):
                                # If argfirst is a requisite then we must merge
                                # our requisite with that of the target state
                                if argfirst in STATE_REQUISITE_KEYWORDS:
                                    high[id_][state][hind][argfirst].extend(arg[argfirst])
                                # otherwise, its not a requisite and we are just extending (replacing)
                                else:
                                    high[id_][state][hind] = arg
                                update = True
                            if (argfirst == 'name' and
                                next(iter(high[id_][state][hind])) == 'names'):
                                # If names are overwritten by name use the name
                                high[id_][state][hind] = arg
                    if not update:
                        high[id_][state].append(arg)
    return high, errors
