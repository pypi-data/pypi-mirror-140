#!/usr/bin/env python
from setuptools import setup, find_packages
setup(
 name = 'QiqiaoPlus',
 version = '0.0.1',
 description = 'autotest',
 long_description = 'Qiqiao Web Test Keywords ',
 author = 'Donny',
 author_email = '981772991@qq.com',
 url = 'https://github.com/donny/qiqiaoplus',
 license = 'MIT Licence',
 keywords = 'testing testautomation',
 platforms = 'any',
 python_requires = '>=3.7.*',
 install_requires = [],
 package_dir = {'': 'QiqiaoPlus'},
 packages = find_packages('QiqiaoPlus')
 )