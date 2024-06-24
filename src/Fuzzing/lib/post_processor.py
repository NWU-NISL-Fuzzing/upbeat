import re
import sqlite3


def check_outputs(outputs):  
    """ If `Zero/One/True/False` exists in the output, do not compare. (Random output) """   
    
    first_output_found_zero, first_output_found_true = True, True
    for output in outputs:
        stdout = output.stdout
        if "Zero" in stdout or "One" in stdout or "True" in stdout or "False" in stdout:
            return False
    return True      


def is_digit_space_format(line):
    """ xxxx   xxxx """
    
    parts = line.split()
    return len(parts) == 2 and all(part.isdigit() for part in parts)


def get_prob_distribution(output_content: str):
    """ Get probabilities. """

    if "The method or operation is not implemented" in output_content:
        return output_content

    classical_results = ""
    prob_list = []
    skip_lines = 0
    add_one = False
    lines = output_content.split("\n")
    for i, line in enumerate(lines):
        if "Offset" in line or "State Data" in line:
            if i + 2 < len(lines) and  all(char.isdigit() or char.isspace() for char in lines[i + 2]) \
                    and i + 3 < len(lines) and is_digit_space_format(lines[i + 3]):
                skip_lines = 4
            elif i + 2 < len(lines) and all(char.isdigit() or char.isspace() for char in lines[i + 2]):
                skip_lines = 3
            else:
                skip_lines = 2
            add_one = True
        if skip_lines > 0:
            skip_lines -= 1
            continue
        if len(line) == 0:
            continue
        match = re.match(r"\|([0-9]+)⟩.*\[ ([0-9.]+) \].*", line)
        if match:
            if match.group(2) != "0.000000":
                prob_list.append(match.group(2))
        else:
            classical_results += line + "\n"
    if add_one:
        prob_list.insert(0, '1.000000')
    prob_list.sort()
    return str(prob_list) + "\n" + classical_results.strip()


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

