import os
import re
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline, interp1d
import shutil
import subprocess

class colors:
    """ Define colors for printing. """
    
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def extract_tables_from_md(md_file):
    """ 
    Extracts Markdown tables from a given Markdown file.
    
    Args:
        md_file (str): The path to the Markdown file.
        
    Returns:
        list: A list of Markdown tables found in the file.
    """

    # Open the Markdown file specified by md_file in read mode
    with open(md_file, 'r', encoding='utf-8') as file:
        md_content = file.read()
    # Regular expression pattern to match Markdown tables
    table_pattern = r'\|.*\|[\s\S]*?\n(?=\n|\Z)'
    # Find all occurrences of tables in md_content using the pattern
    tables = re.findall(table_pattern, md_content)
    return tables

def draw_one_line(y, label, color):
    """ 
    Draw a smooth curve line with a given label and color.

    Args:
        y (list): A list of y-values.
        label (str): The label for the line chart.
        color (str): The color for the line chart.
    """

    x = range(0, 25)
    x_list = np.linspace(0, 24, 50)
    f = interp1d(x, y, kind='linear')
    y_list = f(x_list)
    plt.plot(x_list, y_list, label=label, color=color)

def run_one_testcase(cmd, dst_folder, testcase):
    """
    Run one test case.

    Parameters:
        cmd (list): The list of command.
        dst_folder (str): The destination folder where the test case is executed.
        testcase (str): The name of the test case.
    """

    # Remove the bin and obj folders.
    for root, dirs, files in os.walk(dst_folder):
        for dirName in dirs:
            if dirName == "bin" or dirName == "obj":
                shutil.rmtree(os.path.join(dst_folder, dirName), ignore_errors=True)
    # Run the test case.
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=dst_folder)
    # If the output contains "InvalidOperationException", skip the test case.
    if "InvalidOperationException" in result.stdout:
        return
    # Print the output.
    print(colors.BOLD+"Output of "+" ".join(cmd)+f" for {testcase}:"+colors.RESET)
    print(result.stdout)
    # print(result.stderr)

def run_all_testcases(src_folder, dst_folder, cmd_list):
    """
    Run all test cases.

    Parameters:
        src_folder (str): The source folder where the test cases are located.
        dst_folder (str): The destination folder where the test cases are executed.
        cmd_list (list): The list of command.
    """

    testcases = os.listdir(src_folder)
    testcases.sort(key = lambda x: int(x[7:x.index(".")]))
    for testcase in testcases:
        # Move the test case to the destination folder.
        src_file = os.path.join(src_folder, testcase)
        dst_file = os.path.join(dst_folder, "Program.qs")
        shutil.copy(src_file, dst_file)
        # Run the test case by QuantumSimulator, SparseSimulator, and ToffoliSimulator.
        for cmd in cmd_list:
            run_one_testcase(cmd, dst_folder, testcase)

def get_rate(num1: int, num2: int):
    """
    Get the ratio of num1 to num2.
    
    Parameters:
        num1 (int): The numerator.
        num2 (int): The denominator.
    
    Returns:
        float: The ratio of num1 to num2.
    """

    if num2 == 0:
        return 0.0
    else:
        return num1 / num2

def convert_to_percent(n):
    """
    Convert the ratio to percentage.
    
    Parameters:
        n (float): The ratio.
    
    Returns:
        str: The percentage.
    """

    n = round(n, 2)
    return "%.0f%%" % (n * 100)

def calculate(d: dict):
    """
    Calculate recall and precision of constraints.

    Parameters:
       d (dict): The dictionary of analysis results.

    Returns:
        tuple: The values of recall and precision.
    """

    classical_id, classical_ex, quantum_id, quantum_ex = 0.0, 0.0, 0.0, 0.0
    classical_id_total, classical_ex_total, quantum_id_total, quantum_ex_total = 0, 0, 0, 0
    for namespace, properties in d.items():
        classical_id += get_rate(properties["classical-identified"], properties["classical-id-total"])
        classical_ex += get_rate(properties["classical-extracted"], properties["classical-ex-total"])
        quantum_id += get_rate(properties["quantum-identified"], properties["quantum-id-total"])        
        quantum_ex += get_rate(properties["quantum-extracted"], properties["quantum-ex-total"])
        if properties["classical-id-total"] != 0:
            classical_id_total += 1
        if properties["classical-ex-total"] != 0:
            classical_ex_total += 1
        if properties["quantum-id-total"] != 0:
            quantum_id_total += 1
        if properties["quantum-ex-total"] != 0:
            quantum_ex_total += 1
    return convert_to_percent(classical_id / classical_id_total), convert_to_percent(classical_ex / classical_ex_total), \
           convert_to_percent(quantum_id / quantum_id_total), convert_to_percent(quantum_ex / quantum_ex_total)

