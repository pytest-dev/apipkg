import pathlib

import apipkg

LOCAL_APIPKG = pathlib.Path(__file__).parent.joinpath("src/apipkg/__init__.py")
INSTALL_TYPE = "editable" if apipkg.__file__ == LOCAL_APIPKG else "full"


def pytest_report_header(startdir):
    return "apipkg {install_type} install version={version}".format(
        install_type=INSTALL_TYPE, version=apipkg.__version__
    )
