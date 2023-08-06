import sys
import json
from testwizard.commands_core import SessionCommandBase
from testwizard.commands_core import OkErrorCodeAndMessageResult

class AddCustomDataCommand(SessionCommandBase):
    def __init__(self, session):
        SessionCommandBase.__init__(self, session, "AddCustomData")

    def execute(self, key, value):
        if key is None:
            raise Exception("key is required")

        requestObj = [key, value]

        result = self.executeCommand(requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(result, "AddCustomData was successful", "AddCustomData failed")                