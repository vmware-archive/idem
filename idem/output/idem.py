# NOTES
# This is a VERY simple outputter for idem, it does not do everything the
# Salt highstate outputter does, and nor should it! This outputter should
# not become hyper complicated, things like terse should be another
# outputter, this should really just get things like errors added

# Import third party libs
from colored import fg, attr


def display(hub, data):
    '''
    Display the data from an idem run
    '''
    endc = attr(0)
    strs = []
    for tag in sorted(
            data,
            key=lambda k: data[k].get('__run_num', 0)):
        ret = data[tag]
        comps = tag.split('_|-')
        state = comps[0]
        id_ = comps[1]
        fun = comps[3]
        name = ret['name']
        result = ret['result']
        comment = ret['comment']
        changes = hub.output.nested.display(ret['changes'])
        if result is True and changes:
            tcolor = fg(6)
        elif result is True:
            tcolor = fg(2)
        elif result is None:
            tcolor = fg(11)
        elif result is False:
            tcolor = fg(9)
        
        strs.append(f'{tcolor}--------{endc}')
        strs.append(f'{tcolor}      ID: {id_}{endc}')
        strs.append(f'{tcolor}Function: {state}.{fun}{endc}')
        strs.append(f'{tcolor}  Result: {result}{endc}')
        strs.append(f'{tcolor} Comment: {comment}{endc}')
        strs.append(f'{tcolor} Changes: {changes}{endc}')
    return '\n'.join(strs)
