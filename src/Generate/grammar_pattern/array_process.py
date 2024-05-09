import re
import random



def array_max_process_1(input_code: str,count) -> str:
    """处理量子数组超过最大索引问题，例如 use a=Qubit[2]，后面使用到q[2]报错问题"""

    def get_max_index_1(lines, variable_names):
        max_index = -1
        pattern = re.compile(r'({})\[(\d+)\]'.format('|'.join(variable_names)))
        for line in lines:
            matches = pattern.findall(line)
            for _, index in matches:
                max_index = max(max_index, int(index))
        return max_index

    lines = input_code.split('\n')

    new_lines = []
    for line in lines:
        match = re.search(r'use\s+([^=\s]+)\s*=\s*Qubit\[(\d+)\];', line)
        if match:
            var_name = match.group(1)
            old_size = int(match.group(2))

            alias_names = set()
            for alias_line in lines:
                alias_match = re.search(r'let\s+([^=\s]+)\s*=\s*{};'.format(var_name), alias_line)
                if alias_match:
                    alias_names.add(alias_match.group(1))

            alias_names.add(var_name)
            max_index = get_max_index_1(lines, alias_names)

            if max_index >= old_size:
                new_size = max_index + 1
                line = line.replace(match.group(0), f'use {var_name} = Qubit[{new_size}];')
                print(type(count))

                count += 1

        new_lines.append(line)

    return '\n'.join(new_lines), count


def get_max_index(lines, variable_names):
    """"""

    max_index = -1
    num_pattern = re.compile(r'({})\[(\d+)\]'.format('|'.join(variable_names)))
    var_pattern = re.compile(r'({})\[(\w+)\]'.format('|'.join(variable_names)))
    # First, find direct number indices
    for line in lines:
        matches = num_pattern.findall(line)
        for _, index in matches:
            max_index = max(max_index, int(index))
    # Then, find variable indices and get their values from the code
    for line in lines:
        matches = var_pattern.findall(line)
        for _, var in matches:
            # Search for the variable value across ALL lines, not just the current line
            for search_line in lines:
                var_value_match = re.search(r'(let|mutable)\s+{}\s*=\s*(\d+);'.format(var), search_line)
                if var_value_match:
                    var_value = int(var_value_match.group(2))
                    max_index = max(max_index, var_value)
                    break  # Break once we find the value for this variable
    return max_index


def array_max_process(input_code: str, count) -> str:
    lines = input_code.split('\n')
    new_lines = []
    for line in lines:
        match = re.search(r'use\s+([^=\s]+)\s*=\s*Qubit\[(\d+)\];', line)
        if match:
            var_name = match.group(1)
            old_size = int(match.group(2))
            
            alias_names = set([var_name])
            max_index = get_max_index(lines, alias_names)

            if max_index >= old_size:
                for idx, l in enumerate(lines):
                    var_replacements = re.findall(r'(let|mutable)\s+(\w+)\s*=\s*(\d+);', l)
                    for _, var, value in var_replacements:
                        if int(value) >= old_size:
                        
                            count = count + 1
                            lines[idx] = l.replace(f'{var} = {value}', f'{var} = {old_size-1}')

    return '\n'.join(lines), count

def modify_input_code(input_code: str,count) -> str:
    lines = input_code.split('\n')
    new_lines = []

    for line in lines:
        # Check for patterns like 'mutable A = 2^63-1;' or 'mutable A = -2^63-1;'
        mutable_match = re.search(r'mutable\s+(\w+)\s*=\s*(2\^63-1|-2\^63-1);', line)
        if mutable_match:
            var_name = mutable_match.group(1)

            # Check if there exists a line with 'use B = Qubit[A];'
            for use_line in lines:
                if re.search(r'use\s+\w+\s*=\s*Qubit\[' + var_name + r'\];', use_line):
                    # Modify the mutable line
                    line = f'mutable {var_name} = 10;'
                    count = count+1
                    break

        new_lines.append(line)

    return '\n'.join(new_lines),count


def array_negative_numbers(test_case: str, count) -> str:
    """ 解决数组负数 """

    if "wrong" not in test_case :
        lines = test_case.split('\n')
        modified_lines = []
    
        variables_to_modify = set()
        variables_to_modify_let = set()
        for line in lines:
            mutable_match = re.match(r'^\s*mutable\s+(\w+)\s*=\s*(-\d+(\.\d+)?);', line)
            if mutable_match:
                variable_name = mutable_match.group(1)
                variables_to_modify.add(variable_name)
        
            let_match = re.match(r'^\s*let\s+(\w+)\s*=\s*(\w+);', line)
            if let_match:
                variable_name = let_match.group(1)
                dependent_variable_name = let_match.group(2)
                if dependent_variable_name in variables_to_modify:
                    variables_to_modify_let.add(variable_name)
        # print(variables_to_modify_let,"s",variables_to_modify)
        exit_q =[]
        for line in lines:
            modified_line = line
            pattern = r'use\s+\w+\s*=\s*Qubit\[(\w+)\]'  # 正则表达式匹配模式
            matches = re.findall(pattern, line)
            # 将匹配的值添加到数组cc中
            for match in matches:
                exit_q.append(match) 
        for line in lines:
            modified_line = line
            # 处理 mutable 变量
            for variable_name in variables_to_modify:
                if variable_name in line:
                    pattern = r'(mutable\s+' + re.escape(variable_name) + r'\s*=\s*)-\d+(\.\d+)?'
                    match = re.search(pattern, modified_line)
                    if match and variable_name in exit_q :
                        # print(match)
                        # 重建字符串，将负数替换为20
                        count += 1
                        random_number = random.randint(0, 10)
                        modified_line = modified_line[:match.start(1)] + match.group(1) + str(random_number) + modified_line[match.end():]
                        break

            # 处理 let 变量
            for variable_name in variables_to_modify_let:
                if variable_name in line and f'[{variable_name}]' in test_case:
                    pattern = r'(let\s+' + re.escape(variable_name) + r'\s*=\s*)\w+;'
                    match = re.search(pattern, modified_line)
                    if match and variable_name in exit_q:
                        # 替换为原始的 mutable 变量名
                        count += 1
                        modified_line = modified_line[:match.start(1)] + match.group(1) + next(iter(variables_to_modify)) + modified_line[match.end():]
                        break

            # 处理 Qubit 数组
            qubit_array_match = re.match(r'^\s*use\s+(\w+)\s*=\s*Qubit\[-\d+\];', line)
            if qubit_array_match:
                # 如果匹配到负数，直接替换为 5
                count += 1
                modified_line = re.sub(r'Qubit\[-\d+\]', 'Qubit[5]', modified_line)
        
            modified_lines.append(modified_line)

        return '\n'.join(modified_lines), count
    else :
        return test_case, count


def fix_negative_exponents(test_case: str,count) -> str:
    """Resolve negative exponents by replacing them with 20."""
    
    if "//wrong" in test_case :
        return test_case ,count
    lines = test_case.split('\n')
    modified_lines = []
    
    variables_to_modify = set()
    variables_to_modify_let = set()

    # Identify all mutable variable assignments with negative values
    for line in lines:
        mutable_match = re.match(r'^\s*mutable\s+(\w+)\s*=\s*(-\d+);', line)
        if mutable_match:
            variable_name = mutable_match.group(1)
            variables_to_modify.add(variable_name)
    
    # Identify if those variables are being used elsewhere, especially in let assignments
    for line in lines:
        let_match = re.match(r'^\s*let\s+(\w+)\s*=\s*(\w+);', line)
        if let_match:
            variable_name = let_match.group(1)
            dependent_variable_name = let_match.group(2)
            if dependent_variable_name in variables_to_modify:
                variables_to_modify_let.add(variable_name)

    # Process each line and replace negative values 
    for line in lines:
        modified_line = line
        for variable_name in variables_to_modify:
            if variable_name in line and (f'2^{variable_name}' in test_case or f'2^{variable_name}' in test_case):
                pattern = r'(mutable\s+' + re.escape(variable_name) + r'\s*=\s*)-\d+'
                match = re.search(pattern, modified_line)
                if match:
                    count =count+1
                    random_number = random.randint(0, 10)
                    modified_line = modified_line[:match.start(1)] + match.group(1) + str(random_number) + modified_line[match.end():]
                    break
        modified_lines.append(modified_line)

    return '\n'.join(modified_lines), count


def modify_code_ControlledOnInt(test_case,count):
    """ 找到ControlledOnInt的使用，并匹配出其两个变量名称 """
    
    matches = re.findall(r'ControlledOnInt\s*\(\s*([^,]+?)\s*,\s*.*?\)\s*\(\s*([^,]+?)\s*,', test_case, re.DOTALL)
    # 如果没有匹配到，直接返回输入
    if not matches:
        return test_case,count
    
    for match in matches:
        # 变量名
        variable_a, variable_b = match
        # print(variable_a, variable_b)
        # 找到variable_b的定义，并提取其值X
        match_b = re.search(r'use\s+' + variable_b + r'\s+=\s+Qubit\[(\d+)\];', test_case)
        if not match_b:
            continue
        x = int(match_b.group(1))
     
        # 找到variable_a的定义，看它是一个数字还是一个数组
        match_a = re.search(r'mutable\s+(' + re.escape(variable_a) + r'\w*)\s+=\s+(\[.*?\]|-?\d+);', test_case, re.DOTALL)
        if not match_a:
            continue
        max_value = 2**x - 1
        
        actual_variable_name = match_a.group(1)  # 这是变量的实际名称
        value_a = match_a.group(2)  # 这是变量的值

        # 如果variable_a是一个数组
        if '[' in value_a:
            numbers = [int(n) for n in re.findall(r'-?\d+', value_a)]
            corrected_numbers = [str(n if 0 <= n <= max_value else max_value) for n in numbers]
            new_value = '[' + ', '.join(corrected_numbers) + ']'
            test_case = test_case.replace(value_a, new_value)
            count=count+1
            # 如果variable_a是一个数字
        else:
            number = int(value_a)
            corrected_number = str(number if 0 <= number <= max_value else max_value)
            test_case = test_case.replace(value_a, corrected_number)
            count=count+1   
    return test_case, count


def modify_code_ApplyXorInPlace(code_str,count):
    # 从代码中找到所有ApplyXorInPlace的实例
    matches = re.findall(r"ApplyXorInPlace\((\w+), LittleEndian\((\w+)\)\);", code_str)

    var_values = {}
    # 获取所有mutable变量的值
    for var, value in re.findall(r"mutable (\w+) = (-?\d+);", code_str):
        var_values[var] = int(value)

    # 对于每个找到的ApplyXorInPlace实例
    for var_A, var_B in matches:
        # 找到对应的qubit声明
        match = re.search(fr"use {var_B} = Qubit\[(\w+)\];", code_str)
        if match:
            var_C = match.group(1)
            value_C = var_values.get(var_C)

            # 检查A的值是否大于C或小于0，如果是，则设置A的值为0到C之间的值
            if var_A in var_values and value_C is not None and (var_values[var_A] > value_C or var_values[var_A] < 0):
                random_value = random.randint(0, value_C)
                code_str = code_str.replace(f"mutable {var_A} = {var_values[var_A]};", f"mutable {var_A} = {random_value};")
                var_values[var_A] = random_value
                count=count+1

    return code_str,count



def extract_long(test_case: str) -> dict:
    variables_and_lengths = {}
    lines = test_case.split('\n')
    
    for line in lines:
        # 匹配 mutable 和 let 变量赋值
        variable_match = re.match(r'^\s*(mutable\s+|let\s+)(\w+)\s*=\s*(.*?);', line)
        if variable_match:
            var_name = variable_match.group(2)
            value = variable_match.group(3)
            # 检查是否为数组
            if value.startswith('[') and value.endswith(']'):
                # 对于数组，计算元素数量
                value = len(value.split(','))
            else:
                try:
                    # 对于单一值，尝试转换为整数
                    value = int(value)
                except ValueError:
                    # 如果无法转换为整数，则保留原始表达式
                    value = value  
            variables_and_lengths[var_name] = value

        # 提取量子比特数组的长度
        array_match = re.match(r'^\s*use (\w+)\s*=\s*Qubit\[([\w\s\-+*\/]+)\];', line)
        if array_match:
            array_name = array_match.group(1)
            array_length_expression = array_match.group(2)
            try:
                # 尝试计算数组长度
                array_length = eval(array_length_expression, {}, variables_and_lengths)
            except:
                # 如果无法计算，则设置为 None
                array_length = None
            if array_length is not None:
                variables_and_lengths[array_name] = array_length
    keys_to_remove = []
    variables_and_lengths_TEMP=variables_and_lengths
    # 遍历字典，检查每个键的值
    for key, value in variables_and_lengths_TEMP.items():
        # 检查值是否为数字
        if not isinstance(value, (int, float)):
            for key1, value1 in variables_and_lengths_TEMP.items():
                if value== key1:
                    variables_and_lengths[key] = value1

            # 如果不是数字，添加到待删除列表中
    for key, value in variables_and_lengths.items():
        # 检查值是否为数字
        if not isinstance(value, (int, float)):
            keys_to_remove.append(key)

    # 遍历待删除键列表，从字典中删除这些键
    for key in keys_to_remove:
        del variables_and_lengths[key]
    # print("variables_and_lengths",variables_and_lengths)
    return variables_and_lengths

def extract_for_loop_range(test_case: str) -> (int, int):
    """ 使用正则表达式找到 for 循环范围是多少 """

    var_dict=extract_long(test_case)
    for_match = re.search(r'for\s*\([^)]*in\s*(.*?)\s*\.\.\s*(.*?)\)', test_case)
    if for_match:
        start_range = for_match.group(1) 
        end_range = for_match.group(2)  
        # 若开始范围为纯数字，则直接转为整数
        r = int(start_range) if start_range.isdigit() else var_dict.get(start_range, None)
        if not r:
            return None
        # 若结束范围为纯数字，则直接转为整数；否则计算其值
        if end_range.isdigit():
            l = int(end_range)
        else:
            for variable, value in var_dict.items():
                end_range = end_range.replace(variable, str(value))
            if end_range.isdigit():
                l = int(end_range)
                return [r, l]  
            else:
                return None  
    else:
        return None


def extract_array_access_range(test_case):
    """ 寻找除 for循环中数组的访问界限 """

    for_body_match = re.search(r'for\s*\(.*?\)\s*{(.*?)}', test_case, re.DOTALL)
    i_range = extract_for_loop_range(test_case)
    if not i_range:
        return []
    var_dict = extract_long(test_case)
    if not for_body_match:
        return []
    for_body = for_body_match.group(1)
    
    # 使用正则表达式搜索所有数组访问的项
    array_access_matches = re.findall(r'(\w+)\[(.*?)\]', for_body) 
    results = []
    for array_name, index_expr in array_access_matches:
        for variable, value in var_dict.items():
            index_expr = index_expr.replace(variable, str(value))
        if  index_expr=="i":
            index_expr_for_lower = index_expr.replace(index_expr, str(i_range[0])) 
            lower_bound = eval(index_expr_for_lower)
            index_expr_for_upper = index_expr.replace(index_expr, str(i_range[1]))
            upper_bound = eval(index_expr_for_upper)
        else:
            lower_bound = upper_bound = eval(index_expr)   
        results.append((array_name, lower_bound, upper_bound))
    
    return  results


def adjust_for_loop_range(test_case: str,count) -> str:
    """ 获取所有变量和数组的长度，对简单的修改 """

    var_len_dict = extract_long(test_case)
    # 获取所有数组访问的范围
    results = extract_array_access_range(test_case)
    # 计算 results 中数组的最小长度
    min_length = -10
    for array_name, _, _ in results:
        if array_name in var_len_dict and var_len_dict[array_name] < min_length:
            min_length = var_len_dict[array_name]       
    # 如果没有任何数组被匹配，则将 min_length 设置为一个默认值
    if min_length == -10:
        min_length = 0
    # 对每一个数组访问的范围进行检查
    for _, lower_bound, upper_bound in results:
        # 如果某一访问范围超出了其数组长度或者lower_bound > upper_bound，则需要调整 for 循环的范围
        if (lower_bound < 0 or upper_bound >= min_length) or (lower_bound > upper_bound):
            # 将范围调整为 [0, min_length - 1]
            left_matches = re.findall(r'mutable (left\d+) = .*?;', test_case)
            right_matches = re.findall(r'mutable (right\d+) = .*?;', test_case)
            
            if left_matches:
                for match in left_matches:
                    test_case = re.sub(rf'mutable {match} = .*?;', rf'mutable {match} = 0;', test_case)
                    count =count+1
            if right_matches:
                for match in right_matches:
                    test_case = re.sub(rf'mutable {match} = .*?;', rf'mutable {match} = {min_length - 1};', test_case)
            break
    return test_case , count


def check_access_out_of_range(test_case,count):
    """"""
    
    if "right" in test_case and "left" in test_case:
        test_case,count = adjust_for_loop_range(test_case,count)
    var_len_dict = extract_long(test_case)
    results = extract_array_access_range(test_case)
    #计算最大长度差值 
    max_diff = 0
    for array_name, lower_bound, upper_bound in results:
        if array_name in var_len_dict:
            # 注意，因为我们的范围是闭区间，所以实际的访问长度是 upper_bound - lower_bound + 1
            access_length = upper_bound - lower_bound + 1
            array_length = var_len_dict[array_name]
            if access_length > array_length:
                diff = access_length - array_length
                if diff > max_diff:
                    max_diff = diff
    if max_diff > 0:
        loop_range_match = re.search(r'for\s*\(i\s*in\s*.*?\.\.\s*(.*?)(\)|\s)', test_case)
        if  loop_range_match:
            upper_bound_str = loop_range_match.group(1)
            # 判断上界是否可以直接转换为整数，否则尝试计算其值
            try:
                upper_bound_val = int(upper_bound_str)
            except ValueError:
                # 使用之前的变量字典求值
                for variable, value in var_len_dict.items():
                    upper_bound_str = upper_bound_str.replace(variable, str(value))
                upper_bound_val = eval(upper_bound_str)
            modified_upper_bound = str(upper_bound_val - max_diff)
            # 使用re.sub()方法替换原始上界值
            modified_test_case = re.sub(re.escape(upper_bound_str), modified_upper_bound, test_case, count=1)
            count =count +1
            return  modified_test_case,count
    return test_case,count


def modify_controlled_x(test_case: str,count) -> str:
    """  """
    
    # 使用正则表达式匹配Controlled X的模式
    pattern = r'Controlled X\(\[([a-zA-Z0-9_]+)\[([a-zA-Z0-9_]+)\]\],\s*([a-zA-Z0-9_]+)\[([a-zA-Z0-9_]+)\]\);'
    match = re.search(pattern, test_case)
    
    # 如果没有找到匹配的模式，直接返回原始的测试用例
    if not match:
        return test_case,count
    
    array_name = match.group(1)
    idx1_name = match.group(2)
    idx2_name = match.group(4)

    # 获取变量idx1和idx2的真实值
    idx1_value_pattern = rf"mutable {idx1_name} = (\d+);"
    idx2_value_pattern = rf"mutable {idx2_name} = (\d+);"
    
    idx1_value = int(re.search(idx1_value_pattern, test_case).group(1)) if re.search(idx1_value_pattern, test_case) else int(idx1_name)
    idx2_value = int(re.search(idx2_value_pattern, test_case).group(1)) if re.search(idx2_value_pattern, test_case) else int(idx2_name)
    # print(idx1_value,idx2_value)
    if idx1_value == idx2_value:
        # 修改量子比特数组的长度
        test_case = re.sub(r'use ' + array_name + r' = Qubit\[\d+\];', 'use ' + array_name + ' = Qubit[2];', test_case)
        
        # 更新idx1和idx2的值
        test_case = test_case.replace(f'mutable {idx1_name} = {idx1_value};', f'mutable {idx1_name} = 0;')
        test_case = test_case.replace(f'mutable {idx2_name} = {idx2_value};', f'mutable {idx2_name} = 1;')
        count= count+1
    return test_case,count

def prevent_qubit_overflow(test_case: str, count) -> str:
    """防止量子比特数组越界，并处理 mutable 关键字定义的变量"""
    
    lines = test_case.split('\n')
    
    # 存储变量名和对应的值
    variable_values = {}
    # 记录需要修改的变量以及其在代码中的位置和缩进
    variables_to_modify = {}

    # 遍历代码行，提取 let、use 和 mutable 中定义的变量及其值
    for i, line in enumerate(lines):
        let_match = re.match(r'(\s*)(let|mutable)\s+(\w+)\s*=\s*(\d+);', line)
        use_match = re.match(r'^\s*use\s+(\w+)\s*=\s*Qubit\[(\w+)\];', line)
        
        if let_match:
            indentation, _, variable, value = let_match.groups()
            variable_values[variable] = int(value)
            # 记录变量的位置和缩进
            variables_to_modify[variable] = [i, indentation, None]
        
        if use_match:
            _, size_variable = use_match.groups()
            size = int(size_variable) if size_variable.isdigit() else variable_values.get(size_variable, 0)

            # 如果大小超过 30，则记录需要修改的变量的新值
            if size > 30 and size_variable in variables_to_modify:
                variables_to_modify[size_variable][2] = 30

    # 修改超过 30 的变量
    for variable, [line_index, indentation, new_value] in variables_to_modify.items():
        if new_value is not None:
            count += 1
            lines[line_index] = f"{indentation}let {variable} = {new_value};"

    return '\n'.join(lines), count


def array_process(test_case: str, count):
    # print("===in array process===\n\n"+test_case+"===out array process===\n")
    if "//wrong" in test_case :
        return test_case,count
    test_case,count = array_max_process_1(test_case,count)
    test_case,count = array_negative_numbers(test_case,count)
    test_case,count = array_max_process(test_case,count)
    test_case,count = modify_input_code(test_case,count)
    test_case,count = fix_negative_exponents(test_case,count)
    test_case,count = modify_code_ControlledOnInt(test_case,count)
    test_case,count = modify_code_ApplyXorInPlace(test_case,count)
    test_case,count = check_access_out_of_range(test_case,count)
    test_case,count = modify_controlled_x(test_case,count)
    test_case,count = prevent_qubit_overflow(test_case,count)
    return test_case,count


# if __name__ == "__main__":

#     test_case="""

# namespace NISLNameSpace {
#     open Microsoft.Quantum.Oracles;
#     open Microsoft.Quantum.Logical;
#     open Microsoft.Quantum.Arithmetic;
#     open Microsoft.Quantum.Intrinsic;
#     open Microsoft.Quantum.Diagnostics;
#     open Microsoft.Quantum.Canon;
#     open Microsoft.Quantum.Math;
#     open Microsoft.Quantum.Convert;
#     open Microsoft.Quantum.Arrays;


    
#     @EntryPoint()
#     operation main() : Unit {
#         //correct
#         let modulus91 = 0;
#         let power91 = 63 - 1;
#         let generator91 = 0 + 1;
#         //no cons
#         mutable nSites6206 = -66;
#         mutable time6206 = PI()/4.0;
#         mutable dt6206 = -26.25847610932649734;
#                 use qs6206 = Qubit[nSites6206];
#                 ApplyToEach(H, qs6206);
#                 let nSteps6206 = Floor(time6206 / dt6206);
#         let target91 = qs6206;
#             MultiplyByModularInteger(ExpModI(generator91, power91, modulus91), modulus91, LittleEndian(target91));
#             let bitsize91 = BitSizeI(modulus91);
#         DumpMachine();
#         Message($"{bitsize91}");
#         ResetAll(target91);
#         ResetAll(qs6206);
        
#     }
# }
#         """
# a,v2=array_process(test_case,1)
# print(a)