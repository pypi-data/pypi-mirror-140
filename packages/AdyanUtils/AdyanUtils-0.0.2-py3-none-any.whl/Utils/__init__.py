#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/26 13:52
# @Author  : Adyan
# @File    : __init__.py.py


import os

import pip

current = [
    str(i.split(' ')[0])
    for i in os.popen(f'pip list').readlines()
]


def package(package_name: list):
    exist_lst = []
    for i in package_name:
        if i not in current:
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
