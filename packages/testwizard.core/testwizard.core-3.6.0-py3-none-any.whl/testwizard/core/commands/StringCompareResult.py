import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class StringCompareResult(ResultBase):
    def __init__(self, result, successMessage, failMessage):
        ResultBase.__init__(self, True, successMessage, failMessage)

        if "distance" in result:
            self.distance = result["distance"]
            
        if self.success is True:
            return

        if "message" in result:
            self.message = result["message"]

        if "errorMessage" in result:
            self.message = result["errorMessage"]

        if "errorCode" in result:
            self.message = self.getMessageForErrorCode(self.message, result["errorCode"])