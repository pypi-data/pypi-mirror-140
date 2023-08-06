#!/usr/bin/env python

from setuptools import find_packages
from distutils.core import setup

setup(name='dglenter',
      version='0.0.1',
      description='DGL enter',
      author='DGL Team',
      author_email='wmjlyjemaine@gmail.com',
      packages=find_packages(),
      install_requires=[
          #   'dgl>=0.7.2',
          'typer>=0.4.0',
          'isort>=5.10.1',
          'autoflake8>=0.2.2',
          'numpydoc>=1.1.0'
      ],
      license='APACHE',
      entry_points={
          'console_scripts': [
              "dgl-enter = dglenter.cli.cli:main"
          ]
      },
      url='https://github.com/dmlc/dgl',
      )
