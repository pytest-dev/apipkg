import re
from setuptools import setup, find_packages


def readme():
    with open('README.rst') as fp:
        return fp.read()


def main():
    setup(
        name='apipkg',
        description='apipkg: namespace control and lazy-import mechanism',
        long_description=readme(),
        setup_requires=[
            'setuptools_scm',
            'setuptools>=30.3.0',  # introduced setup.cfg metadata
        ],
        use_scm_version={
            'write_to': 'src/apipkg/version.py'
        },
        url='http://github.com/pytest-dev/apipkg',
        license='MIT License',
        platforms=['unix', 'linux', 'osx', 'cygwin', 'win32'],
        author='holger krekel',
        author_email='holger at merlinux.eu',
        maintainer="Ronny Pfannschmidt",
        maintainer_email="opensource@ronnypfannschmidt.de",
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: MacOS :: MacOS X',
            'Topic :: Software Development :: Libraries',
            'Programming Language :: Python'],
        packages=find_packages('src'),
        package_dir={'': 'src'},
    )

if __name__ == '__main__':
    main()
