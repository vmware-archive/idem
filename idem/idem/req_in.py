def reconcile(hub, high, disabled_reqs=None):
    '''
    Extend the data reference with requisite_in arguments
    '''
    req_in = {'require_in', 'watch_in', 'onfail_in', 'onchanges_in', 'use', 'use_in', 'prereq', 'prereq_in'}
    req_in_all = req_in.union({'require', 'watch', 'onfail', 'onfail_stop', 'onchanges'})
    extend = {}
    errors = []
    if disabled_reqs is None:
        disabled_reqs = []
    if not isinstance(disabled_reqs, list):
        disabled_reqs = [disabled_reqs]
    # Highdata iterator
    for id_, body, state, run, arg in hub.idem.tools.iter_high(high):
        # Iterator yields args
        if isinstance(arg, dict):
            # It is not a function, verify that the arg is a
            # requisite in statement
            if len(arg) < 1:
                # Empty arg dict
                # How did we get this far?
                continue
            # Split out the components
            key = next(iter(arg))
            if key not in req_in:
                continue
            if key in disabled_reqs:
                continue
            rkey = key.split('_')[0]
            items = arg[key]
            if isinstance(items, dict):
                # Formatted as a single req_in
                for _state, name in items.items():
                    # Not a use requisite_in
                    found = False
                    if name not in extend:
                        extend[name] = {}
                    if '.' in _state:
                        errors.append(
                            f'Invalid requisite in {rkey}: {_state} for '
                            f'{name}, in SLS "{body["__sls__"]}". Requisites must '
                            f'not contain dots, did you mean "{_state[:_state.find(".")]}"?'
                        )
                        _state = _state.split('.')[0]
                    if _state not in extend[name]:
                        extend[name][_state] = []
                    extend[name]['__env__'] = body['__env__']
                    extend[name]['__sls__'] = body['__sls__']
                    for ind in range(len(extend[name][_state])):
                        if next(iter(
                            extend[name][_state][ind])) == rkey:
                            # Extending again
                            extend[name][_state][ind][rkey].append(
                                    {state: id_}
                                    )
                            found = True
                    if found:
                        continue
                    # The rkey is not present yet, create it
                    extend[name][_state].append(
                            {rkey: [{state: id_}]}
                            )
            if isinstance(items, list):
                # Formed as a list of requisite additions
                hinges = []
                for ind in items:
                    if not isinstance(ind, dict):
                        # Malformed req_in
                        if ind in high:
                            _ind_high = [x for x
                                            in high[ind]
                                            if not x.startswith('__')]
                            ind = {_ind_high[0]: ind}
                        else:
                            found = False
                            for _id in iter(high):
                                for state in [state for state
                                                in iter(high[_id])
                                                if not state.startswith('__')]:
                                    for j in iter(high[_id][state]):
                                        if isinstance(j, dict) and 'name' in j:
                                            if j['name'] == ind:
                                                ind = {state: _id}
                                                found = True
                            if not found:
                                continue
                    if len(ind) < 1:
                        continue
                    pstate = next(iter(ind))
                    pname = ind[pstate]
                    if pstate == 'sls':
                        # Expand hinges here
                        hinges = find_sls_ids(pname, high)
                    else:
                        hinges.append((pname, pstate))
                    if '.' in pstate:
                        errors.append(
                            'Invalid requisite in {0}: {1} for '
                            '{2}, in SLS \'{3}\'. Requisites must '
                            'not contain dots, did you mean \'{4}\'?'
                            .format(
                                rkey,
                                pstate,
                                pname,
                                body['__sls__'],
                                pstate[:pstate.find('.')]
                            )
                        )
                        pstate = pstate.split(".")[0]
                    for tup in hinges:
                        name, _state = tup
                        if key == 'prereq_in':
                            # Add prerequired to origin
                            if id_ not in extend:
                                extend[id_] = {}
                            if state not in extend[id_]:
                                extend[id_][state] = []
                            extend[id_][state].append(
                                    {'prerequired': [{_state: name}]}
                                    )
                        if key == 'prereq':
                            # Add prerequired to prereqs
                            ext_ids = find_name(name, _state, high)
                            for ext_id, _req_state in ext_ids:
                                if ext_id not in extend:
                                    extend[ext_id] = {}
                                if _req_state not in extend[ext_id]:
                                    extend[ext_id][_req_state] = []
                                extend[ext_id][_req_state].append(
                                        {'prerequired': [{state: id_}]}
                                        )
                            continue
                        if key == 'use_in':
                            # Add the running states args to the
                            # use_in states
                            ext_ids = find_name(name, _state, high)
                            for ext_id, _req_state in ext_ids:
                                if not ext_id:
                                    continue
                                ext_args = state_args(ext_id, _state, high)
                                if ext_id not in extend:
                                    extend[ext_id] = {}
                                if _req_state not in extend[ext_id]:
                                    extend[ext_id][_req_state] = []
                                ignore_args = req_in_all.union(ext_args)
                                for arg in high[id_][state]:
                                    if not isinstance(arg, dict):
                                        continue
                                    if len(arg) != 1:
                                        continue
                                    if next(iter(arg)) in ignore_args:
                                        continue
                                    # Don't use name or names
                                    if next(arg.keys()) == 'name':
                                        continue
                                    if next(arg.keys()) == 'names':
                                        continue
                                    extend[ext_id][_req_state].append(arg)
                            continue
                        if key == 'use':
                            # Add the use state's args to the
                            # running state
                            ext_ids = find_name(name, _state, high)
                            for ext_id, _req_state in ext_ids:
                                if not ext_id:
                                    continue
                                loc_args = state_args(id_, state, high)
                                if id_ not in extend:
                                    extend[id_] = {}
                                if state not in extend[id_]:
                                    extend[id_][state] = []
                                ignore_args = req_in_all.union(loc_args)
                                for arg in high[ext_id][_req_state]:
                                    if not isinstance(arg, dict):
                                        continue
                                    if len(arg) != 1:
                                        continue
                                    if next(iter(arg)) in ignore_args:
                                        continue
                                    # Don't use name or names
                                    if next(arg.keys()) == 'name':
                                        continue
                                    if next(arg.keys()) == 'names':
                                        continue
                                    extend[id_][state].append(arg)
                            continue
                        found = False
                        if name not in extend:
                            extend[name] = {}
                        if _state not in extend[name]:
                            extend[name][_state] = []
                        extend[name]['__env__'] = body['__env__']
                        extend[name]['__sls__'] = body['__sls__']
                        for ind in range(len(extend[name][_state])):
                            if next(iter(
                                extend[name][_state][ind])) == rkey:
                                # Extending again
                                extend[name][_state][ind][rkey].append(
                                        {state: id_}
                                        )
                                found = True
                        if found:
                            continue
                        # The rkey is not present yet, create it
                        extend[name][_state].append(
                                {rkey: [{state: id_}]}
                                )
    high['__extend__'] = []
    for key, val in extend.items():
        high['__extend__'].append({key: val})
    req_in_high, req_in_errors = hub.idem.extend.reconcile(high)
    errors.extend(req_in_errors)
    return req_in_high, errors