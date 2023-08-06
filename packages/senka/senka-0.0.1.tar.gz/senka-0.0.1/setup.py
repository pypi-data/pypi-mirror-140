from setuptools import setup, find_packages

def _requires_from_file(filename):
    return open(filename).read().splitlines()

setup(
    name='senka',
    version='0.0.1',
    license='mit',
    description='making journal for transactions on blockchain',

    author='ca3-caaip',
    author_email='',
    url='https://github.com/ca3-caaip/senka',
    install_requires=_requires_from_file('requirements.txt'),
    extras_require={
        "test": ["pytest", "pytest-cov"]
    },
    package_dir={'': 'src'}
)
