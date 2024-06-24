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
    if api_name in ["Length", "LittleEndian", "BigEndian", "PhaseLittleEndian", "ResetAll", "Reset"]:
        return []
    sql = "select * from "+table_name+" where func_name='"+api_name+"'"
    try:
        data_list = reference_db.selectAll(sql)
        return data_list
    except:
        traceback.print_exc()
    return None

def cl_cwvp_by_tree(bool_expr: str, args_dict: dict):
    generator = GenerateCorrectAndWrong()
    correct_stmt, wrong_stmt = "//valid\n", "//invalid\n"

    # Get the ConstraintTreeList instance.
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
        rand = len(cons.treeList) - 1
        one_cons_tree = cons.treeList[rand]
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
        i = 0
        for one_cons_tree in reversed(cons.treeList[:-1]):
            # print("generate always true tree:")
            # one_cons_tree.printAll()
            if i == len(cons.treeList) - 2:
                tmp_correct_stmt, tmp_wrong_stmt = generator.generate_value_pair(one_cons_tree, cons.argsDict, True,
                                                                                 True)
            else:
                tmp_correct_stmt, tmp_wrong_stmt = generator.generate_value_pair(one_cons_tree, cons.argsDict, True,
                                                                                 False)
            # print("==tmp_correct_stmt:\n"+tmp_correct_stmt+"==tmp_wrong_stmt:\n"+tmp_wrong_stmt)
            if "?" in tmp_correct_stmt:
                correct_stmt += tmp_correct_stmt
                wrong_stmt += tmp_wrong_stmt
            else:
                correct_stmt = tmp_correct_stmt+correct_stmt
                wrong_stmt = tmp_wrong_stmt+wrong_stmt
            i += 1
    correct_stmt = correct_stmt.replace("**", "^").replace("<<", "<<<")
    wrong_stmt = wrong_stmt.replace("**", "^").replace("<<", "<<<")
    # print("==correct:\n"+correct_stmt+"==wrong:\n"+wrong_stmt)
    return correct_stmt, wrong_stmt

def qt_cwvp_by_quaternion(assert_stmt: str, arg_name: str, arg_type: str, already_gen: dict):
    # print(">>>already_gen:",already_gen,"arg_name:",arg_name,"arg_type:",arg_type)
    correct_stmt, wrong_stmt = "//valid\n", "//invalid\n"
    if arg_name in already_gen.keys() and arg_type == already_gen[arg_name]:
        pass
    else:
        tmp_stmt = generate_qubit_dec(arg_name, arg_type)
        correct_stmt += tmp_stmt
        wrong_stmt += tmp_stmt
    base, result, prob, tol = ast.literal_eval(assert_stmt)
    if (result == "One" and prob == "0.0") or (result == "Zero" and prob == "1.0"):
        flag = True
    else:
        flag = False
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
    correct_stmt, wrong_stmt = "", ""
    already_gen = {}
    correct_has_failed, wrong_has_failed = False, False
    if len(bool_expr_list) > 0:
        bool_expr = " and ".join(bool_expr_list)
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
    if len(qt_cons) > 0 and len(qt_cons[0]) > 0:
        arg_info = qt_cons[0][3]
        if len(arg_info) > 0:
            if type(arg_info) == str:
                arg_name, arg_type = ast.literal_eval(arg_info)
            else:
                arg_name, arg_type = arg_info
            tmp_correct_stmt, tmp_wrong_stmt = qt_cwvp_by_quaternion(qt_cons[0][2], arg_name, arg_type, already_gen)
            correct_stmt += tmp_correct_stmt
            wrong_stmt += tmp_wrong_stmt
    if not correct_has_failed and wrong_has_failed:
        return correct_stmt, None
    elif correct_has_failed and not wrong_has_failed:
        return None, wrong_stmt
    elif correct_has_failed and wrong_has_failed:
        return None, None
    return correct_stmt, wrong_stmt

def generate_context_for_api(api_info: API):
    standard_api_args = api_info.get_api_args()
    api_namespace = api_info.namespace
    api_name = api_info.name
    open_stmt = "open " + api_namespace + ";\n"
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
    if len(standard_api_args) > 0:
        call_stmt = "mutable APIResult = " + api_name + "("
        for var_name in standard_api_args.keys():
            call_stmt += var_name + ", "
        call_stmt = call_stmt[:-2] + ");\n"
    else:
        call_stmt = "mutable APIResult = " + api_name + "();"
    if "Unit" in api_info.returnType:
        output_stmt = "DumpMachine();\n"
    else:
        output_stmt = "Message($\"{APIResult}\");\n"
    return open_stmt, call_stmt, reset_stmt, output_stmt

api_count, api_cons_count = 0, 0

def generate_fragment_cs(api_info):
    global api_count, api_cons_count

    result_list = []
    bool_expr_list, func_ret_list, arg_dict = [], [], {}
    cl_cons_result = has_cons("ClConsStmt", api_info.name)
    if len(cl_cons_result) > 0:
        bool_expr_list, func_ret_list, arg_dict = merge_cl_cons(cl_cons_result)
        # print("===bool_expr_list:",bool_expr_list,"\n===func_ret_list:",func_ret_list)
    qt_cons_result = has_cons("QtConsStmt", api_info.name)
    if len(qt_cons_result) > 0:
        correct_stmt, wrong_stmt = generate_if_cons_exist(bool_expr_list, func_ret_list, qt_cons_result, arg_dict)
    else:
        correct_stmt, wrong_stmt = generate_if_cons_exist(bool_expr_list, func_ret_list, [], arg_dict)
    if correct_stmt is None or wrong_stmt is None:
        return []
    standard_api_args = api_info.get_api_args()
    rest_args = get_rest_args(standard_api_args, arg_dict)
    if len(arg_dict) == 0:
        correct_stmt += "//no cons\n"
        wrong_stmt += "//no cons\n"
    else:
        api_cons_count += 1
    other_arg_dec, concrete_reset_stmt = "", ""
    concrete_type_dict = {} 
    for var_name, var_type in rest_args.items():
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
            if var_type == "Qubit":
                concrete_reset_stmt += "Reset("+var_name+");\n"
            elif var_type == "Qubit[]":
                concrete_reset_stmt += "ResetAll("+var_name+");\n"
        # print("1generate rest args:" + var_name + "-" + var_type+"-")
        other_arg_dec = randomVal.generate_random(var_name, var_type)
        # print("==check other_arg_dec:", other_arg_dec)
        if other_arg_dec:
            correct_stmt += other_arg_dec
            wrong_stmt += other_arg_dec
        else:
            break
    if other_arg_dec is None:
        return []

    open_stmt, call_stmt, reset_stmt, output_stmt = generate_context_for_api(api_info)
    defined_call_str = ""
    for call in randomVal.defined_call:
        if isinstance(call, str):
            defined_call_str += call
        else:
            defined_call_str += call.content
    randomVal.defined_call.clear()
    if correct_stmt == wrong_stmt:
        final_stmt = correct_stmt+call_stmt+reset_stmt+concrete_reset_stmt+output_stmt
        code_fragment = CodeFragmentInfo(final_stmt, standard_api_args, {}, open_stmt,
                                    defined_call_str, "QuantumConsStmt").format_to_save()
        result_list.append(code_fragment)
    else:
        final_stmt1 = correct_stmt+call_stmt+reset_stmt+concrete_reset_stmt+output_stmt
        final_stmt2 = wrong_stmt+call_stmt+reset_stmt+concrete_reset_stmt+output_stmt
        code_fragment1 = CodeFragmentInfo(final_stmt1, standard_api_args, {}, open_stmt,
                                    defined_call_str, "QuantumConsStmt").format_to_save()
        code_fragment2 = CodeFragmentInfo(final_stmt2, standard_api_args, {}, open_stmt,
                                    defined_call_str, "QuantumConsStmt").format_to_save()
        result_list.append(code_fragment1)
        result_list.append(code_fragment2)
    api_count += 1
    return result_list

def select_all():
    result_list = []
    for api_info in standard_api_list:
        result_list.extend(generate_fragment_cs(api_info))
    save_into_db(params["corpus_db"], "CodeFragment_CS", result_list)

if __name__ == "__main__":
    select_all()
    # print(has_cons("QtConsStmt", "SquareSI"))
