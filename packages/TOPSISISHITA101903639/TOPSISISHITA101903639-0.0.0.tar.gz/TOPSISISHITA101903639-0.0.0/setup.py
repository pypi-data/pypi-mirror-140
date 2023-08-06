from setuptools import setup, find_packages
import codecs
import os

DESCRIPTION ='TOPSIS_ISHITA_101903639'
LONG_DESCRIPTION ='Assignment 4 Topsis'
# Setting up
setup(
    name="TOPSISISHITA101903639",
    version=None,
    author="IshitaParmar",
    author_email="iparmar_be19@thapar.edu",
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
