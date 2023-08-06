import sys
import json

from testwizard.commands_core import CommandBase
from testwizard.commands_core.SimpleResult import SimpleResult


class AddCapabilityCommand(CommandBase):
    def __init__(self, testObject):
        CommandBase.__init__(self, testObject, "Selenium.AddCapability")

    def execute(self, key, value):
        if key is None:
            raise Exception("key is required")
        if value is None:
            raise Exception("value is required")

        requestObj = [key, value]

        result = self.executeCommand(requestObj, "Could not execute command")

        return SimpleResult(result, "AddCapability was successful", "AddCapability failed")
