import sys
import json
from testwizard.commands_core import SessionCommandBase
from .StringCompareResult import StringCompareResult

class StringCompareCommand(SessionCommandBase):
    def __init__(self, session):
        SessionCommandBase.__init__(self, session, "StringCompare")

    def execute(self, string1, string2):
        if string1 is None:
            raise Exception("string1 is required")
        if string2 is None:
            raise Exception("string2 is required")
        requestObj = [string1, string2]

        result = self.executeCommand(requestObj, "Could not execute command")

        return StringCompareResult(result, "StringCompare was successful", "StringCompare failed")