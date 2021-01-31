# mypkg/__init__.py
import apipkg

apipkg.initpkg(
    __name__,
    {
        "SomeClass": "_mypkg.somemodule:SomeClass",
        "sub": {
            "OtherClass": "_mypkg.somemodule:OtherClass",
        },
    },
)
