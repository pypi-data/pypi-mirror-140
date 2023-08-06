from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkErrorCodeAndMessageResult import OkErrorCodeAndMessageResult


class SwitchToNewWindowCommand(CommandBase):
    def __init__(self, testObject):
        CommandBase.__init__(self, testObject, "Selenium.SwitchToNewWindow")

    def execute(self, windowName, url):
        if windowName is None:
            raise Exception("window name is required")

        requestObj = [windowName]
        if url is not None:
            requestObj = [windowName, url]
            
        result = self.executeCommand(requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(result, "SwitchToNewWindow was successful", "SwitchToNewWindow failed")
