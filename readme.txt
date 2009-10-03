
Welcome to apipkg! 
------------------------

apipkg helps to make using your package API fun.  It provides
a simple function that allows you to declare a public 
namespace for your Python Package.  Users of your package can 
then only import and see the official namespace. 
Internally you can access all modules of your package independently
from the public namespace definition.  

* allow lazy on-demand loading of objects 

* greatly reduce the number of import statements in your program. 

* simple to use.  compatible to all CPython 2.3-3.1


Usage example 
-------------------

Suppose you have a ``mypkg`` and want to expose
objects for usage like this::

    # mypkg/__init__.py
    
    from apipkg import apipkg
    apipkg({
        'SomeClass': "somefile.py::SomeClass",
        'sub': {
            'manager': 'subdir/xfile.py',
        }
    })

:This will
lead your package to only expose the names of all
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

