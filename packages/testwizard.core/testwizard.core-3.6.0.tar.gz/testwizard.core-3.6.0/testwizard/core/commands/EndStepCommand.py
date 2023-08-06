import sys
import json

from testwizard.commands_core import SessionCommandBase
from .StepExecutionResult import StepExecutionResult
from .EndStepResult import EndStepResult

class EndStepCommand(SessionCommandBase):
    def __init__(self, session):
        SessionCommandBase.__init__(self, session, "EndStep")

    def execute(self, result, message):
        if result is None:
            raise Exception("result is required")

        requestObj = [result, message]

        result = self.executeCommand(requestObj, "Could not execute command")
        
        return EndStepResult(result, "EndStep was successful", "EndStep failed")        