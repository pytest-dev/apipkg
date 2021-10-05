"""
apipkg: control the exported namespace of a Python package.

see https://pypi.python.org/pypi/apipkg

(c) holger krekel, 2009 - MIT license
"""
import os
import sys
from types import ModuleType

# Prior to Python 3.7 threading support was optional
try:
    import threading
except ImportError:
    threading = None
else:
    import functools

from .version import version as __version__  # NOQA:F401


_PY2 = sys.version_info[0] == 2
_PRESERVED_MODULE_ATTRS = {
    "__file__",
    "__version__",
    "__loader__",
    "__path__",
    "__package__",
    "__doc__",
    "__spec__",
    "__dict__",
}


def _py_abspath(path):
    """
    special version of abspath
    that will leave paths from jython jars alone
    """
    if path.startswith("__pyclasspath__"):

        return path
    else:
        return os.path.abspath(path)


def distribution_version(name):
    """try to get the version of the named distribution,
    returs None on failure"""
    from pkg_resources import get_distribution, DistributionNotFound

    try:
        dist = get_distribution(name)
    except DistributionNotFound:
        pass
    else:
        return dist.version


def initpkg(pkgname, exportdefs, attr=None, eager=False):
    """ initialize given package from the export definitions. """
    attr = attr or {}
    mod = sys.modules.get(pkgname)

    if _PY2:
        mod = _initpkg_py2(mod, pkgname, exportdefs, attr=attr)
    else:
        mod = _initpkg_py3(mod, pkgname, exportdefs, attr=attr)

    # eagerload in bypthon to avoid their monkeypatching breaking packages
    if "bpython" in sys.modules or eager:
        for module in list(sys.modules.values()):
            if isinstance(module, ApiModule):
                module.__dict__

    return mod


def _initpkg_py2(mod, pkgname, exportdefs, attr=None):
    """Python 2 helper for initpkg.

    In Python 2 we can't update __class__ for an instance of types.Module, and
    imports are protected by the global import lock anyway, so it is safe for a
    module to replace itself during import.

    """
    d = {}
    f = getattr(mod, "__file__", None)
    if f:
        f = _py_abspath(f)
    d["__file__"] = f
    if hasattr(mod, "__version__"):
        d["__version__"] = mod.__version__
    if hasattr(mod, "__loader__"):
        d["__loader__"] = mod.__loader__
    if hasattr(mod, "__path__"):
        d["__path__"] = [_py_abspath(p) for p in mod.__path__]
    if hasattr(mod, "__package__"):
        d["__package__"] = mod.__package__
    if "__doc__" not in exportdefs and getattr(mod, "__doc__", None):
        d["__doc__"] = mod.__doc__
    d["__spec__"] = getattr(mod, "__spec__", None)
    d.update(attr)
    if hasattr(mod, "__dict__"):
        mod.__dict__.update(d)
    mod = ApiModule(pkgname, exportdefs, implprefix=pkgname, attr=d)
    sys.modules[pkgname] = mod
    return mod


def _initpkg_py3(mod, pkgname, exportdefs, attr=None):
    """Python 3 helper for initpkg.

    Python 3.3+ uses finer grained locking for imports, and checks sys.modules before
    acquiring the lock to avoid the overhead of the fine-grained locking. This
    introduces a race condition when a module is imported by multiple threads
    concurrently - some threads will see the initial module and some the replacement
    ApiModule. We avoid this by updating the existing module in-place.

    """
    if mod is None:
        d = {"__file__": None, "__spec__": None}
        d.update(attr)
        mod = ApiModule(pkgname, exportdefs, implprefix=pkgname, attr=d)
        sys.modules[pkgname] = mod
    else:
        f = getattr(mod, "__file__", None)
        if f:
            f = _py_abspath(f)
        mod.__file__ = f
        if hasattr(mod, "__path__"):
            mod.__path__ = [_py_abspath(p) for p in mod.__path__]
        if "__doc__" in exportdefs and hasattr(mod, "__doc__"):
            del mod.__doc__
        for name in dir(mod):
            if name not in _PRESERVED_MODULE_ATTRS:
                delattr(mod, name)

        # Updating class of existing module as per importlib.util.LazyLoader
        mod.__class__ = ApiModule
        mod.__init__(pkgname, exportdefs, implprefix=pkgname, attr=attr)
    return mod


def importobj(modpath, attrname):
    """imports a module, then resolves the attrname on it"""
    module = __import__(modpath, None, None, ["__doc__"])
    if not attrname:
        return module

    retval = module
    names = attrname.split(".")
    for x in names:
        retval = getattr(retval, x)
    return retval


def _synchronized(wrapped_function):
    """Decorator to synchronise __getattr__ calls."""
    if threading is None:
        return wrapped_function

    # Lock shared between all instances of ApiModule to avoid possible deadlocks
    lock = threading.RLock()

    @functools.wraps(wrapped_function)
    def synchronized_wrapper_function(*args, **kwargs):
        with lock:
            return wrapped_function(*args, **kwargs)

    return synchronized_wrapper_function


class ApiModule(ModuleType):
    """the magical lazy-loading module standing"""

    def __docget(self):
        try:
            return self.__doc
        except AttributeError:
            if "__doc__" in self.__map__:
                return self.__makeattr("__doc__")

    def __docset(self, value):
        self.__doc = value

    __doc__ = property(__docget, __docset)

    def __init__(self, name, importspec, implprefix=None, attr=None):
        self.__name__ = name
        self.__all__ = [x for x in importspec if x != "__onfirstaccess__"]
        self.__map__ = {}
        self.__implprefix__ = implprefix or name
        if attr:
            for name, val in attr.items():
                setattr(self, name, val)
        for name, importspec in importspec.items():
            if isinstance(importspec, dict):
                subname = "{}.{}".format(self.__name__, name)
                apimod = ApiModule(subname, importspec, implprefix)
                sys.modules[subname] = apimod
                setattr(self, name, apimod)
            else:
                parts = importspec.split(":")
                modpath = parts.pop(0)
                attrname = parts and parts[0] or ""
                if modpath[0] == ".":
                    modpath = implprefix + modpath

                if not attrname:
                    subname = "{}.{}".format(self.__name__, name)
                    apimod = AliasModule(subname, modpath)
                    sys.modules[subname] = apimod
                    if "." not in name:
                        setattr(self, name, apimod)
                else:
                    self.__map__[name] = (modpath, attrname)

    def __repr__(self):
        repr_list = []
        if hasattr(self, "__version__"):
            repr_list.append("version=" + repr(self.__version__))
        if hasattr(self, "__file__"):
            repr_list.append("from " + repr(self.__file__))
        if repr_list:
            return "<ApiModule {!r} {}>".format(self.__name__, " ".join(repr_list))
        return "<ApiModule {!r}>".format(self.__name__)

    @_synchronized
    def __makeattr(self, name, isgetattr=False):
        """lazily compute value for name or raise AttributeError if unknown."""
        target = None
        if "__onfirstaccess__" in self.__map__:
            target = self.__map__.pop("__onfirstaccess__")
            importobj(*target)()
        try:
            modpath, attrname = self.__map__[name]
        except KeyError:
            # __getattr__ is called when the attribute does not exist, but it may have
            # been set by the onfirstaccess call above. Infinite recursion is not
            # possible as __onfirstaccess__ is removed before the call (unless the call
            # adds __onfirstaccess__ to __map__ explicitly, which is not our problem)
            if target is not None and name != "__onfirstaccess__":
                return getattr(self, name)
            # Attribute may also have been set during a concurrent call to __getattr__
            # which executed after this call was already waiting on the lock. Check
            # for a recently set attribute while avoiding infinite recursion:
            # * Don't call __getattribute__ if __makeattr was called from a data
            #   descriptor such as the __doc__ or __dict__ properties, since data
            #   descriptors are called as part of object.__getattribute__
            # * Only call __getattribute__ if there is a possibility something has set
            #   the attribute we're looking for since __getattr__ was called
            if threading is not None and isgetattr:
                return super(ApiModule, self).__getattribute__(name)
            raise AttributeError(name)
        else:
            result = importobj(modpath, attrname)
            setattr(self, name, result)
            try:
                del self.__map__[name]
            except KeyError:
                pass  # in a recursive-import situation a double-del can happen
            return result

    def __getattr__(self, name):
        return self.__makeattr(name, isgetattr=True)

    @property
    def __dict__(self):
        # force all the content of the module
        # to be loaded when __dict__ is read
        dictdescr = ModuleType.__dict__["__dict__"]
        dict = dictdescr.__get__(self)
        if dict is not None:
            hasattr(self, "some")
            for name in self.__all__:
                try:
                    self.__makeattr(name)
                except AttributeError:
                    pass
        return dict


def AliasModule(modname, modpath, attrname=None):
    mod = []

    def getmod():
        if not mod:
            x = importobj(modpath, None)
            if attrname is not None:
                x = getattr(x, attrname)
            mod.append(x)
        return mod[0]

    x = modpath + ("." + attrname if attrname else "")
    repr_result = "<AliasModule {!r} for {!r}>".format(modname, x)

    class AliasModule(ModuleType):
        def __repr__(self):
            return repr_result

        def __getattribute__(self, name):
            try:
                return getattr(getmod(), name)
            except ImportError:
                if modpath == "pytest" and attrname is None:
                    # hack for pylibs py.test
                    return None
                else:
                    raise

        def __setattr__(self, name, value):
            setattr(getmod(), name, value)

        def __delattr__(self, name):
            delattr(getmod(), name)

    return AliasModule(str(modname))
