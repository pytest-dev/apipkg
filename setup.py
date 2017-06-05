from setuptools import setup

def main():
    setup(
        setup_requires=[
            "setuptools_scm",
            "setuptools>=30.3.0",
        ],
        use_scm_version={'write_to': 'src/apipkg/version.py'},
    )

if __name__ == '__main__':
    main()
