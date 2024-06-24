# -*- coding: utf-8 -*-
import random
import re


class Reconstructor:

    def __init__(self, content):
        self.content = content

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

    def parseLibraries(self, namespaceBody):
        pattern = re.compile(r"open\s*([\w\\.]+)(?: as \w+)?;")
        matchObj = pattern.findall(namespaceBody)
        return matchObj

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

    def parseArgs(self, args):
        args_list = args.split(',')
        args_dict = dict()
        for arg in args_list:
            if arg.strip() != "":
                try:
                    arg_name, arg_type = arg.split(":")
                except:
                    continue
                args_dict[arg_name.strip()] = arg_type.strip()
        return args_dict

    # def conjunction(self, namespaceName, libraries, callables, mainBody):
    #     testcase = "namespace" + " " + namespaceName + " {\n"
    #     for library in libraries:
    #         testcase += "\topen " + library + ";\n"
    #     for callableContent in callables:
    #         testcase += "\n\n\t" + callableContent
    #     testcase += "\n\n\t@EntryPoint()\n"
    #     testcase += "\toperation main() : Unit {\n"
    #     testcase += mainBody
    #     testcase += "\t}\n"
    #     testcase += "}"
    #     return testcase

    def reconstruct(self):
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
                for library in libraries:
                    if library == "Microsoft.Quantum.Primitive":
                        libraries.remove(library)
                        libraries.append("Microsoft.Quantum.Intrinsic")
                    if not library.startswith("Microsoft"):
                        libraries.remove(library)

                for key, value in args.items():
                    choice = random.randint(0, 3)
                    if choice != 0 and value in ["Int", "BigInt", "Double"]:
                        args[key] = "Boundary" + value

                assign = Assignment(args)
                params = assign.generate_params()
                resetQubits = {"simple": [], "array": []}
                for param in params:
                    name = param[0]
                    type = param[1]
                    value = param[2]
                    if type.lower() == "qubit":
                        elems = value.find('[')
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
                mainBody += "\t\tmutable end = 1;\n"
            callable_strs.append(self.objToString(callableObj))
        testcase = self.conjunction(namespaceName, libraries, callable_strs, mainBody)
        return testcase, params
