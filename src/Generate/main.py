import ast
import random

from basic_operation.file_operation import initParams
from basic_operation.dict_operation import get_rest_args
from cons_generator.cwvp import generate_if_cons_exist
from class_for_info.fragment_info import CodeFragmentInfo
from combine_fragment import CodeFragmentGenerator, get_contained_cons
from generate import Generate
from DBOperation.dboperation_sqlite import DataBaseHandle
from grammar_pattern.array_process import array_process

params = initParams("../config.json")
testcase_num = 0

def complete_frag_by_cons(frag, targetDB):
    """ Generate test cases using specific fragment. """

    global testcase_num

    generate = Generate("../config.json")
    fragment = CodeFragmentGenerator(params["level"], params["ingredient_table_name"])
    available_variables = ast.literal_eval(frag[2])
    needful_variables = ast.literal_eval(frag[3])
    bool_expr_list, func_ret_list, quanternion_list, needful_args, partial_reset_stmt = \
        get_contained_cons(frag[1], needful_variables)
    if len(bool_expr_list) > 0 or len(func_ret_list) > 0:
        correct_stmt, wrong_stmt = \
            generate_if_cons_exist(bool_expr_list, func_ret_list, quanternion_list, needful_args)
    else:
        correct_stmt, wrong_stmt = "//no cons\n", "//no cons\n"
    if correct_stmt is None:
        return
    needful_variables = get_rest_args(needful_variables, needful_args)
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
    defined_callables = ""
    for item in fragment.self_defined_callables:
        if isinstance(item, str):
            if item not in defined_callables:
                defined_callables += item
        else:
            if item.content not in defined_callables:
                defined_callables += item.content
    correct_fragment = correct_stmt+combined_fragment+partial_reset_stmt
    correct_import = combined_import
    correct_testcase = generate.assemble_testcase(correct_fragment, correct_import, [defined_callables])
    correct_testcase, count = array_process(correct_testcase, 0)
    targetDB.insertToCorpus(["fragment_id", "Content"], [frag[0], correct_testcase])
    testcase_num += 1
    if wrong_stmt is None or wrong_stmt == correct_stmt:
        return
    wrong_fragment = wrong_stmt+combined_fragment+partial_reset_stmt
    wrong_import = combined_import
    wrong_testcase = generate.assemble_testcase(wrong_fragment, wrong_import, [defined_callables])
    wrong_testcase, count = array_process(wrong_testcase, 0)
    targetDB.insertToCorpus(["fragment_id", "Content"], [frag[0], wrong_testcase])
    testcase_num += 1

def main():
    global testcase_num

    targetDB = DataBaseHandle(params["result_db"])
    targetDB.createTable("corpus")
    frag_db = DataBaseHandle(params["corpus_db"])
    frag_list = frag_db.selectAll("select * from CodeFragment")
    fragment_num = params["fragment_num"]
    if fragment_num < len(frag_list):
        frag_list = random.sample(frag_list, fragment_num)
    print(f"\033[94mTotally get {fragment_num} fragment. Start to generate testcase.\033[0m")
    for i, frag in enumerate(frag_list):
        print(f"--{i}--")
        complete_frag_by_cons(frag, targetDB)
    targetDB.finalize()
    print(f"\033[94mFinished. Totally get {testcase_num} test cases.\033[0m")


if __name__ == "__main__":
    main()
