import os
import sys
import pathlib

from DBOperation.dboperation_sqlite import DataBaseHandle
from Fuzzing.lib.Harness import run_testcase
from Fuzzing.lib.labdate import getUtcMillisecondsNow
from Generate.basic_operation.file_operation import initParams


params = initParams("../config.json")

def run_and_analysis(targetDB, index: int, testcaseContent: str):
    print("running "+str(index))
    tempProj = pathlib.Path(params["projectPattern"])
    # 获取flag
    if "//correct" in testcaseContent:
        flag = 1
    elif "//wrong" in testcaseContent:
        flag = 0
    else:
        flag = -1
    # 运行
    command = ["dotnet", "run"]
    output = run_testcase(tempProj, index, testcaseContent, command)
    # 添加原始用例执行结果
    targetDB.insertToTotalResult(output, "originResult_cw")
    targetDB.commit()
    # 对结果进行分析
    if  ((flag == 1 and output.returnCode != 0) or 
        (flag == 0 and output.returnCode == 0) or 
        output.outputClass in ["timout", "crash"]):
        print("\033[91m!!!find wrong cons\033[0m")
        targetDB.insertToDifferentialResult(output, "differentialResult_cw")
    else:
        print("\033[92mnothing happened\033[0m")


def main():
    # start_time = getUtcMillisecondsNow()
    # 获取数据库
    targetDB = DataBaseHandle(params["result_db"])
    # 创建剩余三个表
    # differentialResult表存放可疑用例执行结果，mutation表存放变异后测试用例，originResult表存放所有用例执行结果
    targetDB.createTable("differentialResult_cw")
    targetDB.createTable("originResult_cw")
    # 遍历所有生成的程序
    testcaseList = targetDB.selectAll("select Content from corpus;")
    # testcaseList = targetDB.selectAll("select Content from corpus limit 0,1;")
    print("Here are "+str(len(testcaseList))+" test cases.")
    for index, testcaseContent in enumerate(testcaseList, start=1):
        # print(testcaseContent)
        if len(testcaseContent) == 0:
            continue
        run_and_analysis(targetDB, index, testcaseContent[0])
        # break
    targetDB.finalize()
    # end_time = getUtcMillisecondsNow()
    # print("Finished. Spending time:"+str(end_time-start_time))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
    # main()
