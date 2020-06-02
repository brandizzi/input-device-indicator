#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="xinput-indicator",
    version="0.0.1.dev1",
    author='Adam Victor Brandizzi',
    author_email='adam@brandizzi.com.br',
    description='xinput-indicator',
    license='LGPLv3',
    url='https://github.com/brandizzi/xinput-indicator',

    packages=find_packages(),
    test_suite='xinputindicator.tests',
    test_loader='unittest:TestLoader',
)
