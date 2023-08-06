class EnvironmentInfo():
    def __init__(self, jsonObj):
        self.__scriptsBasePath = jsonObj.get('scriptsBasePath')
        self.__storageBasePath = jsonObj.get('storageBasePath')
        self.__ocrEngine = jsonObj.get('ocrEngine')
        self.__testWizardVersion = jsonObj.get('testWizardVersion')
        
    @property
    def scriptsBasePath(self):
        return self.__scriptsBasePath
        
    @property
    def storageBasePath(self):
        return self.__storageBasePath
        
    @property
    def ocrEngine(self):
        return self.__ocrEngine
        
    @property
    def testWizardVersion(self):
        return self.__testWizardVersion
