from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Implementation of Conways Game of Life'

# Setting up
setup(
    name="uu-tora-gameoflife",
    version=VERSION,
    author="Tora Hävermark",
    author_email="<tora.havermark@icm.uu.se>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['numpy', 'matplotlib'],
   
)