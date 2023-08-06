#!/usr/bin/env python
#-*- coding:utf-8 -*-
 
#############################################
# File Name: setup.py
# Author: cikuu
# Mail: info@cikuu.com
# Created Time: 2022-2-13
#############################################
 
from setuptools import setup, find_packages
 
setup(
  name = "cikuu",
  version = "2022.2.26",
  keywords = ("pip"),
  description = "cikuu tools",
  long_description = "cikuu tools, commonly used",
  license = "MIT Licence",
 
  url = "http://www.cikuu.com",
  author = "cikuu",
  author_email = "info@cikuu.com",
 
  packages = find_packages(),
  include_package_data = True,
  platforms = "any",
  install_requires = ["lmdb","fire","redis","elasticsearch","pymysql","pika"]
)
