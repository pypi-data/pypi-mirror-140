from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.9'
DESCRIPTION = 'Calculating the TOPSIS scores for various criterions'
# Setting up
setup(
    name="TOPSIS-Prakhar-101903098",
    version=VERSION,
    author="Prakhar Bhateja",
    author_email="<pbhateja_be19@thapar.edu>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['pandas','numpy','sklearn'],
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