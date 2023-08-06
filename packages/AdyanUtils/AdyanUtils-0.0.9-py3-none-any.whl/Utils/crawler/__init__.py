#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/28 13:39
# @Author  : Adyan
# @File    : __init__.py.py


from Utils import package

pk_lst = [
    'requests==2.27.1',
    'Faker==13.2.0',
    'Scrapy==2.5.1',
    'scrapy-redis==0.7.2',
    'Twisted==22.1.0',
]
package(pk_lst)
