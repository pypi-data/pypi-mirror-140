from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'Topsis Score Calculator'
LONG_DESCRIPTION = 'A package to find topsis score for a dataset'

# Setting up
setup(
    name="Topsis-Jai-101903156",
    version=VERSION,
    author="Jai Singh Batth",
    author_email="batthjaisingh2000@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'topsis', '101903156', 'JaiSinghBatth'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)