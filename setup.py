#!/usr/bin/env python
# Copyright © 2020 Adam Brandizzi
#
# This file is part of Input Device Indicator.
#
# Input Device Indicator is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Input Device Indicator is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Input Device Indicator.  If not, see <https://www.gnu.org/licenses/>
#

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
