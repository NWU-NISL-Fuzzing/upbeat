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
    """ 选出数目最多的输出 """

    majority_stdout, stdout_majority_size = collections.Counter([
        output.stdout for output in outputs
    ]).most_common(1)[0]
    return majority_stdout, stdout_majority_size


def vote(outputs, testcase_content):
    """ 使用投票机制选出正确结果，将错误结果存入可疑用例表中 """

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
    """ 执行,获取结果,存入数据库 """

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
    """ 在使用dotnet run时截取覆盖率部分的输出 """

    lines = output.split("\n")
    return lines[0]+"\n"+"\n".join(output[4:-1])

def run_and_get_cov(temp_proj: pathlib.Path, testcaseId: int, testcaseContent: str):
    """ 该函数用于构建、运行并获取一个Q#测试用例的覆盖率结果 """

    os.chdir(temp_proj)
    # 更新测试用例内容
    update_content(temp_proj, testcaseContent)
    # 前期准备
    os.system("rm -rf obj bin")
    os.system("dotnet build")
    os.system("cp ../pdb_zip/* bin/Debug/net6.0/")
    # 运行并收集覆盖率
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
    # 移动覆盖率文件
    if os.path.exists("output.coverage"):
        new_file_name = "../cov/output"+str(testcaseId)+".coverage"
        shutil.move("output.coverage", new_file_name)
    end_time = labdate.getUtcMillisecondsNow()
    duration_ms = int(round((end_time - start_time).total_seconds() * 1000))
    output = Output(testcaseId=testcaseId, testcaseContent=testcaseContent, command="dotnet run", returncode=returnCode,
                    stdout=stdout, stderr=stderr, duration_ms=duration_ms)
    return output


def run_testcase(temp_proj: pathlib.Path, testcaseId: int, testcaseContent: str, cmd: list):
    """ 该函数用于执行一个Q#测试用例 """
    
    # print("temp_proj:",temp_proj)
    os.chdir(temp_proj)
    # 需要删除bin和obj目录
    # 否则对于相同的测试用例，会抛出错误：Program does not contain a static 'Main' method suitable for an entry point
    for root, dirs, files in os.walk(temp_proj):
        for dirName in dirs:
            if dirName == "bin" or dirName == "obj":
                shutil.rmtree(os.path.join(temp_proj, dirName), ignore_errors=True)
    update_content(temp_proj, testcaseContent)
    start_time = labdate.getUtcMillisecondsNow()
    # 在windows下，命令行的默认编码格式是gbk
    # 在linux下，命令行的编码格式是utf-8
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
    """ 将当前测试用例内容写到临时项目中 """

    tempQsharpPath = temp_proj.joinpath("Program.qs")
    # encoding_str = "gbk"
    encoding_str = "utf-8"
    tempQsharpPath.write_text(testcaseContent, encoding=encoding_str)
