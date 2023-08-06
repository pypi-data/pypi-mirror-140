#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/26 11:24
# @Author  : Adyan
# @File    : __init__.py.py

from Utils import package

pk_lst = ['pymongo', 'pika', 'redis']
package(pk_lst)

import mongo_conn, rabbit_conn, redis_conn

rabbit = rabbit_conn.RabbitClient
rabbit_monitor = rabbit_conn.MonitorRabbit
redis = redis_conn.ReidsClient
mongo = mongo_conn.MongoPerson
