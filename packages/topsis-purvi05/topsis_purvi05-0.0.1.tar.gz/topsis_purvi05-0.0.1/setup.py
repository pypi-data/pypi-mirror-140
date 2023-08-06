# -*- coding: utf-8 -*-
"""
Created on  Feb 24 17:43:51 2022

@author: PURVI KANANI
"""
from setuptools import setuptools 
from distutils.core import setup
setup(
  name = 'topsis_purvi05',         # How you named your package folder (MyLib)
  packages = ['topsis_purvi05'],   # Chose the same as "name"
  version = '0.0.1',      # Start with a small number and increase it with every change you make
  license='MIT',
  description = 'topsis implementation',   # Give a short description about your library
  author = 'PURVI KANANI',                   # Type in your name
  author_email = 'purvi5kanani@gmail.com',      # Type in your E-Mail
  keywords = ['topsis', 'topsis implementation'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'numpy',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.6',
    
  ],
)

