from setuptools import setup, find_packages
import codecs
import os

#VERSION = '0.0.1'
DESCRIPTION ='TOPSISRAGHAVAN101903636'
LONG_DESCRIPTION ='Assignment 4 Topsis'
# Setting up
setup(
    name="TOPSISRAGHAVAN101903636",
    version=None,
    author="RaghavanMarwaha",
    author_email="rmarwaha_be19@thapar.edu",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'topsis'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
