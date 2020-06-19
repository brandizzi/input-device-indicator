#!/usr/bin/env python
from distutils.core import setup

setup(
    name="input-device-indicator",
    version="0.0.1.dev1",
    author='Adam Brandizzi',
    author_email='adam@brandizzi.com.br',
    description='input-device-indicator',
    license='LGPLv3',
    url='https://github.com/brandizzi/input-device-indicator',
    packages=['inputdeviceindicator'],
    entry_points={
        'gui_scripts': [
            'input-device-indicator=inputdeviceindicator.main:main'
        ]
    },
    test_suite='inputdeviceindicator.tests',
    test_loader='unittest:TestLoader',
)
