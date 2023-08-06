#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/26 13:52
# @Author  : Adyan
# @File    : __init__.py.py


import logging
import os

import pip

current = [
    f'{i.split(" ")[0]}=={i.split(" ")[-1]}'.replace('\n', '')
    for i in os.popen(f'pip list').readlines()[2:]
]


def package(package_name: list):
    exist_lst = []
    logging.info(current)
    for i in package_name:
        if i not in current:
            logging.info(f'正在安装：{i}')
            pip.main(['install', i])
            exist_lst.append(i)
    return exist_lst


pk_lst = [
    'requests==2.27.1',
    'Faker==13.2.0',
    'Scrapy==2.5.1',
    'scrapy-redis==0.7.2',
    'Twisted==22.1.0',
    'pymongo==3.6.0',
    'pika==1.2.0',
    'redis==4.1.4',
]
package(pk_lst)
