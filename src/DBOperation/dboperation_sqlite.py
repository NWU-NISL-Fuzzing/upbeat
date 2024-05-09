# coding:utf-8
import sqlite3 as db


class DataBaseHandle:
    def __init__(self, dbPath: str):
        self.dbPath = dbPath
        self.connection = None
        self.tableName = None

    # clear database table
    def createTable(self, tableName: str):
        self.tableName = tableName
        if tableName == "corpus":
            self.sqlCreateTable = "drop table if exists corpus;" \
                                  "CREATE TABLE IF NOT EXISTS corpus(" \
                                  "Id INTEGER PRIMARY KEY AUTOINCREMENT," \
                                  "fragment_id INTEGER DEFAULT NULL," \
                                  "Content BLOB NOT NULL" \
                                  ");"
        elif tableName == "differentialResult_cw":
            self.sqlCreateTable = "drop table if exists differentialResult_cw;" \
                                  "CREATE TABLE IF NOT EXISTS differentialResult_cw(" \
                                  "Id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                                  "testcase_id INTEGER DEFAULT NULL," \
                                  "Content BLOB NOT NULL," \
                                  "Command BLOB NOT NULL," \
                                  "returncode INTEGER DEFAULT NULL," \
                                  "stdout BLOB DEFAULT NULL," \
                                  "stderr BLOB DEFAULT NULL," \
                                  "duration_ms INTEGER DEFAULT NULL);"
        elif tableName == "differentialResult_sim":
            self.sqlCreateTable = "drop table if exists differentialResult_sim;" \
                                  "CREATE TABLE IF NOT EXISTS differentialResult_sim(" \
                                  "Id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                                  "testcase_id INTEGER DEFAULT NULL," \
                                  "Content BLOB NOT NULL," \
                                  "Command BLOB NOT NULL," \
                                  "returncode INTEGER DEFAULT NULL," \
                                  "stdout BLOB DEFAULT NULL," \
                                  "stderr BLOB DEFAULT NULL," \
                                  "duration_ms INTEGER DEFAULT NULL);"
        elif tableName == "originResult_cw":
            self.sqlCreateTable = "drop table if exists originResult_cw;" \
                                  "CREATE TABLE IF NOT EXISTS originResult_cw(" \
                                  "Id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                                  "testcase_id INTEGER DEFAULT NULL," \
                                  "Content BLOB NOT NULL," \
                                  "Command BLOB NOT NULL," \
                                  "returncode INTEGER DEFAULT NULL," \
                                  "stdout BLOB DEFAULT NULL," \
                                  "stderr BLOB DEFAULT NULL," \
                                  "duration_ms INTEGER DEFAULT NULL);"
        elif tableName == "originResult_sim":
            self.sqlCreateTable = "drop table if exists originResult_sim;" \
                                  "CREATE TABLE IF NOT EXISTS originResult_sim(" \
                                  "Id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                                  "testcase_id INTEGER DEFAULT NULL," \
                                  "Content BLOB NOT NULL," \
                                  "Command BLOB NOT NULL," \
                                  "returncode INTEGER DEFAULT NULL," \
                                  "stdout BLOB DEFAULT NULL," \
                                  "stderr BLOB DEFAULT NULL," \
                                  "duration_ms INTEGER DEFAULT NULL);"
        elif tableName == "codeFragment" or tableName == "CodeFragment":
            self.sqlCreateTable = "drop table if exists CodeFragment;" \
                                  "CREATE TABLE IF NOT EXISTS CodeFragment  (" \
                                  "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                                  "Fragment_content longtext NULL," \
                                  "Available_variables longtext NULL," \
                                  "Needful_variables longtext NULL," \
                                  "Needful_imports longtext NULL," \
                                  "Defined_callables longtext NULL," \
                                  "Source_file longtext NULL);"
        elif tableName == "CodeFragment_CS":
            self.sqlCreateTable = "drop table if exists CodeFragment_CS;" \
                                  "CREATE TABLE IF NOT EXISTS CodeFragment_CS  (" \
                                  "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                                  "Fragment_content longtext NULL," \
                                  "Available_variables longtext NULL," \
                                  "Needful_variables longtext NULL," \
                                  "Needful_imports longtext NULL," \
                                  "Defined_callables longtext NULL," \
                                  "Source_file longtext NULL);"
        elif tableName == "CodeFragment_CW":
            self.sqlCreateTable = "CREATE TABLE IF NOT EXISTS CodeFragment_CW  (" \
                                  "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                                  "Fragment_content longtext NULL," \
                                  "Available_variables longtext NULL," \
                                  "Needful_variables longtext NULL," \
                                  "Needful_imports longtext NULL," \
                                  "Defined_callables longtext NULL," \
                                  "Source_file longtext NULL);"
        elif tableName == "ClConsStmt":
            self.sqlCreateTable =  "CREATE TABLE IF NOT EXISTS ClConsStmt  (" \
                                   "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                                   "func_name varchar(200) NOT NULL," \
                                   "fact_stmt varchar(200) NOT NULL," \
                                   "arg_dict varchar(200) NOT NULL," \
                                   "UNIQUE (func_name, fact_stmt));"
                                  
        elif tableName == "QtConsStmt":
            self.sqlCreateTable = "drop table if exists QtConsStmt;" \
                                  "CREATE TABLE QtConsStmt  (" \
                                  "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                                  "func_name varchar(200) NOT NULL," \
                                  "quaternion varchar(200) NOT NULL," \
                                  "arg_info varchar(200) NOT NULL,"\
                                  "UNIQUE (func_name, quaternion));"
        else:
            raise RuntimeError('Miss sql statement to create a table, please check your table name.')
        conn = self.getConnection()
        cursor = conn.cursor()
        cursor.executescript(self.sqlCreateTable)

    def getConnection(self):
        if self.connection is None:
            self.connection = db.connect(self.dbPath)
        return self.connection

    def execute(self, sql: str):
        """
        Execute the statement of sql to modify the database, and commint the operation to database.

        :arg
        sql: the sql statement want to execute.
        """
        conn = self.getConnection()
        cursor = conn.cursor()
        cursor.execute(sql)

    def tableExists(self, tableName):
        connection = self.getConnection()
        cursor = connection.cursor()
        sql = "SELECT * FROM sqlite_master WHERE type = 'table' AND name = '" + tableName + "'"
        cursor.execute(sql)
        result = cursor.fetchall()
        return not len(result) == 0

    def isEmpty(self):
        connection = self.getConnection()
        cursor = connection.cursor()
        sql = "SELECT count(*) FROM " + self.tableName
        cursor.execute(sql)
        result = cursor.fetchall()
        return result[0][0] == 0

    # def query(self, field="Content"):
    #     conn = self.getConnection()
    #     cursor = conn.cursor()
    #     sql = f"SELECT {field} FROM {self.tableName}"
    #     cursor.execute(sql)
    #     result = cursor.fetchall()
    #     return result

    # def queryAll(self, columns: list, tableName: str):
    #     conn = self.getConnection()
    #     cursor = conn.cursor()

    #     sql = "SELECT "
    #     if columns.__len__() > 0:
    #         sql += columns[0]
    #     for i in range(1, columns.__len__()):
    #         sql += ", "
    #         sql += columns[i]
    #     sql += " FROM " + tableName

    #     cursor.execute(sql)
    #     result = cursor.fetchall()
    #     return result

    # def queryId(self, id: int, tableName: str):
    #     conn = self.getConnection()
    #     cursor = conn.cursor()

    #     sql = f"SELECT * FROM {tableName} where id = {id}"

    #     cursor.execute(sql)
    #     result = cursor.fetchall()
    #     return result

    def selectAll(self, sql: str):
        conn = self.getConnection()
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    def insertToCorpus(self, columnNames: list, values: list):
        conn = self.getConnection()
        cursor = conn.cursor()
        sql = "INSERT INTO " + "corpus" + " ("
        paramList = ""
        if columnNames.__len__() > 0:
            sql += columnNames[0]
            paramList += "?"
        for i in range(1, columnNames.__len__()):
            sql += ","
            sql += columnNames[i]
            paramList += ",?"
        sql = sql + ") VALUES (" + paramList + ")"
        cursor.execute(sql, values)

    # def insertToMutation(self, columnNames: list, value: str):
    #     conn = self.getConnection()
    #     cursor = conn.cursor()
    #     sql = "INSERT INTO " + "mutation" + " ("
    #     paramList = ""
    #     if columnNames.__len__() > 0:
    #         sql += columnNames[0]
    #         paramList += "?"
    #     for i in range(1, columnNames.__len__()):
    #         sql += ","
    #         sql += columnNames[i]
    #         paramList += ",?"
    #     sql = sql + ") VALUES (" + paramList + ")"
    #     cursor.execute(sql, (value,))

    def insertToTotalResult(self, result, tableName="originResult"):
        conn = self.getConnection()
        cursor = conn.cursor()
        sql = f"INSERT OR ignore INTO " + tableName + \
              f"(testcase_id,Content,Command,returncode,stdout,stderr,duration_ms) " \
              f"VALUES(?,?,?,?,?,?,?)"
        cursor.execute(sql,
                       (result.testcaseId, result.testcaseContent, result.command, result.returnCode, result.stdout,
                        result.stderr, result.duration_ms))

    def insertToDifferentialResult(self, result, tableName="differentialResult"):
        conn = self.getConnection()
        cursor = conn.cursor()
        sql = f"INSERT OR ignore INTO " + tableName + \
              f"(testcase_id,Content,Command,returncode,stdout,stderr,duration_ms) " \
              f"VALUES(?,?,?,?,?,?,?)"
        cursor.execute(sql,
                       (result.testcaseId, result.testcaseContent, result.command, result.returnCode, result.stdout,
                        result.stderr, result.duration_ms))

    # def insertToJudgmentResult(self, result):
    #     conn = self.getConnection()
    #     cursor = conn.cursor()
    #     sql = f"INSERT OR ignore INTO " + "differentialResult" \
    #                                       f"(testcase_id,Content,Command,returncode,stdout,stderr,duration_ms) " \
    #                                       f"VALUES(?,?,?,?,?,?,?)"
    #     cursor.execute(sql,
    #                    (result.testcaseId, result.testcaseContent, result.command, result.returnCode, result.stdout,
    #                     result.stderr, result.duration_ms))

    def insertToCodeFragment(self, table_name, result):
        conn = self.getConnection()
        cursor = conn.cursor()
        sql = f"INSERT OR ignore INTO " + table_name + \
                                          f"(Fragment_content, Available_variables, Needful_variables, Needful_imports, Defined_callables, Source_file) " \
                                          f"VALUES(?,?,?,?,?,?)"
        # print(type(result[0]),type(result[1]), type(result[2]), type(result[3]), type(result[4]))
        cursor.execute(sql, (result[0], result[1], result[2], result[3], result[4], result[5]))

    def insertToClCons(self, boundary_info):
        conn = self.getConnection()
        cursor = conn.cursor()
        sql = f"INSERT OR ignore INTO " + "ClConsStmt" \
                                          f"(func_name, fact_stmt, arg_dict)" \
                                          f"VALUES(?,?,?)"
        # cursor.execute(sql,
        #                (boundary_info.api, boundary_info.boolStmt, str(boundary_info.args)))
        for fact_stmt in boundary_info.bool_expr_list:
            cursor.execute(sql, (boundary_info.api, fact_stmt, str(boundary_info.arg_dict)))
        for fact_stmt in boundary_info.func_ret_list:
            cursor.execute(sql, (boundary_info.api, fact_stmt, str(boundary_info.arg_dict)))

    def insertToQtCons(self, boundary_info):
        conn = self.getConnection()
        cursor = conn.cursor()
        sql = f"INSERT OR ignore INTO " + "QtConsStmt" \
                                          f"(func_name, quaternion, arg_info)" \
                                          f"VALUES(?,?,?)"
        # cursor.execute(sql,
        #                (boundary_info.api, boundary_info.boolStmt, str(boundary_info.args)))
        for fact_stmt in boundary_info.bool_expr_list:
            cursor.execute(sql, (boundary_info.api, fact_stmt, str(boundary_info.arg_dict)))
        for fact_stmt in boundary_info.func_ret_list:
            cursor.execute(sql, (boundary_info.api, fact_stmt, str(boundary_info.arg_dict)))

    def delete(self, sql):
        conn = self.getConnection()
        cursor = conn.cursor()
        cursor.execute(sql)

    def commit(self):
        self.connection.commit()

    def finalize(self):
        self.connection.commit()
        self.connection.close()


if __name__ == "__main__":
    handle = DataBaseHandle("../../data/result/code_fragment0406.db")
    black_list = ["JW", "Jordan", "OptimizedBEGeneratorSystem", "unitaryGenerator",
                  "statePrepOp", "InPlaceXorTestHelper", "selector", "''Add''",
                  "EvolutionGenerator", "BlockEncoding", "ContinuousOracle",
                  "decomposition", ")[]", "(Int,Int,(Int -> (''T => Unit is Adj + Ctl)))",
                  "(Int,(Int -> (''T => Unit is Adj + Ctl)))"]
    for black_word in black_list:
        handle.delete("delete from CodeFragment where Needful_variables LIKE '%" + black_word + "%'")
    handle.delete("delete from CodeFragment where Needful_variables LIKE '%->%' and Needful_variables LIKE '%=>%'")
    # handle.delete("delete from CodeFragment where Needful_variables LIKE '%(Pauli[],Qubit[]) => Result%'")
    handle.finalize()
    print("finish")
