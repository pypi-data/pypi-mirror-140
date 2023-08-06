class ManagerSessionInfo():
    def __init__(self, jsonObj):
        self.__id = jsonObj.get('id')
        self.__name = jsonObj['name']
        self.__scriptIndex = jsonObj.get('scriptIndex')
                
    @property
    def id(self):
        return self.__id
                
    @property
    def name(self):
        return self.__name
                
    @property
    def scriptIndex(self):
        return self.__scriptIndex
