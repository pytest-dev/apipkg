from setuptools import setup, find_packages


def readme():
    with open('README.rst') as fp:
        return fp.read()


def main():
    setup(
        name='apipkg',
        description='apipkg: namespace control and lazy-import mechanism',
        long_description=readme(),
        python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
        setup_requires=[
            'setuptools_scm',
            'setuptools>=30.3.0',  # introduced setup.cfg metadata
        ],
        use_scm_version={
            'write_to': 'src/apipkg/version.py'
        },
        url='https://github.com/pytest-dev/apipkg',
        license='MIT License',
        platforms=['unix', 'linux', 'osx', 'cygwin', 'win32'],
        author='holger krekel',
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
            # Specify the Python versions you support here.
            # In particular,  ensure that you indicate whether
            # you support Python 2, Python 3 or both.
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
        ],
        packages=find_packages('src'),
        package_dir={'': 'src'},
    )


if __name__ == '__main__':
    main()
