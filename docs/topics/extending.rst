==============
Extending Idem
==============

Extending Idem is simple, but it does require a few steps. To extend
Idem you need to create a new Idem plugin project using `POP`. Now don't run
away, this has been designed to be easy!

What is POP?
============

You don't need to understand the inner workings of Plugin Oriented Programming
or `pop` to extend Idem, just think about it as a system for writing and
managing plugins. Idem is all about plugins!

If you want to learn more about the details of `POP`, take a look at the docs.
It is powerful stuff and might change how you program forever:
https://pop.readthedocs.io

Lets Get Down to Business
=========================

Start by installing `idem`:

.. code-block:: bash

    pip install idem

This will download and install both `idem` and `pop`. Now start your project:

.. code-block:: bash

    mkdir stuff
    cd stuff
    pop-seed stuff

We just started the `stuff` project! That last line is critical, as you may have
noticed that it created a bunch of files and directories for you. This
is your first `POP` project! The `pop-seed` command has made everything you
need to get started, a nice `setup.py` file, as well as the structure used
by `POP` projects.

Next open up the `conf.py` file found in the newly created `stuff` directory.
This file contains the configuration that can be loaded into a `pop` project.
We want to start by telling `pop` that this project will be extending two plugin
subsystem in `idem`, they are called `states` and `exec`:

.. code-block:: python

    DYNE = {
        'states': ['states'],
        'exec': ['exec'],
        }

This tells `pop` to extend the plugin systems in `idem` called `states` and
`exec`.

Now you can add these two plugin types to `idem` by just making the directories
inside the new python package called `stuff`:

.. code-block:: bash

    cd stuff
    mkdir exec
    mkdir states

Now, `exec` is where to put the plugins that do the work and `states` is where
you put the plugins that enforce idempotent state.

Making Your First Idem State
============================

Make a new file under `states` called `trial.py`:

.. code-block:: python

    async def run(hub, name):
        '''
        Do a simple trial run
        '''
        return {
            'name': name,
            'result': True,
            'changes': {},
            'comment': 'It Ran!',
            }

For idem to run, `states` functions need to return a python dict that has 4 fields,
`name`, `result`, `changes`, and `comment`. These fields are used by Idem to not
only expose data to the user, but also to track the internal execution of the system.

Next install your new project. For `idem` to be able to use it your project, it
needs to be in the python path. There are a lot of convenient ways to manage the
installation and deployment of `POP` projects, but for now we can just use good
old `pip`:

.. code-block:: bash

    pip install -e <path to your project root>

Now you can execute a state with `idem`. As you will see, `pop` and `idem` are
all about hierarchical code. `Idem` runs code out of a directory, you need to
point `idem` to a directory that contains `sls` files. Go ahead and `cd` to
another directory and make a new `sls` directory.

.. code-block:: bash

    mkdir try
    cd try

Now open a file called `try.sls`:

.. code-block:: yaml

    try something:
        trial.run

Now from that directory run idem:

.. code-block:: bash

    idem --sls try

And you will see the results from running your trial.run state!
