import os
import pathlib

from DBOperation.dboperation_sqlite import DataBaseHandle
from Fuzzing.lib.Harness import *
from Fuzzing.lib.post_processor import *
from Generate.basic_operation.file_operation import initParams

params = initParams("../config.json")
targetDB = DataBaseHandle(params["result_db"])
tempProj = pathlib.Path("./qsharpPattern").absolute()


def diff_testing(index: int, output):
    """ 差分测试主函数 """

    outputs = [output]
    command_list = [["dotnet", "run", "-s", "SparseSimulator"],
                    ["dotnet", "run", "-s", "ToffoliSimulator"]]
    # 使用另外两个模拟器执行测试用例
    for cmd in command_list:
        outputs.append(execute(index, output.testcaseContent, cmd, False))
    # 分析
    vote(outputs, output.testcaseContent)
    # 每执行完一个测试用例就提交一次修改
    targetDB.commit()

def bound_value_testing(index: int, testcase_content: str):
    """ 边界值测试主函数 """

    print("running "+str(index))
    susp_flag = False
    # 获取flag
    if "//correct" in testcase_content:
        flag = 1
    elif "//wrong" in testcase_content:
        flag = 0
    else:
        flag = -1
    # 运行
    output = execute(index, testcase_content, "dotnet run", True)
    # 添加原始用例执行结果
    targetDB.insertToTotalResult(output, "originResult_cw")
    targetDB.commit()
    # 对边界值测试结果进行分析
    if  ((flag == 1 and output.returnCode != 0) or 
        (flag == 0 and output.returnCode == 0) or 
        (flag == -1 and output.outputClass in ["timout", "crash"]) or
        (flag == -1 and "Overflow" in output.stderr) or 
        (flag == -1 and "OutOfMemory" in output.stderr)):
        print("!!!find wrong cons")
        susp_flag = True
        targetDB.insertToDifferentialResult(output, "differentialResult_cw")
    else:
        print("nothing happened")
    # 如果边界值测试结果不可疑，进行差分测试
    if not susp_flag and output.returnCode not in [134, 137]:
        diff_testing(index, output)

def main():
    # 创建剩余三个表
    targetDB.createTable("originResult_cw")
    targetDB.createTable("differentialResult_cw")
    # targetDB.createTable("originResult_sim")
    targetDB.createTable("differentialResult_sim")
    # 遍历所有生成的程序
    testcaseList = targetDB.selectAll("select Content from corpus;")
    print("totoally:"+str(len(testcaseList)))
    for index, testcase_content in enumerate(testcaseList, start=1):
        # print(testcase_content)
        bound_value_testing(index, testcase_content[0])
        # if index == 1:
        #     break
    targetDB.finalize()

if __name__ == "__main__":
    main()
