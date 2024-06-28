# coding=utf-8

import os
import json
import random

from grammar_pattern.API import API

current_path = os.getcwd()
qfuzz_path = current_path[:current_path.find("upbeat")+6]

class APIOperator:

    def init_api_list(self, path = qfuzz_path+"/src/ParseAPI/data/content.json"):
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
