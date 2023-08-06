from testwizard.commands_core import CommandBase
from .OpenInNewWindowResult import OpenInNewWindowResult


class OpenInNewWindow(CommandBase):
    def __init__(self, testObject):
        CommandBase.__init__(self, testObject, "Selenium.OpenInNewWindow")

    def execute(self, selector):
        if selector is None:
            raise Exception("selector is required")

        requestObj = [selector]

        result = self.executeCommand(requestObj, "Could not execute command")

        return OpenInNewWindowResult(result, "OpenInNewWindow was successful", "OpenInNewWindow failed")
