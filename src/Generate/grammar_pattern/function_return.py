import re
import random
import numpy as np
import math

from grammar_pattern.Assignment import Assignment
from grammar_pattern.basic_type import generate_integer, generate_double
from basic_operation.file_operation import initParams
from class_for_info.defined_var_info import DefinedVar

params = initParams("../config.json")
assign = Assignment(params)


def generate_permutation(arr_size: int):
    if arr_size == 0:
        return "[0, size=0]"
    value = "["
    arr = np.arange(arr_size)
    random.shuffle(arr)
    for a in arr:
        value += str(a)+", "
    return value[:-2]+"]"

def generate_not_permutation(arr_size: int):
    # If array length = 0
    if arr_size == 0:
        return None
    # If array length > 0
    value = "["
    arr = np.arange(arr_size)
    random.shuffle(arr)
    for a in arr:
        value += str(a+1)+", "
    return value[:-2]+"]"

def generate_rectangle(arr_size: int):
    value = "["
    n = random.randint(1,10)
    for i in range(arr_size):
        value += "["
        for j in range(n):
            value += generate_integer()+", "
        value = value[:-2]+"], "
    value = value[:-2]+"]"
    return value

def generate_not_rectangle(arr_size: int):
    # If array length = 0
    print("===arr_size:",arr_size)
    if arr_size in [0, 1]:
        return None
    # If array length > 0
    value = "["
    n = random.randint(2,10)
    for i in range(arr_size-1):
        value += "["
        for j in range(n):
            value += generate_integer()+", "
        value = value[:-2]+"], "
    value += "["
    for j in range(n-1):
        value += generate_integer()+", "
    value = value[:-2]+"]]"
    return value

def generate_square(arr_size: int):
    value = "["
    for i in range(arr_size):
        value += "["
        for j in range(arr_size):
            value += generate_integer()+", "
        value = value[:-2]+"], "
    value = value[:-2]+"]"
    return value

def generate_not_square(arr_size: int):
    # If array length = 0
    if arr_size == 0:
        return None
    # If array length > 0
    value = "["
    for i in range(arr_size-1):
        value += "["
        for j in range(arr_size):
            value += generate_integer()+", "
        value = value[:-2]+"], "
    value += "["
    for j in range(arr_size-1):
        value += generate_integer()+", "
    if arr_size == 0:
        return value+"]]"
    else:
        return value[:-2]+"]]"

def generate_abs(value: int):
    choice = int(assign.generatePosInt(2))
    if choice == 1:
        return str(value)
    else:
        return str(-value)

def generate_head(arr_size: int):
    var_type = random.choice(["Int", "BigInt", "Double", "Pauli", "Result", "Bool"])
    return Assignment.generateArrayWithFixedSize(params, var_type, 2, arr_size)

def generate_coprime():
    while True:
        num1 = random.randint(1, 100)
        num2 = random.randint(1, 100)
        if math.gcd(num1, num2) == 1:
            return str(num1), str(num2)

def generate_not_coprime():
    while True:
        num1 = random.randint(1, 100)
        num2 = random.randint(1, 100)
        if math.gcd(num1, num2) != 1:
            return str(num1), str(num2)

def is_coprime(num1: str, num2: str):
    return math.gcd(int(num1), int(num2)) == 1

def generate_pnorm():
    n = random.randint(1, 10)
    s = ""
    for i in range(n):
        s += generate_double()+", "
    return "["+s[:-2]+"]"

def generate_not_pnorm():
    n = random.randint(0, 10)
    if n == 0:
        return "[]"
    else:
        s = "0.0, "*n
        return "["+s[:-2]+"]"

def generate_func_return(expr: str, mid_var_dict: dict, defined_var_dict: dict, generate_correct: bool):
    value = ""
    if "IsPermutation" in expr:
        match = re.match("IsPermutation\((\w+)\)", expr)
        if not match:
            return None
        var_name = match.group(1)
        if var_name+"ArrayLen" in mid_var_dict:
            arr_size = int(mid_var_dict[var_name+"ArrayLen"])
        elif var_name+"QubitArrayLen" in mid_var_dict:
            arr_size = int(mid_var_dict[var_name+"QubitArrayLen"])
        else:
            arr_size = int(assign.generatePosInt(10))
        if generate_correct:
            value = generate_permutation(arr_size)
        else:
            value = generate_not_permutation(arr_size)
        if value:
            final_stmt = "let "+var_name+" = "+value+";\n"
        elif generate_correct:
            value = "[0, size=0]"
            final_stmt = "let "+var_name+" = "+value+";\n"
        else:
            return None
        defined_var_dict[var_name] = DefinedVar(var_name, "Int[]", 0, value)
    elif "IsRectangularArray" in expr:
        var_name = re.match("IsRectangularArray\((\w+)\)", expr).group(1)
        if var_name+"ArrayLen" in mid_var_dict:
            arr_size = int(mid_var_dict[var_name+"ArrayLen"])
        else:
            arr_size = int(assign.generatePosInt(10))
        if generate_correct:
            value = generate_rectangle(arr_size)
        else:
            value = generate_not_rectangle(arr_size)
        # print("===generate_correct",generate_correct,"value:"+value)
        if value is None:
            return None
        final_stmt = "let "+var_name+" = "+value+";\n"
        defined_var_dict[var_name] = DefinedVar(var_name, "Int[][]", 0, value)
    elif "SquareMatrixFact" in expr:
        var_name = re.match("SquareMatrixFact\((\w+)\)", expr).group(1)
        if var_name+"ArrayLen" in mid_var_dict:
            arr_size = int(mid_var_dict[var_name+"ArrayLen"])
        else:
            arr_size = int(assign.generatePosInt(10))
        if generate_correct:
            value = generate_square(arr_size)
        else:
            value = generate_not_square(arr_size)
        final_stmt = "let "+var_name+" = "+value+";\n"
        defined_var_dict[var_name] = DefinedVar(var_name, "Int[][]", 0, value)
    elif "IsSquareMatrix" in expr:
        var_name = re.match("IsSquareMatrix\((\w+)\)", expr).group(1)
        if var_name+"ArrayLen" in mid_var_dict:
            arr_size = int(mid_var_dict[var_name+"ArrayLen"])
        else:
            arr_size = int(assign.generatePosInt(10))
        if generate_correct:
            value = generate_square(arr_size)
        else:
            value = generate_not_square(arr_size)
        final_stmt = "let "+var_name+" = "+value+";\n"
        defined_var_dict[var_name] = DefinedVar(var_name, "Int[][]", 0, value)
    elif "IsCoprimeI" in expr:
        match = re.match("IsCoprimeI\((\w+), (\w+)\)", expr)
        var_name1, var_name2 = match.group(1), match.group(2)
        if var_name1 in defined_var_dict and var_name2 in defined_var_dict:
            value1, value2 = defined_var_dict[var_name1].var_value, defined_var_dict[var_name2].var_value
            if generate_correct and is_coprime(value1, value2):
                return ""
            elif not generate_correct and not is_coprime(value1, value2):
                return ""
            else:
                return None
        if generate_correct:
            value1, value2 = generate_coprime()
        else:
            value1, value2 = generate_not_coprime()
        final_stmt = "let "+var_name1+" = "+value1+";\n"+"let "+var_name2+" = "+value2+";\n"
        # print("final_stmt:\n"+final_stmt)
        defined_var_dict[var_name1] = DefinedVar(var_name1, "Int", 0, value1)
        defined_var_dict[var_name2] = DefinedVar(var_name2, "Int", 0, value2)
    elif "IsCoprimeL" in expr:
        match = re.match("IsCoprimeL\((\w+), (\w+)\)", expr)
        var_name1, var_name2 = match.group(1), match.group(2)
        if generate_correct:
            value1, value2 = generate_coprime()
        else:
            value1, value2 = generate_not_coprime()
        final_stmt = "let "+var_name1+" = "+value1+"L;\n"+"let "+var_name2+" = "+value2+"L;\n"
        defined_var_dict[var_name1] = DefinedVar(var_name1, "BigInt", 0, value1)
        defined_var_dict[var_name2] = DefinedVar(var_name2, "BigInt", 0, value2)
    elif "PNorm" in expr:
        match = re.match("PNorm\(1\.0, (\w+)\) != 0\.0", expr)
        var_name = match.group(1)
        if generate_correct:
            value = generate_pnorm()
        else:
            value = generate_not_pnorm()
        final_stmt = "let "+var_name+" = "+value+";\n"
        defined_var_dict[var_name] = DefinedVar(var_name, "Double[]", 0, value)
    else:
        print("Unhandled situation:"+expr)
        return None
    # print("value:"+value+"-")
    if value is None:
        return None
    return final_stmt


if __name__ == "__main__":
    # print(generate_permutation(36))
    # print(generate_rectangle(2))
    # print(generate_pnorm())
    print(generate_not_rectangle(5))
