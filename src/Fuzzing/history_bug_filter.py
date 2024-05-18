import re

from basic_operation.file_operation import initParams
from DBOperation.dboperation_sqlite import DataBaseHandle

def filter_boundary(result_db, history_db):
    """ 查询history-bugs.db，过滤掉已经发现的bug """

    suspicious_results = result_db.selectAll("select * from differentialResult_cw")
    #  where stderr not like '%build failed%'
    # 获取已经分析过的bug信息
    history_bugs = history_db.selectAll("select * from bug_list_boundary")
    print("There are",len(history_bugs),"historical bugs in database. Start to filter. ")
    # add_rules(history_bugs)
    # print(len(history_bugs))
    # 筛选带有合理值的误报
    valid_faulty = ["ResultArrayAsInt"]
    # 筛选带有不合理值的误报
    invalid_faulty = [  "PNorm", "PNormalized", "ArcCosh", 
                        "ExtendedGreatestCommonDivisorL", "ExtendedGreatestCommonDivisorI", 
                        "GreatestCommonDivisorI", "GreatestCommonDivisorL", 
                        "BitSizeL", "BitSizeI", "TrotterSimulationAlgorithm"]
    # 存放已被发现的bug，最后展示计数
    histotical_bugs, root_bugs = [], []
    count1, count2, count3 = 0, 0, 0
    # 打开文件，开始遍历
    with open("new_anomalies.txt", "w") as f1, open("bug.txt", "w") as f2, open("faulty.txt", "w") as f3:
        for i, res in enumerate(suspicious_results, start=1):
            print("=="+str(i)+"==")
            # 1-需要分析的 2-已经分析过的bug 3-已经分析过的误报
            is_suspicious = 1
            # 筛选掉返回值为134和137的
            if res[4] == 134 or res[4] == 137:
                continue
            for word in valid_faulty:
                if word+"(" in res[2] and "//correct" in res[2]:
                    bug_info = (word, "//correct")
                    is_suspicious = 3
                    break
            for word in invalid_faulty:
                if word+"(" in res[2] and "//wrong" in res[2]:
                    bug_info = (word, "//wrong")
                    is_suspicious = 3
                    break
            for api_name, keyword, root_cause in history_bugs:
                if api_name+"(" in res[2] and keyword in res[5]:
                    bug_info = (api_name, keyword)
                    is_suspicious = 2
                    root_bugs.append(root_cause)
                    break
            # 临时筛选：负数都被改成了20
            if " = 20" in res[2] and "//wrong" in res[2]:
                bug_info = (" = 20", "//wrong")
                is_suspicious = 3
            elif "//correct" in res[2] and "//no cons" in res[2]:
                bug_info = ("//correct", "//no cons")
                is_suspicious = 3
            elif "//correct" in res[2] and "//wrong" in res[2]:
                bug_info = ("//correct", "//wrong")
                is_suspicious = 3
            if is_suspicious == 1:
                f1.write(str(res[1])+"\n")
                count1 += 1
            elif is_suspicious == 2:
                histotical_bugs.append(bug_info)
                f2.write(str(res[1])+str(bug_info)+"\n")
                count2 += 1
            else:
                histotical_bugs.append(bug_info)
                f3.write(str(res[1])+str(bug_info)+"\n")
                count3 += 1
    print(count1, "anomalous await to analyze. ", 
          count2, "anomalous are historical bugs. ",
          count3, "anomalous are recorded faulties. ")
    # print("totally:", len(set(histotical_bugs)))
    # print("root:", len(set(root_bugs)))


def filter_differential(result_db):
    suspicious_results = result_db.selectAll("select * from differentialResult_sim")
    history_bugs = ["Adjoint ApplyAnd", "ApplyLowDepthAnd", 
                    "AssertMeasurement", "AssertPhaseLessThan",
                    "EstimateOverlapBetweenStates", "EstimateFrequencyA", "EstimateClassificationProbabilities",
                    "EstimateClassificationProbability", 
                    "IncrementByModularInteger"]
    faulty = ["EvaluateOddPolynomialFxP", "ComputeReciprocalFxP", "MeasureAllZ", "MaybeChooseElement", "Exp", "ExpFrac"]
    with open("new_anomalies.txt", "a+") as f1, open("bug.txt", "a+") as f2, open("faulty.txt", "a+") as f3:
        for res in suspicious_results:
            # 1-需要分析的 2-已经分析过的bug
            is_suspicious = 1
            for api_name in history_bugs:
                if api_name+"(" in res[2]:
                    is_suspicious = 2
                    break
            if is_suspicious == 2:
                f2.write(str(res[1])+api_name+"\n")
                continue
            for api_name in faulty:
                if api_name+"(" in res[2]:
                    is_suspicious = 3
                    break
            if is_suspicious == 3:
                f3.write(str(res[1])+api_name+"\n")
                continue
            f1.write(str(res[1])+"\n")


def main():
    """ 对两张可疑用例表进行筛选 """

    params = initParams("../config.json")
    result_db = DataBaseHandle(params["result_db"])
    history_db = DataBaseHandle(params["history_db"])
    filter_boundary(result_db, history_db)
    filter_differential(result_db)


if __name__ == "__main__":
    main()