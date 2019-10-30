# Import python libs
import copy


def order_chunks(hub, chunks):
    '''
    Sort the chunk list verifying that the chunks follow the order
    specified in the order options.
    '''
    cap = 1
    for chunk in chunks:
        if 'order' in chunk:
            if not isinstance(chunk['order'], int):
                continue

            chunk_order = chunk['order']
            if chunk_order > cap - 1 and chunk_order > 0:
                cap = chunk_order + 100
    for chunk in chunks:
        if 'order' not in chunk:
            chunk['order'] = cap
            continue

        if not isinstance(chunk['order'], (int, float)):
            if chunk['order'] == 'last':
                chunk['order'] = cap + 1000000
            elif chunk['order'] == 'first':
                chunk['order'] = 0
            else:
                chunk['order'] = cap
        if 'name_order' in chunk:
            chunk['order'] = chunk['order'] + chunk.pop('name_order') / 10000.0
        if chunk['order'] < 0:
            chunk['order'] = cap + 1000000 + chunk['order']
    chunks.sort(key=lambda chunk: (chunk['order'], '{0[state]}{0[name]}{0[fun]}'.format(chunk)))
    return chunks


def compile(hub, high, add_low):
    '''
    "Compile" the high data as it is retrieved from the CLI or YAML into
    the individual state executor structures
    '''
    chunks = []
    for name, body in high.items():
        if name.startswith('__'):
            continue
        for state, run in body.items():
            funcs = set()
            names = []
            if state.startswith('__'):
                continue
            chunk = {}
            chunk['state'] = state
            chunk['name'] = name
            if '__sls__' in body:
                chunk['__sls__'] = body['__sls__']
            if '__env__' in body:
                chunk['__env__'] = body['__env__']
            chunk['__id__'] = name
            for arg in run:
                if isinstance(arg, str):
                    funcs.add(arg)
                    continue
                if isinstance(arg, dict):
                    for key, val in arg.items():
                        if key == 'names':
                            for _name in val:
                                if _name not in names:
                                    names.append(_name)
                        elif key == 'state':
                            # Don't pass down a state override
                            continue
                        elif (key == 'name' and
                                not isinstance(val, str)):
                            # Invalid name, fall back to ID
                            chunk[key] = name
                        else:
                            chunk[key] = val
            if names:
                name_order = 1
                for entry in names:
                    live = copy.deepcopy(chunk)
                    if isinstance(entry, dict):
                        low_name = next(entry.keys())
                        live['name'] = low_name
                        list(map(live.update, entry[low_name]))
                    else:
                        live['name'] = entry
                    live['name_order'] = name_order
                    name_order += 1
                    for fun in funcs:
                        live['fun'] = fun
                        chunks.append(live)
            else:
                live = copy.deepcopy(chunk)
                for fun in funcs:
                    live['fun'] = fun
                    chunks.append(live)
    chunks.extend(add_low)
    chunks = hub.idem.low.order_chunks(chunks)
    return chunks
