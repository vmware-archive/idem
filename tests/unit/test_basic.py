# Import python libs
import os

# Import rosso libs
import pop.hub
import tempfile
import idem.conf


def run_sls(sls):
    '''
    Pass in an sls list and run it!
    '''
    name = 'test'
    hub = pop.hub.Hub()
    hub.pop.sub.add('idem.idem', init=True)
    opts = {}
    for key, value in idem.conf.CLI_CONFIG.items():
        opts[key] = value['default']
    opts['cache_dir'] = tempfile.mkdtemp()
    sls_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sls')
    opts['sls_sources'] = [f'file://{sls_dir}']
    opts['sls'] = sls
    hub.idem.init.create(name, opts)
    hub.pop.loop.start(hub.idem.init.apply(name, opts, *opts['sls']))
    ret = hub.idem.RUNS[name]['running']
    return ret


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
    assert ret['test_|-needs_fail_|-needs_fail_|-nop']['__run_num'] == 2
    assert ret['test_|-needs_|-needs_|-nop']['__run_num'] == 2
    assert ret['test_|-needs_|-needs_|-nop']['result'] == True


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
    assert ret['test_|-bad_|-bad_|-nop']['__run_num'] == 2
    assert ret['test_|-fails_|-fails_|-fail_without_changes']['__run_num'] == 1
    assert ret['test_|-fails_|-fails_|-fail_without_changes']['result'] == False


def test_onchanges():
    ret = run_sls(['changes'])
    assert ret['test_|-watch_changes_|-watch_changes_|-nop']['__run_num'] == 2
    assert ret['test_|-watch_changes_|-watch_changes_|-nop']['result'] == True


def test_run_name():
    ret = run_sls(['update'])
    assert ret['test_|-king_arthur_|-totally_extra_alls_|-nop']['__run_num'] == 2
