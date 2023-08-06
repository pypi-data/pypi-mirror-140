from setuptools import setup, find_packages
import codecs
import os

# VERSION = '0.0.1'
DESCRIPTION = 'Topsis Nikhil'
LONG_DESCRIPTION = 'A package to find area of different figures'

# Setting up
setup(
    name="Topsis Nikhil",
    version=None,
    author="Developer Nikhil",
    author_email="nrawat_be19@thapar.edu",
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