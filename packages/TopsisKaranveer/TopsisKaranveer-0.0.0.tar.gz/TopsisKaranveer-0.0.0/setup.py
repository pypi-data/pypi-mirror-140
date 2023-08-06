from setuptools import setup, find_packages
import codecs
import os


DESCRIPTION = 'TopsisKARAN'
LONG_DESCRIPTION = 'package to find topsis'

# Setting up
setup(
    name="TopsisKaranveer",
    version=None,
    author="KaranveerSingh",
    author_email="ksingh10_be19@thapar.edu",
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