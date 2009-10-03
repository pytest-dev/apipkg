import types
import sys
import py

#
# test support for importing modules
#

class TestRealModule:

    def setup_class(cls):
        cls.tmpdir = py.test.ensuretemp('test_apipkg')
        sys.path = [str(cls.tmpdir)] + sys.path
        pkgdir = cls.tmpdir.ensure('realtest', dir=1)

        tfile = pkgdir.join('__init__.py')
        tfile.write(py.code.Source("""
            import apipkg
            apipkg.init('realtest', x={
                'module': {
                    '__doc__': 'testmodule::__doc__',
                    'mytest0': 'testmodule::mytest0',
                    'mytest1': 'testmodule::mytest1',
                    'MyTest': 'testmodule::MyTest',
            }})
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
        import realtest.x
        assert 'realtest.x.module' in sys.modules
        assert getattr(realtest.x.module, 'mytest0')

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

    def test_realmodule_getimportname(self):
        import realtest
        pkg = realtest.__apipkg__
        p = py.path.local(realtest.__file__).dirpath('testmodule.py')
        s = pkg.getimportname(p)
        assert s == "realtest.__.testmodule"
        s = pkg.getimportname(str(p))
        assert s == "realtest.__.testmodule"
        s = pkg.getimportname(p.dirpath().dirpath())
