Welcome to apipkg !
-------------------

With apipkg you can control the exported namespace of a Python package and
greatly reduce the number of imports for your users.
It is a `small pure Python module`_ that works on CPython 3.7+,
Jython and PyPy. It cooperates well with Python's ``help()`` system,
custom importers (PEP302) and common command-line completion tools.

Usage is very simple: you can require 'apipkg' as a dependency or you
can copy paste the ~200 lines of code into your project.


Tutorial example
-------------------

Here is a simple ``mypkg`` package that exports one top-level object
and one nested namespace object:

.. code-block:: python

    # mypkg/__init__.py
    import apipkg

    apipkg.initpkg(
        __name__,
        {
            "SomeClass": "_mypkg.somemodule:SomeClass",
            "sub": {
                "OtherClass": "_mypkg.somemodule:OtherClass",
            },
        },
    )

The package is initialized with a dictionary as namespace.

You need to create a ``_mypkg`` package with a ``somemodule.py``
and ``othermodule.py`` containing the respective classes.
The ``_mypkg`` is not special - it's a completely
regular Python package.

Namespace dictionaries contain ``name: value`` mappings
where the value may be another namespace dictionary or
a string specifying an import location.  On accessing
an namespace attribute an import will be performed:

.. code-block:: pycon

    >>> import mypkg
    >>> mypkg.SomeClass  # '_mypkg.somemodule' gets imported now
    <class '_mypkg.somemodule.SomeClass'>
    >>> mypkg.sub
    <ApiModule 'mypkg.sub'>
    >>> mypkg.sub.OtherClass
    <class '_mypkg.othermodule.OtherClass'>

The ``mypkg.sub`` namespace and its entry are
loaded when they are accessed.   This means:

* lazy loading - only what is actually needed is ever loaded

* only the root "mypkg" ever needs to be imported to get
  access to the complete functionality

* the underlying modules are also accessible, for example:

.. code-block:: python

    from mypkg.sub import OtherClass


Including apipkg in your package
--------------------------------------

If you don't want to add an ``apipkg`` dependency to your package you
can copy the `apipkg.py`_ file somewhere to your own package,
for example ``_mypkg/apipkg.py`` in the above example.  You
then import the ``initpkg`` function from that new place and
are good to go.

.. _`small pure Python module`:
.. _`apipkg.py`: https://github.com/pytest-dev/apipkg/blob/master/src/apipkg/__init__.py

Feedback?
-----------------------

If you have questions you are welcome to

* join the **#pytest** channel on irc.libera.chat_
  (using an IRC client, via webchat_, or via Matrix_).
* create an issue on the bugtracker_

.. _irc.libera.chat: ircs://irc.libera.chat:6697/#pytest
.. _webchat: https://web.libera.chat/#pytest
.. _matrix: https://matrix.to/#/%23pytest:libera.chat
.. _bugtracker: https://github.com/pytest-dev/apipkg/issues
