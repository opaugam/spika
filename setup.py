import sys
import ez_setup

ez_setup.use_setuptools()

from spika import __version__
from setuptools import setup, find_packages

if sys.version_info < (2, 7):
    raise NotImplementedError("python 2.7 or higher required")

setup(
    name='spika',
    version=__version__,
    packages=find_packages(),
    author='olivier paugam',
    author_email='olivier.paugam@autodesk.com',
    license='Apache License, Version 2.0',
    description='simple subprocess command protocol over stdin/stdout'
)
