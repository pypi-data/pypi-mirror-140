from setuptools import setup, find_packages
import codecs
import os

DESCRIPTION = 'Topsis Package By Sushant Saini Roll No. 1019171157'
LONG_DESCRIPTION = 'This package calculates the Topsis Score for the given data'

# Setting up
setup(
    name="Topsis Sushant",
    version=None,
    author="Sushant Saini",
    author_email="ssaini_be19@thapar.edu",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'Topsis'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)