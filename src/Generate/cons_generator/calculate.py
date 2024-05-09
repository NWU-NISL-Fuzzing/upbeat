from class_for_info.constraint_tree import ConstraintTree


can_cal_dict = {"+": "+", "-": "-", "*": "*", "%": "%", "/": "/", "^": "**", ">>>": ">>", "<<<": "<<"}

def preprocess_value(value: str, final_stmt: str):
    """ 对于Endian类型，获取Qubit数组的长度 """

    if 'NISLQubitArray' in final_stmt:
        start_index = final_stmt.index("Qubit[") + 6
        value = final_stmt[start_index:final_stmt.index("]", start_index)]
    return value

def count_items(tmp_content: str):
    """ 对生成的数组进行计数，返回数组长度 """

    if "[]" in tmp_content:
        return "0"
    elif "Qubit[" in tmp_content:
        return tmp_content[6:-1]
    else:
        return str(tmp_content.count(",")+1)

def calculate_sub_tree(selected_tree: ConstraintTree, final_stmt: str):
    """ 计算子表达式，返回结果 """

    can_calculate = False
    content_list = [selected_tree.leftNode.rootNode, selected_tree.rightNode.rootNode]
    cal_op = selected_tree.rootNode.strip()
    # print("calculating1...left_content:"+content_list[0]+" cal_op:"+cal_op+" right_content:"+content_list[1])
    for index, this_content in enumerate(content_list):
        if this_content.isdigit():
            can_calculate = True
        elif 'Endian' in this_content:
            # print("final_stmt in calculate_sub_tree:\n"+final_stmt)
            start_index = final_stmt.index("Qubit[") + 6
            content_list[index] = final_stmt[start_index:final_stmt.index("]", start_index)]
            can_calculate = True
        else:
            can_calculate = False
            break
    if can_calculate and cal_op in can_cal_dict:
        # print("calculating2...left_content:"+content_list[0]+" cal_op:"+cal_op+" right_content:"+content_list[1])
        return eval(content_list[0] + can_cal_dict[cal_op] + content_list[1])
    else:
        # TODO.增加更多类型的处理
        return random.randint(0, 10)

def calculate_math_expr(expr: str):

    print("calculating expr:"+expr)
    if "?" in expr and "|" in expr:
        return expr
    expr = expr.replace("<<<", "<<").replace(">>>", ">>").replace("^", "**")
    if "L" in expr:
        expr = expr.replace("L", "")
        result = str(eval(expr))+"L"
    else:
        result = str(eval(expr))
    return result
    