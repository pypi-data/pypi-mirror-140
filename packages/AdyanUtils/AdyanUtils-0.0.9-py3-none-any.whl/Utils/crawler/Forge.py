#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/26 11:49
# @Author  : Adyan
# @File    : Forge.py


import hashlib
import re
import time
import urllib.parse

import requests
from faker import Faker

fake = Faker()


def url_code(cookie, ti, formdata):
    string = f'{re.findall("_m_h5_tk=(.*?)_", cookie)[0]}&{ti}&12574478&{formdata.get("data")}'
    m = hashlib.md5()
    m.update(string.encode('UTF-8'))
    return m.hexdigest()


def url_bm(string=None, code='utf-8'):
    quma = str(string).encode(code)
    bianma = urllib.parse.quote(quma)
    return bianma


def gen_headers(string):
    lsl = []
    headers = {}
    for l in string.split('\n')[1:-1]:
        l = l.split(': ')
        lsl.append(l)
    for x in lsl:
        headers[str(x[0]).strip('    ')] = x[1]

    return headers


class Headers:
    def __init__(self, url):
        # f'http://47.107.86.234:9090/cookie?type=UPDATE&host=47.107.86.234&DB=3&login_url=https://huodong.taobao.com/wow/pm/default/default/813b63?'
        self.cookie_url = url
        self.ti = int(time.time())
        self.cookie = requests.get(self.cookie_url).json().get("data")

    def user_agent(self, mobile_headers):
        while True:
            user_agent = fake.chrome(
                version_from=63, version_to=80,
                build_from=999, build_to=3500
            )
            if "Android" in user_agent or "CriOS" in user_agent:
                if mobile_headers:
                    break
                continue
            else:
                break
        return user_agent

    def header(self, string, retry=None, mobile_headers=True):
        headers = gen_headers(string)
        if int(time.time()) > self.ti + 300 or retry == True:
            self.cookie = requests.get(self.cookie_url).json().get("data")
            self.ti = int(time.time())
        headers['user-agent'] = self.user_agent(mobile_headers)
        headers['cookie'] = self.cookie
        return headers

