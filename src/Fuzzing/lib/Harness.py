# -*- coding: utf-8 -*-

import os
import pathlib
import shutil
import subprocess
import collections

from Fuzzing.lib import labdate
from Fuzzing.lib.Result import Output
from Fuzzing.lib.post_processor import *
from DBOperation.dboperation_sqlite import DataBaseHandle
from Generate.basic_operation.file_operation import initParams

params = initParams("../config.json")
history_db_path = params["history_db"]
targetDB = DataBaseHandle(params["result_db"])
temp_proj = pathlib.Path(params["temp_project"])

def get_majority_output(outputs):
    """ Select the most frequent of outputs. """

    majority_stdout, stdout_majority_size = collections.Counter([
        output.stdout for output in outputs
    ]).most_common(1)[0]
    return majority_stdout, stdout_majority_size


def vote(outputs, testcase_content):
    """ Vote scheme. """

    is_susp = False
    if outputs is None:
        return []
    majority_stdout, stdout_majority_size = get_majority_output(outputs)
    # print("majority_stdout: ", majority_stdout, " stdout_majority_size:", stdout_majority_size)
    for output in outputs:
        # print("check output:\n"+output.stdout+"--end--\n")
        if "NotImplementedException" in output.stdout or "The Toffoli simulator" in output.stdout:
            continue
        elif output.stdout != majority_stdout:
            # output.stdout != "" and 
            if check_strings_in_db(history_db_path, testcase_content, output.stdout) and check_outputs(outputs):
                print("\033[91m!!!find inconsistency\033[0m")
                targetDB.insertToDifferentialResult(output, "differentialResult_sim")
                targetDB.commit()
                is_susp = True
    if not is_susp:
        print("\033[92mnothing happened\033[0m")

def execute(index: int, testcase_content: str, command: str, need_coverage: bool):
    """ Run test case and store results in the database. """

    print("\033[1mcmd:\033[0m" + " ".join(command))
    if need_coverage:
        output = run_and_get_cov(temp_proj, index, testcase_content)
        output.stdout = remove_cov_info(output.stdout)
    else:
        output = run_testcase(temp_proj, index, testcase_content, command)
    output.stdout = get_prob_distribution(output.stdout)
    # if output.stdout!="" :
    #     if check_strings_in_db(history_db_path,testcase_content, output.stdout):
    #         targetDB.insertToTotalResult(output, "originResult_sim")
    return output

def remove_cov_info(output: str):
    """ Extract the coverage outputs when running `dotnet run`. """

    lines = output.split("\n")
    return lines[0]+"\n"+"\n".join(output[4:-1])

def run_and_get_cov(temp_proj: pathlib.Path, testcaseId: int, testcaseContent: str, tool_name = "upbeat"):
    """ Run and get coverage results. """

    os.chdir(temp_proj)
    # Write down.
    update_content(temp_proj, testcaseContent)
    # Prepare.
    os.system("rm -rf obj bin")
    os.system("dotnet build")
    os.system("cp ../pdb_zip/* bin/Debug/net6.0/")
    # Collect.
    cmd = ["dotnet-coverage", "collect", "./bin/Debug/net6.0/qsharpPattern"]
    # cmd = ["dotnet-coverage", "collect", "dotnet run"]
    start_time = labdate.getUtcMillisecondsNow()
    encoding_str = "utf-8"
    pro = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False,
                            stderr=subprocess.PIPE, universal_newlines=True, encoding=encoding_str)
    try:
        stdout, stderr = pro.communicate(timeout=120)
        returnCode = pro.returncode
    except subprocess.TimeoutExpired:
        pro.kill()
        stdout = ""
        stderr = "timeout, kill the process"
        returnCode = -9
    except KeyboardInterrupt:
        pro.terminate()
    # Move coverage files.
    if os.path.exists("output.coverage"):
        new_file_name = f"./cov_{tool_name}/output{testcaseId}.coverage"
        shutil.move("output.coverage", new_file_name)
    end_time = labdate.getUtcMillisecondsNow()
    duration_ms = int(round((end_time - start_time).total_seconds() * 1000))
    output = Output(testcaseId=testcaseId, testcaseContent=testcaseContent, command="dotnet run", returncode=returnCode,
                    stdout=stdout, stderr=stderr, duration_ms=duration_ms)
    return output


def run_testcase(temp_proj: pathlib.Path, testcaseId: int, testcaseContent: str, cmd: list):
    """ Run a test case. """
    
    # print("temp_proj:",temp_proj)
    os.chdir(temp_proj)
    # Fresh the bin and obj folders.
    # Or error thrown：Program does not contain a static 'Main' method suitable for an entry point
    for root, dirs, files in os.walk(temp_proj):
        for dirName in dirs:
            if dirName == "bin" or dirName == "obj":
                shutil.rmtree(os.path.join(temp_proj, dirName), ignore_errors=True)
    update_content(temp_proj, testcaseContent)
    start_time = labdate.getUtcMillisecondsNow()
    # encoding_str = "gbk"
    encoding_str = "utf-8"
    pro = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False,
                            stderr=subprocess.PIPE, universal_newlines=True, encoding=encoding_str)
    command = " ".join(cmd)
    try:
        stdout, stderr = pro.communicate(timeout=120)
        returnCode = pro.returncode
    except subprocess.TimeoutExpired:
        pro.kill()
        stdout = ""
        stderr = "timeout, kill the process"
        returnCode = -9
    except KeyboardInterrupt:
        pro.terminate()
    end_time = labdate.getUtcMillisecondsNow()
    duration_ms = int(round((end_time - start_time).total_seconds() * 1000))
    output = Output(testcaseId=testcaseId, testcaseContent=testcaseContent, command=command, returncode=returnCode,
                    stdout=stdout, stderr=stderr, duration_ms=duration_ms)
    return output

def update_content(temp_proj: pathlib.Path, testcaseContent: str):
    """ Write content into temp project. """

    tempQsharpPath = temp_proj.joinpath("Program.qs")
    # encoding_str = "gbk"
    encoding_str = "utf-8"
    tempQsharpPath.write_text(testcaseContent, encoding=encoding_str)
