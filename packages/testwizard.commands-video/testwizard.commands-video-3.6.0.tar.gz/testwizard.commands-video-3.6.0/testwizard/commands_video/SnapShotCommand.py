import sys
import json

from testwizard.commands_core import CommandBase
from .SaveFileResult import SaveFileResult


class SnapShotCommand(CommandBase):
    def __init__(self, testObject):
        CommandBase.__init__(self, testObject, "SnapShot")

    def execute(self, filename, imageFormat, quality):
        if filename is None:
            raise Exception("filename is required")

        if imageFormat is None:
            raise Exception("imageFormat is required")

        requestObj = [filename, imageFormat]

        if quality is not None:
            requestObj = [filename, imageFormat, quality]

        result = self.executeCommand(requestObj, "Could not execute command")

        return SaveFileResult(result, "SnapShot was successful", "SnapShot failed")
