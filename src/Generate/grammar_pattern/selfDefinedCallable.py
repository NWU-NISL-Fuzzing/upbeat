# -*- coding: utf-8 -*-
"""
@Time ： 2022/1/8 14:45
@Auth ： Xing
@File ：selfDefinedCallable.py
@IDE ：PyCharm
@Description：ABC(Always Be Coding)

"""


class Callable:
    def __init__(self, callableType: str, name: str, argTypes: list, return_type: str, content: str):
        """
        :param namespace: API所属库
        :param name: API名称
        :param require_types: API参数类型
        :param return_type: API返回值类型
        """
        self.callableType = callableType
        self.argTypes = argTypes
        self.name = name
        self.returnType = return_type
        self.content = content
