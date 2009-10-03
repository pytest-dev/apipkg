"""
initpkg: control exported namespace of a python package.

compatible to CPython 2.3 through to CPython 3.1, Jython, PyPy

(c) 2009 holger krekel, Holger Krekel
"""

import os, sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from initpkg import __version__

def main():
    setup(
        name='initpkg',
        description='initpkg: control exported namespace of a python package',
        long_description = __doc__,
        version= __version__,
        url='http://bitbucket.org/hpk42/initpkg',
        license='MIT License',
        platforms=['unix', 'linux', 'osx', 'cygwin', 'win32'],
        author='holger krekel and others',
        author_email='holger at merlinux.eu',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: POSIX',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: MacOS :: MacOS X',
            'Topic :: Software Development :: Libraries',
            'Programming Language :: Python'],
        py_modules=['initpkg']
    )

if __name__ == '__main__':
    main()
