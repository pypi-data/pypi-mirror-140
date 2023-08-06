from .EnvironmentInfo import EnvironmentInfo
from .ManagerSessionInfo import ManagerSessionInfo

class SessionInfo():
    def __init__(self, jsonObj):
        self.__scriptFilePath = jsonObj.get('scriptFilePath')
        self.__scriptFileName = jsonObj.get('scriptFileName')
        self.__storagePath = jsonObj.get('storagePath')
        self.__tester = jsonObj.get('tester')
        
        self.__environment = EnvironmentInfo(jsonObj.get('environment', {}))
        
        managerSessionDict = jsonObj.get('session')
        if managerSessionDict is None:
            self.__session = None
        else:
            self.__session =  ManagerSessionInfo(managerSessionDict)

    @property
    def scriptFilePath(self):
        return self.__scriptFilePath

    @property
    def scriptFileName(self):
        return self.__scriptFileName

    @property
    def storagePath(self):
        return self.__storagePath

    @property
    def tester(self):
        return self.__tester

    @property
    def environment(self):
        return self.__environment

    @property
    def session(self):
        return self.__session
