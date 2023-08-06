#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='Topsis-Dhanvi9-101903427',
  version='0.0.1',
  description='Topsis python for decision making based on multiple factors',
  long_description=open('README.md').read() ,
  url='',  
  author='Dhanvi Bansal',
  author_email='dhanvi884@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='topsis', 
  packages=find_packages(),
  install_requires=[''] 
)

