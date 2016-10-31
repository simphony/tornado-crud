from setuptools import setup, find_packages

from tornadowebapi._version import __version__

VERSION = __version__

# main setup configuration class
setup(
    name='tornadowebapi',
    version=VERSION,
    author='SimPhoNy Project',
    license='BSD',
    description='Tornado-based WebAPI framework',
    install_requires=[
        "setuptools>=21.0",
        "tornado>=4.3"
    ],
    packages=find_packages(),
    include_package_data=True,
    )
