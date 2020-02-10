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

This will download and install both `idem` and `pop`. Now you can start your
project by calling `pop-seed` to make the structure you need:

.. code-block:: bash

    pop-seed idem_tester -t v -d exec states

By passing `-t v` to `pop-seed` we are telling `pop-seed` that this is a
*Vertical App Merge* project. By passing `-d exec states` we are asking
`pop-seed` to add the 2 dynamic names `exec` and `states` to the project.

This will create a new project called `idem_tester` with everything you need
to get the ball rolling.


Making Your First Idem State
============================

In your new project there will be a directory called `idem_tester/states`, in
this directory add a file called `trial.py`:

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
