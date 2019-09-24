def high(hub, high):
    '''
    Verify that the high data is viable and follows the data structure
    '''
    errors = []
    if not isinstance(high, dict):
        errors.append('High data is not a dictionary and is invalid')
    reqs = {}
    for id_, body in high.items():
        if id_.startswith('__'):
            continue
        if not isinstance(id_, str):
            errors.append(
                f'ID "{id_}" in SLS "{body["__sls__"]}" is not formed as a string, but '
                f'is a {type(id_).__name__}'
            )
        if not isinstance(body, dict):
            err = f'The type {id_} in {body} is not formatted as a dictionary'
            errors.append(err)
            continue
        for state in body:
            if state.startswith('__'):
                continue
            if not isinstance(body[state], list):
                errors.append(
                    f'State "{id_}" in SLS "{body["__sls__"]}" is not formed as a list'
                )
            else:
                fun = 0
                if '.' in state:
                    fun += 1
                for arg in body[state]:
                    if isinstance(arg, str):
                        fun += 1
                        if ' ' in arg.strip():
                            errors.append((
                                f'The function "{arg}" in state '
                                f'"{id_}" in SLS "{body["__sls__"]}" has '
                                'whitespace, a function with whitespace is '
                                'not supported, perhaps this is an argument '
                                'that is missing a ":"'))
                    elif isinstance(arg, dict):
                        # The arg is a dict, if the arg is require or
                        # watch, it must be a list.
                        #
                        # Add the requires to the reqs dict and check them
                        # all for recursive requisites.
                        argfirst = next(iter(arg))
                        if argfirst in ('require', 'watch', 'prereq', 'onchanges'):
                            if not isinstance(arg[argfirst], list):
                                errors.append((f'The {argfirst}'
                                f' statement in state "{id_}" in SLS "{body["__sls__"]}" '
                                'needs to be formed as a list'))
                            # It is a list, verify that the members of the
                            # list are all single key dicts.
                            else:
                                reqs[id_] = {'state': state}
                                for req in arg[argfirst]:
                                    if isinstance(req, str):
                                        req = {'id': req}
                                    if not isinstance(req, dict):
                                        err = (f'Requisite declaration {req}'
                                        f' in SLS {body["__sls__"]} is not formed as a'
                                        ' single key dictionary')
                                        errors.append(err)
                                        continue
                                    req_key = next(iter(req))
                                    req_val = req[req_key]
                                    if '.' in req_key:
                                        errors.append((
                                            f'Invalid requisite type "{req_key}" '
                                            f'in state "{id_}", in SLS '
                                            f'"{body["__sls__"]}". Requisite types must '
                                            'not contain dots, did you '
                                            f'mean "{req_key[:req_key.find(".")]}"?'
                                        ))
                                    if not hub.idem.tools.ishashable(req_val):
                                        errors.append((
                                            f'Illegal requisite "{str(req_val)}", '
                                            f'is SLS {body["__sls__"]}\n'
                                            ))
                                        continue
                                    # Check for global recursive requisites
                                    reqs[id_][req_val] = req_key
                                    if req_val in reqs:
                                        if id_ in reqs[req_val]:
                                            if reqs[req_val][id_] == state:
                                                if reqs[req_val]['state'] == reqs[id_][req_val]:
                                                    err = ('A recursive '
                                                    'requisite was found, SLS '
                                                    f'"{body["__sls__"]}" ID "{id_}" ID "{req_val}"'
                                                    )
                                                    errors.append(err)
                            # Make sure that there is only one key in the
                            # dict
                            if len(list(arg)) != 1:
                                errors.append(('Multiple dictionaries '
                                f'defined in argument of state "{id_}" in SLS "{body["__sls__"]}"'
                                ))
                if not fun:
                    if state == 'require' or state == 'watch':
                        continue
                    errors.append((f'No function declared in state "{state}" in'
                        f' SLS "{body["__sls__"]}"'))
                elif fun > 1:
                    errors.append(
                        f'Too many functions declared in state "{state}" in '
                        f'SLS "{body["__sls__"]}"'
                    )
    return high, errors