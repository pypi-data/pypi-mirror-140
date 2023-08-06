import quickey_python_sdk
from quickey_python_sdk.config import missing_api_key_message
from quickey_python_sdk.auth import Auth
from quickey_python_sdk.app import App

class QuickeySDK:
    def __init__(self, apiKey):
        self.app = App(apiKey)
        self.auth = Auth(apiKey)

class QuickeySDKError:
    def __init__(self):
        pass

    def setMissingAPiKeyError ():
        return missing_api_key_message
