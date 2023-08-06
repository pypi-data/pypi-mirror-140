from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.2'
DESCRIPTION = 'Topsis Package'
#LONG_DESCRIPTION = 'A package created for program 2 of Assignment-4 that calculates Topsis Score and rank.'

# Setting up
setup(
    name="Topsis-Siddharth-101903218",
    version=VERSION,
    author="Siddharth Juyal",
    author_email="<sjuyal_be19@thapar.edu>",
    description=DESCRIPTION,
    #long_description_content_type="text/markdown",
    #long_description=long_description,
    packages=find_packages(),
    install_requires=['pandas', 'numpy'],
    keywords=['python', 'topsis', 'score', 'rank'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)