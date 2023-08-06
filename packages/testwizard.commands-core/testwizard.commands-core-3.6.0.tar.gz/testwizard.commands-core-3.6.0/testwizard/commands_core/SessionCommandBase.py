class SessionCommandBase():
    def __init__(self, session, commandName):
        if session is None:
            raise Exception("session is required")
        if commandName is None:
            raise Exception("commandName is required")
            
        self.__session = session
        self.__commandName = commandName
        
    def executeCommand(self, requestObj, errorMessagePrefix):
        return self.__session.robot.executeCommand(self.__session.testRunId, " ", self.__commandName, requestObj, errorMessagePrefix)