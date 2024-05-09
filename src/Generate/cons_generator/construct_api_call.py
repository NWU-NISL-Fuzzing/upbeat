from DBOperation.save import save_into_db
from class_for_info.fragment_info import CodeFragmentInfo
from grammar_pattern.APIOperator import APIOperator


standard_api_list = APIOperator().get_func_and_op("/root/UPBEAT/src/ParseAPI/data/content.json")


def single_api_call():
    """ 生成单条API调用语句，没有变量赋值 """

    result_list = []
    # 遍历所有API
    for api_info in standard_api_list:
        # 获取API相关信息
        api_name = api_info.name
        api_namespace = api_info.namespace
        needfule_variables = api_info.get_api_args()
        # 筛选部分无法正确生成的API
        if "ApplyIf" in api_name or api_name in ["Default", "EmptyArray"]:
            continue
        # 构建open语句
        open_stmt = "open " + api_namespace + ";\n"
        # 开始构造调用语句
        if len(needfule_variables) > 0:
            call_stmt = "mutable APIResult = " + api_name + "("
            for var_name in needfule_variables.keys():
                call_stmt += var_name + ", "
            call_stmt = call_stmt[:-2] + ");\n"
        else:
            call_stmt = "mutable APIResult = " + api_name + "();"
        # 对结果进行输出
        if "Unit" in api_info.returnType:
            output_stmt = "DumpMachine();\n"
        else:
            output_stmt = "Message($\"{APIResult}\");\n"
        # 存储结果
        final_stmt = call_stmt + output_stmt
        code_fragment = CodeFragmentInfo(final_stmt, {}, needfule_variables, open_stmt,
                                    "", "").format_to_save()
        result_list.append(code_fragment)
    # 存入数据库
    save_into_db("/root/UPBEAT/data/query/corpus-v3.db", "CodeFragment_CS", result_list)


if __name__ == "__main__":
    single_api_call()
    # print(len(standard_api_list))
