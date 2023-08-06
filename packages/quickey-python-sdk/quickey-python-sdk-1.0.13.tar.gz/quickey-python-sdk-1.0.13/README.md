# QuickeySDK - Python

A Login Management System for Application

## How to Use

```
from quickey_python_sdk import QuickeySDK

sdk = QuickeySDK('YOUR API KEY')
```

### Get App Metadata
```
data = sdk.app.getAppMetaData()
appId = data.json()['app']['_id']
```

### Send SMS OTP
```
input = {'phone':'YOUR PHONE NUMBER', 'provider':'YOUR PROVIDER'}
customerData = sdk.app.sendSMSOTP(**input)
```

### Get Access Token By Email
```
input = {'email':'YOUR USER EMAIL', 'provider':'YOUR PROVIDER'}
token = sdk.auth.getAccessTokenByEmail(**input)
```

### Get Access Token By Phone
```
input = {'phone':'YOUR PHONE NUMBER', 'provider':'YOUR PROVIDER', 'otpCode':'YOUR OTP CODE'}
token = sdk.auth.getAccessTokenByPhone(**input)
```

### Link Phone To Email
```
input = {'phone':'YOUR PHONE NUMBER', 'token':'YOUR ACCESS TOKEN LOGIN FROM EMAIL'}
customerdata = sdk.auth.linkPhoneToEmail(**input)
```