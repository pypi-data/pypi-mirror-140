import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class EndStepResult(ResultBase):
    def __init__(self, result , successMessage, failMessage):
        ResultBase.__init__(self, result["ok"] is True, successMessage, failMessage)

        self.stepName = result["stepName"]

        if self.success is True:
            return

        if "message" in result:
            self.message = result["message"]

        if "errorMessage" in result:
            self.message = result["errorMessage"]

        if "errorCode" in result:
            self.message = self.getMessageForErrorCode(self.message, result["errorCode"])