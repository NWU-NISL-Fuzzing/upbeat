import os
import re
import time
import random
import pathlib

from Fuzzing.lib.Harness import run_and_get_cov
from DBOperation.dboperation_sqlite import DataBaseHandle
from basic_operation.file_operation import initParams, add_to_write


tempProj = pathlib.Path("./qsharpPattern").absolute()

def merge_coverage(tempXml: str):
    """ 默认所有.coverage文件存储在cov子文件夹下，进行合并，最终结果位于final.xml """

    res = os.system("dotnet-coverage merge -o final.xml -f xml cov/*.coverage")
    return res


def read_coverage(path: str):
    standard_block_cov, standard_line_cov = 0.00, 0.00
    numerics_block_cov, numerics_line_cov = 0.00, 0.00
    chemistry_block_cov1, chemistry_line_cov1 = 0.00, 0.00
    chemistry_block_cov2, chemistry_line_cov2 = 0.00, 0.00
    chemistry_block_cov3, chemistry_line_cov3 = 0.00, 0.00
    ml_block_cov, ml_line_cov = 0.00, 0.00

    regex = "<module block_coverage=\"([0-9.]+)\" line_coverage=\"([0-9.]+)\".* path=\"(.*?)\"\>"
    # regex = r"path=\"(.*?)\" block_coverage=\"([\d\.]+)\" line_coverage=\"([\d\.]+)\""
    # 读取覆盖率.xml文件
    with open(path+"/final.xml", "r") as f:
        content = f.read()
    # 识别其中Standard、Numerics、Chemistry和Machine四个模块的覆盖率
    for match in re.finditer(regex, content):
        print("match:"+match.group())
        if "microsoft.quantum.standard.dll" in match.group():
            standard_block_val, standard_line_val = match.group(1), match.group(2)
            # add_to_write("standard_cov.txt", standard_block_val+" "+standard_line_val+"\n")
            standard_block_cov += float(standard_block_val)
            standard_line_cov += float(standard_line_val)
        elif "microsoft.quantum.numerics.dll" in match.group():
            numerics_block_val, numerics_line_val = match.group(1), match.group(2)
            # add_to_write("numerics_cov.txt", numerics_block_val+" "+numerics_line_val+"\n")
            numerics_block_cov += float(numerics_block_val)
            numerics_line_cov += float(numerics_line_val)
        elif "microsoft.quantum.chemistry.datamodel.dll" in match.group():
            chemistry_block_val1, chemistry_line_val1 = match.group(1), match.group(2)
            # add_to_write("chemistry_cov1.txt", chemistry_block_val1+" "+chemistry_line_val1+"\n")
            chemistry_block_cov1 += float(chemistry_block_val1)
            chemistry_line_cov1 += float(chemistry_line_val1)
        elif "microsoft.quantum.chemistry.metapackage.dll" in match.group():
            chemistry_block_val2, chemistry_line_val2 = match.group(1), match.group(2)
            # add_to_write("chemistry_cov2.txt", chemistry_block_val2+" "+chemistry_line_val2+"\n")
            chemistry_block_cov2 += float(chemistry_block_val2)
            chemistry_line_cov2 += float(chemistry_line_val2)
        elif "microsoft.quantum.chemistry.runtime.dll" in match.group():
            chemistry_block_val3, chemistry_line_val3 = match.group(1), match.group(2)
            # add_to_write("chemistry_cov3.txt", chemistry_block_val3+" "+chemistry_line_val3+"\n")
            chemistry_block_cov3 += float(chemistry_block_val3)
            chemistry_line_cov3 += float(chemistry_line_val3)
        elif "microsoft.quantum.machinelearning.dll" in match.group():
            ml_block_val, ml_line_val = match.group(1), match.group(2)
            # add_to_write("ml_cov.txt", ml_block_val+" "+ml_line_val+"\n")
            ml_block_cov += float(ml_block_val)
            ml_line_cov += float(ml_line_val)
    return [standard_block_cov, standard_line_cov, 
            numerics_block_cov, numerics_line_cov, 
            chemistry_block_cov1, chemistry_line_cov1, 
            chemistry_block_cov2, chemistry_line_cov2, 
            chemistry_block_cov3, chemistry_line_cov3, 
            ml_block_cov, ml_line_cov]


def run_all(targetDB: DataBaseHandle, testcaseList: list):
    """ 对所有测试用例执行边界值测试，同时进行覆盖率统计 """

    last_coverage_check = time.time() 
    file_path = os.path.join('/root/UPBEAT/src/Fuzzing/qsharpPattern', 'qfuzz.txt')
    tempXml = "./qsharpPattern/cov" # 存放.xml文件的文件夹
    count =0 
    for index, testcase in enumerate(testcaseList, start=1):
        print(index)
        testcaseContent = testcase[0]
        # TMP.array_processor的错误替换
        if " inf" in testcaseContent:
            continue
        # 获取flag
        if "//correct" in testcaseContent:
            flag = 1
        elif "//wrong" in testcaseContent:
            flag = 0
        else:
            flag = -1
        # 执行
        output = run_and_get_cov(tempProj, index, testcaseContent)
        targetDB.insertToTotalResult(output, "originResult_cw")
        targetDB.commit()
        # 对结果进行分析
        if  ((flag == 1 and output.returnCode != 0) or 
            (flag == 0 and output.returnCode == 0) or 
            output.outputClass in ["timout", "crash"]):
            print("!!!find wrong cons")
            targetDB.insertToDifferentialResult(output, "differentialResult_cw")
        else:
            print("nothing happened")
        # 合并覆盖率
        if time.time() - last_coverage_check >= 3600:
            count += 1
            # 合并并读取覆盖率
            merge_coverage(tempXml)
            result_list = read_coverage(str(tempProj))
            # 获取当前时间，写入结果文件中
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            for i in range(0, 12, 2):
                with open(file_path, 'a') as file:
                    file.write(f"{current_time}: {result_list[i]:.2f} {result_list[i + 1]:.2f}\n")
            # 用于下一轮计算什么时候统计覆盖率
            last_coverage_check = time.time()
        if count == 24:
            break


def main():
    print("Clean the 'cov' folder and ensure you have enough test cases:D")
    params = initParams("../config.json")
    # 获取数据库
    targetDB = DataBaseHandle(params["result_db"])
    targetDB.createTable("differentialResult_cw")
    targetDB.createTable("originResult_cw")
    # 遍历所有可以正确执行的程序
    # sql_str = "select Content from originResult_cw where stderr not like '%build failed%' and Content not like '%//wrong%';"
    # 边界值测试和覆盖率统计同时进行
    sql_str = "select Content from corpus where Content not like '%//wrong%';"
    # sql_str = "select Content from corpus where Content not like '%//wrong%' limit 0,1;"
    testcaseList = targetDB.selectAll(sql_str)
    # 打乱顺序，避免出现两次平缓
    random.shuffle(testcaseList)
    print("totally:",len(testcaseList))
    run_all(targetDB, testcaseList)


if __name__ == "__main__":
    main()
