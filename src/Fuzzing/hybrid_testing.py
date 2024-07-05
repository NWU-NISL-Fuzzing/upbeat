import os
import pathlib

from DBOperation.dboperation_sqlite import DataBaseHandle
from Fuzzing.lib.Harness import *
from Fuzzing.lib.post_processor import *
from Generate.basic_operation.file_operation import initParams

params = initParams("../config.json")
tempProj = pathlib.Path("./qsharpPattern").absolute()


def diff_testing(targetDB: DataBaseHandle, index: int, output):
    outputs = [output]
    command_list = [["dotnet", "run", "-s", "SparseSimulator"],
                    ["dotnet", "run", "-s", "ToffoliSimulator"]]
    for cmd in command_list:
        outputs.append(execute(index, output.testcaseContent, cmd, False))
    vote(outputs, output.testcaseContent)
    targetDB.commit()

def bound_value_testing(targetDB: DataBaseHandle, index: int, testcase_content: str):
    print("==running "+str(index)+"th test case==")
    susp_flag = False
    if "//wrong" in testcase_content or "//invalid" in testcase_content:
        flag = 0
    elif "//correct" in testcase_content or "//valid" in testcase_content:
        flag = 1
    else:
        flag = -1
    output = execute(index, testcase_content, ["dotnet", "run"], False)
    targetDB.insertToTotalResult(output, "originResult_cw")
    targetDB.commit()
    if  ((flag == 1 and output.returnCode != 0) or 
        (flag == 0 and output.returnCode == 0) or 
        output.outputClass in ["timout", "crash"]):
        print("\033[91m!!!find anomaly\033[0m")
        susp_flag = True
        targetDB.insertToDifferentialResult(output, "differentialResult_cw")
    else:
        print("\033[92mnothing happened\033[0m")
    if not susp_flag and output.returnCode not in [134, 137]:
        diff_testing(targetDB, index, output)

def main():
    if not os.path.exists("cov"):
        os.makedirs("cov")
        print("Create the coverage folder.")
    targetDB = DataBaseHandle(params["result_db"])
    targetDB.createTable("originResult_cw")
    targetDB.createTable("differentialResult_cw")
    # targetDB.createTable("originResult_sim")
    targetDB.createTable("differentialResult_sim")
    testcaseList = targetDB.selectAll("select Content from corpus;")
    print("Here are "+str(len(testcaseList))+" test cases.")
    for index, testcase_content in enumerate(testcaseList, start=1):
        # print(testcase_content)
        bound_value_testing(targetDB, index, testcase_content[0])
        # if index == 1:
        #     break
    targetDB.finalize()

if __name__ == "__main__":
    main()
