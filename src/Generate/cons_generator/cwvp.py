import traceback
import random
import ast
import re

from DBOperation.save import save_into_db
from DBOperation.dboperation_sqlite import DataBaseHandle
from basic_operation.file_operation import add_to_write, delete_existing, initParams
from basic_operation.dict_operation import get_rest_args
from grammar_pattern.RandomGenerator import RandomGenerator
from grammar_pattern.API import API
from grammar_pattern.APIOperator import APIOperator
from class_for_info.fragment_info import CodeFragmentInfo
from class_for_info.boundary_info import BoundaryInfo
from cons_generator.generate_by_fact import GenerateCorrectAndWrong
from cons_generator.generate_by_assert import *
from cons_generator.parse_boundary_expr import change_generic, process_bool_expr
from cons_generator.solve_by_z3 import cl_cwvp_by_z3, merge_cl_cons

params = initParams("../config.json")
reference_db = DataBaseHandle(params["reference_db"])
randomVal = RandomGenerator(params["work_dir"]+"/config.json")
standard_api_dict = APIOperator().init_api_dict(params["work_dir"]+"/ParseAPI/data/content_all.json")
standard_api_list = APIOperator().get_func_and_op(params["work_dir"]+"/ParseAPI/data/content.json")

available_newtype = ['LittleEndian', 'BigEndian', 'PhaseLittleEndian', 'Complex', 'ComplexPolar',
                     'FixedPoint', 'GeneratorIndex', 'RotationPhases', 'ReflectionPhases', 
                     'SingleQubitClifford', 'Fraction', 'BigFraction', 'CCNOTop', 'SamplingSchedule', 
                     'TrainingOptions', 'LabeledSample', 'GeneratorSystem', 'SequentialModel',
                     'ControlledRotation', 'ReflectionOracle', 'ObliviousOracle']
need_a_qubit_array = ['LittleEndian', 'BigEndian', 'PhaseLittleEndian', 'FixedPoint']

def has_cons(table_name: str, api_name: str):
    """ 判断是否含有量子/经典约束 """

    # 快捷查找
    if api_name in ["Length", "LittleEndian", "BigEndian", "PhaseLittleEndian", "ResetAll", "Reset"]:
        return []
    # 否则再查询数据库
    sql = "select * from "+table_name+" where func_name='"+api_name+"'"
    # print("sql:"+sql)
    try:
        data_list = reference_db.selectAll(sql)
        return data_list
    except:
        traceback.print_exc()
    return None

def cl_cwvp_by_tree(bool_expr: str, args_dict: dict):
    """ 根据经典约束表达式以及参数信息生成正确/错误声明语句 """

    generator = GenerateCorrectAndWrong()
    correct_stmt, wrong_stmt = "//valid\n", "//invalid\n"
    # correct_stmt, wrong_stmt = "", ""

    # Get the ConstraintTreeList instance.
    # print("===bool_expr:" + bool_expr)
    cons = process_bool_expr(bool_expr)
    cons.argsDict = args_dict
    logicalOp = cons.logicalOp

    # If there is no logical symbol, or it is OR, take only one expression.
    if logicalOp == "" or logicalOp == "or":
        one_cons_tree = random.choice(cons.treeList)
        tmp_correct_stmt, tmp_wrong_stmt = generator.generate_value_pair(one_cons_tree, cons.argsDict, False, True)
        correct_stmt += tmp_correct_stmt
        wrong_stmt += tmp_wrong_stmt
    # If the logical symbol is and, only the correct values need to traverse all trees, wrong values only traverse one.
    else:
        # 获取一个约束树并将该约束树从all_tree_list中移除
        # rand = random.randint(0, len(generator.all_tree_list)-1)
        # rand = 0
        rand = len(cons.treeList) - 1
        one_cons_tree = cons.treeList[rand]
        # 针对该约束树进行生成，只在生成最后一棵树时生成复杂变量
        # print("generate cw tree:")
        # one_cons_tree.printAll()
        if rand == 0:
            tmp_correct_stmt, tmp_wrong_stmt = generator.generate_value_pair(one_cons_tree, cons.argsDict, 
                                                                             False, True)
        else:
            tmp_correct_stmt, tmp_wrong_stmt = generator.generate_value_pair(one_cons_tree, cons.argsDict, 
                                                                             False, False)
        correct_stmt += tmp_correct_stmt
        wrong_stmt += tmp_wrong_stmt
        # 已针对树列表中的一棵进行生成，接下来只需要生成正确的值
        i = 0
        for one_cons_tree in reversed(cons.treeList[:-1]):
            # print("generate always true tree:")
            # one_cons_tree.printAll()
            # 只在生成最后一棵树时生成复杂变量
            if i == len(cons.treeList) - 2:
                tmp_correct_stmt, tmp_wrong_stmt = generator.generate_value_pair(one_cons_tree, cons.argsDict, True,
                                                                                 True)
            else:
                tmp_correct_stmt, tmp_wrong_stmt = generator.generate_value_pair(one_cons_tree, cons.argsDict, True,
                                                                                 False)
            # print("==tmp_correct_stmt:\n"+tmp_correct_stmt+"==tmp_wrong_stmt:\n"+tmp_wrong_stmt)
            # 如果有?|表达式，尽量往后放
            if "?" in tmp_correct_stmt:
                correct_stmt += tmp_correct_stmt
                wrong_stmt += tmp_wrong_stmt
            else:
                correct_stmt = tmp_correct_stmt+correct_stmt
                wrong_stmt = tmp_wrong_stmt+wrong_stmt
            i += 1
    # 对特殊的符号进行替换
    correct_stmt = correct_stmt.replace("**", "^").replace("<<", "<<<")
    wrong_stmt = wrong_stmt.replace("**", "^").replace("<<", "<<<")
    # print("==correct:\n"+correct_stmt+"==wrong:\n"+wrong_stmt)
    return correct_stmt, wrong_stmt

def qt_cwvp_by_quaternion(assert_stmt: str, arg_name: str, arg_type: str, already_gen: dict):
    """ 根据量子约束表达式以及参数信息生成正确/错误声明语句 """

    # 如果变量没有在经典约束部分被声明，在此处生成
    # print(">>>already_gen:",already_gen,"arg_name:",arg_name,"arg_type:",arg_type)
    correct_stmt, wrong_stmt = "//valid\n", "//invalid\n"
    if arg_name in already_gen.keys() and arg_type == already_gen[arg_name]:
        pass
    else:
        tmp_stmt = generate_qubit_dec(arg_name, arg_type)
        correct_stmt += tmp_stmt
        wrong_stmt += tmp_stmt
    # 获取四元组
    base, result, prob, tol = ast.literal_eval(assert_stmt)
    if (result == "One" and prob == "0.0") or (result == "Zero" and prob == "1.0"):
        flag = True
    else:
        flag = False
    # 生成正确和错误的语句
    rotation_or_gate = random.choice([0,1,2])
    if rotation_or_gate == 0:
        correct_stmt += rotate_by_fixed_angle(flag, base, arg_name, arg_type)
        wrong_stmt += rotate_by_fixed_angle(not flag, base, arg_name, arg_type)
    elif rotation_or_gate == 1:
        correct_stmt += rotate_by_calculated_angle(flag, base, prob, tol, arg_name, arg_type)
        wrong_stmt += rotate_by_calculated_angle(not flag, base, prob, tol, arg_name, arg_type)
    else:
        correct_stmt += add_gate(flag, base, arg_name, arg_type)
        wrong_stmt += add_gate(not flag, base, arg_name, arg_type)
    return correct_stmt, wrong_stmt

def generate_if_cons_exist(bool_expr_list, func_ret_list, qt_cons, arg_dict):
    """ 根据给定的经典和量子约束，生成代码片段 """

    # print("===bool_expr_list:",bool_expr_list,"\n===func_ret_list",func_ret_list)
    # print("===arg_dict:",arg_dict)
    # 存放最终代码片段的变量
    # correct_stmt, wrong_stmt = "//valid\n", "//invalid\n"
    correct_stmt, wrong_stmt = "", ""
    # 存放已声明变量，如果同时存在经典和量子约束，避免重复声明部分变量
    already_gen = {}
    correct_has_failed, wrong_has_failed = False, False
    # 如果含有经典约束，生成相关变量的声明语句
    if len(bool_expr_list) > 0:
        # 如果包含?|或者<<或者::，还是使用原来的方法进行生成
        bool_expr = " and ".join(bool_expr_list)
        # 筛选掉一些复杂约束
        if "SequenceI" in bool_expr:
            arg_dict.clear()
        elif "?" in bool_expr or "<<" in bool_expr or "::" in bool_expr or "**" in bool_expr:
            # print("^^^old method")
            tmp_correct_stmt, tmp_wrong_stmt = cl_cwvp_by_tree(bool_expr, arg_dict)
            correct_stmt += tmp_correct_stmt
            wrong_stmt += tmp_wrong_stmt
            if len(func_ret_list) > 0 and func_ret_list[0] != "":
                final_valid_list, final_invalid_list, already_gen = cl_cwvp_by_z3([], func_ret_list, arg_dict)
                correct_stmt += final_valid_list[0][0]
                wrong_stmt += final_invalid_list[0][0]
        else:
            # print("^^^new method")
            final_valid_list, final_invalid_list, already_gen = cl_cwvp_by_z3(bool_expr_list, func_ret_list, arg_dict)
            if len(final_valid_list) > 0:
                correct_stmt += final_valid_list[0][0]
            else:
                correct_has_failed = True
            if len(final_invalid_list) > 0:
                wrong_stmt += final_invalid_list[0][0]
            else:
                wrong_has_failed = True
        # already_gen.update(arg_dict)
    # TODO.没有合并，只有一个参数的信息
    # 如果含有量子约束，生成相关变量的声明语句
    # print("===qt_cons:",qt_cons)
    if len(qt_cons) > 0 and len(qt_cons[0]) > 0:
        # 开始生成正确/错误操作语句
        # print("qt_cons:",qt_cons)
        arg_info = qt_cons[0][3]
        if len(arg_info) > 0:
            if type(arg_info) == str:
                arg_name, arg_type = ast.literal_eval(arg_info)
            else:
                arg_name, arg_type = arg_info
            tmp_correct_stmt, tmp_wrong_stmt = qt_cwvp_by_quaternion(qt_cons[0][2], arg_name, arg_type, already_gen)
            correct_stmt += tmp_correct_stmt
            wrong_stmt += tmp_wrong_stmt
            # already_gen.update({arg_name: arg_type})
    # print("correct_has_failed:",correct_has_failed,"wrong_has_failed:",wrong_has_failed)
    # print("already_gen:",already_gen)
    if not correct_has_failed and wrong_has_failed:
        return correct_stmt, None
    elif correct_has_failed and not wrong_has_failed:
        return None, wrong_stmt
    elif correct_has_failed and wrong_has_failed:
        return None, None
    return correct_stmt, wrong_stmt

def generate_context_for_api(api_info: API):
    """ 生成引入语句、API调用语句、输出语句和释放语句 """

    # 获取API相关信息
    standard_api_args = api_info.get_api_args()
    api_namespace = api_info.namespace
    api_name = api_info.name
    # 构建open语句
    open_stmt = "open " + api_namespace + ";\n"
    # 如果存在Qubit、Qubit[]或者可生成的newtype类型，添加Reset操作以及所需的open语句
    reset_stmt, tmp_stmt = "", ""
    for var_name, var_type in standard_api_args.items():
        if var_type == "Qubit":
            reset_stmt += "Reset(" + var_name + ");\n"
        elif var_type == "Qubit[]":
            reset_stmt += "ResetAll(" + var_name + ");\n"
        elif var_type in need_a_qubit_array:
            reset_stmt += "ResetAll(" + var_name + "QubitArray);\n"
        elif (var_type in available_newtype) and (
                standard_api_dict[var_type].namespace not in open_stmt):
            open_stmt += "open " + standard_api_dict[var_type].namespace + ";\n"
    # 开始构造调用语句
    if len(standard_api_args) > 0:
        call_stmt = "mutable APIResult = " + api_name + "("
        for var_name in standard_api_args.keys():
            call_stmt += var_name + ", "
        call_stmt = call_stmt[:-2] + ");\n"
    else:
        call_stmt = "mutable APIResult = " + api_name + "();"
    # 对结果进行输出
    if "Unit" in api_info.returnType:
        output_stmt = "DumpMachine();\n"
    else:
        output_stmt = "Message($\"{APIResult}\");\n"
    return open_stmt, call_stmt, reset_stmt, output_stmt

api_count, api_cons_count = 0, 0

def generate_fragment_cs(api_info):
    """ 给定一个API的信息，生成仅含调用语句的代码片段 """

    global api_count, api_cons_count

    result_list = []
    bool_expr_list, func_ret_list, arg_dict = [], [], {}
    # 查询数据库中是否存在有关该API的约束，如果有的话，生成相关内容
    cl_cons_result = has_cons("ClConsStmt", api_info.name)
    if len(cl_cons_result) > 0:
        bool_expr_list, func_ret_list, arg_dict = merge_cl_cons(cl_cons_result)
        # print("===bool_expr_list:",bool_expr_list,"\n===func_ret_list:",func_ret_list)
    qt_cons_result = has_cons("QtConsStmt", api_info.name)
    # TODO.这里的四元组传的格式是一致的吗？
    if len(qt_cons_result) > 0:
        correct_stmt, wrong_stmt = generate_if_cons_exist(bool_expr_list, func_ret_list, qt_cons_result, arg_dict)
    else:
        correct_stmt, wrong_stmt = generate_if_cons_exist(bool_expr_list, func_ret_list, [], arg_dict)
    # TODO.合理/不合理有一个生成了一个没生成的情况直接舍弃了
    if correct_stmt is None or wrong_stmt is None:
        return []
    # 获取API所需的参数
    standard_api_args = api_info.get_api_args()
    rest_args = get_rest_args(standard_api_args, arg_dict)
    # 生成未声明变量的声明语句
    if len(arg_dict) == 0:
        correct_stmt += "//no cons\n"
        wrong_stmt += "//no cons\n"
    else:
        api_cons_count += 1
        # with open("have_cons.txt", "a+") as f:
        #     f.write(api_info.name+"\n")
    other_arg_dec, concrete_reset_stmt = "", ""
    concrete_type_dict = {} # {泛型:对应的具体类型}
    for var_name, var_type in rest_args.items():
        # print("0generate rest args:" + var_name + "-" + var_type+"-")
        # 先对泛型进行替换
        if "'" in var_type:
            generic_type_matches = re.finditer("'\w+", var_type)
            for generic_type_match in generic_type_matches:
                generic_type = generic_type_match.group()
                # print("generic_type:"+generic_type)
                if generic_type in concrete_type_dict:
                    var_type = var_type.replace(generic_type, concrete_type_dict[generic_type])
                    continue
                if "->" in var_type and "=>" not in var_type:
                    concrete_type = random.choice(["Int", "BigInt", "Double", "Bool", "Pauli", "Result"])
                elif "->" not in var_type and "=>" in var_type:
                    concrete_type = "Qubit"
                elif "->" not in var_type and "=>" not in var_type:
                    concrete_type = random.choice(["Int", "BigInt", "Double", "Bool", "Pauli", "Result", "Qubit"])
                else:
                    return []
                var_type = var_type.replace(generic_type, concrete_type)
                concrete_type_dict[generic_type] = concrete_type
                # print("concrete_type_dict:",concrete_type_dict)
            # 如果泛型替换成了Qubit，还需要添加对应的Reset语句
            if var_type == "Qubit":
                concrete_reset_stmt += "Reset("+var_name+");\n"
            elif var_type == "Qubit[]":
                concrete_reset_stmt += "ResetAll("+var_name+");\n"
        # 生成变量声明语句
        # print("1generate rest args:" + var_name + "-" + var_type+"-")
        other_arg_dec = randomVal.generate_random(var_name, var_type)
        # print("==check other_arg_dec:", other_arg_dec)
        if other_arg_dec:
            correct_stmt += other_arg_dec
            wrong_stmt += other_arg_dec
        else:
            break
    # 如果生成失败，直接跳过
    if other_arg_dec is None:
        return []

    # 生成上下文需要的语句
    open_stmt, call_stmt, reset_stmt, output_stmt = generate_context_for_api(api_info)
    # 生成自定义函数
    defined_call_str = ""
    for call in randomVal.defined_call:
        if isinstance(call, str):
            defined_call_str += call
        else:
            defined_call_str += call.content
    randomVal.defined_call.clear()
    # 整合所有语句
    if correct_stmt == wrong_stmt:
        final_stmt = correct_stmt+call_stmt+reset_stmt+concrete_reset_stmt+output_stmt
        code_fragment = CodeFragmentInfo(final_stmt, standard_api_args, {}, open_stmt,
                                    defined_call_str, "QuantumConsStmt").format_to_save()
        # print("code_fragment:\n",final_stmt,"\n",defined_call_str)
        result_list.append(code_fragment)
    else:
        final_stmt1 = correct_stmt+call_stmt+reset_stmt+concrete_reset_stmt+output_stmt
        final_stmt2 = wrong_stmt+call_stmt+reset_stmt+concrete_reset_stmt+output_stmt
        code_fragment1 = CodeFragmentInfo(final_stmt1, standard_api_args, {}, open_stmt,
                                    defined_call_str, "QuantumConsStmt").format_to_save()
        code_fragment2 = CodeFragmentInfo(final_stmt2, standard_api_args, {}, open_stmt,
                                    defined_call_str, "QuantumConsStmt").format_to_save()
        # print("code_fragment1:\n",final_stmt1,"\n",defined_call_str)
        # print("code_fragment2:\n",final_stmt2,"\n",defined_call_str)
        result_list.append(code_fragment1)
        result_list.append(code_fragment2)
    # 对成功生成代码片段的API进行计数
    api_count += 1
    return result_list

def select_all():
    """ 遍历所有API进行生成 """
    
    result_list = []
    # 遍历所有API
    for api_info in standard_api_list:
    # for api_info in [standard_api_dict["Padded"]]:
        result_list.extend(generate_fragment_cs(api_info))
        # break
    save_into_db(params["corpus_db"], "CodeFragment_CS", result_list)
    # print("Finish!api count:"+str(api_count)+" api cons count:"+str(api_cons_count))

if __name__ == "__main__":
    select_all()
    # print(has_cons("QtConsStmt", "SquareSI"))
