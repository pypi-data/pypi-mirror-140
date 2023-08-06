import sys
import json

from testwizard.commands_core import CommandBase
from .SaveFileResult import SaveFileResult


class SnapShotJPGCommand(CommandBase):
    def __init__(self, testObject):
        CommandBase.__init__(self, testObject, "SnapShotJPG")

    def execute(self, filename, quality):
        if filename is None:
            raise Exception("filename is required")

        requestObj = [filename]

        if quality is not None:
            requestObj = [filename, quality]

        result = self.executeCommand(requestObj, "Could not execute command")

        return SaveFileResult(result, "SnapShotJPG was successful", "SnapShotJPG failed")
