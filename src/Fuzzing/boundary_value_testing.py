import os
import sys
import pathlib

from DBOperation.dboperation_sqlite import DataBaseHandle
from Fuzzing.lib.Harness import run_testcase
from Fuzzing.lib.labdate import getUtcMillisecondsNow
from Generate.basic_operation.file_operation import initParams


params = initParams("../config.json")

def run_and_analysis(targetDB, index: int, testcase_content: str):
    print("==running "+str(index)+"th test case==")
    tempProj = pathlib.Path(params["temp_project"])
    # Get flag.
    if "//wrong" in testcase_content or "//invalid" in testcase_content:
        flag = 0
    elif "//correct" in testcase_content or "//valid" in testcase_content:
        flag = 1
    else:
        flag = -1
    # Run.
    command = ["dotnet", "run"]
    output = run_testcase(tempProj, index, testcase_content, command)
    # Insert result of original test case.
    targetDB.insertToTotalResult(output, "originResult_cw")
    targetDB.commit()
    # Analysis. 
    if  ((flag == 1 and output.returnCode != 0) or 
        (flag == 0 and output.returnCode == 0) or 
        output.outputClass in ["timout", "crash"]):
        print("\033[91m!!!find anomaly\033[0m")
        targetDB.insertToDifferentialResult(output, "differentialResult_cw")
    else:
        print("\033[92mnothing happened\033[0m")


def main():
    # start_time = getUtcMillisecondsNow()
    # Init the database. 
    targetDB = DataBaseHandle(params["result_db"])
    # Create other three tables.
    targetDB.createTable("differentialResult_cw")
    targetDB.createTable("originResult_cw")
    # Start to walk all test cases.
    testcaseList = targetDB.selectAll("select Content from corpus;")
    # testcaseList = targetDB.selectAll("select Content from corpus limit 0,1;")
    print("Here are "+str(len(testcaseList))+" test cases.")
    for index, testcase_content in enumerate(testcaseList, start=1):
        # print(testcase_content)
        if len(testcase_content) == 0:
            continue
        run_and_analysis(targetDB, index, testcase_content[0])
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
