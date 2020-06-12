#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="input-device-indicator",
    version="0.0.1.dev1",
    author='Adam Victor Brandizzi',
    author_email='adam@brandizzi.com.br',
    description='input-device-indicator',
    license='LGPLv3',
    url='https://github.com/brandizzi/input-device-indicator',

    packages=find_packages(),
    test_suite='inputdeviceindicator.tests',
    test_loader='unittest:TestLoader',
)
