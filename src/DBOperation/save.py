import os

from DBOperation.dboperation_sqlite import DataBaseHandle

def save_into_db(corpus_db: str, table_name: str, fragment_list: list):
    targetDB = DataBaseHandle(corpus_db)
    targetDB.createTable(table_name)
    if "CodeFragment" in table_name:
        for i, fragment in enumerate(fragment_list):
            targetDB.insertToCodeFragment(table_name, fragment)
    targetDB.finalize()
