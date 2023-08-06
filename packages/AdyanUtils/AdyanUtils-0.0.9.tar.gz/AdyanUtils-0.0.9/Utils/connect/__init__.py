#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/26 11:24
# @Author  : Adyan
# @File    : __init__.py.py


from Utils import package

pk_lst = [
    'pymongo==3.6.0',
    'pika==1.2.0',
    'redis==4.1.4',
]
package(pk_lst)

from .mongo_conn import MongoPerson
from .rabbit_conn import RabbitClient, MonitorRabbit
from .redis_conn import ReidsClient
