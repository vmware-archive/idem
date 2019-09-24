# Import python libs
import fnmatch


def apply(self, high):
    '''
    Read in the __exclude__ list and remove all excluded objects from the
    high data
    '''
    if '__exclude__' not in high:
        return high
    ex_sls = set()
    ex_id = set()
    exclude = high.pop('__exclude__')
    for exc in exclude:
        if isinstance(exc, str):
            # The exclude statement is a string, assume it is an sls
            ex_sls.add(exc)
        if isinstance(exc, dict):
            # Explicitly declared exclude
            if len(exc) != 1:
                continue
            key = next(exc.keys())
            if key == 'sls':
                ex_sls.add(exc['sls'])
            elif key == 'id':
                ex_id.add(exc['id'])
    # Now the excludes have been simplified, use them
    if ex_sls:
        # There are sls excludes, find the associated ids
        for name, body in high.items():
            if name.startswith('__'):
                continue
            sls = body.get('__sls__', '')
            if not sls:
                continue
            for ex_ in ex_sls:
                if fnmatch.fnmatch(sls, ex_):
                    ex_id.add(name)
    for id_ in ex_id:
        if id_ in high:
            high.pop(id_)
    return high

