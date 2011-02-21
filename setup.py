
from setuptools import setup

setup(
    name="mock_ext",
    version="0.2",
    description="Python mock library extensions",
    author="Matthew J. Morrison & JR",
    py_modules=('mock_ext',),
    package_dir={'': 'src'},
    install_requires = (
        'mock',
    ),
)
