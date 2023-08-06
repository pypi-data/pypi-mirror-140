import json
import urllib

from .models.TestObjectInfo import TestObjectInfo
from .models.CustomProperties import CustomProperties

#Services commands
from testwizard.commands_services import SendNotificationCommand
#Video commands
from testwizard.commands_video import SetTextOnScreenDisplayCommand
from testwizard.commands_video import SetAttributeOnScreenDisplayCommand
from testwizard.commands_video import ClearOnScreenDisplayCommand

class TestObjectBase():
    def __init__(self, session, name, category):
        if session is None:
            raise Exception("Session is required")
        if name is None:
            raise Exception("Name is required")
        if category is None:
            raise Exception("Category is required")

        if session.robot is None:
            raise Exception("Robot is undefined for session")

        resources = session.metadata["resources"]
        for resource1 in resources:
            if resource1["name"] == name:
                resource = resource1
                break
            else:
                resource = None
        if resource is None:
            raise Exception("No resource found with name " + name)
        
        testobject = session.robot.getTestObject(resource["id"])
        self.info = TestObjectInfo(testobject)
        self.customProperties = CustomProperties(resource.get("customProperties", {}))

        self.session = session
        self.name = name

        self.__isDisposed = False
        

    def executeCommand(self, commandName, requestObj, errorMessagePrefix):
        return self.session.robot.executeCommand(self.session.testRunId, self.name, commandName, requestObj, errorMessagePrefix)

    def dispose(self):
        self.__isDisposed = True

    def throwIfDisposed(self):
        if self.__isDisposed is True:
            print("Cannot access a disposed object")
            raise Exception("Cannot access a disposed object.")

    def sendNotification(self, errorId, description, priority):
        self.throwIfDisposed()
        return SendNotificationCommand(self).execute(errorId, description, priority)
        
    def setAttributeOnScreenDisplay(self, attributeType, osdArea = None,  textColor = None, backgroundColor = None, duration = None):
        self.throwIfDisposed()
        return SetAttributeOnScreenDisplayCommand(self).execute(attributeType, osdArea,  textColor, backgroundColor, duration)
        
    def setTextOnScreenDisplay(self, osdText, osdArea = None,  textColor = None, backgroundColor = None, duration = None):
        self.throwIfDisposed()
        return SetTextOnScreenDisplayCommand(self).execute(osdText, osdArea,  textColor, backgroundColor, duration)
        
    def clearOnScreenDisplay(self, osdArea = None):
        self.throwIfDisposed()
        return ClearOnScreenDisplayCommand(self).execute(osdArea)