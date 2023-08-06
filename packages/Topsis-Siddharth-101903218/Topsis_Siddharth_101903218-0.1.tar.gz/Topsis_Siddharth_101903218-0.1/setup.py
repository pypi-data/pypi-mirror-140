from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.1'
DESCRIPTION = 'Topsis Package'
#LONG_DESCRIPTION = 'A package created for program 2 of Assignment-4 that calculates Topsis Score and rank.'

# Setting up
setup(
    name="Topsis_Siddharth_101903218",
    packages = ['Topsis_Siddharth_101903218'],
    version=VERSION,
    author="Siddharth Juyal",
    author_email="<sjuyal_be19@thapar.edu>",
    description=DESCRIPTION,
    #long_description_content_type="text/markdown",
    #long_description=long_description,
    # packages=find_packages(),
    install_requires=['pandas', 'numpy'],
    keywords=['python', 'topsis', 'score', 'rank'],
    classifiers=[
        'Development Status :: 3 - Alpha',     
        'Intended Audience :: Developers',     
        'License :: OSI Approved :: MIT License',   
        'Programming Language :: Python :: 3',      
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)