Welcome to apipkg!
------------------------

With apipkg you can control the exported namespace of a
python package and greatly reduce the number of imports for your users.
It is a `small pure python module`_ that works on virtually all Python
versions, including CPython2.3 to Python3.1, Jython and PyPy.  It co-operates
well with Python's ``help()`` system and common command line completion
tools.  Usage is very simple: you can require 'apipkg' as a dependency
or you can copy paste the <100 Lines of code into your project.

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
Namespace dictionaries contain ``name: value`` mappings 
where the value may be another namespace dictionary or
a string specifying an import location.  On accessing
the according attribute an import will be performed::

    >>> import mypkg
    >>> mypkg.path
    <ApiModule 'mypkg.path'>
    >>> mypkg.sub.Class1   # '_mypkg.somemodule' gets imported now
    <class _mypkg.somemodule.Class1 at 0xb7d428fc>
    >>> mypkg.sub.Class2   # '_mypkg.othermodule' gets imported now
    <class _mypkg.somemodule.Class1 at 0xb7d428fc>

The ``mypkg.sub`` namespace and both its classes are 
lazy loaded and no imports apart from the root 
``import mypkg`` is required. 

Including apipkg in your package
--------------------------------------

If you don't want to add a depdency to your package you 
can copy the `apipkg.py`_ somewhere to your own package, 
e.g. ``_mypkg/apipkg.py`` in the above example. 

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
