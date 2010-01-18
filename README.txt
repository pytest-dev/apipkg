Welcome to apipkg!
------------------------

With apipkg you can control the exported namespace of a
python package and greatly reduce the number of imports for your users.
It is a `small pure python module`_ that works on virtually all Python
versions, including CPython2.3 to Python3.1, Jython and PyPy.  It co-operates
well with Python's ``help()`` system, custom importers (PEP302) and common 
command line completion tools.  

Usage is very simple: you can require 'apipkg' as a dependency or you
can copy paste the <100 Lines of code into your project.

Tutorial example
-------------------

Here is a simple ``mypkg`` package that specifies one namespace
and exports two objects imported from different modules::

    # mypkg/__init__.py
    import apipkg
    apipkg.initpkg(__name__, {
        'path': {
            'Class1': "_mypkg.somemodule:Class1",
            'Class2': "_mypkg.othermodule:Class2",
        }
    }

The package is initialized with a dictionary as namespace. 

You need to create a ``_mypkg`` package with a ``somemodule.py`` 
and ``othermodule.py`` containing the respective classes.
The ``_mypkg`` is not special - it's a completely 
regular python package. 

Namespace dictionaries contain ``name: value`` mappings 
where the value may be another namespace dictionary or
a string specifying an import location.  On accessing
an namespace attribute an import will be performed::

    >>> import mypkg
    >>> mypkg.path
    <ApiModule 'mypkg.path'>
    >>> mypkg.sub.Class1   # '_mypkg.somemodule' gets imported now
    <class _mypkg.somemodule.Class1 at 0xb7d428fc>
    >>> mypkg.sub.Class2   # '_mypkg.othermodule' gets imported now
    <class _mypkg.somemodule.Class1 at 0xb7d428fc>

The ``mypkg.sub`` namespace and both its classes are 
lazy loaded.  Note that **no imports apart from the root 
'import mypkg' is required**. This means that whoever
uses your Api only ever needs this one import.  Of course
you can still use the import statement like so::

    from mypkg.sub import Class1


Including apipkg in your package
--------------------------------------

If you don't want to add an ``apipkg`` dependency to your package you 
can copy the `apipkg.py`_ file somewhere to your own package, 
for example ``_mypkg/apipkg.py`` in the above example.  You
then import the ``initpkg`` function from that new place and
are good to go. 

.. _`small pure python module`:
.. _`apipkg.py`: http://bitbucket.org/hpk42/apipkg/src/tip/apipkg.py

Feedback? 
-----------------------

If you have questions you are welcome to 

* join the #pylib channel on irc.freenode.net 
* subscribe to the http://codespeak.net/mailman/listinfo/py-dev list. 
* create an issue on http://bitbucket.org/hpk42/apipkg/issues

have fun, 
holger krekel
