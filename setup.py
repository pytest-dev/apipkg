import re
from setuptools import setup


def get_version():
    VERSION_RE = re.compile("__version__ = \'(.*)\'", re.M)
    with open('apipkg.py') as fp:
        return VERSION_RE.search(fp.read()).group(1)


def main():
    setup(
        name='apipkg',
        description='apipkg: namespace control and lazy-import mechanism',
        long_description=open('README.txt').read(),
        version=get_version(),
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
        py_modules=['apipkg'],
    )

if __name__ == '__main__':
    main()
