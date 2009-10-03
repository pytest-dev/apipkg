import types
import sys
import py

from initpkg import ApiModule
glob = []
class MyModule(ApiModule):
    def __init__(self, *args):
        glob.append(self.__dict__)
        assert isinstance(glob[-1], (dict, type(None)))
        ApiModule.__init__(self, *args)

def test_early__dict__access():
    mymod = MyModule("whatever", "myname")
    assert isinstance(mymod.__dict__, dict)

def test_resolve_attrerror():
    extpyish = "./initpkg.py", "hello"
    excinfo = py.test.raises(AttributeError, "py.__pkg__._resolve(extpyish)")
    s = str(excinfo.value)
    assert s.find(extpyish[0]) != -1
    assert s.find(extpyish[1]) != -1

def test_virtual_module_identity():
    from py import path as path1
    from py import path as path2
    assert path1 is path2
    from py.path import local as local1
    from py.path import local as local2
    assert local1 is local2

def test_importall():
    base = py.path.local(py.__file__).dirpath()
    nodirs = [
        base.join('test', 'testing', 'data'),
        base.join('test', 'web'),
        base.join('path', 'gateway',),
        base.join('doc',),
        base.join('rest', 'directive.py'),
        base.join('test', 'testing', 'import_test'),
        base.join('bin'),
        base.join('code', 'oldmagic.py'),
        base.join('execnet', 'script'),
        base.join('compat', 'testing'),
    ]
    if sys.version_info >= (3,0):
        nodirs.append(base.join('code', '_assertionold.py'))
    else:
        nodirs.append(base.join('code', '_assertionnew.py'))

    def recurse(p):
        return p.check(dotfile=0) and p.basename != "attic"

    for p in base.visit('*.py', recurse):
        if p.basename == '__init__.py':
            continue
        relpath = p.new(ext='').relto(base)
        if base.sep in relpath: # not py/*.py itself
            for x in nodirs:
                if p == x or p.relto(x):
                    break
            else:
                relpath = relpath.replace(base.sep, '.')
                modpath = 'py.__.%s' % relpath
                check_import(modpath)

def check_import(modpath):
    py.builtin.print_("checking import", modpath)
    assert __import__(modpath)

#
# test support for importing modules
#

class TestRealModule:

    def setup_class(cls):
        cls.tmpdir = py.test.ensuretemp('test_initpkg')
        sys.path = [str(cls.tmpdir)] + sys.path
        pkgdir = cls.tmpdir.ensure('realtest', dir=1)

        tfile = pkgdir.join('__init__.py')
        tfile.write(py.code.Source("""
            from initpkg import initpkg
            initpkg('realtest', {
                'x.module.__doc__': ('./testmodule.py', '__doc__'),
                'x.module.mytest0': ('testmodule.py', 'mytest0',),
                'x.module.mytest1': ('./testmodule.py', 'mytest1',),
                'x.module.MyTest': ('./testmodule.py', 'MyTest',),
            })
        """))

        tfile = pkgdir.join('testmodule.py')
        tfile.write(py.code.Source("""
            'test module'

            __all__ = ['mytest0', 'mytest1', 'MyTest']

            def mytest0():
                pass
            def mytest1():
                pass
            class MyTest:
                pass

        """))

        import realtest # need to mimic what a user would do
        #py.initpkg('realtest', {
        #    'module': ('./testmodule.py', None)
        #})

    def setup_method(self, *args):
        """Unload the test modules before each test."""
        module_names = ['realtest', 'realtest.x', 'realtest.x.module']
        for modname in module_names:
            if modname in sys.modules:
                del sys.modules[modname]

    def test_realmodule(self):
        import realtest.x.module
        assert 'realtest.x.module' in sys.modules
        assert getattr(realtest.x.module, 'mytest0')

    def test_realmodule_from(self):
        from realtest.x import module
        assert getattr(module, 'mytest1')

    def test_realmodule__all__(self):
        import realtest.x.module
        assert realtest.x.__all__ == ['module']
        assert len(realtest.x.module.__all__) == 3

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
        assert realtest.x.module.__doc__ == 'test module'

    def test_realmodule_getimportname(self):
        import realtest
        pkg = realtest.__pkg__
        p = py.path.local(realtest.__file__).dirpath('testmodule.py')
        s = pkg.getimportname(p)
        assert s == "realtest.__.testmodule"
        s = pkg.getimportname(str(p))
        assert s == "realtest.__.testmodule"
        s = pkg.getimportname(p.dirpath().dirpath())
