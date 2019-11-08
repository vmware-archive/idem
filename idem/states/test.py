# -*- coding: utf-8 -*-
'''
Test States
===========

Provide test case states that enable easy testing of things to do with state
calls, e.g. running, calling, logging, output filtering etc.

.. code-block:: yaml

    always-passes-with-any-kwarg:
      test.nop:
        - name: foo
        - something: else
        - foo: bar

    always-passes:
      test.succeed_without_changes:
        - name: foo

    always-fails:
      test.fail_without_changes:
        - name: foo

    always-changes-and-succeeds:
      test.succeed_with_changes:
        - name: foo

    always-changes-and-fails:
      test.fail_with_changes:
        - name: foo
'''
# Import Python libs
import random

TREQ = {
        'treq': {
            'require': [
                'test.nop',
                ]
            },
        }


def treq(hub, ctx, name, **kwargs):
    '''
    Ensure that a transparent requisite is applied
    '''
    return succeed_without_changes(hub, ctx, name)


def nop(hub, ctx, name, **kwargs):
    '''
    A no-op state that does nothing. Useful in conjunction with the `use`
    requisite, or in templates which could otherwise be empty due to jinja
    rendering
    '''
    return succeed_without_changes(hub, ctx, name)


def succeed_without_changes(hub, ctx, name, **kwargs):
    '''
    name
        A unique string.
    '''
    ret = {
        'name': name,
        'changes': {},
        'result': True,
        'comment': 'Success!'
    }
    return ret


def fail_without_changes(hub, ctx, name, **kwargs):
    '''
    Returns failure.

    name:
        A unique string.
    '''
    ret = {
        'name': name,
        'changes': {},
        'result': False,
        'comment': 'Failure!'
    }

    return ret


def succeed_with_changes(hub, ctx, name, **kwargs):
    '''
    Returns successful and changes is not empty

    name:
        A unique string.
    '''
    ret = {
        'name': name,
        'changes': {},
        'result': True,
        'comment': 'Success!'
    }

    ret['changes'] = {
        'testing': {
            'old': 'Unchanged',
            'new': 'Something pretended to change'
        }
    }

    return ret


def fail_with_changes(hub, ctx, name, **kwargs):
    '''
    Returns failure and changes is not empty.

    name:
        A unique string.
    '''
    ret = {
        'name': name,
        'changes': {},
        'result': False,
        'comment': 'Failure!'
    }
    ret['changes'] = {
        'testing': {
            'old': 'Unchanged',
            'new': 'Something pretended to change'
        }
    }
    return ret


def update_low(hub, ctx, name):
    '''
    Use the __run_name to add a run to the low
    '''
    extra = {
        '__sls__': 'none',
        'name': 'totally_extra_alls',
        '__id__': 'king_arthur',
        'state': 'test',
        'fun': 'nop'}
    hub.idem.RUNS[ctx['run_name']]['add_low'].append(extra)
    return succeed_without_changes(hub, ctx, name)


def mod_watch(hub, ctx, name, **kwargs):
    '''
    Return a mod_watch call for test
    '''
    ret = {
        'name': name,
        'changes': {'watch': True},
        'result': True,
        'comment': 'Watch ran!'
    }
    return ret
