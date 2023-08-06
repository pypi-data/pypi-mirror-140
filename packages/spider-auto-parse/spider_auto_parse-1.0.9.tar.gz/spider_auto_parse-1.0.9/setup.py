#!/usr/bin/env python
# coding: utf-8
import setuptools
from setuptools import setup

setup(
    name='spider_auto_parse',
    version='1.0.9',
    author='xueqiuyu',
    author_email='xueqy.boot@foxmail.com',
    url='https://blog.csdn.net/m0_50889678/article/details/122344474',
    description=u'自动解析详情、时间、列表',
    packages=setuptools.find_packages(),
    install_requires=['cchardet', 'dateparser', 'Distance', 'environs', 'joblib', 'loguru', 'lxml', 'matplotlib',
                      'numpy', 'python_Levenshtein', 'readability_lxml', 'requests', 'scikit_learn', 'setuptools',
                      'w3lib', 'jsonpath'
                      ],
    entry_points={
    }
)
