from setuptools import setup, find_packages
import codecs
import os
import pathlib

HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()
VERSION = '1.0.0'
DESCRIPTION = ' A Topsis package developed by ABHAY KANSAL'
# Setting up
setup(
    name="Topsis_AbhayKansal_101903685",
    version=VERSION,
    author="Abhay Kansal",
    author_email="<akansal1_be19@thapar.edu>",
    description=DESCRIPTION,
    long_description=README,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)