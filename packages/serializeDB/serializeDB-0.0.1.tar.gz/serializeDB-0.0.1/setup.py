#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools


with open('README.md', 'r', encoding='utf-8') as f:
    README = f.read()

setuptools.setup(
    name='serializeDB',
    version='0.0.1',
    description='A lightweight key-value database based on serialization',
    author='Yi Zhang',
    author_email='yizhang.dev@gmail.com',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/imyizhang/serializeDB',
    download_url='https://github.com/imyizhang/serializeDB',
    packages=setuptools.find_packages(),
    py_modules=['serializedb'],
    keywords=[
        'key-value', 'database', 'serialization',
    ],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    license='three-clause BSD',
)
