from email import header


#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   setup.py
@Time    :   2022/02/17 11:18:18
@Author  :   Shenxian Shi 
@Version :   
@Contact :   shishenxian@bluemoon.com.cn
@Desc    :   None
'''

# here put the import lib
from setuptools import setup, find_packages

setup(
    name='dm-easy-email',
    version='0.2.0',
    description='Data mining Group develop utils',
    author='Shenxian Shi',
    author_email='shishenxian@bluemoon.com.cn',
    url='http://gitlab.admin.bluemoon.com.cn/BigData-DataAlgorithm/dm-utils.git',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    python_requires='>=3.7',
    license=open('LICENSE.md').read(),
    long_description=open('README.md', encoding='utf8').read(),
    long_description_content_type='text/markdown'
)
