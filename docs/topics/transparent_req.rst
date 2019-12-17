======================
Transparent Requisites
======================

Transparent requisites is a powerful feature inside of Idem. It
allows requisites to be defines on a function by function basis. This
means that a given function can always requires any instance of
another function, in the background. This makes it easy for
state authors to ensure that executions are always executed in the
correct order without the end user needing to define those orders.

It is easy to do, at the top of your system module just define the
`TREQ` dict, this dict defines what functions will require what
other functions:

.. code-block:: python

    TREQ = {
            'treq': {
                'require': [
                    'test.nop',
                    ]
                },
            }

This stanza will look for the function named `treq` inside of the module
that it is deinfed in, then it will add `require : - test.nop` for every
instance found of `test.nop` in the current run. If test.nop is never used,
then no requisites are set. Any requisite can be used, and multiple requisites
can be used.
