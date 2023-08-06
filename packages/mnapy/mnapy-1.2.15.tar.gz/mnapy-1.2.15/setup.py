#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  4 09:17:55 2021

@author: christian
"""

from setuptools import setup

setup(name='mnapy',
      version='1.2.15',
      author='Christian Nimako-Boateng',
      author_email='summersedge23@gmail.com',
      packages=['mnapy'],
      url='https://github.com/SummersEdge23/mnapy',
      license='MIT',
      description='Dynamic Cross Platform Circuit Simulation Platform.',
      long_description=open('README.txt').read(),
      zip_safe=False,
      install_requires=[
      ])
