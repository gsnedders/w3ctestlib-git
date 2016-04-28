#!/usr/bin/python
# CSS Test Suite Manipulation Library
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause: <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>

from setuptools import setup, find_packages

setup(name='w3ctestlib',
      version='0.1',
      description='CSS WG testing tools/library',
      packages=find_packages(),
      package_data={'w3ctestlib': ['catalog/*', 'templates/*']},
      )
