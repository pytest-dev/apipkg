
def pytest_generate_tests(metafunc):
    multi = getattr(metafunc.function, 'multi', None)
    if multi is None:
        return
    assert len(multi.kwargs) == 1
    for name, l in multi.kwargs.items():
        for val in l:
            metafunc.addcall(funcargs={name: val})
