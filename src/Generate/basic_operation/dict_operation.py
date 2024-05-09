import random

from class_for_info.defined_var_info import DefinedVar
from grammar_pattern.APIOperator import APIOperator

api_op = APIOperator()
standard_api_dict = api_op.init_api_dict("/root/UPBEAT/src/ParseAPI/data/content.json")


def get_key_by_value(d, value):
    """ 根据值查找键 """
    return [k for k, v in d.items() if v == value][0]


def merge_two_dict(d1: dict, d2: dict):
    """合并两个字典"""

    d = {}
    d.update(d1)
    d.update(d2)
    return d


def minus_dict(d1: dict, d2: dict):
    """ 从d1中删除d2中存在的元素 """
    for key in d2.keys():
        if key in d1:
            d1.pop(key)
    return d1


def get_rest_args(dict1: dict, dict2: dict):
    """ Get the content that is in dictionary A but not in B. """

    dict3 = {}
    for key, value in dict1.items():
        if key in dict2 and dict2[key] == value:
            pass
        else:
            dict3[key] = value
    return dict3


def get_undefined_args(dict1: dict, dict2: dict):
    """  """

    dict3 = {}
    flag = True
    for key1, value1 in sorted(dict1.items(), reverse=True):
        # print("key1:"+key1)
        if key1 in dict2:
            continue
        for key2, value2 in dict2.items():
            # print("compare:"+value2.var_name+" "+key1)
            flag = True
            if value2.var_name == key1:
                flag = False
                continue
        if flag:
            dict3[key1] = value1
    return dict3


def add_item(d: dict, var_name: str, var_type: str, middle_dict: dict):
    """ 构建needfule_variables时使用，将需要生成的变量存入字典 """

    if var_name not in d and not var_name.isdigit() and var_name not in middle_dict and var_name not in standard_api_dict:
        d[var_name] = var_type
    return d


def random_select_dict(d: dict, n):
    if n > len(d):
        return {}, d
    keys = list(d.keys())
    selected_keys = random.sample(keys, n)
    selected_items = {}
    for key in selected_keys:
        selected_items[key] = d[key]
    return selected_items, get_rest_args(d, selected_items)


def is_subset(dict1, dict2):
    """ 判断dict1是否在dict2中 """

    return all(item in dict2.items() for item in dict1.items())


if __name__ == "__main__":
    dict1 = {'phases': 'ReflectionPhases', 'phases::AboutTarget': 'Double[]', 'phases::AboutStart': 'Double[]'}
    dict2 = {'AboutTarget': DefinedVar("phases::AboutTarget", "", 0, "", "")}
    print(get_undefined_args(dict1, dict2))
