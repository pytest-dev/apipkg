import types
import sys
import py
import apipkg
import subprocess
import pytest
#
# test support for importing modules
#
ModuleType = types.ModuleType


class TestRealModule:

    def setup_class(cls):
        cls.tmpdir = py.test.ensuretemp('test_apipkg')
        sys.path = [str(cls.tmpdir)] + sys.path
        pkgdir = cls.tmpdir.ensure('realtest', dir=1)

        tfile = pkgdir.join('__init__.py')
        tfile.write(py.code.Source("""
            import apipkg
            apipkg.initpkg(__name__, {
                'x': {
                    'module': {
                        '__doc__': '_xyz.testmodule:__doc__',
                        'mytest0': '_xyz.testmodule:mytest0',
                        'mytest1': '_xyz.testmodule:mytest1',
                        'MyTest':  '_xyz.testmodule:MyTest',
                    }
                }
            }
            )
        """))

        ipkgdir = cls.tmpdir.ensure("_xyz", dir=1)
        tfile = ipkgdir.join('testmodule.py')
        ipkgdir.ensure("__init__.py")
        tfile.write(py.code.Source("""
            'test module'
            from _xyz.othermodule import MyTest

            #__all__ = ['mytest0', 'mytest1', 'MyTest']

            def mytest0():
                pass
            def mytest1():
                pass
        """))
        ipkgdir.join("othermodule.py").write("class MyTest: pass")

    def setup_method(self, *args):
        # Unload the test modules before each test.
        module_names = ['realtest', 'realtest.x', 'realtest.x.module']
        for modname in module_names:
            if modname in sys.modules:
                del sys.modules[modname]

    def test_realmodule(self):
        import realtest.x
        assert 'realtest.x.module' in sys.modules
        assert getattr(realtest.x.module, 'mytest0')

    def test_realmodule_repr(self):
        import realtest.x
        assert "<ApiModule 'realtest.x'>" == repr(realtest.x)

    def test_realmodule_from(self):
        from realtest.x import module
        assert getattr(module, 'mytest1')

    def test_realmodule__all__(self):
        import realtest.x.module
        assert realtest.x.__all__ == ['module']
        assert len(realtest.x.module.__all__) == 4

    def test_realmodule_dict_import(self):
        "Test verifying that accessing the __dict__ invokes the import"
        import realtest.x.module
        moddict = realtest.x.module.__dict__
        assert 'mytest0' in moddict
        assert 'mytest1' in moddict
        assert 'MyTest' in moddict

    def test_realmodule___doc__(self):
        """test whether the __doc__ attribute is set properly from initpkg"""
        import realtest.x.module
        print (realtest.x.module.__map__)
        assert realtest.x.module.__doc__ == 'test module'


class TestScenarios:
    def test_relative_import(self, monkeypatch, tmpdir):
        pkgdir = tmpdir.mkdir("mymodule")
        pkgdir.join('__init__.py').write(py.code.Source("""
            import apipkg
            apipkg.initpkg(__name__, exportdefs={
                '__doc__': '.submod:maindoc',
                'x': '.submod:x',
                'y': {
                    'z': '.submod:x'
                },
            })
        """))
        pkgdir.join('submod.py').write("x=3\nmaindoc='hello'")
        monkeypatch.syspath_prepend(tmpdir)
        import mymodule
        assert isinstance(mymodule, apipkg.ApiModule)
        assert mymodule.x == 3
        assert mymodule.__doc__ == 'hello'
        assert mymodule.y.z == 3

    def test_recursive_import(self, monkeypatch, tmpdir):
        pkgdir = tmpdir.mkdir("recmodule")
        pkgdir.join('__init__.py').write(py.code.Source("""
            import apipkg
            apipkg.initpkg(__name__, exportdefs={
                'some': '.submod:someclass',
            })
        """))
        pkgdir.join('submod.py').write(py.code.Source("""
            import recmodule
            class someclass: pass
            print (recmodule.__dict__)
        """))
        monkeypatch.syspath_prepend(tmpdir)
        import recmodule
        assert isinstance(recmodule, apipkg.ApiModule)
        assert recmodule.some.__name__ == "someclass"

    def test_module_alias_import(self, monkeypatch, tmpdir):
        pkgdir = tmpdir.mkdir("aliasimport")
        pkgdir.join('__init__.py').write(py.code.Source("""
            import apipkg
            apipkg.initpkg(__name__, exportdefs={
                'some': 'os.path',
            })
        """))
        monkeypatch.syspath_prepend(tmpdir)
        import aliasimport
        for k, v in py.std.os.path.__dict__.items():
            assert getattr(aliasimport.some, k) == v

    def test_from_module_alias_import(self, monkeypatch, tmpdir):
        pkgdir = tmpdir.mkdir("fromaliasimport")
        pkgdir.join('__init__.py').write(py.code.Source("""
            import apipkg
            apipkg.initpkg(__name__, exportdefs={
                'some': 'os.path',
            })
        """))
        monkeypatch.syspath_prepend(tmpdir)
        from fromaliasimport.some import join
        assert join is py.std.os.path.join


def xtest_nested_absolute_imports():
    apipkg.ApiModule('email', {
        'message2': {
            'Message': 'email.message:Message',
            },
        })
    # nesting is supposed to put nested items into sys.modules
    assert 'email.message2' in sys.modules

# alternate ideas for specifying package + preliminary code
#


def test_parsenamespace():
    spec = """
        path.local    __.path.local::LocalPath
        path.svnwc    __.path.svnwc::WCCommandPath
        test.raises   __.test.outcome::raises
    """
    d = parsenamespace(spec)
    print (d)
    assert d == {
        'test': {'raises': '__.test.outcome::raises'},
        'path': {
            'svnwc': '__.path.svnwc::WCCommandPath',
            'local': '__.path.local::LocalPath'}
    }


def xtest_parsenamespace_errors():
    py.test.raises(ValueError, """
        parsenamespace('path.local xyz')
    """)
    py.test.raises(ValueError, """
        parsenamespace('x y z')
    """)


def parsenamespace(spec):
    ns = {}
    for line in spec.split("\n"):
        line = line.strip()
        if not line or line[0] == "#":
            continue
        parts = [x.strip() for x in line.split()]
        if len(parts) != 2:
            raise ValueError("Wrong format: %r" % (line,))
        apiname, spec = parts
        if not spec.startswith("__"):
            raise ValueError("%r does not start with __" % (spec,))
        apinames = apiname.split(".")
        cur = ns
        for name in apinames[:-1]:
            cur.setdefault(name, {})
            cur = cur[name]
        cur[apinames[-1]] = spec
    return ns


def test_initpkg_replaces_sysmodules(monkeypatch):
    mod = ModuleType('hello')
    monkeypatch.setitem(sys.modules, 'hello', mod)
    apipkg.initpkg('hello', {'x': 'os.path:abspath'})
    newmod = sys.modules['hello']
    assert newmod != mod
    assert newmod.x == py.std.os.path.abspath


def test_initpkg_transfers_attrs(monkeypatch):
    mod = ModuleType('hello')
    mod.__version__ = 10
    mod.__file__ = "hello.py"
    mod.__loader__ = "loader"
    mod.__doc__ = "this is the documentation"
    monkeypatch.setitem(sys.modules, 'hello', mod)
    apipkg.initpkg('hello', {})
    newmod = sys.modules['hello']
    assert newmod != mod
    assert newmod.__file__ == py.path.local(mod.__file__)
    assert newmod.__version__ == mod.__version__
    assert newmod.__loader__ == mod.__loader__
    assert newmod.__doc__ == mod.__doc__


def test_initpkg_nodoc(monkeypatch):
    mod = ModuleType('hello')
    mod.__file__ = "hello.py"
    monkeypatch.setitem(sys.modules, 'hello', mod)
    apipkg.initpkg('hello', {})
    newmod = sys.modules['hello']
    assert not newmod.__doc__


def test_initpkg_overwrite_doc(monkeypatch):
    hello = ModuleType('hello')
    hello.__doc__ = "this is the documentation"
    monkeypatch.setitem(sys.modules, 'hello', hello)
    apipkg.initpkg('hello', {"__doc__": "sys:__doc__"})
    newhello = sys.modules['hello']
    assert newhello != hello
    assert newhello.__doc__ == sys.__doc__


def test_initpkg_not_transfers_not_existing_attrs(monkeypatch):
    mod = ModuleType('hello')
    mod.__file__ = "hello.py"
    assert not hasattr(mod, '__path__')
    monkeypatch.setitem(sys.modules, 'hello', mod)
    apipkg.initpkg('hello', {})
    newmod = sys.modules['hello']
    assert newmod != mod
    assert newmod.__file__ == py.path.local(mod.__file__)
    assert not hasattr(newmod, '__path__')


def test_initpkg_not_changing_jython_paths(monkeypatch):
    mod = ModuleType('hello')
    mod.__file__ = '__pyclasspath__/test.py'
    mod.__path__ = ['__pyclasspath__/fun', 'ichange']
    monkeypatch.setitem(sys.modules, 'hello', mod)
    apipkg.initpkg('hello', {})
    newmod = sys.modules['hello']
    assert newmod != mod
    assert newmod.__file__.startswith('__pyclasspath__')
    unchanged, changed = newmod.__path__
    assert changed != 'ichange'
    assert unchanged.startswith('__pyclasspath__')


def test_initpkg_defaults(monkeypatch):
    mod = ModuleType('hello')
    monkeypatch.setitem(sys.modules, 'hello', mod)
    apipkg.initpkg('hello', {})
    newmod = sys.modules['hello']
    assert newmod.__file__ is None
    assert not hasattr(newmod, '__version__')


def test_name_attribute():
    api = apipkg.ApiModule('name_test', {
        'subpkg': {},
        })
    assert api.__name__ == 'name_test'
    assert api.subpkg.__name__ == 'name_test.subpkg'


def test_error_loading_one_element(monkeypatch, tmpdir):
    pkgdir = tmpdir.mkdir("errorloading1")
    pkgdir.join('__init__.py').write(py.code.Source("""
        import apipkg
        apipkg.initpkg(__name__, exportdefs={
            'x': '.notexists:x',
            'y': '.submod:y'
            },
        )
    """))
    pkgdir.join('submod.py').write("y=0")
    monkeypatch.syspath_prepend(tmpdir)
    import errorloading1
    assert isinstance(errorloading1, apipkg.ApiModule)
    assert errorloading1.y == 0
    py.test.raises(ImportError, 'errorloading1.x')
    py.test.raises(ImportError, 'errorloading1.x')


def test_onfirstaccess(tmpdir, monkeypatch):
    pkgdir = tmpdir.mkdir("firstaccess")
    pkgdir.join('__init__.py').write(py.code.Source("""
        import apipkg
        apipkg.initpkg(__name__, exportdefs={
            '__onfirstaccess__': '.submod:init',
            'l': '.submod:l',
            },
        )
    """))
    pkgdir.join('submod.py').write(py.code.Source("""
        l = []
        def init():
            l.append(1)
    """))
    monkeypatch.syspath_prepend(tmpdir)
    import firstaccess
    assert isinstance(firstaccess, apipkg.ApiModule)
    assert len(firstaccess.l) == 1
    assert len(firstaccess.l) == 1
    assert '__onfirstaccess__' not in firstaccess.__all__


@pytest.mark.parametrize('mode', ['attr', 'dict', 'onfirst'])
def test_onfirstaccess_setsnewattr(tmpdir, monkeypatch, mode):
    pkgname = 'mode_' + mode
    pkgdir = tmpdir.mkdir(pkgname)
    pkgdir.join('__init__.py').write(py.code.Source("""
        import apipkg
        apipkg.initpkg(__name__, exportdefs={
            '__onfirstaccess__': '.submod:init',
            },
        )
    """))
    pkgdir.join('submod.py').write(py.code.Source("""
        def init():
            import %s as pkg
            pkg.newattr = 42
    """ % pkgname))
    monkeypatch.syspath_prepend(tmpdir)
    mod = __import__(pkgname)
    assert isinstance(mod, apipkg.ApiModule)
    if mode == 'attr':
        assert mod.newattr == 42
    elif mode == "dict":
        print (list(mod.__dict__.keys()))
        assert 'newattr' in mod.__dict__
    elif mode == "onfirst":
        assert not hasattr(mod, '__onfirstaccess__')
        assert not hasattr(mod, '__onfirstaccess__')
    assert '__onfirstaccess__' not in vars(mod)


def test_bpython_getattr_override(tmpdir, monkeypatch):
    def patchgetattr(self, name):
        raise AttributeError(name)
    monkeypatch.setattr(apipkg.ApiModule, '__getattr__', patchgetattr)
    api = apipkg.ApiModule('bpy', {
        'abspath': 'os.path:abspath',
        })
    d = api.__dict__
    assert 'abspath' in d


def test_chdir_with_relative_imports_shouldnt_break_lazy_loading(tmpdir):
    tmpdir.join('apipkg.py').write(py.code.Source(apipkg))
    pkg = tmpdir.mkdir('pkg')
    tmpdir.mkdir('messy')
    pkg.join('__init__.py').write(py.code.Source("""
        import apipkg
        apipkg.initpkg(__name__, {
            'test': '.sub:test',
        })
    """))
    pkg.join('sub.py').write('def test(): pass')

    tmpdir.join('main.py').write(py.code.Source("""
        import os
        import sys
        sys.path.insert(0, '')
        import pkg
        import py
        print(py.__file__)
        py.builtin.print_(pkg.__path__, file=sys.stderr)
        py.builtin.print_(pkg.__file__, file=sys.stderr)
        py.builtin.print_(pkg, file=sys.stderr)
        os.chdir('messy')
        pkg.test()
        assert os.path.isabs(pkg.sub.__file__), pkg.sub.__file__
    """))
    res = subprocess.call(
        [py.std.sys.executable, 'main.py'],
        cwd=str(tmpdir),
    )
    assert res == 0


def test_dotted_name_lookup(tmpdir, monkeypatch):
    pkgdir = tmpdir.mkdir("dotted_name_lookup")
    pkgdir.join('__init__.py').write(py.code.Source("""
        import apipkg
        apipkg.initpkg(__name__, dict(abs='os:path.abspath'))
    """))
    monkeypatch.syspath_prepend(tmpdir)
    import dotted_name_lookup
    assert dotted_name_lookup.abs == py.std.os.path.abspath


def test_extra_attributes(tmpdir, monkeypatch):
    pkgdir = tmpdir.mkdir("extra_attributes")
    pkgdir.join('__init__.py').write(py.code.Source("""
        import apipkg
        apipkg.initpkg(__name__, dict(abs='os:path.abspath'), dict(foo='bar'))
    """))
    monkeypatch.syspath_prepend(tmpdir)
    import extra_attributes
    assert extra_attributes.foo == 'bar'


def test_aliasmodule_aliases_an_attribute():
    am = apipkg.AliasModule("mymod", "pprint", 'PrettyPrinter')
    r = repr(am)
    assert "<AliasModule 'mymod' for 'pprint.PrettyPrinter'>" == r
    assert am.format
    assert not hasattr(am, "lqkje")


def test_aliasmodule_aliases_unimportable():
    am = apipkg.AliasModule("mymod", "qlwkejqlwe", 'main')
    r = repr(am)
    assert "<AliasModule 'mymod' for 'qlwkejqlwe.main'>" == r
    assert am.qwe is None


def test_aliasmodule_unicode():
    am = apipkg.AliasModule(py.builtin._totext("mymod"), "pprint")
    assert am


def test_aliasmodule_repr():
    am = apipkg.AliasModule("mymod", "sys")
    r = repr(am)
    assert "<AliasModule 'mymod' for 'sys'>" == r
    am.version
    assert repr(am) == r


def test_aliasmodule_proxy_methods(tmpdir, monkeypatch):
    pkgdir = tmpdir
    pkgdir.join('aliasmodule_proxy.py').write(py.code.Source("""
        def doit():
            return 42
    """))

    pkgdir.join('my_aliasmodule_proxy.py').write(py.code.Source("""
        import apipkg
        apipkg.initpkg(__name__, dict(proxy='aliasmodule_proxy'))

        def doit():
            return 42
    """))

    monkeypatch.syspath_prepend(tmpdir)
    import aliasmodule_proxy as orig
    from my_aliasmodule_proxy import proxy

    doit = proxy.doit
    assert doit is orig.doit

    del proxy.doit
    py.test.raises(AttributeError, "orig.doit")

    proxy.doit = doit
    assert orig.doit is doit


def test_aliasmodule_nested_import_with_from(tmpdir, monkeypatch):
    import os
    pkgdir = tmpdir.mkdir("api1")
    pkgdir.ensure("__init__.py").write(py.std.textwrap.dedent("""
        import apipkg
        apipkg.initpkg(__name__, {
            'os2': 'api2',
            'os2.path': 'api2.path2',
            })
    """))
    tmpdir.join("api2.py").write(py.std.textwrap.dedent("""
        import os, sys
        from os import path
        sys.modules['api2.path2'] = path
        x = 3
    """))
    monkeypatch.syspath_prepend(tmpdir)
    from api1 import os2
    from api1.os2.path import abspath
    assert abspath == os.path.abspath
    # check that api1.os2 mirrors os.*
    assert os2.x == 3
    import api1
    assert 'os2.path' not in api1.__dict__


def test_initpkg_without_old_module():
    apipkg.initpkg("initpkg_without_old_module",
                   dict(modules="sys:modules"))
    from initpkg_without_old_module import modules
    assert modules is sys.modules


def test_get_distribution_version():
    assert apipkg.distribution_version('setuptools') is not None
    assert apipkg.distribution_version('email') is None


def test_eagerload_on_bython(monkeypatch):
    monkeypatch.delitem(sys.modules, 'bpython', raising=False)
    apipkg.initpkg(
        'apipkg.testmodule.example.lazy',
        {'test': 'apipkg.does_not_exist'})
    monkeypatch.setitem(sys.modules, 'bpython', True)
    with pytest.raises(ImportError):
        apipkg.initpkg(
            'apipkg.testmodule.example.lazy',
            {'test': 'apipkg.does_not_exist'})


def test_autoset_version_attribute_from_distribution(monkeypatch):
    monkeypatch.setitem(sys.modules, 'setuptools', None)
    apipkg.initpkg('setuptools', {})

    assert sys.modules['setuptools'].__version__
