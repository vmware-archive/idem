CLI_CONFIG = {
    'sls_sources': {
        'default': ['file://'],
        'nargs': '*',
        'help': 'list off the sources that should be used for gathering sls files and data',
        },
    'cache_dir': {
        'default': '/var/cache/idem',
        'help': 'The location to use for the cache directory',
        },
    'root_dir': {
        'default': '/',
        'help': 'The root directory to run idem from. By default it will be "/", or in the case of running as non-root it is set to <HOMEDIR>/.idem',
        },
    'render': {
        'default': 'yaml',
        'help': 'The render pipe to use, this allows for the language to be specified',
        },
    'runtime': {
        'default': 'parallel',
        'help': 'Select which execution runtime to use',
        },
    'sls': {
        'default': [],
        'nargs': '*',
        'help': 'A space delimited list of sls refs to execute',
        },
    }
CONFIG = {}
GLOBAL = {}
SUBS = {}
