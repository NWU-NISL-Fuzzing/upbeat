import os
import json
import shutil
import argparse
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate

from Reproduction.simple_tools import *
from Fuzzing.get_code_coverage import run_all
from Fuzzing.calculate_code_coverage import calculate_coverage
from Fuzzing.hybrid_testing import bound_value_testing
from DBOperation.dboperation_sqlite import DataBaseHandle

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rq", type=int, default=2, help="run rq2_1 or rq3")
    return parser.parse_args()

def rq1():
    md_file = '/root/upbeat/data/experiment/BugList.md'
    # Extract tables from the Markdown file
    tables = extract_tables_from_md(md_file)
    # Print each table found
    for table in tables:
        print(table)

def rq2_1():
    color_list = ['#9EB3C2', '#AFCAD0', '#C0E0DE', '#8BC3D9', '#6EACC7', '#468FAF', '#297596', '#014F86', '#013A63']
    tool_list = ['qsharpfuzz', 'quito', 'qsharpcheck', 'upbeat-m', 'muskit', 'qdiff', 'morphq', 'upbeat-r', 'upbeat']

    input_folder = "/root/upbeat/data/experiment/cov-result-origin/"
    output_folder = "/root/upbeat/data/experiment/cov-result-calculated/"
    line_cov_list, block_cov_list = [], []

    # Get the coverage results of all tools
    for tool, color in zip(tool_list, color_list):
        line_cov, block_cov = [0.0], [0.0]
        output_file = tool+".txt"
        with open(output_folder+output_file, "r") as f:
            lines = f.readlines()
        for line in lines:
            if len(line) == 0:
                continue
            block_cov.append(float(line.split(" ")[1]))
            line_cov.append(float(line.split(" ")[2]))
        line_cov_list.append(line_cov)
        block_cov_list.append(block_cov)

    # Draw the plot picture for the line coverage
    plt.figure(figsize=(6, 4))
    for line_cov, tool, color in zip(line_cov_list, tool_list, color_list):
        draw_one_line(line_cov, tool, color)
    plt.legend(fontsize='small')
    plt.xticks(np.arange(0, 25, 1))
    plt.yticks(np.arange(0, 60, 5))
    plt.margins(x=0, y=0)
    plt.savefig('rq2_1_1.png')

    # Draw the plot picture for the block coverage
    plt.figure(figsize=(6, 4))
    for block_cov, tool, color in zip(block_cov_list, tool_list, color_list):
        draw_one_line(block_cov, tool, color)
    plt.legend(fontsize='small')
    plt.xticks(np.arange(0, 25, 1))
    plt.yticks(np.arange(0, 45, 5))
    plt.margins(x=0, y=0)
    plt.savefig('rq2_1_2.png')

def rq2_2():
    # Get the anomaly results from lang_dir.
    lang_dir = "/root/upbeat/data/experiment/anomalies-lang/"
    regex = r"Can be detected by (.*)\."
    lang_results, diff_results = {}, {}
    lang_dir = "/root/upbeat/data/experiment/anomalies-lang/"
    for f in os.listdir(lang_dir):
        with open(lang_dir+f) as fi:
            second_line = fi.readlines()[1]
        match = re.search(regex, second_line)
        tool = match.group(1)
        if tool in lang_results:
            lang_results[tool] += 1
        else:
            lang_results[tool] = 1

    # Print the table. 
    print(tabulate(lang_results.items(), headers=["Tool", "#Anomalies via language-level test"]))
    print("\n")

    # Get the anomaly results from diff_dir.
    diff_dir = "/root/upbeat/data/experiment/anomalies-diff/"
    for f in os.listdir(diff_dir):
        with open(diff_dir+f) as fi:
            second_line = fi.readlines()[1]
        match = re.search(regex, second_line)
        tool = match.group(1)
        if tool in diff_results:
            diff_results[tool] += 1
        else:
            diff_results[tool] = 1

    # Print the table.
    print(tabulate(diff_results.items(), headers=["Tool", "#Anomalies via differential testing"]))

def run_baselines():
    baselines = ["qsharpfuzz", "quito", "qsharpcheck", "muskit", "qdiff", "morphq", "upbeat-m", "upbeat-r", "upbeat"]
    # Start to run
    for baseline in baselines:
        print(f"==Start to run test cases from {baseline}.==")
        targetDB = DataBaseHandle(f"/root/upbeat/data/experiment/database/{baseline}.db")
        targetDB.createTable("differentialResult_cw")
        targetDB.createTable("originResult_cw")
        sql_str = "select Content from corpus"
        testcaseList = targetDB.selectAll(sql_str)
        # Clean the coverage folder
        cov_folder = f"/root/upbeat/src/Reproduction/qsharpPattern/cov_{baseline}"
        if os.path.exists(cov_folder):
            shutil.rmtree(cov_folder)
        os.makedirs(cov_folder)
        # Run and get code coverage
        run_all(targetDB, testcaseList, 0.1, 0.1, baseline)
    for baseline in baselines:
        with open(f"/root/upbeat/src/Reproduction/qsharpPattern/{baseline}.txt", "r") as f:
            content = f.readlines()
        total_block_coverage, total_line_coverage = calculate_coverage(content[-6:])
        # pretty print
        total_block_coverage = round(total_block_coverage, 2)
        total_line_coverage = round(total_line_coverage, 2)
        print(f"{baseline:<{12}} (block){total_block_coverage} (line){total_line_coverage}")

def rq3():
    regex = r"Can be detected by (.*)\."
    # Get the ablation study results.
    abl_results = {}
    abl_dir = "/root/upbeat/data/experiment/ablation-study/"
    for f in os.listdir(abl_dir):
        with open(abl_dir+f) as fi:
            second_line = fi.readlines()[1]
        match = re.search(regex, second_line)
        tool = match.group(1)
        if tool in abl_results:
            abl_results[tool] += 1
        else:
            abl_results[tool] = 1

    # Print the table.
    print(tabulate(abl_results.items(), headers=["Tool", "#Bugs"]))

def run_ablation():
    # variants = ["upbeat-a", "upbeat-b", "upbeat"]
    variants = ["upbeat-b"]
    for variant in variants:
        print(f"==Start to run test cases from {variant}.==")
        targetDB = DataBaseHandle(f"/root/upbeat/data/experiment/database/{variant}.db")
        targetDB.createTable("originResult_cw")
        targetDB.createTable("differentialResult_cw")
        targetDB.createTable("differentialResult_sim")
        sql_str = "select Content from corpus"
        testcaseList = targetDB.selectAll(sql_str)
        # start to run
        for i, testcase in enumerate(testcaseList, start=1):
            bound_value_testing(targetDB, i, testcase[0])
            break

def rq4():
    # Calculate the analysis results of constraints from source code. 
    with open("/root/upbeat/data/experiment/constraint-extraction/source-code.json") as f1:
        code_dict = json.load(f1)
    code_result = calculate(code_dict)
    tab = [("Source Code", "classical", code_result[0], code_result[1]), ("", "quantum", code_result[2], code_result[3])]

    # Calculate the analysis results of constraints from API documents.
    with open("/root/upbeat/data/experiment/constraint-extraction/api-document.json") as f2:
        doc_dict = json.load(f2)
    doc_result = calculate(doc_dict)
    tab.append(("API Document", "classical", doc_result[0], doc_result[1]))
    tab.append(("", "quantum", doc_result[2], doc_result[3]))

    # Print the tables.
    print(tabulate(tab, headers=["Source", "Type", "Recall", "Precision"]))

def main():
    args = get_args()
    if args.rq == 1:
        rq1()
    elif args.rq == 2:
        rq2_1()
        rq2_2()
        run_baselines()
    elif args.rq == 3:
        rq3()
        run_ablation()
    elif args.rq == 4:
        rq4()
    else:
        print("Please input the right rq number: 1, 2, 3 or 4.")

if __name__ == "__main__":
    main()
