import apipkg

apipkg.init(__name__,
    Cls = 'x::Cls',
    y = 'x::Cls2',
    sub1 = dict(
        sub2= {
            'hello': 'x::Cls3',
        }
    )
)

