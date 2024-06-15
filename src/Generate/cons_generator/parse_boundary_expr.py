import random
import ast
import sys
import re

from grammar_pattern.APIOperator import APIOperator
from class_for_info.constraint_tree import ConstraintTree, ConstraintTreeList

standard_api_dict = APIOperator().init_api_dict("../ParseAPI/data/content.json")

change_dict = {"+": "-", "-": "+", "/": "*", "%": "*", "*": "/", ">>>": "<<<", "<<<": ">>>"}

regex_for_bool = r"([\S ]+?) (==|!=|>=|<=|>|<) ([\S ]+)"
regex_for_cal = r"([\S ]+)(\+|-|\*|\/|\%|\^|>>>|<<<)([\S ]+)"
regex_for_sub_expr = r"(?<=\().*(?=\))"

def is_certain_value(node_content: str):
    """ 确定值的类型：整数、浮点数、Pauli """

    node_content = node_content.replace('.', '').replace('L', '')
    return (node_content.isdigit()) or (node_content in ['PauliX', 'PauliY', 'PauliZ', 'PauliI']) or (node_content.startswith('0x'))

def change_generic(arg_dict: dict):
    """ 如果存在参数的类型为泛型，随机选择一种可生成的具体类型进行替换 """

    selected_type = random.choice(["Int", "BigInt", "Double", "Pauli", "Bool", "Range"])
    for var_name, var_type in arg_dict.items():
        if "'" in var_type:
            new_var_type = var_type
            for match in re.finditer(r"'\w+", var_type):
                new_var_type = new_var_type.replace(match.group(), selected_type)
            arg_dict[var_name] = new_var_type
    return arg_dict

def countOp(expr: str):
    """ 对表达式中的运算符进行计数 """

    return expr.count('+')+expr.count('-')+expr.count('/')+expr.count('%')+expr.count('^')+expr.count('<<<')+expr.count('>>>')

def change_calculate_op(op: str):
    """ 将部分项从左式移到右式时，改变操作符 """
    
    op = " " + change_dict[op.strip()] + " "

    return op

def get_basic_cons_tree(sub_expr: str):
    cons_tree_list = []
    match = re.match(regex_for_bool, sub_expr)
    one_cons_tree = ConstraintTree(match.group(2).strip())
    # 如果左节点为复杂表达式，将多于一个的变量挪至右侧
    match_for_left = re.match(regex_for_cal, match.group(1).replace(" ", ""))
    if match_for_left:
        # print("left item:"+match_for_left.group(1))
        if not is_certain_value(match_for_left.group(1)):
            new_left_node = match_for_left.group(1)
            new_right_node = match.group(3) + change_calculate_op(match_for_left.group(2)) + match_for_left.group(3)
            if match_for_left.group(2) == "%":
                new_right_node += "+1"
            # print("new left:"+new_left_node+" new right:"+new_right_node)
            one_cons_tree.setLeftNode(ConstraintTree(new_left_node), False)
            one_cons_tree.setRightNode(ConstraintTree(new_right_node), False)
        else:
            new_left_node = match_for_left.group(3)
            new_right_node = match.group(3) + change_calculate_op(match_for_left.group(2)) + match_for_left.group(1)
            # print("new left:"+new_left_node+" new right:"+new_right_node)
            one_cons_tree.setLeftNode(ConstraintTree(new_left_node), False)
            one_cons_tree.setRightNode(ConstraintTree(new_right_node), False)
    else:
        one_cons_tree.setLeftNode(ConstraintTree(match.group(1)), is_certain_value(match.group(1)))
        one_cons_tree.setRightNode(ConstraintTree(match.group(3)), is_certain_value(match.group(3)))

    # one_cons_tree.printAll()
    cons_tree_list.append(one_cons_tree)
    return cons_tree_list

def process_bool_expr(bool_expr: str):
    """ 对bool表达式进行处理，获取约束树 """

    cons_tree_list = []
    # 获取具体的变量约束表达式，存入列表
    for sub_expr in re.split(' and ', bool_expr):
        if " ^ " in sub_expr:
            continue
        cons_tree_list.extend(get_basic_cons_tree(sub_expr))
    return ConstraintTreeList("and", cons_tree_list)


if __name__ == "__main__":
    exp = "where id = 46"
    cons_list = parse_boundary_expr(exp)
    for cons in cons_list:
        cons.printAll()
