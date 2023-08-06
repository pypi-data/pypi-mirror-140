#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/8 10:36 AM
# @Author  : chenDing
from setuptools import setup, find_packages

import ssl

ssl._create_default_https_context = ssl._create_unverified_context
with open("readme.md", "r") as fh:
    long_description = fh.read()

setup(
    name='mlogs',
    version='0.1.3',
    description='loguru packaging log tools',
    packages=find_packages(),
    author='Caturbhuja',
    author_email='caturbhuja@foxmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='',
    install_requires=[
        'loguru>=0.6.0',
        'notifiers>=1.2.0',
        'numpy>=1.19.0',
    ],
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
