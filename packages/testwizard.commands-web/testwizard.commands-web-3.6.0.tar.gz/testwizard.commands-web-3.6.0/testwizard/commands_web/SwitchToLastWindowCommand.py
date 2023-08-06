from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkErrorCodeAndMessageResult import OkErrorCodeAndMessageResult


class SwitchToLastWindowCommand(CommandBase):
    def __init__(self, testObject):
        CommandBase.__init__(self, testObject, "Selenium.SwitchToLastWindow")

    def execute(self):
        requestObj = []

        result = self.executeCommand(requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(result, "SwitchToLastWindow was successful", "SwitchToLastWindow failed")
