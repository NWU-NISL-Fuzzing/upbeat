# -*- coding: utf-8 -*-
import random
import re

from grammar_pattern.selfDefinedCallable import Callable


class OperationLoad:
    def parseOperation(self, operationContent):
        pattern = re.compile(r"(operation|function)\s*(\w+)\s*\((.*)\)\s*:(.*)?(?:\s)*{")
        searchObj = pattern.search(operationContent)
        callableType = searchObj.group(1).strip()
        name = searchObj.group(2).strip()
        args = searchObj.group(3).strip()
        returnType = searchObj.group(4).strip()
        argTypes = []
        if not args.strip():
            argTypes = ["Unit"]
        else:
            argList = args.split(",")
            for argument in argList:
                argTypes.append(argument.split(":")[1].strip())

        return Callable(callableType, name.strip(), argTypes, returnType.strip(), operationContent.strip())

    def loadFile(self, filePath):
        parsedOpration = []
        with open(filePath, "r", encoding="utf-8") as f:
            content = f.read()
            operations = content.split("========================================")
            for op in operations:
                if op.strip():
                    parsedOpration.append(self.parseOperation(op))
        return parsedOpration

    def classifyCallable(self, parsedOperations: list):
        operations = []
        functions = []
        for callable in parsedOperations:
            if callable.callableType == "function":
                functions.append(callable)
            elif callable.callableType == "operation":
                operations.append(callable)
        return functions, operations

    def loadCallables(self, file_path = r"../data/selfDefinedOperations.txt"):
        parsedOperations = self.loadFile(file_path)
        return self.classifyCallable(parsedOperations)

    # def randomChooseCallable(self, callables):
    #     callable = random.choice(callables)
    #     return callable
