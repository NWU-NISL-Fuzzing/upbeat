# This Python file uses the following encoding: utf-8
import re
import pathlib

from Fuzzing.lib.Harness import *
from Fuzzing.lib.Result import Output
from Fuzzing.lib.post_processor import *
from Fuzzing.lib.labdate import getUtcMillisecondsNow
from DBOperation.dboperation_sqlite import DataBaseHandle
from Generate.basic_operation.file_operation import initParams


class DifferentialTest:
    def __init__(self, db_path=""):
        self.params = initParams("../config.json")
        if db_path == "":
            self.targetDB = DataBaseHandle(self.params["result_db"])
        else:
            self.targetDB = DataBaseHandle(db_path)
        self.command = [["dotnet", "run", "-s", "SparseSimulator"],
                        ["dotnet", "run", "-s", "ToffoliSimulator"]]

    def execute_and_analysis(self, result):
        """ 进行差分测试 """

        # print("result:",result)
        # 从边界值测试结果中获取dotnet run的输出
        outputs = []
        output = Output(testcaseId=result[1], testcaseContent=result[2], command=result[3], returncode=result[4],
                        stdout=result[5], stderr=result[6], duration_ms=result[7])
        output.stdout = get_prob_distribution(output.stdout)
        outputs.append(output)
        # 运行
        command_list = self.command
        for cmd in command_list:
            outputs.append(execute(result[1], result[2], cmd, False))
        # 分析
        vote(outputs, result[2])
        # 每执行完一个测试用例就提交一次修改
        self.targetDB.commit()


def main():
    start_time = getUtcMillisecondsNow()
    tester = DifferentialTest()
    tester.targetDB.createTable("differentialResult_sim")
    # tester.targetDB.createTable("originResult_sim")
    # 遍历每个可以正确运行的生成片段
    sql =   "select * from originResult_cw where stderr not like '%build failed%' and "+\
            "testcase_id not in (select testcase_id from differentialResult_cw);"
    result = tester.targetDB.selectAll(sql)
    # result = result[:1]
    print("totally:" + str(len(result)))
    for index, item in enumerate(result, start=1):
        print(index)
        tester.execute_and_analysis(item)
    tester.targetDB.finalize()
    end_time = getUtcMillisecondsNow()
    print("Spending time:"+str(end_time-start_time))


if __name__ == "__main__":
    main()