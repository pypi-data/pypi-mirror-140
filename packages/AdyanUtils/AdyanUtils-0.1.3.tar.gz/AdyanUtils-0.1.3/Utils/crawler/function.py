#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/3/2 15:22
# @Author  : Adyan
# @File    : function.py



class Fun:
    @classmethod
    def find(
            cls, target: str,
            dictData: dict,
    ) -> list:
        queue = [dictData]
        result = []
        while len(queue) > 0:
            data = queue.pop()
            for key, value in data.items():
                if key == target:
                    result.append(value)
                elif isinstance(value, dict):
                    queue.append(value)
        if result:
            return result[0]

    @classmethod
    def finds(
            cls, target: str,
            dictData: dict,
    ) -> list:
        queue = [dictData]
        result = []
        while len(queue) > 0:
            data = queue.pop()
            if isinstance(data, str):
                continue
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == target:
                        result.insert(0, value)
                    elif isinstance(value, dict):
                        queue.append(value)
                    elif isinstance(value, list):
                        for dic in value:
                            queue.append(dic)
        if result:
            return result[0]