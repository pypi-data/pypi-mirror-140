# -*- coding: utf-8 -*-
"""
@Author: HuangJingCan
@Date: 2020-08-21 14:59:50
@LastEditTime: 2020-08-21 14:59:50
@LastEditors: HuangJingCan
@Description: 
"""
from __future__ import print_function
from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="seven_cloudapp_ndjyfs",
    version="1.0.1.9",
    author="seven",
    author_email="tech@gao7.com",
    description="seven_cloudapp_ndjyfs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="http://gitlab.tdtech.gao7.com/TaoBaoCloud/seven_cloudapp_ndjyfs.git",
    packages=find_packages(),
    install_requires=[
        "seven-cloudapp-frame>=1.0.11.117"
    ],
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires='~=3.4',
)