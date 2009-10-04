# mypkg/__init__.py

import apipkg
apipkg.init(__name__, {
    'SomeClass': 'somemodule::SomeClass',
    'sub': {
        'OtherClass': 'somemodule::OtherClass',
    }
})
