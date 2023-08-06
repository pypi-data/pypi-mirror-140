import codecs
from importlib_metadata import packages_distributions
from setuptools import setup, find_packages
import codecs
import os

VERSION='0.0.2'
DESCRIPTION = 'Topsis-Yashi-101903415'
LONG_DESCRIPTION='A package to perform TOPSIS'

#setting up
setup(
    name="TOPSIS-Yashi-101903415",
    version=VERSION,
    author="Yashi",
    author_email="yagarwal_be19@thapar.edu",
    description=DESCRIPTION,
    long_description_content_type='text/markdown',
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['pandas','math'],
    keywords=['python'] ,
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
