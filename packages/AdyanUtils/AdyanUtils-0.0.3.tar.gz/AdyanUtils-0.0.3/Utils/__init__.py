#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/26 13:52
# @Author  : Adyan
# @File    : __init__.py.py


import os

import pip

current = [
    str(i.split(' ')[0])
    for i in os.popen(f'pip list').readlines()[2:]
]


def package(package_name: list):
    exist_lst = []
    print(current)
    for i in package_name:
        if i not in current:
            print(i)
            pip.main(['install', i])
            exist_lst.append(i)
    return exist_lst


pk_lst = [
    'requests',
    'Faker',
    'requests',
    'Scrapy',
    'Twisted',
    'scrapy-redis',
    'pymongo',
    'pika',
    'redis'
]
package(pk_lst)
