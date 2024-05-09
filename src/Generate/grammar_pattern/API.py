# coding=utf-8

class API:
    def __init__(self, callableType: str, namespace: str, name: str, require_names: list, require_types: list, return_type: str):
        """
        :param namespace: API所属库
        :param name: API名称
        :param require_types: API参数类型
        :param return_type: API返回值类型
        """
        self.callableType = callableType
        self.namespace = namespace
        self.name = name
        self.requireNames = require_names
        self.requireTypes = require_types
        self.returnType = return_type

    def get_api_args(self):
        """ 将requireNames和requireTypes组装为字典 """
        
        args_dict = {}
        for var_name, var_type in zip(self.requireNames, self.requireTypes):
            args_dict[var_name] = var_type
        return args_dict
