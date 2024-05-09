""" 目前包含对于变量声明语句以及API调用的处理 """

import re
import os

from grammar_pattern.APIOperator import APIOperator
from basic_operation.list_operation import get_clear_list
from basic_operation.dict_operation import merge_two_dict, minus_dict, add_item
from class_for_info.block_info import CodeBlockInfo
from class_for_info.api_call_info import APICallInfo

from code_extractor.process_block import is_first_part
from code_extractor.process_expr import *

# Get the UPBEAT work directionary, like /.../UPBEAT.
current_path = os.getcwd()
qfuzz_path = current_path[:current_path.find("UPBEAT")+6]
# Get reference.
api_op = APIOperator()
standard_api_dict = api_op.init_api_dict(qfuzz_path+"/src/ParseAPI/data/content.json")
new_type_dict = api_op.init_newtype_dict()

regex_for_var_dec = r"(let|mutable|use|set) (.*?) ?= ?(.*?);"
regex_for_set = r"set (\w+) w/= .*? <- (.*);"
regex_for_call = r"([A-Za-z0-9_:]+) ?\((.*)\)"
regex_for_call_with_modifier = r"\(?(Controlled |Adjoint )+([A-Za-z0-9_:]+)\)? *\((.*)\)"
regex_for_new = r"new (.*?)\[(.*?)\]"
regex_for_sub_arr = r"(\w+)\[(.*?)\]"
regex_for_arr_item = r"(\w+)\[(.*)\]"
regex_for_arg = r"([a-zA-Z0-9_]+)"


def is_basic_type(dec_content: str):
    """根据声明语句中的赋值表达式，尝试获取变量类型"""

    # print("===dec_content:"+dec_content)
    # 如果是数组，截取第一个元素判断类型
    if dec_content.startswith("[["):
        dimension = 2
        real_content = dec_content[dimension:dec_content.find(",")]
    elif dec_content.startswith("["):
        dimension = 1
        real_content = dec_content[dimension:dec_content.find(",")]
    else:
        dimension = 0
        real_content = dec_content
    # 去除正负号
    real_content = real_content.replace("-", "").replace("+", "")
    # 判断类型
    if real_content.isdigit():
        return "Int" + "[]" * dimension
    elif real_content.replace("L", "").isdigit():
        return "BigInt" + "[]" * dimension
    elif real_content.replace(".", "").replace("e", "").replace("E", "").isdigit():
        return "Double" + "[]" * dimension
    elif "Qubit()" in real_content:
        return "Qubit"
    elif "Qubit[" in dec_content:
        return "Qubit[]"
    elif "Pauli" in real_content:
        return "Pauli" + "[]" * dimension
    elif "One" in real_content or "Zero" in real_content:
        return "Result" + "[]" * dimension
    elif "true" in real_content or "false" in real_content:
        return "Bool" + "[]" * dimension
    elif "\"" in real_content:
        return "String" + "[]" * dimension
    else:
        return None


def is_bool_expr(content: str):
    related_word = ["==", " < ", " > ", "<=", ">=", "!="]
    for word in related_word:
        if word in content:
            return True
    return False


def is_cal_expr(content: str):
    related_word = ["+", "-", "*", "%", "/", "|", "^"]
    for word in related_word:
        if word in content:
            return True
    return False


def not_a_var(expr: str):
    related_word = ["<", ">", "=", "[", "]"]
    for word in related_word:
        if word in expr:
            return True
    return False


def get_real_args_list(args_list: list):
    real_args_list = []
    one_arg = ""
    start_to_merge = False
    print("args_list:",args_list)
    for word in args_list:
        word = word.replace("Adjoint ", "")
        word = word.strip()
        if start_to_merge:
            one_arg += word + ", "
            if one_arg.count("(") == one_arg.count(")") and one_arg.count("[") == one_arg.count("]"):
                start_to_merge = False
                # print("one_arg:"+one_arg[:-2])
                real_args_list.append(one_arg[:-2])
        elif word.count("(") != word.count(")") or word.count("[") != word.count("]"):
            start_to_merge = True
            one_arg = word + ", "
        else:
            real_args_list.append(word)
    print("real_args_list:",real_args_list)
    return real_args_list


def parse_dec_content(content: str, outmost_type: str, needful_variables: dict, known_dict: dict, middle_dict: dict):
    """ 这里处理的是只包含变量和API调用的，用，或者算术符号连接的句子 """

    print("content:"+content)
    for match_var in re.finditer(r"[\w\(\)\[\]]+", content):
        var = match_var.group()
        print("var:"+var)
        # idxFermions[1]
        match_sub_arr = re.match(r"(\w+)\[[0-9]+\]", var)
        if match_sub_arr:
            add_item(needful_variables, match_sub_arr.group(1), outmost_type+"[]", middle_dict)
            continue
        # 根据已知列表确定类型
        if var in known_dict and var not in needful_variables:
            needful_variables[var] = known_dict[var]
            if not outmost_type:
                outmost_type = known_dict[var]
            continue
        # TODO.嵌套API怎么处理？
        # 根据API参数列表确定类型
        match_for_call = re.match(regex_for_call, var)
        if match_for_call:
            api_name = match_for_call.group(1)
            api_args = match_for_call.group(2)
            if api_name in standard_api_dict:
                args_list = get_real_args_list(re.split(", |,", api_args))
                args_type = standard_api_dict[api_name].requireTypes
                print("args_list:",args_list,"args_type:",args_type)
                for arg_name, arg_type in zip(args_list, args_type):
                    if "[" in arg_name and arg_name.endswith("]"):
                        arg_name = arg_name[:arg_name.index("[")]
                    add_item(needful_variables, arg_name, arg_type, middle_dict)
            continue
        # 根据outmost_type确定类型，此时假设已知outmost_type
        add_item(needful_variables, var, outmost_type, middle_dict)


def add_var_dec(var_name: str, var_type: str, is_newtype):
    """ 根据给定信息将变量添加至var_dec_dict """

    # print("tuple here:" + var_name + " " + var_type)
    tmp_var_dec_dict = {}
    if "(" in var_name and ")" in var_name and "," in var_name:
        if is_newtype:
            for match in re.finditer(r"\w+", var_name):
                tmp_var_dec_dict[match.group()] = var_type + "ATTR"
        else:
            match_for_name = re.finditer(r"\w+", var_name)
            match_for_type = re.finditer(r"[\w\[\]]+", var_type)
            for (one_name, one_type) in zip(match_for_name, match_for_type):
                tmp_var_dec_dict[one_name.group()] = one_type.group()
    else:
        tmp_var_dec_dict[var_name] = var_type
    # print("处理完元组变量后：" + str(tmp_var_dec_dict))
    return tmp_var_dec_dict


def self_organizing_arr(var_name: str, var_dec_content: str, api_list: list, known_dict: dict):
    """ 如果变量赋值为自组数组，获取具体的类型 """
    
    if var_dec_content.count("[") != var_dec_content.count("]"):
        return {}
    var_dec_dict = {}
    # 如果是空数组
    if var_dec_content == "[]":
        return {var_name: "'T[]"}
    # 去除中括号
    if var_dec_content.startswith("[[") and var_dec_content.endswith("]]"):
        dimension = 2
        var_dec_content = var_dec_content[2:-2]
    elif var_dec_content.startswith("["):
        dimension = 1
        if var_dec_content.endswith("]"):
            var_dec_content = var_dec_content[1:-1]
        else:
            var_dec_content = var_dec_content[1:var_dec_content.rindex("]")]
    # 获取第一个元素
    first_item = get_real_args_list(re.split(", |,", var_dec_content))[0]
    # 如果是已知变量
    if first_item in known_dict:
        var_dec_dict[var_name] = known_dict[first_item] + "[]" * dimension
        return var_dec_dict
        # 如果是基础类型
    tmp_type = is_basic_type(first_item)
    if tmp_type:
        var_dec_dict[var_name] = tmp_type + "[]" * dimension
        return var_dec_dict
    # 如果是newtype
    api_call_match = re.match(regex_for_call, first_item)
    if api_call_match:
        if api_call_match.group(1) in new_type_dict:
            var_dec_dict[var_name] = api_call_match.group(1) + "[]" * dimension
            api_list.append(api_call_match.group(1))
            return var_dec_dict
        elif api_call_match.group(1) in standard_api_dict:
            var_dec_dict[var_name] = standard_api_dict[api_call_match.group(1)].returnType + "[]" * dimension
            api_list.append(api_call_match.group(1))
            return var_dec_dict
    # 如果是元组
    if first_item.startswith("(") and first_item.endswith(")"):
        tmp_type = ""
        for i in range(first_item.count(",")):
            tmp_type += "Int, "
        var_dec_dict[var_name] = "(Int, " + tmp_type[:-2] + ")" + "[]" * dimension
        return var_dec_dict
    else:
        return {}

def get_needful_var(arg: str, arg_type: str, var_dec_dict: dict, known_dict: dict, middle_dict: dict, needful_variables: dict):
    """ 排除不是变量名的情况，获取needful_variables """

    arg = arg.replace("Adjoint ", "")
    # print("in get_needful_var:" + arg)
    # 如果是嵌套的API调用，不在外层处理
    if "PROCESSED" in arg:
        return {}
    # 如果是基础类型值，不必生成
    elif is_basic_type(arg):
        # print(arg + " is basic type")
        return {}
    # 如果是API名，不必生成
    elif arg in standard_api_dict:
        return {}
    elif arg.startswith("Microsoft.Quantum"):
        return {}
    # 如果是_或[]，不必生成
    elif arg == "_" or arg == "[]" or arg == "":
        return {}
    # 如果包含函数调用，在最底层识别（不能删）
    elif re.match(r"\w+\(.*\)", arg):
        return {}

    # 如果是a .. b，并避免a[0 .. 1]在此处被处理
    if ".." in arg and "[" not in arg:
        for word in re.split(r" \.\. |\.\.", arg):
            if word not in middle_dict and word not in var_dec_dict and word not in needful_variables and not word.isdigit():
                needful_variables[word] = "Int"
        return needful_variables

    # 如果是newtype的某个属性，需要生成的参数是newtype本身
    if "::" in arg:
        arg = arg[:arg.find("::")]
    # 如果是数组元素或者子数组，需要生成的参数是数组本身
    elif re.match(regex_for_sub_arr, arg):
        tmp_match = re.match(regex_for_sub_arr, arg)
        arr_name, arr_size = tmp_match.group(1), tmp_match.group(2)
        if ".." in arr_size:
            add_item(needful_variables, arr_name, arg_type, middle_dict)
        else:
            add_item(needful_variables, arr_name, arg_type+"[]", middle_dict)
        parse_dec_content(arr_size, "Int", needful_variables, known_dict, middle_dict)
        return needful_variables
    # 通过！访问量子比特数组
    elif arg.endswith("!"):
        arg = arg.replace("!", "")

    # 如果是bool表达式
    if is_bool_expr(arg):
        items = re.split("==|!=|<=|>=| < | > ", arg)
        # print("is a bool expr.left:"+items[0]+" right:"+items[1])
        right_item_type = is_basic_type(items[1].strip())
        if right_item_type:
            arg = items[0].strip()
            arg_type = right_item_type

    # 如果是计算表达式，其中所有变量都是该表达式的类型
    # print("~~~is_cal_expr(arg):", is_cal_expr(arg))
    if is_cal_expr(arg):
        for match in re.finditer(regex_for_arg, arg):
            real_arg = match.group()
            # print("real_arg:"+real_arg)
            # print("known_dict:",known_dict)
            # TODO.为什么要筛选real_arg not in known_dict and ？
            if is_basic_type(real_arg):
                pass
            elif real_arg in needful_variables or real_arg in var_dec_dict or real_arg in middle_dict:
                pass
            elif real_arg in standard_api_dict:
                pass
            else: 
                needful_variables[match.group()] = arg_type
    elif not_a_var(arg):
        pass
    elif arg not in var_dec_dict and arg not in middle_dict and arg not in needful_variables:
        # print(arg + " is a var:")
        # 如果known_dict中已经有，并且不是泛型，可以替换掉是泛型的arg_type
        if arg in known_dict and "'" not in known_dict[arg]:
            arg_type = known_dict[arg]
        needful_variables[arg] = arg_type
    # print("~~~needful_variables:",needful_variables)
    return needful_variables


def get_call_list(content: str):
    """ （更新）获取API调用信息 """

    call_list = []
    call_start_regex = r"(\w+) ?\("
    for match in re.finditer(call_start_regex, content):
        call_start_index = match.start()
        front_str = content[:call_start_index]
        if front_str.endswith("Controlled "):
            functor = "Controlled"
        elif front_str.endswith("Adjoint "):
            functor = "Adjoint"
        else:
            functor = None
        call_name = match.group(1)
        find_index = call_start_index
        while True:
            call_end_index = content.index(")", find_index)
            call_str = content[call_start_index:call_end_index+1]
            # print("call_str:"+call_str)
            if call_str.count("(") == call_str.count(")"):
                call_args = call_str[call_str.index("(")+1:call_str.rindex(")")].strip()
                # print("call_args:"+call_args)
                # TODO.这里没有存储完整的API调用语句，修饰符没有加
                call_list.append(APICallInfo(call_name, call_args, call_str, functor))
                break
            find_index = call_end_index + 1
    return call_list


def process_functor(api_param: str, known_dict: dict):
    """ 对Controlled xxx的第一个参数进行识别 """
    
    first_end = api_param.find(",")
    first_param = api_param[:first_end]
    api_param = api_param[first_end + 1:].strip()
    # TODO.这里是否需要输入middle_dict？
    if first_param.startswith("[") and first_param.endswith("]"):
        real_first_param = first_param[1:-1]
        return get_needful_var(real_first_param, "Qubit", {}, known_dict, {}, {}), api_param
    else:
        real_first_param = first_param
        return get_needful_var(real_first_param, "Qubit[]", {}, known_dict, {}, {}), api_param


def get_all_call_name(one_block: CodeBlockInfo, stmt: str, known_dict: dict):
    """获取API名列表，对API参数进行解析，获取需要生成的变量字典"""

    # print("stmt:"+stmt)
    api_call_list = get_call_list(stmt)
    # print("size of api_call_list:" + str(len(api_call_list)))
    if len(api_call_list) == 0:
        return []
    api_list = []
    needful_variables = {}
    for index, api_call in enumerate(api_call_list, start=1):
        # 排除掉常用API以及newtype
        this_api_name = api_call.api_name
        print("api_name:"+this_api_name+"-")
        if "::" in this_api_name or this_api_name in known_dict:
            pass
        # 这里过滤的话不会影响下面识别变量么？
        elif this_api_name in ['Qubit', 'Message', 'Length', 'Reset', 'ResetAll']:
            continue
        elif this_api_name in ["using", "if", "while", "for", "let", "mutable", "use"]:
            continue
        elif this_api_name not in standard_api_dict:
            return None
        if api_call.api_name in standard_api_dict:
            tmp_import = "open " + standard_api_dict[api_call.api_name].namespace + ";\n"
            if tmp_import not in one_block.import_in_calls:
                one_block.import_in_calls += tmp_import
        # 删除参数列表中嵌套的API调用
        api_call.delete_api_call(api_call_list[index:])
        # print("after delete api call:" + api_call.api_param)
        # 如果是Controlled xxx，第一个参数是Qubit[]类型
        # print("···check functor:" + api_call.call_stmt + str(api_call.functor))
        if api_call.functor == "Controlled " or api_call.functor == "Controlled":
            tmp_needful_variables, api_call.api_param = process_functor(api_call.api_param, known_dict)
            # print("---after process functor:" + str(tmp_needful_variables))
            needful_variables.update(tmp_needful_variables)
        # 开始处理参数列表
        args_list = get_real_args_list(re.split(r",(?![^<]*>)", api_call.api_param))
        # print("args_list:", args_list)
        if api_call.api_name in standard_api_dict:
            api_list.append(api_call.api_name)
            args_type = standard_api_dict[api_call.api_name].requireTypes
            # print("---args type:", args_type)
            if len(args_type) == 0 or len(args_list) != len(args_type):
                continue
            for i in range(len(args_list)):
                arg_name = args_list[i].strip()
                arg_type = args_type[i]
                # 如果把元组截取了，把左右括号去除一下
                if arg_name.startswith("(") and not has_closed_brackets(arg_name):
                    arg_name = arg_name[1:]
                elif not arg_name.endswith("(") and not has_closed_brackets(arg_name):
                    arg_name = arg_name[:-1]
                print("arg name:" + arg_name + " arg type:" + arg_type)
                needful_variables.update(
                    get_needful_var(arg_name, arg_type, one_block.var_dec_dict, known_dict, one_block.middle_dict, needful_variables))
                if arg_name in standard_api_dict:
                    tmp_import = "open " + standard_api_dict[arg_name].namespace + ";\n"
                    if tmp_import not in one_block.import_in_calls:
                        one_block.import_in_calls += tmp_import
        elif "::" in api_call.api_name:
            pass
        # 对照参数列表中的API获取需要生成的变量
        elif api_call.api_name in known_dict:
            api_list.append(api_call.api_name)
            op_type = remove_redundant_brackets(known_dict[api_call.api_name])
            op_inputs = re.split("=>|->", op_type)[0].strip()
            args_list = re.split(r",(?![^(]*\))", api_call.api_param)
            inputs_list = re.split(r",(?![^(]*\))", remove_redundant_brackets(op_inputs))
            for arg, input_str in zip(args_list, inputs_list):
                print("arg:"+arg+" input_str:"+input_str)
                # add_item(needful_variables, arg, input_str, one_block.middle_dict)
                needful_variables.update(
                    get_needful_var(arg, input_str, one_block.var_dec_dict, known_dict, one_block.middle_dict, needful_variables))
        else:
            return []
    one_block.var_use_dict.update(needful_variables)
    # print("after parse api:\n" + str(one_block.var_use_dict) + str(api_list))
    return get_clear_list(api_list)


def parse_dec_stmt(one_block: CodeBlockInfo, known_dict: dict):
    """根据变量声明语句，收集字典{变量名：变量类型}"""

    # 获取中间变量
    tmp_needful_variables = one_block.get_middle_var()
    # 检查一下是否为复杂表达式，如果是，不返回var_dec_dict
    if is_first_part(one_block.content_str):
        is_complex_stmt = True
    else:
        is_complex_stmt = False
    # 开始
    var_dec_dict = {}
    # needful_variables = {}
    needful_variables = tmp_needful_variables
    api_list = []
    block_content = one_block.content_str
    # new_block_content = block_content
    # print("===block_content:"+block_content+"-")
    for match_var_dec in re.finditer(regex_for_var_dec, block_content):
        # print("match_var_dec:" + match_var_dec.group())
        # new_block_content = new_block_content.replace(match_var_dec.group(), "")
        var_name_content = match_var_dec.group(2)
        if "w/=" in match_var_dec.group() or "[" in var_name_content:
            return None, None
        var_dec_content = match_var_dec.group(3)
        # dimension = 0
        # 情况0 let (a, b) = (c, d);
        var_tuple = re.match(r"\((.*?)(, .*?)*\)", var_name_content)
        if var_tuple:
            # TODO.赋予实际类型
            # 给声明的变量传类型
            for sub_match in re.finditer(regex_for_arg, var_name_content):
                var_dec_dict[sub_match.group()] = "'T"
            # 处理需要生成的变量
            if var_dec_content.startswith("(") and var_dec_content.endswith(")"):
                var_dec_content = var_dec_content[1:-1]
                parse_dec_content(var_dec_content, "'T", needful_variables, known_dict, one_block.middle_dict)
                continue
        # 情况1.1 使用new声明数组
        new_arr = re.match(regex_for_new, var_dec_content)
        if new_arr:
            var_dec_dict[var_name_content] = new_arr.group(1)+"[]"
            parse_dec_content(new_arr.group(2), "Int", needful_variables, known_dict, one_block.middle_dict)
            continue
        # 情况1.2 自组数组[1,2,3]
        # print("---check var_dec_content:" + var_dec_content)
        if var_dec_content.startswith("["):
            var_dec_dict.update(self_organizing_arr(var_name_content, var_dec_content, api_list, known_dict))
            continue
        # 情况1.3 数组元素或子数组
        match_arr_item = re.match(regex_for_arr_item, var_dec_content)
        if match_arr_item:
            arr_name, arr_index = match_arr_item.group(1), match_arr_item.group(2)
            print("match_arr_item:"+match_arr_item.group())
            if arr_name == "Qubit":
                var_dec_dict[var_name_content] = "Qubit[]"
            else:
                tmp_dict = merge_two_dict(known_dict, needful_variables)
                # print("tmp_dict:",tmp_dict)
                if arr_name in tmp_dict:
                    # qs[0 .. 2]取得是qs的第0到第2个元素，类型还是数组的类型
                    if ".." in arr_index:
                        var_type = tmp_dict[arr_name]
                    # qs[0]，类型是元素的类型
                    else:
                        var_type = tmp_dict[arr_name][:-2]
                    var_dec_dict[var_name_content] = var_type
            if arr_name in known_dict and arr_name not in needful_variables:
                needful_variables[arr_name] = known_dict[arr_name]
            # 如果索引或者范围中存在变量，以Int作为类型，添加到需要生成的字典中
            parse_dec_content(arr_index, "Int", needful_variables, known_dict, one_block.middle_dict)
            # print("after match arr,var_dec_dict:",var_dec_dict)
            # print("after match arr,needful_variables", needful_variables)
            # 如果已匹配，不必检查下面的几种情况
            continue
        # 情况3 函数调用，将函数返回值传给变量作为类型
        match_call = re.match(regex_for_call, var_dec_content)
        if match_call:
            # 如果存在API调用，检查一下正则匹配是否是正确的
            real_var_dec_content = cut_proper_bracket(match_call.group())
            match_call = re.search(regex_for_call, real_var_dec_content)
            # 获取API返回值作为声明变量的类型
            # print("20230907:match_call:"+match_call.group())
            api_name = match_call.group(1)
            if api_name == "Qubit":
                var_dec_dict[var_name_content] = "Qubit"
            elif api_name in standard_api_dict:
                api_info = standard_api_dict[api_name]
                if api_info.callableType == "user":
                    var_dec_dict.update(add_var_dec(var_name_content, api_name, True))
                else:
                    var_dec_dict.update(add_var_dec(var_name_content, api_info.returnType, False))
                # print("使用API返回值作为声明变量的类型：" + var_name_content + " " + api_info.returnType)
                if api_info.namespace not in one_block.import_in_calls:
                    one_block.import_in_calls += "open " + api_info.namespace + ";\n"
                # 对API参数部分进行识别
                args_type = api_info.requireTypes
                args_list = get_real_args_list(re.split(", |,", match_call.group(2)))
                # 20230723：尝试修改，即使有嵌套API，识别其参数也不影响最终的需要声明的变量？
                # args_str = match_call.group(2)
                # args_list = []
                # for item in re.finditer(r"\w+", args_str):
                #     args_list.append(item.group())
                # 20230723:修改结束，尝试失败，因为参数变量和参数类型需要一对一对应
                if len(args_type) > 0 and len(args_type) == len(args_list):
                    print("---args_type:", args_type, " args_list:", args_list)
                    for arg_name, arg_type in zip(args_list, args_type):
                        if arg_name in standard_api_dict:
                            tmp_import = "open " + standard_api_dict[arg_name].namespace + ";\n"
                            if tmp_import in one_block.import_in_calls:
                                one_block.import_in_calls += tmp_import
                            continue
                        needful_variables.update(
                            get_needful_var(arg_name, arg_type, var_dec_dict, known_dict, one_block.middle_dict, needful_variables))
                        print("+++needful_variables:",needful_variables)
                else:
                    print("解析参数失败，参数名与参数类型不匹配")
                    one_block.var_dec_dict = None
                    one_block.var_use_dict = None
                    return None, None
                api_list.append(api_name)
            else:
                # print("check use:", one_block.var_list)
                print("不是标准API")
                one_block.var_dec_dict = None
                one_block.var_use_dict = None
                return None, None
            continue
        # 情况4 如果是let a = b!;查找b的类型
        if var_dec_content.endswith("!"):
            # print(">>>var_dec_content:"+var_dec_content)
            # TODO.推断被声明的变量的类型
            # 获取需要的参数
            real_var_dec_content = var_dec_content[:-1]
            if real_var_dec_content in known_dict:
                needful_variables[real_var_dec_content] = known_dict[real_var_dec_content]
            continue
        # 情况5 如果是let a = 0;就把Int传给a（所有基础类型）
        basic_type = is_basic_type(var_dec_content)
        if basic_type:
            # print("situation3:"+var_dec_content+" "+basic_type)
            var_dec_dict[var_name_content] = basic_type
            continue
        # 情况6 如果是简单计算，根据表达式中的变量类型推断声明变量的类型
        is_inferred = False
        for known_var_name, known_var_type in known_dict.items():
            # print("===known_var_name:"+known_var_name+" known_var_type:"+known_var_type)
            if known_var_name in var_dec_content:
                # 推断被声明的变量的类型
                if "[" in var_dec_content and "]" in var_dec_content:
                    var_dec_dict[var_name_content] = known_var_type.replace("[]", "")
                    is_inferred = True
                else:
                    var_dec_dict.update(add_var_dec(var_name_content, known_var_type, True))
                    is_inferred = True
                # 获取需要的参数
                if known_var_name not in needful_variables and known_var_name not in one_block.middle_dict:
                    needful_variables[known_var_name] = known_var_type
        if not is_inferred:
            for match_word in re.finditer(r"[\w\.\(\)]+", var_dec_content):
                word = match_word.group()
                basic_type = is_basic_type(word)
                # print("word:",word,"basic_type:",basic_type)
                if basic_type:
                    var_dec_dict[var_name_content] = basic_type
                    break
                elif word == "PI()":
                    var_dec_dict[var_name_content] = "Double"
                    break
        # print("===1var_dec_dict:",var_dec_dict)
    # 如果不是复杂代码块，声明变量可以放在var_dec_dict
    if not is_complex_stmt:
        one_block.var_dec_dict.update(var_dec_dict)
        one_block.var_use_dict.update(needful_variables)
    # 否则，变量声明不能被别的块使用
    else:
        one_block.middle_dict.update(var_dec_dict)
        one_block.var_use_dict.update(minus_dict(needful_variables, var_dec_dict))
    print("---check after parse:", one_block.var_dec_dict, one_block.var_use_dict, api_list)
    # 20230905:为什么是new_block_content?
    # return new_block_content, api_list
    return block_content, api_list
