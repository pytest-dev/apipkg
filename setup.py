"""
apipkg: namespace control and lazy-import mechanism.

compatible to CPython 2.3 through to CPython 3.1, Jython, PyPy

(c) 2009 holger krekel, Holger Krekel
"""

import os, sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from apipkg import __version__

def main():
    setup(
        name='apipkg',
        description=
        'apipkg: namespace control and lazy-import mechanism',
        long_description = open('readme.txt').read(),
        version= __version__,
        url='http://bitbucket.org/hpk42/apipkg',
        license='MIT License',
        platforms=['unix', 'linux', 'osx', 'cygwin', 'win32'],
        author='holger krekel',
        author_email='holger at merlinux.eu',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: MacOS :: MacOS X',
            'Topic :: Software Development :: Libraries',
            'Programming Language :: Python'],
        py_modules=['apipkg']
    )

if __name__ == '__main__':
    main()
