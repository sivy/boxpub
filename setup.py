#!/usr/bin/env python

#  _______  _______  __   __  _______  __   __  _______
# |  _    ||       ||  |_|  ||       ||  | |  ||  _    |
# | |_|   ||   _   ||       ||    _  ||  | |  || |_|   |
# |       ||  | |  ||       ||   |_| ||  |_|  ||       |
# |  _   | |  |_|  | |     | |    ___||       ||  _   |
# | |_|   ||       ||   _   ||   |    |       || |_|   |
# |_______||_______||__| |__||___|    |_______||_______|

# Copyright (c) 2014 Steve Ivy <steveivy@gmail.com>
#

import os

from distutils.core import setup

with open('README.md') as f:
    README = f.read()

with open('requirements.txt') as f:
    REQUIREMENTS = f.read()
    REQUIREMENTS = REQUIREMENTS.split('\n')

setup (
    name='boxpub',
    version='0.1',
    description='basic dropbox web publisher',
    long_description=README,
    author='Steve Ivy',
    author_email='steveivy@gmail.com',
    url='http://monkinetic.com',
    packages=['boxpub'],
    include_package_data=True,
    install_requires=REQUIREMENTS,
    data_files=[
        ('/etc/boxpub', ['files/config.py']),
        ('/etc/supervisor/conf.d', ['files/boxpub.conf']),
        ],
    )