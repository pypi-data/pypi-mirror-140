#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools


with open('README.md', 'r', encoding='utf-8') as f:
    README = f.read()

setuptools.setup(
    name='collections-mapping',
    version='0.0.1',
    description='Specialized container datatypes providing dict-like key-value mapping objects',
    author='Yi Zhang',
    author_email='yizhang.dev@gmail.com',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/imyizhang/collections-mapping',
    download_url='https://github.com/imyizhang/collections-mapping',
    packages=setuptools.find_packages(),
    py_modules=['collections_mapping'],
    keywords=[
        'key-value', 'dict', 'collections', 'mapping', 'serialization',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    license='MIT',
)
