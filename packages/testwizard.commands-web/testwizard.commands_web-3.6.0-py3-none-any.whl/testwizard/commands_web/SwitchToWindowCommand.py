import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkErrorCodeAndMessageResult import OkErrorCodeAndMessageResult


class SwitchToWindow(CommandBase):
    def __init__(self, testObject):
        CommandBase.__init__(self, testObject, "Selenium.SwitchToWindow")

    def execute(self, windowName):
        if windowName is None:
            raise Exception("window name is required")

        requestObj = [windowName]

        result = self.executeCommand(requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(result, "SwitchToWindow was successful", "SwitchToWindow failed")
