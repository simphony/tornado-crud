from setuptools import setup, find_packages

from tornadocrud import __version__

VERSION = __version__

with open("requirements.txt") as f:
    INSTALL_REQUIRES = f.readlines()

# main setup configuration class
setup(
    name='tornadocrud',
    version=VERSION,
    author='SimPhoNy Project',
    description='Tornado-based CRUD framework',
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
    )
