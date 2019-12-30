# Import python libs
import os
import tempfile

# Import pop libs
import pop.hub
import idem.conf
import rend.exc

# Import third party libs
import pytest


def run_sls(sls, runtime='parallel', test=False):
    '''
    Pass in an sls list and run it!
    '''
    name = 'test'
    hub = pop.hub.Hub()
    hub.pop.sub.add('idem.idem', init=True)
    hub.pop.sub.add('nest')
    hub.pop.sub.load_subdirs(hub.nest)
    hub.pop.sub.load_subdirs(hub.nest.nest)
    hub.pop.sub.load_subdirs(hub.nest.nest.again)
    render = 'jinja|yaml'
    cache_dir = tempfile.mkdtemp()
    sls_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sls')
    sls_sources = [f'file://{sls_dir}']
    hub.pop.loop.start(hub.idem.init.apply(name, sls_sources, render, runtime, ['states', 'nest'], cache_dir, sls, test))
    errors = hub.idem.RUNS[name]['errors']
    if errors:
        return errors
    ret = hub.idem.RUNS[name]['running']
    return ret


def test_treq():
    ret = run_sls(['treq'])
    assert ret['test_|-to_treq_|-to_treq_|-treq']['__run_num'] == 4


def test_ugly1():
    ret = run_sls(['ugly1'])
    assert ret == ['ID foo in SLS ugly1 is not a dictionary']


def test_shebang():
    ret = run_sls(['bang'])
    assert 'test_|-test_|-test_|-nop' in ret


def test_req_chain():
    '''
    Test that you can chain requisites, bug #11
    '''
    ret = run_sls(['recreq'])
    assert ret.get('test_|-first thing_|-first thing_|-nop', {}).get('__run_num') == 1
    assert ret.get('test_|-second thing_|-second thing_|-nop', {}).get('__run_num') == 2
    assert ret.get('test_|-third thing_|-third thing_|-nop', {}).get('__run_num') == 3


def test_nest():
    ret = run_sls(['nest'])
    assert ret['nest.again.another.test_|-baz_|-baz_|-nop']['result']
    assert ret['nest.again.test_|-bar_|-bar_|-nop']['result']
    assert ret['nest.test_|-foo_|-foo_|-nop']['result']
    # verify that the invalid state is not run
    assert not ret['idem.init_|-quo_|-quo_|-create']['result']
    assert ret['test_|-req_|-req_|-nop']['__run_num'] == 5


def test_basic():
    '''
    Test the basic funcitonality of Idem
    '''
    ret = run_sls(['simple'])
    assert ret['test_|-happy_|-happy_|-nop']['result'] == True
    assert ret['test_|-happy_|-happy_|-nop']['changes'] == {}
    assert ret['test_|-happy_|-happy_|-nop']['name'] == 'happy'
    assert ret['test_|-sad_|-sad_|-fail_without_changes']['result'] == False
    assert ret['test_|-sad_|-sad_|-fail_without_changes']['name'] == 'sad'
    assert ret['test_|-sad_|-sad_|-fail_without_changes']['changes'] == {}


def test_req():
    '''
    Test basic requisites
    '''
    ret = run_sls(['req'])
    assert ret['test_|-needs_fail_|-needs_fail_|-nop']['result'] == False
    assert ret['test_|-needs_fail_|-needs_fail_|-nop']['__run_num'] == 4
    assert ret['test_|-needs_|-needs_|-nop']['__run_num'] == 3
    assert ret['test_|-needs_|-needs_|-nop']['result'] == True


def test_req_test_mode():
    '''
    Test basic requisites in test mode
    '''
    ret = run_sls(['req'], test=True)
    assert ret['test_|-needs_fail_|-needs_fail_|-nop']['result'] == False
    assert ret['test_|-needs_fail_|-needs_fail_|-nop']['__run_num'] == 4
    assert ret['test_|-needs_|-needs_|-nop']['__run_num'] == 3
    # "needed" returned None and needs did not fail to run
    assert ret['test_|-needs_|-needs_|-nop']['result'] == None


def test_watch():
    '''
    Test basic requisites
    '''
    ret = run_sls(['watch'])
    assert ret['test_|-watch_changes_|-watch_changes_|-nop']['__run_num'] == 2
    assert ret['test_|-watch_changes_|-watch_changes_|-nop']['comment'] == 'Watch ran!'
    assert ret['test_|-watch_changes_|-watch_changes_|-nop']['result'] == True
    assert ret['test_|-changes_|-changes_|-succeed_with_changes']['result'] == True
    assert ret['test_|-changes_|-changes_|-succeed_with_changes']['changes']


def test_onfail():
    '''
    Test basic requisites
    '''
    ret = run_sls(['fails'])
    assert ret['test_|-runs_|-runs_|-nop']['__run_num'] == 2
    assert ret['test_|-runs_|-runs_|-nop']['result'] == True
    assert ret['test_|-bad_|-bad_|-nop']['result'] == False
    assert ret['test_|-bad_|-bad_|-nop']['__run_num'] == 3
    assert ret['test_|-fails_|-fails_|-fail_without_changes']['__run_num'] == 1
    assert ret['test_|-fails_|-fails_|-fail_without_changes']['result'] == False


def test_onchanges():
    ret = run_sls(['changes'])
    assert ret['test_|-watch_changes_|-watch_changes_|-nop']['__run_num'] == 2
    assert ret['test_|-watch_changes_|-watch_changes_|-nop']['result'] == True


def test_run_name():
    ret = run_sls(['update'])
    assert ret['test_|-king_arthur_|-totally_extra_alls_|-nop']['__run_num'] == 2


def test_params():
    ret = run_sls(['order'], runtime='serial')
    assert ret['test_|-first_|-first_|-noop']['__run_num'] == 1
    assert ret['test_|-second_|-second_|-noop']['__run_num'] == 2
    assert ret['test_|-third_|-third_|-noop']['__run_num'] == 3
    assert ret['test_|-forth_|-forth_|-noop']['__run_num'] == 4
    assert ret['test_|-fifth_|-fifth_|-noop']['__run_num'] == 5
    assert ret['test_|-sixth_|-sixth_|-noop']['__run_num'] == 6
    assert ret['test_|-seventh_|-seventh_|-noop']['__run_num'] == 7
    assert ret['test_|-eighth_|-eighth_|-noop']['__run_num'] == 8
    assert ret['test_|-ninth_|-ninth_|-noop']['__run_num'] == 9
    assert ret['test_|-tenth_|-tenth_|-noop']['__run_num'] == 10

def test_blocks():
    ret = run_sls(['blocks'])
    assert 'test_|-wow_|-wow_|-nop' in ret


def test_dup_keys():
    with pytest.raises(rend.exc.RenderException):
        ret = run_sls(['dupkeys'])
