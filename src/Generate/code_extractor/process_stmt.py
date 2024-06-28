import re
import os

from grammar_pattern.APIOperator import APIOperator
from basic_operation.list_operation import get_clear_list
from basic_operation.dict_operation import merge_two_dict, minus_dict, add_item
from class_for_info.block_info import CodeBlockInfo
from class_for_info.api_call_info import APICallInfo

from code_extractor.process_block import is_first_part
from code_extractor.process_expr import *

# Get the upbeat work directionary, like /.../upbeat.
current_path = os.getcwd()
qfuzz_path = current_path[:current_path.find("upbeat")+6]
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
    if dec_content.startswith("[["):
        dimension = 2
        real_content = dec_content[dimension:dec_content.find(",")]
    elif dec_content.startswith("["):
        dimension = 1
        real_content = dec_content[dimension:dec_content.find(",")]
    else:
        dimension = 0
        real_content = dec_content
    real_content = real_content.replace("-", "").replace("+", "")
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
    # print("args_list:",args_list)
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
    # print("real_args_list:",real_args_list)
    return real_args_list


def parse_dec_content(content: str, outmost_type: str, needful_variables: dict, known_dict: dict, middle_dict: dict):
    for match_var in re.finditer(r"[\w\(\)\[\]]+", content):
        var = match_var.group()
        match_sub_arr = re.match(r"(\w+)\[[0-9]+\]", var)
        if match_sub_arr:
            add_item(needful_variables, match_sub_arr.group(1), outmost_type+"[]", middle_dict)
            continue
        if var in known_dict and var not in needful_variables:
            needful_variables[var] = known_dict[var]
            if not outmost_type:
                outmost_type = known_dict[var]
            continue
        # TODO. What about nested APIs?
        match_for_call = re.match(regex_for_call, var)
        if match_for_call:
            api_name = match_for_call.group(1)
            api_args = match_for_call.group(2)
            if api_name in standard_api_dict:
                args_list = get_real_args_list(re.split(", |,", api_args))
                args_type = standard_api_dict[api_name].requireTypes
                # print("args_list:",args_list,"args_type:",args_type)
                for arg_name, arg_type in zip(args_list, args_type):
                    if "[" in arg_name and arg_name.endswith("]"):
                        arg_name = arg_name[:arg_name.index("[")]
                    add_item(needful_variables, arg_name, arg_type, middle_dict)
            continue
        add_item(needful_variables, var, outmost_type, middle_dict)


def add_var_dec(var_name: str, var_type: str, is_newtype):
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
    return tmp_var_dec_dict


def self_organizing_arr(var_name: str, var_dec_content: str, api_list: list, known_dict: dict):
    if var_dec_content.count("[") != var_dec_content.count("]"):
        return {}
    var_dec_dict = {}
    if var_dec_content == "[]":
        return {var_name: "'T[]"}
    if var_dec_content.startswith("[[") and var_dec_content.endswith("]]"):
        dimension = 2
        var_dec_content = var_dec_content[2:-2]
    elif var_dec_content.startswith("["):
        dimension = 1
        if var_dec_content.endswith("]"):
            var_dec_content = var_dec_content[1:-1]
        else:
            var_dec_content = var_dec_content[1:var_dec_content.rindex("]")]
    first_item = get_real_args_list(re.split(", |,", var_dec_content))[0]
    if first_item in known_dict:
        var_dec_dict[var_name] = known_dict[first_item] + "[]" * dimension
        return var_dec_dict
    tmp_type = is_basic_type(first_item)
    if tmp_type:
        var_dec_dict[var_name] = tmp_type + "[]" * dimension
        return var_dec_dict
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
    if first_item.startswith("(") and first_item.endswith(")"):
        tmp_type = ""
        for i in range(first_item.count(",")):
            tmp_type += "Int, "
        var_dec_dict[var_name] = "(Int, " + tmp_type[:-2] + ")" + "[]" * dimension
        return var_dec_dict
    else:
        return {}

def get_needful_var(arg: str, arg_type: str, var_dec_dict: dict, known_dict: dict, middle_dict: dict, needful_variables: dict):
    arg = arg.replace("Adjoint ", "")
    if "PROCESSED" in arg:
        return {}
    elif is_basic_type(arg):
        return {}
    elif arg in standard_api_dict:
        return {}
    elif arg.startswith("Microsoft.Quantum"):
        return {}
    elif arg == "_" or arg == "[]" or arg == "":
        return {}
    elif re.match(r"\w+\(.*\)", arg):
        return {}

    if ".." in arg and "[" not in arg:
        for word in re.split(r" \.\. |\.\.", arg):
            if word not in middle_dict and word not in var_dec_dict and word not in needful_variables and not word.isdigit():
                needful_variables[word] = "Int"
        return needful_variables

    if "::" in arg:
        arg = arg[:arg.find("::")]
    elif re.match(regex_for_sub_arr, arg):
        tmp_match = re.match(regex_for_sub_arr, arg)
        arr_name, arr_size = tmp_match.group(1), tmp_match.group(2)
        if ".." in arr_size:
            add_item(needful_variables, arr_name, arg_type, middle_dict)
        else:
            add_item(needful_variables, arr_name, arg_type+"[]", middle_dict)
        parse_dec_content(arr_size, "Int", needful_variables, known_dict, middle_dict)
        return needful_variables
    elif arg.endswith("!"):
        arg = arg.replace("!", "")

    if is_bool_expr(arg):
        items = re.split("==|!=|<=|>=| < | > ", arg)
        right_item_type = is_basic_type(items[1].strip())
        if right_item_type:
            arg = items[0].strip()
            arg_type = right_item_type

    if is_cal_expr(arg):
        for match in re.finditer(regex_for_arg, arg):
            real_arg = match.group()
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
        if arg in known_dict and "'" not in known_dict[arg]:
            arg_type = known_dict[arg]
        needful_variables[arg] = arg_type
    return needful_variables


def get_call_list(content: str):
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
                call_list.append(APICallInfo(call_name, call_args, call_str, functor))
                break
            find_index = call_end_index + 1
    return call_list


def process_functor(api_param: str, known_dict: dict):
    first_end = api_param.find(",")
    first_param = api_param[:first_end]
    api_param = api_param[first_end + 1:].strip()
    if first_param.startswith("[") and first_param.endswith("]"):
        real_first_param = first_param[1:-1]
        return get_needful_var(real_first_param, "Qubit", {}, known_dict, {}, {}), api_param
    else:
        real_first_param = first_param
        return get_needful_var(real_first_param, "Qubit[]", {}, known_dict, {}, {}), api_param


def get_all_call_name(one_block: CodeBlockInfo, stmt: str, known_dict: dict):
    api_call_list = get_call_list(stmt)
    if len(api_call_list) == 0:
        return []
    api_list = []
    needful_variables = {}
    for index, api_call in enumerate(api_call_list, start=1):
        this_api_name = api_call.api_name
        # print("api_name:"+this_api_name+"-")
        if "::" in this_api_name or this_api_name in known_dict:
            pass
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
        api_call.delete_api_call(api_call_list[index:])
        if api_call.functor == "Controlled " or api_call.functor == "Controlled":
            tmp_needful_variables, api_call.api_param = process_functor(api_call.api_param, known_dict)
            needful_variables.update(tmp_needful_variables)
        args_list = get_real_args_list(re.split(r",(?![^<]*>)", api_call.api_param))
        if api_call.api_name in standard_api_dict:
            api_list.append(api_call.api_name)
            args_type = standard_api_dict[api_call.api_name].requireTypes
            # print("---args type:", args_type)
            if len(args_type) == 0 or len(args_list) != len(args_type):
                continue
            for i in range(len(args_list)):
                arg_name = args_list[i].strip()
                arg_type = args_type[i]
                if arg_name.startswith("(") and not has_closed_brackets(arg_name):
                    arg_name = arg_name[1:]
                elif not arg_name.endswith("(") and not has_closed_brackets(arg_name):
                    arg_name = arg_name[:-1]
                # print("arg name:" + arg_name + " arg type:" + arg_type)
                needful_variables.update(
                    get_needful_var(arg_name, arg_type, one_block.var_dec_dict, known_dict, one_block.middle_dict, needful_variables))
                if arg_name in standard_api_dict:
                    tmp_import = "open " + standard_api_dict[arg_name].namespace + ";\n"
                    if tmp_import not in one_block.import_in_calls:
                        one_block.import_in_calls += tmp_import
        elif "::" in api_call.api_name:
            pass
        elif api_call.api_name in known_dict:
            api_list.append(api_call.api_name)
            op_type = remove_redundant_brackets(known_dict[api_call.api_name])
            op_inputs = re.split("=>|->", op_type)[0].strip()
            args_list = re.split(r",(?![^(]*\))", api_call.api_param)
            inputs_list = re.split(r",(?![^(]*\))", remove_redundant_brackets(op_inputs))
            for arg, input_str in zip(args_list, inputs_list):
                needful_variables.update(
                    get_needful_var(arg, input_str, one_block.var_dec_dict, known_dict, one_block.middle_dict, needful_variables))
        else:
            return []
    one_block.var_use_dict.update(needful_variables)
    return get_clear_list(api_list)


def parse_dec_stmt(one_block: CodeBlockInfo, known_dict: dict):
    tmp_needful_variables = one_block.get_middle_var()
    if is_first_part(one_block.content_str):
        is_complex_stmt = True
    else:
        is_complex_stmt = False
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
        # case 0: let (a, b) = (c, d);
        var_tuple = re.match(r"\((.*?)(, .*?)*\)", var_name_content)
        if var_tuple:
            for sub_match in re.finditer(regex_for_arg, var_name_content):
                var_dec_dict[sub_match.group()] = "'T"
            if var_dec_content.startswith("(") and var_dec_content.endswith(")"):
                var_dec_content = var_dec_content[1:-1]
                parse_dec_content(var_dec_content, "'T", needful_variables, known_dict, one_block.middle_dict)
                continue
        # case 1.1: new
        new_arr = re.match(regex_for_new, var_dec_content)
        if new_arr:
            var_dec_dict[var_name_content] = new_arr.group(1)+"[]"
            parse_dec_content(new_arr.group(2), "Int", needful_variables, known_dict, one_block.middle_dict)
            continue
        # case 1.2: [1,2,3]
        # print("---check var_dec_content:" + var_dec_content)
        if var_dec_content.startswith("["):
            var_dec_dict.update(self_organizing_arr(var_name_content, var_dec_content, api_list, known_dict))
            continue
        # case 1.3: array or subarray
        match_arr_item = re.match(regex_for_arr_item, var_dec_content)
        if match_arr_item:
            arr_name, arr_index = match_arr_item.group(1), match_arr_item.group(2)
            # print("match_arr_item:"+match_arr_item.group())
            if arr_name == "Qubit":
                var_dec_dict[var_name_content] = "Qubit[]"
            else:
                tmp_dict = merge_two_dict(known_dict, needful_variables)
                # print("tmp_dict:",tmp_dict)
                if arr_name in tmp_dict:
                    if ".." in arr_index:
                        var_type = tmp_dict[arr_name]
                    else:
                        var_type = tmp_dict[arr_name][:-2]
                    var_dec_dict[var_name_content] = var_type
            if arr_name in known_dict and arr_name not in needful_variables:
                needful_variables[arr_name] = known_dict[arr_name]
            parse_dec_content(arr_index, "Int", needful_variables, known_dict, one_block.middle_dict)
            continue
        # case 3: api call
        match_call = re.match(regex_for_call, var_dec_content)
        if match_call:
            real_var_dec_content = cut_proper_bracket(match_call.group())
            match_call = re.search(regex_for_call, real_var_dec_content)
            api_name = match_call.group(1)
            if api_name == "Qubit":
                var_dec_dict[var_name_content] = "Qubit"
            elif api_name in standard_api_dict:
                api_info = standard_api_dict[api_name]
                if api_info.callableType == "user":
                    var_dec_dict.update(add_var_dec(var_name_content, api_name, True))
                else:
                    var_dec_dict.update(add_var_dec(var_name_content, api_info.returnType, False))
                if api_info.namespace not in one_block.import_in_calls:
                    one_block.import_in_calls += "open " + api_info.namespace + ";\n"
                args_type = api_info.requireTypes
                args_list = get_real_args_list(re.split(", |,", match_call.group(2)))
                if len(args_type) > 0 and len(args_type) == len(args_list):
                    # print("---args_type:", args_type, " args_list:", args_list)
                    for arg_name, arg_type in zip(args_list, args_type):
                        if arg_name in standard_api_dict:
                            tmp_import = "open " + standard_api_dict[arg_name].namespace + ";\n"
                            if tmp_import in one_block.import_in_calls:
                                one_block.import_in_calls += tmp_import
                            continue
                        needful_variables.update(
                            get_needful_var(arg_name, arg_type, var_dec_dict, known_dict, one_block.middle_dict, needful_variables))
                        # print("+++needful_variables:",needful_variables)
                else:
                    one_block.var_dec_dict = None
                    one_block.var_use_dict = None
                    return None, None
                api_list.append(api_name)
            else:
                one_block.var_dec_dict = None
                one_block.var_use_dict = None
                return None, None
            continue
        # case 4: let a = b!;
        if var_dec_content.endswith("!"):
            # print(">>>var_dec_content:"+var_dec_content)
            real_var_dec_content = var_dec_content[:-1]
            if real_var_dec_content in known_dict:
                needful_variables[real_var_dec_content] = known_dict[real_var_dec_content]
            continue
        # case 5: let a = 0;
        basic_type = is_basic_type(var_dec_content)
        if basic_type:
            # print("situation3:"+var_dec_content+" "+basic_type)
            var_dec_dict[var_name_content] = basic_type
            continue
        # case 6: simple calculation
        is_inferred = False
        for known_var_name, known_var_type in known_dict.items():
            # print("===known_var_name:"+known_var_name+" known_var_type:"+known_var_type)
            if known_var_name in var_dec_content:
                if "[" in var_dec_content and "]" in var_dec_content:
                    var_dec_dict[var_name_content] = known_var_type.replace("[]", "")
                    is_inferred = True
                else:
                    var_dec_dict.update(add_var_dec(var_name_content, known_var_type, True))
                    is_inferred = True
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
    if not is_complex_stmt:
        one_block.var_dec_dict.update(var_dec_dict)
        one_block.var_use_dict.update(needful_variables)
    else:
        one_block.middle_dict.update(var_dec_dict)
        one_block.var_use_dict.update(minus_dict(needful_variables, var_dec_dict))
    return block_content, api_list
