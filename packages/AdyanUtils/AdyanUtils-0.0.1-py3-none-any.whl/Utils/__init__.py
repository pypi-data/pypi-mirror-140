#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/26 13:52
# @Author  : Adyan
# @File    : __init__.py.py


import os

import pip


def package(package_name: list):
    exist_lst = []
    for i in package_name:
        exist = os.system(f'pip show {i}')
        print(exist)
        if exist == 1:
            pip.main(['install', i])
            exist_lst.append(i)
    return exist_lst


pk_lst = [
    'hashlib',
    're',
    'urllib',
    'requests',
    'faker',
    'random',
    'requests',
    'scrapy',
    'twisted',
    'scrapy_redis'
]
package(pk_lst)
