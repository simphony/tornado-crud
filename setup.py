from setuptools import setup, find_packages

from tornado_crud import __version__

VERSION = __version__

with open("requirements.txt") as f:
    INSTALL_REQUIRES = f.readlines()

# main setup configuration class
setup(
    name='tornado_crud',
    version=VERSION,
    author='SimPhoNy Project',
    description='Remote application manager sub-executable',
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
    )
