'''
Author:  BDFD
Date: 2021-10-27 18:39:19
LastEditTime: 2022-03-01 18:05:14
LastEditors: BDFD
Description: In User Settings Edit
FilePath: \5.2-PyPi-WES_Calculation\setup.py
'''
from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

VERSION = '1.0.6'
DESCRIPTION = 'Write Your Package Description Here'
PACKAGE_NAME = 'WES_Calculation'

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author="BDFD",
    author_email="bdfd2005@gmail.com",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bdfd",
    project_urls={
        "Bug Tracker": "https://github.com/bdfd",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.6",
)
