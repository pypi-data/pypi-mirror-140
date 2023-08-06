from quickey_python_sdk.config import base_url
import requests

class App():
    def __init__(self, apiKey):
        self.__apiKey = apiKey
        pass
    
    def getAppMetaData(self):
        payload = {'apiKey':self.__apiKey}
        return requests.post('{0}/auth/apiKey'.format(base_url), data=payload)

    def sendOTP(self, phone, provider):
        headers = {'authorization':self.__apiKey}
        payload = {'phone':phone, 'provider':provider}
        return requests.post('{0}/otp/sendToUserPhone'.format(base_url), data=payload, headers=headers)
