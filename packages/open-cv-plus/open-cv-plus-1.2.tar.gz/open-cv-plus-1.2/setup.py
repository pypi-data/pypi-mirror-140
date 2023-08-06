from setuptools import setup, find_packages
import codecs
import os

VERSION = '1.2'
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
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
    ]
)
