======================
Encrypted Data Storage
======================

.. note::

    Takara is very new and this interface is going to evolve over time. The
    basic interface presented here will not likely change, but many more
    options are planned

It is very common that you need to store credentials on disk. Idem makes this
easy via the `takara` system. Using `takara` you can store encrypted data
securely and then call it up from within your `sls` files!

Using `takara` from within Idem is easy! First take a look at the `takara`
docs on how to set up a secret storage unit, and how to set and get secrets
from that unit.

Now make a new `sls` file that calls `takara.init.get` from the hub:

.. code-block:: yaml

    takara_test:
      test.succeed_with_comment:
        - comment: {{ hub.takara.init.get(unit='main', path='foo/bar/baz') }}

Now you can run `idem` with the `--takara-unit` or `-u` option to define what
unit to unseal for the use of this `idem` run:

.. code-block:: bash

    idem -u main --sls test

Idem will prompt you to unseal the `takara` store, making the secrets in the named
unit available to the sls files as they run.
