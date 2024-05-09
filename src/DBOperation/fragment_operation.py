from dboperation_sqlite import DataBaseHandle


def delete_failed():
    """ 根据运行结果，删除语法错误的代码片段 """

    result = DataBaseHandle("../../data/result/qfuzz-cw-20240110.db")
    fragment = DataBaseHandle("../../data/query/corpus-v3.db")
    failed_id_list = result.selectAll("select fragment_id from corpus where id in (select testcase_id from originResult_cw where stderr like '%build failed%')")
    print(len(failed_id_list))
    for failed_id in failed_id_list:
        fragment.delete("delete from CodeFragment_CW where id = ("+str(failed_id[0])+");")
    fragment.finalize()

def merge_fragment_tables():
    """ 将CodeFragment_CW和CodeFragment_CS合并为一张表 """

    corpus_db = "/root/QFuzz/data/query/corpus-v3.db"
    targetDB = DataBaseHandle(corpus_db)
    targetDB.createTable("CodeFragment")
    targetDB.execute("INSERT INTO CodeFragment (Fragment_content, Available_variables, Needful_variables, Needful_imports, Defined_callables, Source_file) SELECT Fragment_content, Available_variables, Needful_variables, Needful_imports, Defined_callables, Source_file FROM CodeFragment_CW")
    targetDB.execute("INSERT INTO CodeFragment (Fragment_content, Available_variables, Needful_variables, Needful_imports, Defined_callables, Source_file) SELECT Fragment_content, Available_variables, Needful_variables, Needful_imports, Defined_callables, Source_file FROM CodeFragment_CS")
    targetDB.finalize()

if __name__ == "__main__":
    # delete_failed()
    merge_fragment_tables()
