import base64
import json
import hashlib
import datetime
import random
import string
import os
from test_users import *
from robot.api.deco import keyword
import requests
import time
import datetime

def createNonceb64():
    nonce_size = 24;
    return base64.b64encode(str.encode(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(nonce_size))))
    #import uuid
    #return uuid.uuid4().hex + uuid.uuid1().hex
    #from: https://stackoverflow.com/a/40328464/3898873

def createPasswordToken(nonceb64, timestamp, password):
    m = hashlib.sha1()
    m.update(password)
    password_hash = m.digest()
    m = hashlib.sha1()
    m.update(base64.b64decode(nonceb64))
    m.update(timestamp)
    m.update(password_hash)
    return base64.b64encode(m.digest())
 
def create1AAuthHeaderValue(orga, officeId, userId, password):
    nonceb64 = createNonceb64()
    timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
    token = createPasswordToken(nonceb64, timestamp.encode('utf-8'), password.encode('utf-8'))
 
    jwt = { "userId": userId,
            "officeId": officeId,
            "timestamp": timestamp,
            "nonce": bytes.decode(nonceb64),
            "password": bytes.decode(token),
            "organization": orga }
    return base64.b64encode(str.encode(json.dumps(jwt)))

def get1AAuthToken(user=USER_ESKY):
    #credentials = getCredentials()[phase]
    username = user[OFFICE_KEY_USER]
    office = user[OFFICE_KEY_NAME]
    password = user[OFFICE_KEY_PWD]
    organization = user[OFFICE_KEY_ORGA]
    key = bytes.decode(create1AAuthHeaderValue(organization,office,username,password))
    print("1AAuth",key)
    return key

def getLssUrl(phase):
    prefix = phase.lower()
    if prefix == 'prd':
        prefix = 'www'
    return "https://{}.accounts.amadeus.com/LoginService/services/rs/auth2.0/signIn?service=PAYMENT&responseType=JSON".format(prefix)

def getCredentials():
    baseDir = os.path.dirname(os.path.abspath(__file__))
    credentials = os.path.join(baseDir,'credentials.json')
    with open(credentials,encoding='utf-8-sig') as json_file:
        json_data = json.load(json_file)
        return json_data

def get_POSTCheckoutform(jsonMessage, baseURL):
    
    # Build the tocken string for the header
    token = "1AAuth  " + get1AAuthToken()
    print("Token: ", token)

    # This is the data that will be sent
    print("JSON Message: ",  jsonMessage)
    
    # The full header
    headers = {
            "Content-Type": "application/json",
            "Authorization": token
        }
    print("Headers: ", headers)

    # Shoot the POST message
    response = requests.post(baseURL, data=json.dumps(jsonMessage), headers=headers, timeout=15 )
    print("Response: ", response.text)

    # Extract PPID from reply
    resp_dict = response.json()
    PPID = resp_dict["data"]["id"]
    print("ID: ",PPID)

    return resp_dict

def getBearerToken(phase,user=USER_ESKY):
    params = {
        "officeId": user[OFFICE_KEY_NAME],
        "userAlias": user[OFFICE_KEY_USER],
        "userId": user[OFFICE_KEY_USER],
        "email": "",
        "organization": user[OFFICE_KEY_ORGA],
        "password": user[OFFICE_KEY_PWD],
        "agentSign": user[OFFICE_KEY_SIGN],
        "authMode": "HOS",
        "language": "en_gb",
        "nonce": ""
    }
    url = getLssUrl(phase)
    auth_response = requests.post(url,json=params).json()
    token = auth_response.get('accessToken','')
    print("token:",token)

    return token

def build_authlocalStorage(phase,user=USER_ESKY):
    # Build a auth local storage to use to automatically login into XPP
    
    authToken = getBearerToken(phase,user)
    
    local_storage = {
	"access_token": "",
	"expires": 1637428939077,
	"data": {
		"at_hash": "",
		"sub": "",
		"clientId": "",
		"sign": "",
		"iss": "accounts.amadeus.com",
		"dutyCode": "GS",
		"lastSignInDate": "20211108113632",
		"office": "",
		"login": "",
		"env": "",
		"nonce": "",
		"authMode": "",
		"nbDaysBeforePwdExpiration": "37",
		"aud": "PAYMENT",
		"organization": "",
		"scope": "openid",
		"be_type": "LSS",
		"exp": 1636628939,
		"iat": 1636628939,
		"email": ""
	    },
	"viewMerchant": ""
    }

    local_storage["access_token"]= str(authToken)
    d = datetime.datetime.now() + datetime.timedelta(hours=6)    
    local_storage["data"]["exp"]= int(datetime.datetime.timestamp(d))
    local_storage["data"]["iat"]= int(datetime.datetime.timestamp(d))
    local_storage["data"]["lastSignInDate"]= int(datetime.datetime.timestamp(d))  
    local_storage["expires"]=int(datetime.datetime.timestamp(d)*1000)
    local_storage["data"]["sub"]= user[OFFICE_KEY_USER]
    local_storage["data"]["login"]= user[OFFICE_KEY_USER]
    local_storage["data"]["organization"]= user[OFFICE_KEY_ORGA]
    
    return str(local_storage)

def get_PaymentPageUrl(JSON_message, PNR_recloc, Base_url):

    # Update JSON with new PNR created
    PNR_recloc=PNR_recloc.rstrip('\n')
    PNR_recloc=PNR_recloc.strip()
    JSON_message_dict = json.loads(JSON_message)
    JSON_message_dict["data"]["salesSummary"]["reference"] = PNR_recloc
    resp_dict = get_POSTCheckoutform(JSON_message_dict, Base_url)

    # Extract PPID from reply
    targetUrl = resp_dict["data"]["targetUrl"]
    print("TargetUrl: ",targetUrl)

    return targetUrl

def get_PPID(jsonMessage, baseURL):
    JSON_message_dict = json.loads(jsonMessage)
    resp_dict = get_POSTCheckoutform(JSON_message_dict, baseURL)
    # Extract PPID from reply
    PPID = resp_dict["data"]["id"]
    print("ID: ",PPID)

    return PPID

if __name__ == "__main__":
    
    build_authlocalStorage("UAT",user=USER_ESKY)