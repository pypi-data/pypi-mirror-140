#!/usr/bin/env python
# coding: utf-8




from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
description1="The Technique for Order of Preference by Similarity to Ideal Solution (TOPSIS) is a multi-criteria decision analysis method, which was originally developed by Ching-Lai Hwang and Yoon in 1981[1] with further developments by Yoon in 1987,[2] and Hwang, Lai and Liu in 1993.[3] TOPSIS is based on the concept that the chosen alternative should have the shortest geometric distance from the positive ideal solution (PIS)[4] and the longest geometric distance from the negative ideal solution (NIS)."
setup(
  name='Topsis-Ananya-101903073',
  version='0.0.1',
  description='Topsis',
  long_description=description1,
  url='',  
  author='Ananya Goel',
  author_email='agoel_be19@thapar.edu',
  license='MIT', 
  classifiers=classifiers,
  keywords='Topsis', 
  packages=find_packages(),
  install_requires=[''] 
)


