# coding=utf-8

from DBOperation.dboperation_sqlite import DataBaseHandle
from combine_fragment import CodeFragmentGenerator
from basic_operation.file_operation import initParams, delete_existing


class Generate:
    def __init__(self, config_path):
        self.params = initParams(config_path)
    
    def generate_main_content(self, n=-1):
        # NOTE.这里没有使用配置文件中的表
        fragment = CodeFragmentGenerator(self.params["level"], "CodeFragment")
        one_fragment_info = fragment.select_corpus(n)
        this_stmt, this_namespace = fragment.generate_a_code_frag(one_fragment_info)
        this_def_callables = list(set(fragment.self_defined_callables))
        fragment.self_defined_callables.clear()
        return this_stmt, this_namespace, this_def_callables

    def assemble_testcase(self, this_stmt: str, this_namespace:str, this_def_callables:str):
        namespaces = ["Microsoft.Quantum.Intrinsic", "Microsoft.Quantum.Convert", "Microsoft.Quantum.Math",
                      "Microsoft.Quantum.Diagnostics", "Microsoft.Quantum.Logical", "Microsoft.Quantum.Arithmetic",
                      "Microsoft.Quantum.Canon", "Microsoft.Quantum.Oracles", "Microsoft.Quantum.Arrays"]
        statements = []
        if not this_stmt:
            return None
        statements.append(this_stmt)
        # print("检查需要引入的命名空间："+this_namespace)
        for one_namespace in this_namespace.split('\n'):
            if one_namespace not in namespaces and len(one_namespace) > 0:
                namespaces.append(one_namespace)
        namespaces = list(set(namespaces))
        self_defined_callables = list(set(this_def_callables))

        operationBody = ""
        for statement in statements:
            if statement.strip() != "":
                for line in statement.split("\n"):
                    operationBody += "        " + line + "\n"
        insertCallables = []
        for call in self_defined_callables:
            if isinstance(call, str):
                insertCallables.append(call)
            else:
                insertCallables.append(call.content)
        return self.combine(namespaces, operationBody, insertCallables)

    def combine(self, namespaces, body: str, self_defined_callables: list):
        namespace_str = ""
        for namespace in namespaces:
            if namespace in namespace_str or namespace == "Microsoft.Quantum.Simulation.QuantumProcessor.Extensions":
                continue
            # print("namespace:"+namespace)
            if 'open' not in namespace:
                namespace_str += "    open " + namespace + ";\n"
            else:
                namespace_str += "    " + namespace + "\n"

        self_defined_callables_str = ""
        for call in self_defined_callables:
            lines = call.split("\n")
            reformat = []
            for line in lines:
                reformat.append("    " + line)
            self_defined_callables_str += "\n" + "\n".join(reformat)

        testcase = "namespace NISLNameSpace {\n" + \
                   namespace_str + \
                   "\n" + self_defined_callables_str + "\n" + \
                   "    @EntryPoint()\n    operation main() : Unit {\n" + \
                   body + \
                   "    }" + \
                   "\n}"
        return testcase

    def construct_seed_pool(self):
        fail_count = 0
        targetDB = DataBaseHandle(self.params["result_db"])
        corpusDB = DataBaseHandle(self.params["corpus_db"])
        frag_num = corpusDB.selectAll("select count(id) from CodeFragment")[0][0]
        targetDB.createTable("corpus")
        count = min(self.params["testcaseCount"], frag_num)
        # 这里需要从1开始，表CodeFragment的索引是从1开始的
        # 如果要使用其他表，需要注意索引不是连续的
        for i in range(1, count):
            print(i)
            this_stmt, this_namespace, this_def_callables = self.generate_main_content(i)
            # ***仅拼接代码片段时使用下面语句
            # if this_stmt is None:
            #     continue
            # elif "//correct" in this_stmt or "//wrong" in this_stmt:
            #     continue
            # 组装成完整的测试用例
            testcase = self.assemble_testcase(this_stmt, this_namespace, this_def_callables)
            # print(testcase)
            if testcase is None:
                fail_count += 1
                # continue
                # TODO.为什么不是跳过？
                targetDB.insertToCorpus(["fragment_id", "Content"], [str(i+1), ""])
            else:
                targetDB.insertToCorpus(["fragment_id", "Content"], [str(i+1), testcase])
        targetDB.finalize()
        print("Finished!Fail num:" + str(fail_count))


if __name__ == '__main__':
    delete_existing("can_not_gen.txt")

    config_path = "../config.json"
    generate = Generate(config_path)
    generate.construct_seed_pool()
