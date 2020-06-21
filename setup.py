#!/usr/bin/env python
from distutils.core import setup
import setuptools

setup(
    name="input-device-indicator",
    version="0.0.1.dev1",
    author='Adam Brandizzi',
    author_email='adam@brandizzi.com.br',
    description='Enable and disables such as keyboards, mouses and trackpads.',
    license='GPLv3',
    url='https://github.com/brandizzi/input-device-indicator',
    packages=['inputdeviceindicator'],
    package_data={
        'inputdeviceindicator': ['resources/*']
    },
    entry_points={
        'gui_scripts': [
            'input-device-indicator=inputdeviceindicator.main:main'
        ]
    },
    test_suite='inputdeviceindicator.tests',
    test_loader='unittest:TestLoader',
    data_files=[
        (
            'share/applications/',
            ['inputdeviceindicator/resources/input-device-indicator.desktop']
        ),
        (
            'share/icons/',
            ['inputdeviceindicator/resources/input-device-indicator.svg']
        ),
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: Gnome",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Topic :: Desktop Environment :: Gnome",
    ],
)
