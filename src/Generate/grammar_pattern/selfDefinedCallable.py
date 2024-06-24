# -*- coding: utf-8 -*-


class Callable:
    def __init__(self, callableType: str, name: str, argTypes: list, return_type: str, content: str):
        self.callableType = callableType
        self.argTypes = argTypes
        self.name = name
        self.returnType = return_type
        self.content = content
