#!/usr/bin/env python

from distutils.core import setup

setup(
    name='nuggets',
    version='0.2.0',
    description='A Django app similar to django-flatblocks or django-chunks to add dynamic snippets of content to a django website.',
    long_description=open('README.md').read(),
    author='Daniel J. Becker',
    url='http://github.com/danieljb/django-nuggets',
    packages=('nuggets',),
    license='GPL',
)