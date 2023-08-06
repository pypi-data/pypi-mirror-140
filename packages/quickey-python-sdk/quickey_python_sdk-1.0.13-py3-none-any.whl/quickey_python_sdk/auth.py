from quickey_python_sdk.config import base_url
import requests

class Auth():
    def __init__(self, apiKey):
        self.__apiKey = apiKey
        pass
        
    def getAccessTokenByEmail(self, email, provider):
        headers = {'authorization':self.__apiKey}
        payload = {'email':email, 'provider':provider}
        return requests.post('{0}/loginCustomer'.format(base_url), data=payload, headers=headers)

    def getAccessTokenByPhone(self, phone, provider, otpCode):
        headers = {'authorization':self.__apiKey}
        payload = {'phone':phone, 'provider':provider, 'otpCode':otpCode}
        return requests.post('{0}/loginCustomer'.format(base_url), data=payload, headers=headers)

    def verifyToken(self, token):
        headers = {'authorization':self.__apiKey}
        payload = {'token':token}
        return requests.post('{0}/auth/verifyToken'.format(base_url), data=payload, headers=headers)

    def linkPhoneToEmail(self, phone, token):
        headers = {'authorization':self.__apiKey}
        payload = {'phone':phone, 'token':token}
        return requests.post('{0}/otp/linkToEmail'.format(base_url), data=payload, headers=headers)
