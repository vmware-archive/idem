def kwargs(hub, ctx, name, one=None, two=None, three=None):
    return {
        'name': name,
        'result': True,
        'comment': f'{one} {two} {three}',
        'changes': {},
            }
