
Usage example:

    from py.initpkg import initpkg
    initpkg(__name__, exportdefs={
        'name1.name2' : ('path/to/file.py', 'name')
        ...
    })

into your package's __init__.py file.  This will
lead your package to only expose the names of all
your implementation files that you explicitely
specify.  In the above example 'name1' will
become a Module instance where 'name2' is
bound in its namespace to the 'name' object
in the relative './path/to/file.py' python module.
Note that you can also use a '.c' file in which
case it will be compiled via distutils-facilities
on the fly.
