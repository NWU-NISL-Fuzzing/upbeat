# coding=utf-8

"""
@author: xing
@contact: 1059252359@qq.com
@file: APIOperator.py
@date: 2021/11/25 16:23
@desc: 实现与API相关的操作
"""
import os
import json
import random

from grammar_pattern.API import API

current_path = os.getcwd()
qfuzz_path = current_path[:current_path.find("UPBEAT")+6]

class APIOperator:

    def init_api_list(self, path = qfuzz_path+"/src/ParseAPI/data/content.json"):
        """
        :param path: API文件存储地址，为json文件格式
        :return: 返回json格式的API信息
        """
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        data = json.loads(content)
        apiList = []
        # 1、namespace
        libraries = data.keys()
        for library in libraries:
            # 2、API
            apis = data[library].keys()
            for apiName in apis:
                # 3、api message
                callableType = data[library][apiName]["callableType"]
                requireNames = data[library][apiName]["argName"]
                requireTypes = data[library][apiName]["argType"]
                returnType = data[library][apiName]["returnType"]
                api = API(callableType, library, apiName, requireNames, requireTypes, returnType)
                apiList.append(api)
        return apiList

    def init_api_dict(self, path = qfuzz_path+"/src/ParseAPI/data/content.json"):
        """
        :param path: API文件存储地址，为json文件格式
        :return: 返回json格式的API信息
        """
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        data = json.loads(content)
        apiDict = {}
        # 1、namespace
        libraries = data.keys()
        for library in libraries:
            # 2、API
            apis = data[library].keys()
            for apiName in apis:
                # 3、api message
                callableType = data[library][apiName]["callableType"]
                requireNames = data[library][apiName]["argName"]
                requireTypes = data[library][apiName]["argType"]
                returnType = data[library][apiName]["returnType"]
                api = API(callableType, library, apiName, requireNames, requireTypes, returnType)
                apiDict[apiName] = api
        return apiDict


    def get_func_and_op(self, path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        data = json.loads(content)
        apiList = []
        # 1、namespace
        libraries = data.keys()
        for library in libraries:
            # 2、API
            apis = data[library].keys()
            for apiName in apis:
                if data[library][apiName]["callableType"] == "user":
                    continue
                # 3、api message
                callableType = data[library][apiName]["callableType"]
                requireNames = data[library][apiName]["argName"]
                requireTypes = data[library][apiName]["argType"]
                returnType = data[library][apiName]["returnType"]
                api = API(callableType, library, apiName, requireNames, requireTypes, returnType)
                apiList.append(api)
        return apiList


    def init_newtype_dict(self):
        path = qfuzz_path+"/src/ParseAPI/data/newtype.json"
        return self.init_api_dict(path)

    def randomChooseApi(self, apiList):
        api = random.choice(apiList)
        return api


# if __name__ == "__main__":
#     t = APIOperator()
#     b = t.init_api_list()
