"""
initpkg: control the exported namespace of your package.

(c) holger krekel, 2009 - MIT license
"""

import sys
import os
from types import ModuleType

__version__ = "1.0a1"

class Package(object):
    def __init__(self, name, exportdefs, metainfo):
        pkgmodule = sys.modules[name]
        assert pkgmodule.__name__ == name
        self.name = name
        self.exportdefs = exportdefs
        self.module = pkgmodule
        assert not hasattr(pkgmodule, '__pkg__')
        pkgmodule.__pkg__ = self

        # make internal python modules available under pkgname.__.
        # instead of pkgname. directly.
        implname = name + '.' + '__'
        self.implmodule = ModuleType(implname)
        self.implmodule.__name__ = implname
        self.implmodule.__file__ = os.path.abspath(pkgmodule.__file__)
        self.implmodule.__path__ = [os.path.abspath(p)
                                    for p in pkgmodule.__path__]
        pkgmodule.__ = self.implmodule
        setmodule(implname, self.implmodule)
        # inhibit further direct filesystem imports through the package module
        del pkgmodule.__path__

        # set metainfo
        for name, value in metainfo.items():
            setattr(self, name, value)
        version = metainfo.get('version', None)
        if version:
            pkgmodule.__version__ = version

    def importobj(self, importspec):
        """ return object specified by importspec."""
        fspath, modpath = importspec
        implmodule = self.importfile(fspath[:-3])
        if not isinstance(modpath, str): # export the entire module
            return implmodule

        current = implmodule
        for x in modpath.split('.'):
            try:
                current = getattr(current, x)
            except AttributeError:
                raise AttributeError("resolving %r failed: %s" %(
                                     importspec, x))
        return current

    def getimportname(self, path):
        """ return module name useable with __import__(name). """
        path = str(path)
        if path.endswith('.py'):
            path = path[:-3]
            base = os.path.dirname(self.implmodule.__file__)
            if path.startswith(base):
                names = path[len(base)+1:].split(os.sep)
                dottedname = ".".join([self.implmodule.__name__] + names)
                return dottedname

    def importfile(self, relfile):
        """ import module pointed to by relfile. """
        parts = [x.strip() for x in relfile.split('/') if x and x!= '.']
        modpath = ".".join([self.implmodule.__name__] + parts)
        return __import__(modpath, None, None, ['__doc__'])

def setmodule(modpath, module):
    sys.modules[modpath] = module

# ---------------------------------------------------
# API Module Object
# ---------------------------------------------------

class ApiModule(ModuleType):
    def __init__(self, pkg, name):
        self.__map__ = {}
        self.__pkg__ = pkg
        self.__name__ = name
        self.__all__ = []

    def __repr__(self):
        return '<ApiModule %r>' % (self.__name__,)

    def __getattr__(self, name):
        try:
            importspec = self.__map__.pop(name)
        except KeyError:
            __tracebackhide__ = True
            raise AttributeError(name)
        else:
            result = self.__pkg__.importobj(importspec)
        setattr(self, name, result)
        #self._fixinspection(result, name)
        return result

    def __setattr__(self, name, value):
        super(ApiModule, self).__setattr__(name, value)
        try:
            del self.__map__[name]
        except KeyError:
            pass

    def __dict__(self):
        # force all the content of the module to be loaded when __dict__ is read
        dictdescr = ModuleType.__dict__['__dict__']
        dict = dictdescr.__get__(self)
        if dict is not None:
            for name in list(self.__all__):
                hasattr(self, name)  # force attribute load, ignore errors
        return dict
    __dict__ = property(__dict__)

# ---------------------------------------------------
# Bootstrap Virtual Module Hierarchy
# ---------------------------------------------------

def initpkg(pkgname, exportdefs, **kw):
    pkg = Package(pkgname, exportdefs, kw)
    seen = { pkgname : pkg.module }
    deferred_imports = []

    for pypath, importspec in pkg.exportdefs.items():
        pyparts = pypath.split('.')
        modparts = pyparts[:]
        lastmodpart = modparts.pop()
        current = pkgname

        # ensure modules
        for name in modparts:
            previous = current
            current += '.' + name
            if current not in seen:
                seen[current] = mod = ApiModule(pkg, current)
                setattr(seen[previous], name, mod)
                if isinstance(seen[previous], ApiModule):
                    seen[previous].__all__.append(name)
                setmodule(current, mod)

        mod = seen[current]
        if not hasattr(mod, '__map__'):
            assert mod is pkg.module, \
                   "only root modules are allowed to be non-lazy. "
            deferred_imports.append((mod, pyparts[-1], importspec))
        else:
            if importspec[1] == '__doc__':
                mod.__doc__ = pkg.importobj(importspec)
            else:
                mod.__map__[lastmodpart] = importspec
                mod.__all__.append(lastmodpart)

    for mod, pypart, importspec in deferred_imports:
        setattr(mod, pypart, pkg.importobj(importspec))
