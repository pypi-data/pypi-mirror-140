import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.OkErrorCodeAndMessageResult import OkErrorCodeAndMessageResult


class SwitchToFullScreenCommand(CommandBase):
    def __init__(self, testObject):
        CommandBase.__init__(self, testObject, "Selenium.SwitchToFullScreen")

    def execute(self, windowName):
        requestObj = []
        if windowName is not None:
            requestObj = [windowName]

        result = self.executeCommand(requestObj, "Could not execute command")

        return OkErrorCodeAndMessageResult(result, "SwitchToFullScreen was successful", "SwitchToFullScreen failed")
