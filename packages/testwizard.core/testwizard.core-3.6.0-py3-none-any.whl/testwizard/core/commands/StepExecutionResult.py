from enum import Enum

class StepExecutionResult(Enum):
    NotRun = "NotRun",
    Pass = "Pass",
    Fail = "Fail",
    Skip = "Skip"