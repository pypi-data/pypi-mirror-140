from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'Topsis_code'
LONG_DESCRIPTION = 'A Python package implementing Topsis method sed for multi-criteria decision analysis. Topsis stands for Technique for Order of Preference by Similarity to Ideal Solution'

# Setting up
setup(
    name="101903700-Topsis-code",
    version=VERSION,
    author="Bhavy Garg",
    author_email="bgarg1_be19@thapar.edu",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['topsis','Topsis'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)