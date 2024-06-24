import re
import ast
import sys
import copy
import random
from io import StringIO

from DBOperation.dboperation_sqlite import DataBaseHandle
from basic_operation.file_operation import *
from grammar_pattern.Assignment import Assignment
from grammar_pattern.APIOperator import APIOperator
from grammar_pattern.function_return import generate_func_return
from class_for_info.defined_var_info import DefinedVar
from code_extractor.process_stmt import is_basic_type

params = initParams("../config.json")
assign = Assignment(params)
var_num = 0
standard_api_dict = APIOperator().init_api_dict("/root/UPBEAT/src/ParseAPI/data/content_all.json")

def assemble_dec_stmt(var_name, var_type, value):
    global var_num

    # print("var_name:",var_name,"var_type:",var_type,"value:",value)
    if var_type in ["Int", "Double", "BigInt"]:
        return "mutable "+var_name+" = "+value+";\n"
    elif var_type == "Qubit[]":
        return "use "+var_name+" = Qubit["+value+"];\n"
    elif "[]" in var_type:
        real_value, var_num = assign.generateArrayWithFixedSize(params, var_type.replace("[]", ""), 1,
                                                                    int(value), var_num)
        return "mutable "+var_name+" = "+real_value+";\n"
    elif var_type in ["LittleEndian", "BigEndian"]:
        stmt = "use "+var_name+"QubitArray = Qubit["+value+"];\n"
        stmt += "mutable "+var_name+" = "+var_type+"("+var_name+"QubitArray);\n"
        return stmt
    elif var_type == "SignedLittleEndian":
        stmt = "use "+var_name+"QubitArray = Qubit["+value+"];\n"
        stmt += "mutable "+var_name+" = SignedLittleEndian(LittleEndian("+var_name+"QubitArray));\n"
        return stmt
    else:
        return ""

def get_all_occurrence(string: str, substrings: list):
    occurrences = []
    for substring in substrings:
        start = string.find(substring)
        while start != -1:
            occurrences.append((start, start + len(substring), substring))
            start = string.find(substring, start + 1)
    occurrences.sort()
    # print("occurrences:",occurrences)
    return occurrences

def construct_bool_exprs(input_str: str):
    constructed_list = [input_str]
    count = input_str.count("<=")+input_str.count(">=")
    if count >= 2:
        occurrences = get_all_occurrence(input_str, [">=", "<="])[1:]
        for start, end, substring in occurrences:
            new_input_str = input_str[:start]+"=="+input_str[end:]
            # print("new_input_str:"+new_input_str)
            constructed_list.append(new_input_str)
    return constructed_list

def inverse_bool_exprs(input_str: str):
    constructed_list = []
    for match in re.finditer(r"Or\(.*?\)", input_str):
        new_input_str = input_str.replace(match.group(), "Not("+match.group()+")")
        constructed_list.append(new_input_str)
        input_str = input_str.replace(match.group(), "")
    bool_expr_list = input_str.split(", ")
    for bool_expr in bool_expr_list:
        if bool_expr == "":
            continue
        new_input_str = input_str.replace(bool_expr, "Not("+bool_expr+")")
        constructed_list.append(new_input_str)
    return constructed_list

def get_symbol_type(word: str, arg_dict: dict):
    # print("1word:"+word+" arg_dict:"+str(arg_dict))
    if word in arg_dict:
        word_type = arg_dict[word]
        if word_type == "Int" or  word_type == "BigInt":
            return "Int"
        elif word_type == "Double":
            return "Real"
    if word.startswith("Length("):
        return "Int"
    return None

def replace_words(bool_expr_list: list, arg_dict: dict):
    symbols_str, new_constraint, extra_input_str = "", "", ""
    new_bool_expr_list = []
    for idx, expr in enumerate(bool_expr_list):
        if not any(char.isalpha() for char in expr):
            continue
        if " or " in expr:
            new_sub_bool_expr_list = []
            sub_bool_expr_list = expr.split(" or ")
            for sub_bool_expr in sub_bool_expr_list:
                if any(char.isalpha() for char in sub_bool_expr):
                    # print("sub_bool_expr:"+sub_bool_expr)
                    new_sub_bool_expr_list.append(sub_bool_expr)
            expr = "Or("+", ".join(new_sub_bool_expr_list)+")"
            # print("expr:"+expr)
        new_bool_expr_list.append(expr)
    if len(new_bool_expr_list) == 0:
        return None, None, None, None
    input_str = ", ".join(new_bool_expr_list)
    # print("input_str:"+input_str)
    input_str = input_str.replace("^", "**")
    # print("input_str1:"+input_str)
    processed_word = []
    match_for_word = re.finditer(r"[\w\(\)!:]+", input_str)
    for idx, item in enumerate(match_for_word):
        word = item.group()
        # print("0word:"+word)
        if word.startswith("Or("):
            word = word[3:]
        elif word.count("(") != word.count(")"):
            word = word[:-1]
        if word.endswith("L"):
            input_str = input_str.replace(word, word[:-1])
        elif is_basic_type(word) or word.startswith("0x") or word in ["!", "Or", "or", "(", ")"]:
            pass
        elif word not in processed_word:
            letter = chr(ord('a') + idx)
            if "2**"+word in input_str or "2**("+word in input_str or "2 ** "+word in input_str or "2 ** ("+word in input_str:
                extra_input_str += ", "+letter+" == "+random.choice(["0", "1", "2"])
            elif word.startswith("Length("):
                extra_input_str += ", "+letter+" >= 0"
            input_str = input_str.replace(word, letter)
            symbol_type = get_symbol_type(word, arg_dict)
            if symbol_type is None:
                return None, None, None, None
            symbols_str += letter + " = "+symbol_type+"('"+word+"')\n"
            new_constraint += letter+" != model["+letter+"], "
            processed_word.append(word)
    new_constraint = "Or("+new_constraint[:-2]+")"
    # print("input_str2:"+input_str)
    return input_str, symbols_str, new_constraint, extra_input_str

def construct_single_solution(input_str: str, symbols_str: str, new_constraint: str, extra_input_str: str):
    # print("input_str:",input_str)
    solver_code = "from z3 import *\n"
    solver_code += symbols_str
    solver_code += "expr = And("+input_str+extra_input_str+")\n"
    solver_code += "solver = Solver()\nsolver.add(expr)\n"+\
                   "if solver.check() == sat:\n"+\
                   "    model = solver.model()\n"+\
                   "    print(model)\n"
    # print("single solver code:\n"+solver_code)
    return solver_code

def construct_multiple_solutions(input_str: str, symbols_str: str, new_constraint: str, extra_input_str: str):
    # print("input_str:",input_str)
    solver_code = "from z3 import *\n"
    solver_code += symbols_str
    solver_code += "expr = And("+input_str+extra_input_str+")\n"
    solver_code +=  "solver = Solver()\nsolver.add(expr)\n"+\
                    "solutions = []\n"+\
                    "for i in range(3):\n"+\
                    "    if solver.check() == sat:\n"+\
                    "        model = solver.model()\n"+\
                    "        solutions.append(model)\n"+\
                    "        new_constraint = "+new_constraint+"\n"+\
                    "        solver.add(new_constraint)\n"+\
                    "for solution in solutions:\n"+\
                    "    print(solution)\n"
    # print("multiple solver code:\n"+solver_code)
    return solver_code

def get_solver_from_z3(solver_code: str):    
    # print("===start solve===")
    stdout = StringIO()
    sys.stdout = stdout
    try:
        exec(solver_code)
    except:
        return ""
    sys.stdout = sys.__stdout__
    output = stdout.getvalue()
    # print("===end solve===\n")
    # print("output:"+output+"-")
    return output

def process_single_solution(output: str, arg_dict: dict):
    output = output.replace("\n", "")
    # print("output:"+output+"-")
    dec_stmt = ""
    defined_vars, mid_vars = {}, {}
    item_list = output[1:-1].split(", ")
    item_list.sort()
    for item in item_list:
        # print("item:"+item)
        if len(item) == 0:
            continue
        var_name, value = item.split(" = ")
        if var_name.startswith("Length(LittleEndian(") and var_name.endswith("!)"):
            var_name = re.match("Length\(LittleEndian\((\w+)!*\)!\)", var_name).group(1)
            var_type = arg_dict[var_name]
            mid_vars[var_name+"QubitArrayLen"] = value
        elif var_name.startswith("Length(ResultArrayAsBoolArray(") and var_name.endswith("))"):
            var_name = re.match("Length\(ResultArrayAsBoolArray\((\w+)\)\)", var_name).group(1)
            var_type = arg_dict[var_name]
            mid_vars[var_name+"QubitArrayLen"] = value
        elif var_name.startswith("Length(") and var_name.endswith(")"):
            var_name = re.match("Length\((\w+)!*\)", var_name).group(1)
            var_type = arg_dict[var_name]
            mid_vars[var_name+"QubitArrayLen"] = value
        elif var_name.startswith("Length("):
            var_name = var_name[7:-1]
            var_type = arg_dict[var_name]
            mid_vars[var_name+"ArrayLen"] = value
        else:
            var_type = arg_dict[var_name]
            if var_type == "Double":
                value = str(float(eval(value)))
            dec_stmt += assemble_dec_stmt(var_name, var_type, value)
            defined_vars[var_name] = DefinedVar(var_name, var_type, var_type.count("[]"), value)
    return dec_stmt, defined_vars, mid_vars

def process_multiple_solutions(output: str, arg_dict: dict):
    dec_stmt_list = []
    for match in re.finditer(r"\[[\s\S]+?\]", output):
        solution = match.group()
        # print("+++solution:"+solution+"-")
        dec_stmt, defined_vars, mid_vars = process_single_solution(solution, arg_dict)
        # print(">>>after process_single_solution<<<\n"+dec_stmt+str(mid_vars)+str(defined_vars))
        if (dec_stmt, mid_vars) not in dec_stmt_list:
            dec_stmt_list.append((dec_stmt, defined_vars, mid_vars))
    return dec_stmt_list

def generate_by_z3(bool_expr_list: list, arg_dict: dict):
    # print("+++arg_dict:",arg_dict)
    valid_dec_stmt_list, invalid_dec_stmt_list = [], []
    input_str, symbols_str, new_constraint, extra_input_str = replace_words(bool_expr_list, arg_dict)
    if input_str is None:
        return [], []
    # print("===valid===")
    constructed_list = construct_bool_exprs(input_str)
    for constructed in constructed_list:
        solver_code = construct_multiple_solutions(constructed, symbols_str, new_constraint, extra_input_str)
        output = get_solver_from_z3(solver_code)
        dec_stmt_list = process_multiple_solutions(output, arg_dict)
        valid_dec_stmt_list.extend(dec_stmt_list)
        # print("valid_dec_stmt_list:",valid_dec_stmt_list)
    # print("===invalid===")
    constructed_list = inverse_bool_exprs(input_str)
    for constructed in constructed_list:
        # print("constructed:"+constructed)
        solver_code = construct_single_solution(constructed, symbols_str, new_constraint, extra_input_str)
        # print("solver_code:\n"+solver_code)
        output = get_solver_from_z3(solver_code)
        if len(output) == 0:
            continue
        tmp_dec_stmt, tmp_defined_vars, tmp_mid_vars = process_single_solution(output, arg_dict)
        invalid_dec_stmt_list.append((tmp_dec_stmt, tmp_defined_vars, tmp_mid_vars))
        # print("dec_stmt:\n"+dec_stmt)
        # print("defined_vars:",defined_vars,"mid_vars:",mid_vars)
    return valid_dec_stmt_list, invalid_dec_stmt_list

def generate_by_func_ret(func_ret_list: list, defined_vars: dict, mid_vars: dict):
    mid_vars_copy = copy.deepcopy(mid_vars)
    defined_vars_copy = copy.deepcopy(defined_vars)
    valid_dec_stmt, invalid_dec_stmt = [], []
    valid_dec_stmt_list, invalid_dec_stmt_list = [], []
    # print("func_ret_list:",func_ret_list)
    for expr in func_ret_list:
        if len(expr) == 0:
            continue
        # print("process:"+expr)
        tmp_dec_stmt = generate_func_return(expr, mid_vars, defined_vars, True)
        if tmp_dec_stmt:
            valid_dec_stmt.append(tmp_dec_stmt)
        # print("generate valid:\n"+tmp_dec_stmt)
        tmp_dec_stmt = generate_func_return(expr, mid_vars_copy, defined_vars_copy, False)
        if tmp_dec_stmt:
            invalid_dec_stmt.append(tmp_dec_stmt)
        # print("generate invalid:\n"+tmp_dec_stmt)
    # print("valid_dec_stmt:",valid_dec_stmt,"defined_vars:",defined_vars,"mid_vars:",mid_vars)
    valid_dec_stmt_list.append(("".join(valid_dec_stmt), defined_vars, mid_vars))
    if len(invalid_dec_stmt) < len(func_ret_list):
        return valid_dec_stmt_list, []
    for i in range(len(func_ret_list)):
        tmp_dec_stmt = "".join(valid_dec_stmt[:i])+invalid_dec_stmt[i]+"".join(valid_dec_stmt[i+1:])
        # print("===tmp_dec_stmt:\n"+tmp_dec_stmt)
        invalid_dec_stmt_list.append((tmp_dec_stmt, defined_vars_copy, mid_vars))
    return valid_dec_stmt_list, invalid_dec_stmt_list

def generate_by_mid_vars(mid_vars: dict, defined_vars: dict, arg_dict: dict):
    # print("---mid_vars:",mid_vars)
    tmp_dec_stmt = ""
    for mid_var_name, mid_value in mid_vars.items():
        if "QubitArrayLen" in mid_var_name: 
            real_var_name = mid_var_name.replace("QubitArrayLen", "")
            if real_var_name not in defined_vars:
                tmp_dec_stmt += assemble_dec_stmt(real_var_name, arg_dict[real_var_name], mid_value)
        elif "ArrayLen" in mid_var_name: 
            real_var_name = mid_var_name.replace("ArrayLen", "")
            if real_var_name not in defined_vars:
                tmp_dec_stmt += assemble_dec_stmt(real_var_name, arg_dict[real_var_name], mid_value)
    return tmp_dec_stmt

def generate_value_pair(bool_expr_list: list, func_ret_list: list, arg_dict: dict):
    if len(bool_expr_list) > 0 and bool_expr_list[0] != "":
        front_valid_list, front_invalid_list = generate_by_z3(bool_expr_list, arg_dict)
    else:
        front_valid_list, front_invalid_list = [], []
        defined_vars = {}
    # print("size of front_valid_list:",len(front_valid_list),"size of front_invalid_list:",len(front_invalid_list))
    # print(">>>after generate_by_z3<<<")
    # for var_name, var_info in defined_vars.items():
    #     print(">>>var_name:",var_name,"var_value:",var_info.var_value)
    front_invalid_back_valid_list = []
    back_valid_list, back_invalid_list = [], []
    if len(func_ret_list) > 0 and func_ret_list[0] != "":
        for front_valid in front_valid_list:
            back_valid_list, back_invalid_list = generate_by_func_ret(func_ret_list, front_valid[1], front_valid[2])
        for front_invalid in front_invalid_list:
            tmp_back_valid_list, tmp_back_invalid_list = generate_by_func_ret(func_ret_list, front_invalid[1], front_invalid[2])
            # print("===front_invalid_back_valid_list:\n",tmp_back_valid_list[0])
            front_invalid_back_valid_list.append(tmp_back_valid_list[0])
        # print("===size of front_invalid_back_valid_list:",len(front_invalid_back_valid_list))
        if len(front_valid_list) == 0 and len(front_invalid_list) == 0:
            back_valid_list, back_invalid_list = generate_by_func_ret(func_ret_list, {}, {})
    # print("size of back_valid_list:",len(back_valid_list),"size of back_invalid_list:",len(back_invalid_list))
    final_valid_list, final_invalid_list = [], []
    if len(back_valid_list) > 0 and len(front_valid_list) > 0:
        for (front_dec_stmt, front_defined_vars, front_mid_vars), (back_dec_stmt, back_defined_vars, back_mid_vars) in zip(front_valid_list, back_valid_list):
            still_not_generated = generate_by_mid_vars(front_mid_vars, back_defined_vars, arg_dict)
            final_dec_stmt = front_dec_stmt+back_dec_stmt+still_not_generated
            # print("final_valid:\n"+final_dec_stmt)
            final_mid_vars = {**front_mid_vars, **back_mid_vars}
            final_valid_list.append(("//valid\n"+final_dec_stmt, final_mid_vars))
    elif len(back_valid_list) > 0:
        for back_dec_stmt, back_defined_vars, back_mid_vars in back_valid_list:
            final_valid_list.append(("//valid\n"+back_dec_stmt, back_mid_vars))
    if len(front_invalid_back_valid_list) > 0:
        for (front_dec_stmt, front_defined_vars, front_mid_vars), (back_dec_stmt, back_defined_vars, back_mid_vars) in zip(front_invalid_list, front_invalid_back_valid_list):
            still_not_generated = generate_by_mid_vars(front_mid_vars, back_defined_vars, arg_dict)
            final_dec_stmt = front_dec_stmt+back_dec_stmt+still_not_generated
            # print("final_invalid:\n"+final_dec_stmt)
            final_mid_vars = {**front_mid_vars, **back_mid_vars}
            final_invalid_list.append(("//invalid\n"+final_dec_stmt, final_mid_vars))
    if len(back_invalid_list) > 0 and len(front_valid_list) > 0:
        still_not_generated = generate_by_mid_vars(front_valid_list[0][2], front_valid_list[0][1], arg_dict)
        for back_dec_stmt, back_defined_vars, back_mid_vars in back_invalid_list:
            final_dec_stmt = back_dec_stmt+front_valid_list[0][0]+still_not_generated
            # print("final_invalid:\n"+final_dec_stmt)
            final_mid_vars = {**back_mid_vars, **front_valid_list[0][1]}
            final_invalid_list.append(("//invalid\n"+final_dec_stmt, final_mid_vars))
    elif len(back_invalid_list) > 0:
        for back_dec_stmt, back_defined_vars, back_mid_vars in back_invalid_list:
            final_invalid_list.append(("//invalid\n"+back_dec_stmt, back_mid_vars))
    if len(back_valid_list) == 0 and len(back_invalid_list) == 0:
        for front_dec_stmt, front_defined_vars, front_mid_vars in front_valid_list:
            still_not_generated = generate_by_mid_vars(front_mid_vars, front_defined_vars, arg_dict)
            final_dec_stmt = front_dec_stmt+still_not_generated
            final_valid_list.append(("//valid\n"+final_dec_stmt, front_mid_vars))
        for front_dec_stmt, front_defined_vars, front_mid_vars in front_invalid_list:
            still_not_generated = generate_by_mid_vars(front_mid_vars, front_defined_vars, arg_dict)
            final_dec_stmt = front_dec_stmt+still_not_generated
            final_invalid_list.append(("//invalid\n"+final_dec_stmt, front_mid_vars))
    return final_valid_list, final_invalid_list

def merge_cl_cons(result_list: list):
    bool_expr_list, func_ret_list = [], []
    arg_dict = {}
    for result in result_list:
        # print("result:",result)
        fact_stmt = result[2]
        arg_dict.update(ast.literal_eval(result[3]))
        if fact_stmt.startswith("Is") or fact_stmt.startswith("PNorm"):
            func_ret_list.append(fact_stmt)
        elif " and " in fact_stmt:
            bool_expr_list.extend(fact_stmt.split(" and "))
        else:
            bool_expr_list.append(fact_stmt)
    # print("func_ret_list:",func_ret_list)
    return bool_expr_list, func_ret_list, arg_dict

def cl_cwvp_by_z3(bool_expr_list: list, func_ret_list: list, arg_dict: dict):
    final_valid_list, final_invalid_list = generate_value_pair(bool_expr_list, func_ret_list, arg_dict)
    return final_valid_list, final_invalid_list, arg_dict

def main():
    db_path = "/root/UPBEAT/data/query/fact_stmt_1.db"
    targetDB = DataBaseHandle(db_path)
    api_name_list = targetDB.selectAll("select func_name from ClConsStmt where id = 20")
    for api_name in api_name_list:
        # print("api_name:",api_name)
        api_name = api_name[0]
        if api_name in standard_api_dict:
            result_list = targetDB.selectAll("select * from ClConsStmt_sim where func_name = '"+api_name+"';")
            # print("result_list:\n",result_list)
            bool_expr_list, func_ret_list, arg_dict = merge_cl_cons(result_list)
            cl_cwvp_by_z3(bool_expr_list, func_ret_list, arg_dict)

if __name__ == "__main__":
    main()
