import re
import sqlite3


def check_outputs(outputs):  
    """ 如果输出中出现Zero/One/True/False，不进行比较（返回False） """   
    
    first_output_found_zero, first_output_found_true = True, True
    for output in outputs:
        stdout = output.stdout
        if "Zero" in stdout or "One" in stdout or "True" in stdout or "False" in stdout:
            return False
    return True      


def is_digit_space_format(line):
    """ 检查一行是否为 'xxxx   xxxx' 格式（数字和空格） """
    
    parts = line.split()
    return len(parts) == 2 and all(part.isdigit() for part in parts)


def get_prob_distribution(output_content: str):
    """ 只获取概率分布 """

    if "The method or operation is not implemented" in output_content:
        return output_content

    classical_results = ""
    prob_list = []
    skip_lines = 0  # 添加一个计数器来跳过特定行数
    add_one = False  # 标志位，用于检测是否需要添加 '1.000000'
    lines = output_content.split("\n")
    for i, line in enumerate(lines):
        # 检查是否包含 "Offset" 和 "State Data"
        if "Offset" in line or "State Data" in line:
            # 检查第三行是否为纯数字
            if i + 2 < len(lines) and  all(char.isdigit() or char.isspace() for char in lines[i + 2]) \
                    and i + 3 < len(lines) and is_digit_space_format(lines[i + 3]):
                skip_lines = 4  # 只跳过第三行
            elif i + 2 < len(lines) and all(char.isdigit() or char.isspace() for char in lines[i + 2]):
                skip_lines = 3
            else:
                skip_lines = 2  # 否则跳过前两行
            add_one = True
        if skip_lines > 0:  # 如果计数器大于0，跳过这一行
            skip_lines -= 1
            continue
        if len(line) == 0:
            continue
        match = re.match(r"\|([0-9]+)⟩.*\[ ([0-9.]+) \].*", line)
        if match:
            if match.group(2) != "0.000000":
                prob_list.append(match.group(2))
        else:
            classical_results += line + "\n"  # 添加换行符以便在结果中区分不同的行
    if add_one:  # 如果标志位为 True，添加 '1.000000'
        prob_list.insert(0, '1.000000')
    prob_list.sort()
    return str(prob_list) + "\n" + classical_results.strip()  # 使用 strip() 去掉最后一个换行符


def check_strings_in_db(database_path, testcase_content, stdout):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bug_list")
    for row in cursor.fetchall():
        first_column, second_column = row[0], row[1]
        if first_column in testcase_content and second_column in stdout:
            conn.close()
            return 0
    conn.close()
    return 1

