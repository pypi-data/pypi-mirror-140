import sys
import json

from testwizard.commands_core import SessionCommandBase
from testwizard.commands_core import OkErrorCodeAndMessageResult

class BeginStepCommand(SessionCommandBase):
    def __init__(self, session):
        SessionCommandBase.__init__(self, session, "BeginStep")

    def execute(self, name):
        if name is None:
            raise Exception("name is required")

        requestObj = [name]

        result = self.executeCommand(requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(result, "BeginStep was successful", "BeginStep failed")        