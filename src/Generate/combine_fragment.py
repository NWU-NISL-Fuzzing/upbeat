import random
import ast
import re

from basic_operation.dict_operation import get_key_by_value, get_rest_args
from grammar_pattern.RandomGenerator import RandomGenerator
from class_for_info.fragment_info import CodeFragmentInfo
from basic_operation.file_operation import initParams
from DBOperation.dboperation_sqlite import DataBaseHandle
from Generate.grammar_pattern.APIOperator import APIOperator
from code_extractor.process_stmt import is_basic_type, get_real_args_list, get_call_list
from cons_generator.cwvp import has_cons, merge_cl_cons, generate_if_cons_exist

api_op = APIOperator()
standard_api_dict = api_op.init_api_dict("../ParseAPI/data/content.json")
params = initParams("../config.json")
need_a_qubit_array = [  'LittleEndian', 'BigEndian', 'PhaseLittleEndian', 'FixedPoint', 'SignedLittleEndian',
                        'LogicalRegister']


def generate_int(a, b):
    return random.randint(a, b)

def replace(param_name: str, arg_name: str, expr: str):
    """ 将约束语句中的形参名替换成变量/值 """

    # 如果形参名与实参名不同，将形参名替换为实参名
    if arg_name != param_name:
        expr = re.sub(r"\b"+param_name+r"\b", arg_name, expr)
        # print("expr:"+expr)
    return expr

def api_call_in_arg(api_name: str, arg_name: str, needful_variables: dict):
    match_length = re.search(api_name+r"\((\w+)!*\)", arg_name)
    if match_length and match_length.group(1) in needful_variables:
        return {match_length.group(1):needful_variables[match_length.group(1)]}

def get_arg_dict(arg_name, needful_variables):
    """ 对于IntAsBoolArray(F, Length(register))，arg_dict中存放的是F和register，但是arg_name需要是F和Length(register) """

    print("arg_name:",arg_name,"needful_variables:",needful_variables)
    # 情况1.实参是一个变量
    if arg_name in needful_variables:
        return {arg_name:needful_variables[arg_name]}
    # 情况2.实参是一个具体的值
    basic_type = is_basic_type(arg_name)
    if basic_type:
        return {"":basic_type}
    # 情况3.实参是API调用语句
    if "Length(" in arg_name:
        return api_call_in_arg("Length", arg_name, needful_variables)
    elif "LittleEndian(" in arg_name:
        return api_call_in_arg("LittleEndian", arg_name, needful_variables)
    elif "ResultArrayAsBoolArray(" in arg_name:
        return api_call_in_arg("ResultArrayAsBoolArray", arg_name, needful_variables)
    elif "Sqrt(" in arg_name:
        return api_call_in_arg("Sqrt", arg_name, needful_variables)
    # 情况4.实参是newtype变量访问语句
    match_access1 = re.fullmatch(r"(\w+)!*", arg_name)
    if match_access1 and match_access1.group(1) in needful_variables:
        return {match_access1.group(1):needful_variables[match_access1.group(1)]}
    # 情况5.实参是数学表达式
    match_calculation = re.fullmatch(r"([\w\.-]+)* *(\+|-|\*|/|\^) *(\w+)", arg_name)
    if match_calculation:
        tmp_arg_dict = {}
        if match_calculation.group(1) in needful_variables:
            tmp_arg_dict[match_calculation.group(1)] = needful_variables[match_calculation.group(1)]
        if match_calculation.group(3) in needful_variables:
            tmp_arg_dict[match_calculation.group(3)] = needful_variables[match_calculation.group(3)]
            return tmp_arg_dict
    # 情况6.实参是::访问表达式
    match_access2 = re.fullmatch(r"(\w+)::\w+", arg_name)
    if match_access2 and match_access2.group(1) in needful_variables:
        return {match_access2.group(1):needful_variables[match_access2.group(1)]}
    with open("20240115.txt", "a+") as f:
        f.write("arg_name:"+arg_name+" needful_variables:"+str(needful_variables)+"\n")
    return None

def replace_param_with_arg(param_dict, real_args_list, needful_variables, bool_expr_list, func_ret_list, quan_param):
    """ 将约束语句中的形参转换为实参 """

    print("===start to replace===")
    # print("param_dict:",param_dict,"arg_dict:",arg_dict)
    arg_dict, new_quan_param, reset_stmt = {}, [], ""
    # 先将bool_expr_list和func_ret_list拼接为字符串，避免再加一层循环
    bool_expr = " and ".join(bool_expr_list)
    func_ret = " and ".join(func_ret_list)
    print("bool_expr:"+bool_expr+" func_ret:"+func_ret)
    # 开始检查和替换
    for param_name, param_type, arg_name in zip(param_dict.keys(), param_dict.values(), real_args_list):
        # print("param_name:"+param_name)
        # 确定这个实参的类型
        tmp_arg_dict = get_arg_dict(arg_name, needful_variables)
        # 可能会失败
        if tmp_arg_dict is None:
            return ([], [], [], "", {})
            # continue
        elif len(tmp_arg_dict) == 0:
            return ([], [], [], "", {})
            # continue
        # 处理特殊情况
        # 如果是sqrt(a) >= 1.0，直接转换成a >= 1.0
        if arg_name.startswith("Sqrt("):
            arg_name = arg_name[5:-1]
        # 如果形参中是具体的类型，实参中推断的是泛型，替换arg_dict中的内容
        for real_arg_name, arg_type in tmp_arg_dict.items():
            in_cons = False
            # 如果在布尔表达式中
            if param_name in bool_expr:
                bool_expr = replace(param_name, arg_name, bool_expr)
                in_cons = True
            # 如果在特殊函数中
            if param_name in func_ret:
                func_ret = replace(param_name, arg_name, func_ret)
                in_cons = True
            # 如果在四元组中
            # print("param_name:",param_name," quan_param:",quan_param)
            if len(quan_param) > 0 and param_name == quan_param[0]:
                new_quan_param = [real_arg_name, arg_type]
                in_cons = True
            # 判断参数是否在约束语句中
            if not in_cons:
                continue
            # 添加到arg_dict中
            if "'" in arg_type and "'" not in param_type:
                arg_dict[real_arg_name] = param_type
            else:
                arg_dict[real_arg_name] = arg_type
            # 添加释放语句
            if arg_type == "Qubit":
                reset_stmt += "Reset("+real_arg_name+");\n"
            elif arg_type == "Qubit[]":
                reset_stmt += "ResetAll("+real_arg_name+");\n"
            elif arg_type in need_a_qubit_array and real_arg_name+"QubitArray" not in reset_stmt:
                reset_stmt += "ResetAll("+real_arg_name+"QubitArray);\n"
    print("=== finish to replace===")
    # print("bool_expr:",bool_expr," func_ret:",func_ret," new_quan_param:",new_quan_param)
    new_bool_expr_list = bool_expr.split(" and ")
    new_func_ret_list = func_ret.split(" and ")
    return (new_bool_expr_list, new_func_ret_list, new_quan_param, reset_stmt, arg_dict)

def get_contained_cons(frag_content: str, needful_variables: dict):
    """ 识别代码片段中的API调用语句，并提取约束语句 """
    
    # print("frag content:\n"+frag_content)
    # print("needful_variables:",needful_variables)
    bool_expr_list, func_ret_list, quan_param_list, arg_dict = [], [], [], {}
    reset_stmt = ""
    try:
        api_call_list = get_call_list(frag_content)
    except:
        api_call_list = []
    for api_call_info in api_call_list:
        # print("match:"+match_call.group())
        # api_name = match_call.group(1)
        api_name = api_call_info.api_name
        print("api:"+api_name+"-")
        param_str = api_call_info.api_param
        # 将复杂情况排除
        # if "(" in param_str or "[" in param_str or "!" in param_str or "_" in param_str:
        if "[" in param_str or "_" in param_str:
            continue
        # 使用has_cons获取约束
        cl_cons_result = has_cons("ClConsStmt", api_name)
        qt_cons_result = has_cons("QtConsStmt", api_name)
        # 如果没有约束，不执行下面的操作
        if len(cl_cons_result) == 0 and len(qt_cons_result) == 0:
            continue
        # 如果有约束，先对约束进行处理
        if len(cl_cons_result) > 0:
            this_bool_expr_list, this_func_ret_list, this_needful_args = merge_cl_cons(cl_cons_result)
        else:
            this_bool_expr_list, this_func_ret_list, this_needful_args = [], [], {}
        if len(qt_cons_result) > 0:
            qt_cons = qt_cons_result[0]
            quantum_param = ast.literal_eval(qt_cons[3])
        else:
            quantum_param = []
        # 从标准文档中获取API信息
        api = standard_api_dict[api_name]
        # 在这里只获取参数列表real_args_list，不遍历实参
        real_args_list = get_real_args_list(re.split(r",(?![^<]*>)", param_str))
        # 获取形参
        param_dict = api.get_api_args()
        print(">>>real_args_list:",real_args_list,"param_dict:", param_dict)
        # 开始替换
        if len(param_dict) == len(real_args_list):
            result = replace_param_with_arg(param_dict, real_args_list, needful_variables, 
                                            this_bool_expr_list, this_func_ret_list, quantum_param)
            bool_expr_list.extend(result[0])
            func_ret_list.extend(result[1])
            if len(qt_cons_result) > 0:
                quan_param_list.append((qt_cons[0], qt_cons[1], qt_cons[2], result[2]))
            reset_stmt += result[3]
            arg_dict.update(result[4])
    return bool_expr_list, func_ret_list, quan_param_list, arg_dict, reset_stmt

class CodeFragmentGenerator:
    def __init__(self, level:int, table_name: str):
        self.level = level
        self.rand_gen = RandomGenerator("../config.json")
        self.generic_to_concrete = ["Int", "Double", "Bool"]
        self.corpus_handler = DataBaseHandle(params["corpus_db"])
        self.self_defined_callables = []
        self.available_variables = {}
        self.table_name = table_name

    def get_stmt_by_var(self, var_name: str, var_type: str, last_fragment: str):
        """ 尝试拼接其他代码块，通过self.level指定次数，注意是次数不是层数 """

        # print("调用getStmtByVar："+var_name+"-"+var_type)
        final_fragment, final_import, final_reset = "", "",""
        # 如果level已经为0，直接随机生成
        if self.level <= 0:
            tmp_fragment = self.rand_gen.generate_random(var_name, var_type)
            if tmp_fragment is None:
                print("can not gen1:"+var_name+" "+var_type)
                return None, None, None, None
            else:
                final_fragment += tmp_fragment
            if len(self.rand_gen.defined_call) > 0:
                self.self_defined_callables.extend(self.rand_gen.defined_call)
            if len(self.rand_gen.needful_namespace) > 0:
                tmp_namespace = self.rand_gen.needful_namespace
                if "open " not in tmp_namespace:
                    final_import += "open " + tmp_namespace + ";\n"
                else:
                    final_import += tmp_namespace
                # print("===check namespace:\n" + tmp_namespace)
            return final_fragment, final_import, last_fragment, final_reset
        # 开始查找可拼接的片段
        sql = "SELECT * FROM " + self.table_name + " WHERE Available_variables LIKE '%''" + var_type + \
             "''%' and Available_variables NOT LIKE '%''" + var_name + \
             "''%' and Needful_variables NOT LIKE '%''" + var_name + "''%';"
        # ***仅拼接代码片段时使用下面语句
        # sql = "SELECT * FROM " + self.table_name + " WHERE Available_variables LIKE '%''" + var_type + \
        #      "''%' and Available_variables NOT LIKE '%''" + var_name + \
        #      "''%' and Needful_variables NOT LIKE '%''" + var_name + \
        #      "''%' and Fragment_content NOT LIKE '%//correct%' and Fragment_content NOT LIKE '%//wrong%';"
        # sql = "SELECT * FROM CodeFragment where id = 2869;"
        # print("check sql:"+sql)
        available_fragment_list = self.corpus_handler.selectAll(sql)
        # 如果存在可拼接的片段
        if len(available_fragment_list) > 0:
            self.level -= 1
            # 选择下一个要拼接的代码片段
            # choice = 0
            choice = generate_int(0, len(available_fragment_list) - 1)
            # 获取该片段各列的内容
            added_fragment = available_fragment_list[choice]
            added_fragment_content = added_fragment[1]
            available_variables = ast.literal_eval(added_fragment[2])
            # print("检查可用变量字典：", available_variables)
            # 根据需要的类型查找变量名
            try:
                new_var_name = get_key_by_value(available_variables, var_type)
            except:
                return None, None, None, None
            # 检查两个片段中是否包含相同的变量声明，如果存在，则删除后面一个
            for arg_name in available_variables.keys():
                regex = "(let|mutable|use) "+arg_name+" ?= ?(.*?);\n"
                match = re.search(regex, last_fragment)
                if match:
                    last_fragment = last_fragment.replace(match.group(), "")
            # 生成拼接的代码片段所需的参数
            needful_variables = ast.literal_eval(added_fragment[3])
            # ！！！检查这里
            bool_expr_list, func_ret_list, quanternion_list, needful_args, partial_reset_stmt = \
                get_contained_cons(added_fragment_content, needful_variables)
            # ***仅拼接代码片段时使用下面语句
            bool_expr_list, func_ret_list, quanternion_list, needful_args, partial_reset_stmt = \
                [], [], [], {}, ""
            # 如果存在约束，生成相关变量，否则不生成
            if len(bool_expr_list) > 0 or len(func_ret_list) > 0 or len(quanternion_list) > 0:
                correct_stmt, wrong_stmt = \
                    generate_if_cons_exist(bool_expr_list, func_ret_list, quanternion_list, needful_args)
            else:
                correct_stmt, wrong_stmt = "//no cons\n", "//no cons\n"
            print("correct_stmt",correct_stmt,"wrong_stmt",wrong_stmt)
            # 如果生成失败
            if correct_stmt is None:
                return  None, None, None, None
            final_fragment += correct_stmt
            final_reset += partial_reset_stmt
            # 生成其他变量
            needful_variables = get_rest_args(needful_variables, needful_args)
            generic_sign = {}
            for a_var_name, a_var_type in needful_variables.items():
                # 处理泛型
                for match in re.finditer("'[A-Za-z]+", a_var_type):
                    if match.group() in generic_sign:
                        a_var_type = a_var_type.replace(match.group(), generic_sign[match.group()])
                    else:
                        a_new_type = random.choice(self.generic_to_concrete)
                        a_var_type = a_var_type.replace(match.group(), a_new_type)
                        generic_sign[match.group()] = a_new_type
                # 开始生成
                tmp_fragment = self.rand_gen.generate_random(a_var_name, a_var_type)
                if a_var_type == "Qubit":
                    tmp_reset = "Reset(" + a_var_name + ");\n"
                elif a_var_type == "Qubit[]":
                    tmp_reset = "ResetAll(" + a_var_name + ");\n"
                else:
                    tmp_reset = ""
                if not tmp_fragment:
                    print("can not gen2:"+a_var_name+" "+a_var_type)
                    return None, None, None, None
                final_fragment += tmp_fragment
                final_reset += tmp_reset
            # 添加拼接的代码片段、可用变量以及需要引入的命名空间
            final_fragment += added_fragment_content
            if var_name != new_var_name:
                final_fragment += "let "+var_name+" = "+new_var_name+";\n"
            final_import += added_fragment[4]
            self.available_variables.update(available_variables)
        # 没有可拼接的代码片段，则需要生成随机值
        else:
            tmp_fragment = self.rand_gen.generate_random(var_name, var_type)
            if tmp_fragment:
                final_fragment += tmp_fragment
            else:
                return None, None, None, None
        # 添加随机生成过程中使用的自定义函数和命名空间
        if len(self.rand_gen.defined_call) > 0:
            self.self_defined_callables.extend(self.rand_gen.defined_call)
        if len(self.rand_gen.needful_namespace) > 0:
            tmp_namespace = self.rand_gen.needful_namespace
            if "open " not in tmp_namespace:
                final_import += "open " + tmp_namespace + ";\n"
            else:
                final_import += tmp_namespace
        # print("---final_import:\n"+final_import)
        return final_fragment, final_import, last_fragment, final_reset

    def select_corpus(self, n=-1):
        """ 根据指定id/随机读取一个代码片段的信息 """

        if n == -1:
            sql = "SELECT * FROM CodeFragment ORDER BY RANDOM() LIMIT 1;"
        else:
            sql = "SELECT * FROM CodeFragment WHERE ID ="+str(n)+";"
        # print(self.corpus_handler.selectAll(sql))
        one_fragment = self.corpus_handler.selectAll(sql)[0]
        # print(one_fragment)
        # print("n:",n)
        # one_fragment = all_fragment_record[n]
        # 新表
        if len(one_fragment) == 7:
            one_fragment_info = CodeFragmentInfo(one_fragment[1], ast.literal_eval(one_fragment[2]),
                                                ast.literal_eval(one_fragment[3]), one_fragment[4], 
                                                one_fragment[5], one_fragment[6])
        # 旧表
        elif len(one_fragment) == 6:
            one_fragment_info = CodeFragmentInfo(one_fragment[1], ast.literal_eval(one_fragment[2]),
                                                 ast.literal_eval(one_fragment[3]), one_fragment[4], 
                                                 "", one_fragment[5])
        return one_fragment_info

    def generate_a_code_frag(self, one_fragment_info: CodeFragmentInfo):
        final_fragment, final_import, final_reset = "", "", ""
        last_fragment = one_fragment_info.fragment_content
        self.available_variables.clear()
        # 用于将泛型进行统一替换
        generic_sign = {}
        for var_name, var_type in one_fragment_info.needful_variables.items():
            # print("---needful var:" + var_name + "-" + var_type)
            # 如果是泛型，使用基础类型进行替换，并且保证一致性
            for match in re.finditer("'[A-Za-z]+", var_type):
                if match.group() in generic_sign:
                    var_type = var_type.replace(match.group(), generic_sign[match.group()])
                else:
                    new_type = random.choice(self.generic_to_concrete)
                    var_type = var_type.replace(match.group(), new_type)
                    generic_sign[match.group()] = new_type
                # print("here is a generic type, after process:"+var_name+"-"+var_type)
            # 组装片段或生成随机值
            this_fragment, this_import, last_fragment, this_reset = self.get_stmt_by_var(var_name, var_type, last_fragment)
            if not this_fragment:
                return None, None
            # 如果是Qubit、Qubit[]或者需要量子比特数组的类型，添加reset操作
            print("===var_name:"+var_name+" var_type:"+var_type)
            if var_type == "Qubit":
                final_reset += "Reset(" + var_name + ");\n"
            elif var_type == "Qubit[]":
                final_reset += "ResetAll(" + var_name + ");\n"
            # 20240126-需要检查该变量是否由另一个代码片段传入，如果是，不需要释放
            elif var_type in need_a_qubit_array and var_name+"QubitArray" in final_fragment:
                final_reset += "ResetAll(" + var_name + "QubitArray);\n"
            # 将生成的变量声明/代码片段添加到final_fragment中
            final_fragment += this_fragment
            final_import += this_import
            final_reset += this_reset
        # 添加该代码片段
        final_fragment += last_fragment
        # 从源码或官方文档中截取，需要给包含量子电路的片段添加输出语句
        if "DumpMachine" not in final_fragment and "use " in final_fragment:
            final_fragment += "DumpMachine();\n"
        # 添加新生成变量的输出和释放语句
        for var_name, var_type in one_fragment_info.available_variables.items():
            # print("~~~available var:"+var_name+" "+var_type)
            if var_type == "Qubit":
                final_reset += "Reset(" + var_name + ");\n"
            elif var_type == "Qubit[]":
                final_reset += "ResetAll(" + var_name + ");\n"
            elif var_type not in need_a_qubit_array and "(" not in var_name:
                final_fragment += "Message($\"{" + var_name + "}\");\n"
        for var_name, var_type in self.available_variables.items():
            if var_type == "Qubit":
                final_reset += "Reset(" + var_name + ");\n"
            elif var_type == "Qubit[]":
                final_reset += "ResetAll(" + var_name + ");\n"
        # 添加reset操作
        final_fragment += final_reset
        # print(final_fragment)
        final_import += one_fragment_info.needful_imports
        # print("---final_import:\n"+final_import)
        # 把代码片段需要的自定义函数添加
        self.self_defined_callables.append(one_fragment_info.defined_callables)
        return final_fragment, final_import


if __name__ == '__main__':
    c = CodeFragmentGenerator(1, "CodeFragment_CW")
    # print(c.generate_a_code_frag(417)[0])
    res = c.select_corpus(326)
    final_fragment, final_import = c.generate_a_code_frag(res)
    print(final_fragment+"\n"+final_import)
