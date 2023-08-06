# -*- coding: utf-8 -*-

import io
import os
import re

from setuptools import find_packages
from setuptools import setup

# setup
setup(
  name='braindynamics',
  version='0.0.0',
  description='BrainDynamics: Brain Dynamics Programming in Python',
  long_description='',
  long_description_content_type="text/markdown",
  author='BrainPy Team',
  author_email='chao.brain@qq.com',
  packages=find_packages(),
  python_requires='>=3.6',
  install_requires=[
  ],
  url='https://github.com/PKU-NIP-Lab/BrainPy',
  keywords='computational neuroscience, brain-inspired computation, '
           'dynamical systems, differential equations, '
           'brain modeling, brain dynamics programming',
  classifiers=[
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'Topic :: Scientific/Engineering :: Mathematics',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    'Topic :: Software Development :: Libraries',
  ],
  license='GPL-3.0 License',
)
