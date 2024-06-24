import re

from basic_operation.file_operation import initParams
from DBOperation.dboperation_sqlite import DataBaseHandle

def filter_boundary(result_db, history_db):
    """ Query history-bugs.db and filter. """

    suspicious_results = result_db.selectAll("select * from differentialResult_cw")
    #  where stderr not like '%build failed%'
    history_bugs = history_db.selectAll("select * from bug_list_boundary")
    print("There are",len(history_bugs),"historical bugs in database. Start to filter. ")
    valid_faulty = ["ResultArrayAsInt"]
    invalid_faulty = [  "PNorm", "PNormalized", "ArcCosh", 
                        "ExtendedGreatestCommonDivisorL", "ExtendedGreatestCommonDivisorI", 
                        "GreatestCommonDivisorI", "GreatestCommonDivisorL", 
                        "BitSizeL", "BitSizeI", "TrotterSimulationAlgorithm"]
    histotical_bugs, root_bugs = [], []
    count1, count2, count3 = 0, 0, 0
    with open("new_anomalies.txt", "w") as f1, open("bug.txt", "w") as f2, open("faulty.txt", "w") as f3:
        for i, res in enumerate(suspicious_results, start=1):
            print("=="+str(i)+"==")
            # 1-Need to analyze; 2- Already analyzed bugs; 3- Already analyzed faulties
            is_suspicious = 1
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
            # TEMP. 20
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
    print("\033[94m", count1, "anomalous await to analyze. ", 
          count2, "anomalous are historical bugs. ",
          count3, "anomalous are recorded faulties. \033[0m")
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
    count1, count2, count3 = 0, 0, 0
    with open("new_anomalies.txt", "a+") as f1, open("bug.txt", "a+") as f2, open("faulty.txt", "a+") as f3:
        for res in suspicious_results:
            # 1-Need to analyze; 2-Already analized
            is_suspicious = 1
            for api_name in history_bugs:
                if api_name+"(" in res[2]:
                    is_suspicious = 2
                    count2 += 1
                    break
            if is_suspicious == 2:
                f2.write(str(res[1])+api_name+"\n")
                continue
            for api_name in faulty:
                if api_name+"(" in res[2]:
                    is_suspicious = 3
                    count3 += 1
                    break
            if is_suspicious == 3:
                f3.write(str(res[1])+api_name+"\n")
                continue
            f1.write(str(res[1])+"\n")
            count1 += 1
    print("\033[94m", count1, "anomalous await to analyze. ", 
          count2, "anomalous are historical bugs. ",
          count3, "anomalous are recorded faulties. \033[0m")


def main():
    params = initParams("../config.json")
    result_db = DataBaseHandle(params["result_db"])
    history_db = DataBaseHandle(params["history_db"])
    print("==language-level testing==")
    filter_boundary(result_db, history_db)
    print("==differential testing==")
    filter_differential(result_db)


if __name__ == "__main__":
    main()