def seq(hub, low, running):
    '''
    Return the sequence map that should be used to execute the lowstate
    The sequence needs to identify:
    1. recursive requisites
    2. what chunks are free to run
    3. Bahavior augments for the next chunk to run
    '''
    ret = {}
    for ind, chunk in enumerate(low):
        tag = hub.idem.tools.gen_tag(chunk)
        if tag in running:
            # Already ran this one, don't add it to the sequence
            continue
        ret[ind] = {'chunk': chunk, 'reqrets': [], 'unmet': set()}
        for req in hub.idem.RMAP:
            if req in chunk:
                for rdef in chunk[req]:
                    if not isinstance(rdef, dict):
                        # TODO: Error check
                        continue
                    state = next(iter(rdef))
                    name = rdef[state]
                    r_chunks = hub.idem.tools.get_chunks(low, state, name)
                    if not r_chunks:
                        ret[ind]['errors'].append(f'Requisite {req} {state}:{name} not found')
                    for r_chunk in r_chunks:
                        r_tag = hub.idem.tools.gen_tag(r_chunk)
                        if r_tag in running:
                            reqret = {
                                'req': req,
                                'name': name,
                                'state': state,
                                'r_tag': r_tag,
                                'ret': running[r_tag],
                                }
                            # it has been run, check the rules
                            ret[ind]['reqrets'].append(reqret)
                        else:
                            ret[ind]['unmet'].add(r_tag)
    return ret
