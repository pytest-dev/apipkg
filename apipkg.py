"""
apipkg: control the exported namespace of a python package.

see http://pypi.python.org/pypi/apipkg

(c) holger krekel, 2009 - MIT license
"""

import os, sys
from types import ModuleType

__version__ = "1.0a1"

def init(pkgname, exportdefs):
    """ initialize package namespace from the export definitions. """
    pkgmodule = sys.modules[pkgname]
    pkg = ApiPackage(pkgmodule)
    deferred_imports = []
    for name, importspec in exportdefs.items():
        assert '.' not in name
        if isinstance(importspec, dict):
            apimod = ApiModule(name, pkg, pkg.module, importspec, pkgname)
        else:
            deferred_imports.append((name, importspec))
    for name, importspec in deferred_imports:
        setattr(pkg.module, name, pkg.importobj(importspec))


class ApiPackage(object):
    """ Hold information about implementation modules. """
    def __init__(self, pkgmodule):
        self.module = pkgmodule
        assert not hasattr(pkgmodule, '__apipkg__')
        pkgmodule.__apipkg__ = self

        # make all raw original python modules available under pkgname.__.
        implname = pkgmodule.__name__ + "." + "__"
        self.implmodule = ModuleType(implname)
        self.implmodule.__name__ = implname
        self.implmodule.__file__ = pkgmodule.__file__
        self.implmodule.__path__ = pkgmodule.__path__
        pkgmodule.__ = self.implmodule
        sys.modules[implname] = self.implmodule
        # inhibit further direct filesystem imports through the package module
        del pkgmodule.__path__

    def importobj(self, importspec):
        """ return object specified by importspec."""
        modpath, attrname = importspec.split("::")
        importname = self.implmodule.__name__ + "." + modpath
        module = __import__(importname, None, None, ['__doc__'])
        return getattr(module, attrname)

    def getimportname(self, path):
        """ return a module name for usage with __import__(name). """
        path = str(path)
        if path.endswith('.py'):
            path = path[:-3]
            base = os.path.dirname(self.implmodule.__file__)
            if path.startswith(base):
                names = path[len(base)+1:].split(os.sep)
                dottedname = ".".join([self.implmodule.__name__] + names)
                return dottedname


class ApiModule(ModuleType):
    def __init__(self, name, pkg, parent, importspec, parentname):
        self.__name__ = name
        self.__apipkg__ = pkg
        self.__all__ = list(importspec)
        self.__map__ = {}
        setattr(parent, name, self)
        self.__myfullname__ = myfullname = parentname + "." + name
        sys.modules[myfullname] = self
        for name, importspec in importspec.items():
            if isinstance(importspec, dict):
                obj = ApiModule(name, pkg, self, importspec, myfullname)
            else:
                if not importspec.count("::") == 1:
                    raise ValueError("invalid importspec %r" % (importspec,))
                if name == '__doc__':
                    self.__doc__ = pkg.importobj(importspec)
                else:
                    self.__map__[name] = importspec

    def __repr__(self):
        return '<ApiModule %r>' % (self.__myfullname__,)

    def __getattr__(self, name):
        try:
            importspec = self.__map__.pop(name)
        except KeyError:
            raise AttributeError(name)
        else:
            result = self.__apipkg__.importobj(importspec)
        setattr(self, name, result)
        return result

    def __dict__(self):
        # force all the content of the module to be loaded when __dict__ is read
        dictdescr = ModuleType.__dict__['__dict__']
        dict = dictdescr.__get__(self)
        if dict is not None:
            for name in self.__all__:
                hasattr(self, name)  # force attribute load, ignore errors
        return dict
    __dict__ = property(__dict__)
