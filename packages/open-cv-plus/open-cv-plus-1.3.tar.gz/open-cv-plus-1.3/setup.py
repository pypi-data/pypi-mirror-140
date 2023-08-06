from setuptools import setup, find_packages
import codecs
import os

VERSION = '1.3'
DESCRIPTION = 'OpenCV Plus'
LONG_DESCRIPTION = 'A package that gives you extra OpenCV functions.'

# Setting up
setup(
    name="open-cv-plus",
    version=VERSION,
    author="TheCoder1001 (Atharv Baluja)",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    keywords=['python', 'opencv'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
    ]
)
