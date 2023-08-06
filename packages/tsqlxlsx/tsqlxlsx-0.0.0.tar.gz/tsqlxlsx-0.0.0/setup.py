from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.0'
DESCRIPTION = 'Pip package for pushing files csv, xlsx to sql server'
LONG_DESCRIPTION = 'Pip package for pushing files to sql server.'

# Setting up
setup(
    name="tsqlxlsx",
    version=VERSION,
    author="bgovi (Brandon Govindarajoo)",
    author_email="<bgovi@umich.edu>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(include=['tsqlxlsx', 'tsqlxlsx.*']),
    install_requires=['pandas', 'pyodbc'],
    keywords=['python', 'tsql', 'xlsx'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)