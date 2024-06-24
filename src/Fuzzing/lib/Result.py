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
