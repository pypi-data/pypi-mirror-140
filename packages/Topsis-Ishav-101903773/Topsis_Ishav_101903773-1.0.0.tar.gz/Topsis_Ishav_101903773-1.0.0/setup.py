# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 17:43:51 2020

@author: Ishav Gupta	
"""

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


import setuptools
from distutils.core import setup
setup(
  description = "A Python package implementing TOPSIS technique by Ishav_101903773.",
  long_description = readme(),
  long_description_content_type = "text/markdown",
  name = 'Topsis_Ishav_101903773',         # How you named your package folder (MyLib)
  packages = ['Topsis_Ishav_101903773'],   # Chose the same as "name"
  version = '1.0.0',      # Start with a small number and increase it with every change you make
  license='MIT',
  author = 'Ishav Gupta',                   # Type in your name
  author_email = 'igupta1_be19@thapar.edu',      # Type in your E-Mail
  keywords = ['topsis', 'topsis implementation'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'numpy','pandas',
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
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)

