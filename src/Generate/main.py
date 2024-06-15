# import re
import ast
import random

from basic_operation.file_operation import initParams
from basic_operation.dict_operation import get_rest_args
# from grammar_pattern.APIOperator import APIOperator
# from code_extractor.process_expr import cut_proper_bracket
# from code_extractor.process_stmt import is_basic_type, get_real_args_list
from cons_generator.cwvp import generate_if_cons_exist
from class_for_info.fragment_info import CodeFragmentInfo
from combine_fragment import CodeFragmentGenerator, get_contained_cons
from generate import Generate
from DBOperation.dboperation_sqlite import DataBaseHandle
from grammar_pattern.array_process import array_process

params = initParams("../config.json")
# api_op = APIOperator()
# standard_api_dict = api_op.init_api_dict("../ParseAPI/data/content.json")
# regex_for_call = r"([A-Za-z0-9_:]+)\((.*)\)"
testcase_num = 0

def complete_frag_by_cons(frag, targetDB):
    """ Generate test cases using specific fragment. """

    global testcase_num

    generate = Generate("../config.json")
    # 初始化代码片段拼接使用的class
    fragment = CodeFragmentGenerator(params["level"], params["ingredient_table_name"])
    # 获取代码片段生成和所需的变量
    available_variables = ast.literal_eval(frag[2])
    needful_variables = ast.literal_eval(frag[3])
    # 获取新的约束
    bool_expr_list, func_ret_list, quanternion_list, needful_args, partial_reset_stmt = \
        get_contained_cons(frag[1], needful_variables)
    # print("bool_expr_list:",bool_expr_list,"func_ret_list:",func_ret_list)
    if len(bool_expr_list) > 0 or len(func_ret_list) > 0:
        correct_stmt, wrong_stmt = \
            generate_if_cons_exist(bool_expr_list, func_ret_list, quanternion_list, needful_args)
    else:
        correct_stmt, wrong_stmt = "//no cons\n", "//no cons\n"
    # 如果生成失败
    if correct_stmt is None:
        # print("correct_stmt is None")
        return
    # 如果没有问题，从needful_variables中删去已经生成的变量
    # print("===needful_args:",needful_args)
    needful_variables = get_rest_args(needful_variables, needful_args)
    # print("correct_stmt:\n"+correct_stmt+"wrong_stmt:\n"+wrong_stmt)
    # 不管是正确还是错误的语句，拼接的代码片段应该是同一个
    if len(frag) == 7:
        this_fragment_info = CodeFragmentInfo(frag[1], available_variables,
                                              needful_variables, frag[4], 
                                              frag[5], frag[6])
    elif len(frag) == 6:
        this_fragment_info = CodeFragmentInfo(frag[1], available_variables,
                                              needful_variables, frag[4], 
                                              "", frag[5])
    combined_fragment, combined_import = fragment.generate_a_code_frag(this_fragment_info)
    if combined_fragment is None:
        return
    # 获取拼接时附带的自定义函数
    defined_callables = ""
    for item in fragment.self_defined_callables:
        if isinstance(item, str):
            if item not in defined_callables:
                defined_callables += item
        else:
            if item.content not in defined_callables:
                defined_callables += item.content
    # print("===defined_callables:\n"+defined_callables+"\n")
    # ==处理正确语句==
    # 添加布尔表达式中量子比特（数组）的释放语句
    correct_fragment = correct_stmt+combined_fragment+partial_reset_stmt
    correct_import = combined_import
    # 组装测试用例
    correct_testcase = generate.assemble_testcase(correct_fragment, correct_import, [defined_callables])
    # 存入数据库
    correct_testcase, count = array_process(correct_testcase, 0)
    # print("===correct_testcase:\n",correct_testcase)
    targetDB.insertToCorpus(["fragment_id", "Content"], [frag[0], correct_testcase])
    testcase_num += 1
    # ==处理错误语句==
    # 如果correct_stmt和wrong_stmt相等，不再组装wrong_stmt
    if wrong_stmt is None or wrong_stmt == correct_stmt:
        return
    # 否则，开始组装
    wrong_fragment = wrong_stmt+combined_fragment+partial_reset_stmt
    wrong_import = combined_import
    wrong_testcase = generate.assemble_testcase(wrong_fragment, wrong_import, [defined_callables])
    wrong_testcase, count = array_process(wrong_testcase, 0)
    # print("===wrong_testcase:\n"+wrong_testcase)
    targetDB.insertToCorpus(["fragment_id", "Content"], [frag[0], wrong_testcase])
    testcase_num += 1
    # print("correct testcase:\n"+correct_testcase+"\nwrong testcase:\n"+wrong_testcase)

def main():
    global testcase_num

    # 初始化结果表
    targetDB = DataBaseHandle(params["result_db"])
    targetDB.createTable("corpus")
    # 加载代码片段表，获取所有代码片段
    frag_db = DataBaseHandle(params["corpus_db"])
    frag_list = frag_db.selectAll("select * from CodeFragment")
    # 获取配置文件中的次数
    fragment_num = params["fragment_num"]
    if fragment_num < len(frag_list):
        frag_list = random.sample(frag_list, fragment_num)
    print(f"\033[94mTotally get {fragment_num} fragment. Start to generate testcase.\033[0m")
    for i, frag in enumerate(frag_list):
        print(f"--{i}--")
        complete_frag_by_cons(frag, targetDB)
    targetDB.finalize()
    print(f"\033[94mFinished. Totally get {testcase_num} test cases.\033[0m")


if __name__ in "__main__":
    main()
