# Import python libs
import os
import tempfile
import shutil

# Import rosso libs
import pop.hub
import idem.conf


def run_sls(sls, runtime='parallel'):
    '''
    Pass in an sls list and run it!
    '''
    name = 'test'
    hub = pop.hub.Hub()
    hub.pop.sub.add('idem.idem', init=True)
    hub.pop.sub.add('nest')
    hub.pop.sub.add(dyne_name='takara')
    hub.pop.sub.load_subdirs(hub.nest)
    hub.pop.sub.load_subdirs(hub.nest.nest)
    hub.pop.sub.load_subdirs(hub.nest.nest.again)
    render = 'jinja|yaml'
    cache_dir = tempfile.mkdtemp()
    sls_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sls')
    sls_sources = [f'file://{sls_dir}']
    hub.pop.loop.start(takara_sls(hub, name, sls_sources, render, runtime, ['states', 'nest'], cache_dir, sls))
    errors = hub.idem.RUNS[name]['errors']
    if errors:
        return errors
    ret = hub.idem.RUNS[name]['running']
    return ret

async def takara_sls(hub, name, sls_sources, render, runtime, subs, cache_dir, sls):
    unit_dir = tempfile.mkdtemp()
    data_dir = tempfile.mkdtemp()
    kw = {
            'unit': 'main',
            'seal_raw': 'foobar',
            'unit_dir': unit_dir,
            'data_dir': data_dir,
            'store': 'file',
            'cipher': 'fernet',
            'seal': 'passwd',
            'path': 'foo/bar/baz',
            'string': 'cheese',
            }
    await hub.takara.init.create(**kw)
    await hub.takara.init.set(**kw)
    await hub.idem.init.apply(name, sls_sources, render, runtime, subs, cache_dir, sls)
    shutil.rmtree(unit_dir)
    shutil.rmtree(data_dir)


def test_takara():
    ret = run_sls(['takara1'])
    assert ret['test_|-foo_|-foo_|-succeed_with_comment']['comment'] == 'cheese'
