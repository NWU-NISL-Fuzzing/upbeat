# -*- coding: utf-8 -*-
"""
@Time ： 2021/6/26 11:17
@Auth ： Xing
@File ：Reconstructor.py
@IDE ：PyCharm
@Description：测试用例中可能包含不能出现在入口函数处的Qubit类型，此处进行代码重构

"""
import random
import re

# from Fuzzing.lib.Assignment import Assignment


class Reconstructor:

    def __init__(self, content):
        self.content = content

    # 解析测试用例的namespace
    def parseNameSpace(self):
        pattern = re.compile(r"namespace\s*([\w\\.]+)\s*{")
        nameSpaceName = pattern.search(self.content).group(1)
        index = self.content.find(nameSpaceName)
        while self.content[index] != "{":
            index += 1
        index += 1
        left_brace = 1
        right_brace = 0
        start_index = end_index = index
        while index < len(self.content):
            if self.content[index] == "{":
                left_brace += 1
            elif self.content[index] == "}":
                right_brace += 1
                if left_brace == right_brace:
                    end_index = index
                    break
            index += 1
        namespaceBody = self.content[start_index-1:end_index+1]
        return nameSpaceName, namespaceBody

    # 解析测试用例的library
    def parseLibraries(self, namespaceBody):
        pattern = re.compile(r"open\s*([\w\\.]+)(?: as \w+)?;")
        matchObj = pattern.findall(namespaceBody)
        return matchObj

    # 解析测试用例的operation和function
    def parseOperation(self, operationBody):
        pattern = re.compile(r"(operation|function)\s*(\w+(?:\<'T\>)?)\s*\((.*)\)\s*:(.*)?(?:\s)*{")
        searchObj = pattern.search(operationBody)
        callableType = searchObj.group(1)
        name = searchObj.group(2)
        args = searchObj.group(3)
        returnType = searchObj.group(4)
        index = searchObj.end()
        left_brace = 1
        right_brace = 0
        start_index = end_index = index
        while index < len(operationBody):
            if operationBody[index] == "{":
                left_brace += 1
            elif operationBody[index] == "}":
                right_brace += 1
                if left_brace == right_brace:
                    end_index = index
                    break
            index += 1
        operationBody = operationBody[start_index:end_index]
        return {"callableType": callableType, "name": name.strip(), "args": args.strip(), "returnType": returnType.strip(), "body": operationBody}

    def parseCallables(self, namespaceBody):
        results = []
        callables = re.split(r'operation|function', namespaceBody)
        stepwords = re.findall(r'operation|function', namespaceBody)
        callables.__delitem__(0)
        callableContents = [x + " " + y for x, y in zip(stepwords, callables)]
        for content in callableContents:
            results.append(self.parseOperation(content))
        return results

    def objToString(self, callable):
        callableType = callable["callableType"]
        name = callable["name"]
        args = callable["args"]
        returnType = callable["returnType"]
        body = callable["body"]
        return callableType + " " + name + " (" + args + ") : " + returnType + " { \n\t\t" + body.strip() + "\n\t}"

    # 解析测试用例operation的参数
    def parseArgs(self, args):
        args_list = args.split(',')
        args_dict = dict()
        for arg in args_list:
            if arg.strip() != "":
                # ToDO:可能会存在 “statePrep : ((Qubit, Int) => Unit)”这样的参数
                try:
                    arg_name, arg_type = arg.split(":")
                except:
                    continue
                args_dict[arg_name.strip()] = arg_type.strip()
        return args_dict

    # 重新拼接测试用例
    def conjunction(self, namespaceName, libraries, callables, mainBody):
        testcase = "namespace" + " " + namespaceName + " {\n"
        for library in libraries:
            testcase += "\topen " + library + ";\n"
        for callableContent in callables:
            testcase += "\n\n\t" + callableContent
        testcase += "\n\n\t@EntryPoint()\n"
        # 入口函数的返回值类型不能为unit is adj
        testcase += "\toperation main() : Unit {\n"
        testcase += mainBody
        testcase += "\t}\n"
        testcase += "}"
        return testcase

    def liveCodeInsert1(self, insertCode: str):
        # AFCB和ATCB变异算法的代码插入
        namespaceName, namespaceBody = self.parseNameSpace()
        callables = self.parseCallables(namespaceBody)
        operationInfo = None
        for callable in callables:
            if callable["name"] == "NISLOperation":
                operationInfo = callable
        operationBody = operationInfo["body"]
        # 在operation开头处插入
        pos = self.content.find(operationBody)
        lines = insertCode.split("\n")
        # 调整代码缩进
        lines = ["\t\t" + line for line in lines]
        insertCode = "\n".join(lines)
        mutationTestcase = self.content[0:pos] + "\n" + insertCode + "\n" + self.content[pos+1:len(self.content)]
        return mutationTestcase

    def liveCodeInsert2(self, insertCode: str):
        # ATG变异算法的代码插入
        namespaceName, namespaceBody = self.parseNameSpace()
        callables = self.parseCallables(namespaceBody)
        operationInfo = None
        for callable in callables:
            if callable["name"] == "NISLOperation":
                operationInfo = callable
        operationBody = operationInfo["body"]
        bodylines = operationBody.split("\n")
        # 解析测试用例函数体，获取第一行语句
        saveLine = -1
        for i in range(len(bodylines)):
            # if语句体中不能包含变量定义和return语句
            line = bodylines[i].strip()
            if line == "":
                continue

            canNotStart = ["if", "else", "{", "}", "let", "mutable", "for", "repeat", "use"]
            flag = True
            for keyWord in canNotStart:
                if line.startswith(keyWord):
                    flag = False
            if flag:
                saveLine = i
                break

        if saveLine == -1:
            return self.content

        chooseLineCode = bodylines[saveLine]
        insertLines = insertCode.split("\n")
        insertLines = ["\t\t" + insertLine for insertLine in insertLines]
        insertLines.insert(2, chooseLineCode)
        insertCode = "\n\t".join(insertLines)
        pos = self.content.find(chooseLineCode)
        rest = self.content[pos+len(chooseLineCode):len(self.content)]
        mutationTestcase = self.content[0:pos] + "\t" + insertCode + "\t" + rest
        return mutationTestcase

    def liveCodeInsert3(self, namespaceBody:str , insertStatements: list):
        # 解析main函数
        pattern = re.compile(r"operation main\(\).*?{")
        globalSearch = pattern.search(self.content)
        globalIndex = globalSearch.end()
        global_start = global_end = globalIndex

        searchObj = pattern.search(namespaceBody)
        index = searchObj.end()
        left_brace = 1
        right_brace = 0
        start_index = end_index = index
        while index < len(namespaceBody):
            if namespaceBody[index] == "{":
                left_brace += 1
            elif namespaceBody[index] == "}":
                right_brace += 1
                if left_brace == right_brace:
                    end_index = index
                    break
            index += 1
            global_end += 1
        mainBody = namespaceBody[start_index:end_index]
        # 最后一行是return语句
        mainContents = mainBody.split("\n")
        for statement in mainContents:
            if statement.strip() == "":
                mainContents.remove(statement)
        newContents = []

        # 在repeat函数体内的内容缩进三行
        threeTab = False
        for i in range(len(insertStatements)):
            statement = insertStatements[i]
            if "until" in statement:
                threeTab = False
            if threeTab:
                newContents.append("\t\t\t" + statement)
            else:
                newContents.append("\t\t" + statement)
            if "repeat" in statement:
                threeTab = True
        for i in range(len(mainContents)):
            newContents.append(mainContents[i])
        insertCode = '\n'.join(newContents)
        mutationTestcase = self.content[0:global_start] + "\n" + insertCode + "\n\t" + self.content[global_end:len(self.content)]
        return mutationTestcase

    def reconstruct(self):
        """
        重构测试用例，替换已废弃依赖库，添加main函数调用
        :return: 返回重构后的测试用例，以及参数信息
        """
        namespaceName, namespaceBody = self.parseNameSpace()
        libraries = self.parseLibraries(namespaceBody)
        callables = self.parseCallables(namespaceBody)
        mainBody = ""
        params = []
        callable_strs = []
        for callableObj in callables:
            if callableObj["name"] == "NISLOperation":
                operation = callableObj
                args = self.parseArgs(operation["args"])
                mainBody = ""
                # 重构依赖
                for library in libraries:
                    if library == "Microsoft.Quantum.Primitive":
                        libraries.remove(library)
                        libraries.append("Microsoft.Quantum.Intrinsic")
                    if not library.startswith("Microsoft"):
                        libraries.remove(library)

                # 50%的概率生成边界值
                for key, value in args.items():
                    choice = random.randint(0, 3)
                    if choice != 0 and value in ["Int", "BigInt", "Double"]:
                        args[key] = "Boundary" + value

                # 根据给定参数名称和类型，随机生成参数值和dotnet调用命令
                assign = Assignment(args)
                params = assign.generate_params()
                resetQubits = {"simple": [], "array": []}
                for param in params:
                    name = param[0]
                    type = param[1]
                    value = param[2]
                    # 如果参数是Qubit类型
                    if type.lower() == "qubit":
                        elems = value.find('[')
                        # Qubit[]数组
                        if elems != -1:
                            mainBody += "\t\tuse " + name + " = " + str(value) + ";\n"
                            resetQubits["array"].append(name)
                        else:
                            mainBody += "\t\tuse " + name + " = Qubit();\n"
                            resetQubits["simple"].append(name)
                    elif type.lower() == "string":
                        mainBody += "\t\tmutable " + name + " = " + '"' + str(value) + '"' + ";\n"
                    else:
                        mainBody += "\t\tmutable " + name + " = " + str(value) + ";\n"
                mainBody += "\t\tmutable result = " + operation["name"] + "("
                for key, value in args.items():
                    if key != "":
                        mainBody += key + ", "
                if bool(args):
                    mainBody = mainBody[0:-2]
                mainBody += ");\n"
                if resetQubits["simple"].__len__() != 0:
                    for qubit in resetQubits["simple"]:
                        mainBody += "\t\tReset(" + qubit + ");\n"
                if resetQubits["array"].__len__() != 0:
                    for qubit in resetQubits["array"]:
                        mainBody += "\t\tResetAll(" + qubit + ");\n"
                # 为了返回值类型为unit
                mainBody += "\t\tmutable end = 1;\n"
            callable_strs.append(self.objToString(callableObj))
        testcase = self.conjunction(namespaceName, libraries, callable_strs, mainBody)
        return testcase, params


if __name__ == '__main__':
    file_path = r"../../../data/test/Program.qs"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    rc = Reconstructor(content)
    print(rc.reconstruct()[0])