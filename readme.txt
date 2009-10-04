
Welcome to apipkg!
------------------------

With apipkg you can control the exported namespace of a python package
and greatly reduce the number of imports for your users.  It is a
small pure python module that works on virtually all Python versions,
including CPython2.3 to 3.1, Jython and PyPy.

Tutorial example
-------------------

Let's write a simple ``mypkg`` package and expose one object
in a sub namespace.  First the ``__init__`` file::

    # mypkg/__init__.py
    import apipkg
    apipkg.init(__name__, {
        'sub': {
            'SomeClass': 'somemodule::SomeClass',
        }
    })

Exported namespaces are simple dictionaries where values can be
dictionaries (sub namespaces) or a string specifying which module
to import and which attribute to return. To make the
example work we thus need to create a ``somemodule.py`` like this::

    # mypkg/somemodule.py
    class SomeClass
        pass

Now we are ready to go and can import our package and access
the namespaces and class.

    >>> import mypkg
    >>> mypkg.sub
    <ApiModule 'mypkg.sub'>
    >>> mypkg.sub.SomeClass    # 'somemodule.py' gets imported now
    <class mypkg.__.somemodule.SomeClass at 0xb7d428fc>

The double underscore in ``mypkg.__`` is the raw import viewmodule implementation  gives you a hint prefix indicates an "implementation" module.

that 'somemodule.SomeClass' the that 'somemodulethe actual "implementation" module.
Here you'll notice something important.  ``apipkg`` made it
so that your class


This means


    mypkg.SomeClass        # will be loaded from somemodule.py
    mypkg.sub.OtherClass   # lazy-loaded from somemodule.py

Note that you do not need to ``import mypkg.sub`` to access it.
But of course you can write down an import like this::

    from mypkg.sub import OtherClass

In order for the example to work you need to have referenced
implementation module


Let's go to the Python console we can type::

    >>> import mypkg
    >>> mypkg.SomeClass
    <class mypkg.__.somemodule.SomeClass at 0xb7dcd8cc>



This will lead your package to only expose the names of all
your implementation files that you explicitely
specify.  In the above example 'name1' will
become a Module instance where 'name2' is
bound in its namespace to the 'name' object
in the relative './path/to/file.py' python module.
Note that you can also use a '.c' file in which
case it will be compiled via distutils-facilities
on the fly.


It does this by providing a function that you can import
and call at package `__init__.py`` time.  This function
instruments Python's import system to make all python
modules of the package accessible via a `__` import.


and adds
using your library classes a pleasure. provide
a clean exported helps you to ``pkginit(exportdefs)``
which you

compatibility: CPython 2.4 till 3.1

