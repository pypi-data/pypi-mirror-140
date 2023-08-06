import sys
import json
from testwizard.commands_core import SessionCommandBase
from testwizard.commands_core import OkErrorCodeAndMessageResult

class AddPerformanceDataCommand(SessionCommandBase):
    def __init__(self, session):
        SessionCommandBase.__init__(self, session, "AddPerformanceData")

    def execute(self, dataSetName, key, value, description):
        if dataSetName is None:
            raise Exception("dataSetName is required")
        if key is None:
            raise Exception("key is required")
        if value is None:
            raise Exception("value is required")

        requestObj = [dataSetName, key, value, description]

        result = self.executeCommand(requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(result, "AddPerformanceData was successful", "AddPerformanceData failed")                