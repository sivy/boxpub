#!/usr/bin/env python
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
        ('/opt/boxpub/config.py', ['files/config.py']),
        ],
    )