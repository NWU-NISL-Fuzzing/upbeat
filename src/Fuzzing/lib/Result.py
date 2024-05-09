# -*- coding: utf-8 -*-
import json, re


class Output:
    def __init__(self,
                 testcaseId: int,
                 testcaseContent: str,
                 command: str,
                 returncode: int,
                 stdout: str,
                 stderr: str,
                 duration_ms: int):
        self.testcaseId = testcaseId
        self.testcaseContent = testcaseContent
        self.command = command
        self.returnCode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.duration_ms = duration_ms
        self.outputClass = self.getOutputClass()

    def getOutputClass(self) -> str:
        """
        The order in which branches are judged cannot be reversed，
        because Whether the test case has a syntax error or not, chakraCore's returnCode is equal to 0
        """
        if self.returnCode == -9 and self.duration_ms > 60 * 1000:
            return "timeout"
        elif self.returnCode in [134, 137] or "Overflow" in self.stderr or "OutOfMemory" in self.stderr:
            return "crash"
        elif self.returnCode > 0 or not self.stderr == "":
            return "script_error"
        else:
            return "pass"

    def serialize(self):
        return {"id": self.testcaseId,
                "content": self.testcaseContent,
                "command": self.command,
                "returncode": self.returnCode,
                "stdout": self.stdout,
                "stderr": self.stderr,
                "duration_ms": self.duration_ms}

    def __str__(self):
        return json.dumps({"id": self.testcaseId,
                           "content": self.testcaseContent,
                           "command": self.command,
                           "returncode": self.returnCode,
                           "stdout": self.stdout,
                           "stderr": self.stderr,
                           "duration_ms": self.duration_ms},
                          indent=4)

#     def judge(self):
#         """
#         判断测试用例的类型: 
#         pass_score = -1, 表示无法正确判断此处是否存在一个正确或错误的边界条件;
#         pass_score = 0, 表示这里存在一个错误的边界条件, 如果正常通过测试, 则判断该测试用例可能存在bug;
#         pass_score = 1, 表示这里存在一个正确的边界条件, 如果未能正常通过, 则判断该测试用例可能存在bug;
#         """
#         pass_score = -1
#         result_type = self.getOutputClass()
#         reg_for_wrong = "[w|W]rong"
#         reg_for_right = "[r|R]ight"
#         if re.findall(reg_for_wrong, self.testcaseContent) and result_type == "pass":
#             pass_score = 0
#         elif re.findall(reg_for_right, self.testcaseContent) and not result_type == "pass":
#             pass_score = 1
        
#         return pass_score


# def differentialTest(before_mutation_output: Output, after_mutation_outputs: list):
#     if before_mutation_output is None:
#         return []
#     bugs_info = []
#     result_type = before_mutation_output.getOutputClass()
#     # 如果是timeout或crash，认为是可疑执行结果
#     if result_type == "timeout" or result_type == "crash":
#         bugs_info.append(before_mutation_output)
#     for output in after_mutation_outputs:
#         # Todo:需要完善可疑用例的判断条件
#         # 如果返回的returnCode值不同，认为是可疑执行结果
#         if output.returnCode != before_mutation_output.returnCode:
#             bugs_info.append(output)
#         # 当返回值类型相同，并且都为0，且输出结果不一致时，认为是可疑结果
#         elif output.returnCode == before_mutation_output.returnCode == 0:
#             if output.stdout.strip() != before_mutation_output.stdout.strip():
#                 bugs_info.append(output)
#     return bugs_info

# def JudgmentTest(before_mutation_output: Output, after_mutation_outputs: list):
#     if before_mutation_output is None:
#         return []
#     bugs_info = []
#     # 2023/01/03 运行时报错TypeError: unsupported operand type(s) for +: 'Output' and 'list'
#     all_output = [before_mutation_output] + after_mutation_outputs
#     for output in all_output:
#         # Todo: 判断测试用例类型, 如果pass_core = 0 or 1, 则说明此处存在bug
#         pass_score = output.judge()
#         if pass_score == 0 or pass_score == 1:
#             bugs_info.append(output)
#     return bugs_info
