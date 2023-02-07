import base64
import json
import hashlib
import datetime
import random
import string
import urllib
import urllib.request
import urllib.parse
import ssl
from http.cookiejar import CookieJar
 
def create_nonceb64():
    nonce_size = 24;
    return base64.b64encode(str.encode(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(nonce_size))))
 
def create_password_token(nonceb64, timestamp, password):
    m = hashlib.sha1()
    m.update(password)
    password_hash = m.digest()
    m = hashlib.sha1()
    m.update(base64.b64decode(nonceb64))
    m.update(timestamp)
    m.update(password_hash)
    return base64.b64encode(m.digest())
 
def create_1AAuth_header_value(orga, officeId, userId, password):
    nonceb64 = create_nonceb64()
    timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
    token = create_password_token(nonceb64, timestamp.encode('utf-8'), password.encode('utf-8'))
 
    jwt = { "userId": userId,
            "officeId": officeId,
            "timestamp": timestamp,
            "nonce": bytes.decode(nonceb64),
            "password": bytes.decode(token),
            "organization": orga }
    return base64.b64encode(str.encode(json.dumps(jwt)))
 
print("1AAuth "  + bytes.decode(create_1AAuth_header_value("1A", "NCE1A0955", "B2BW_USER2", "B2BW_USER2_21")))

def authenticate(user, pwd):
        """
        Authenticate to UPM+IC and retrieve a JWT
        :return:
        """
        IC_TOKEN_URL = "https://investigation.forge.amadeus.net/token"
        IC_LOGIN_URL = "https://investigation.forge.amadeus.net/login?next=%s" % urllib.parse.quote(IC_TOKEN_URL)
        request = urllib.request.Request(IC_LOGIN_URL)
        auth = (user, pwd)
        auth = ('%s:%s' % (auth[0], auth[1]))
        encoded_auth = base64.b64encode(auth.encode('ascii'))
        request.add_header("Authorization", "Basic %s" % encoded_auth.decode("ascii"))

        # Cookies are necessary for UPM+IC
        response = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(CookieJar()),
            urllib.request.HTTPSHandler(context=ssl._create_unverified_context())
        ).open(request)
        content = response.read()

        #if response.code != 200:
            #IC_LOGGER.error("Failed to connect to UPM/IC: [%s] %s" % (response.code, content))
            #raise Exception("Authentication failure on UPM/IC: %s (%s)" % (content, response.code))

        #try:
            #self.jwt = json.loads(content)
        #except Exception as _ex:
            #IC_LOGGER.error("Invalid JSON retrieved from IC: %s (%s)" % (content, _ex))
            #raise Exception("Invalid JSON retrieved from IC: %s" % content)
        jwt = json.loads(content)
        return jwt

def getattr(attr, response):
        """
        Custom getattr to retrieve attributes from self/JWT

        :param attr: attribute to retrieve
        :return:
        """
        # First, get it from the current instance
        if attr in response:
            return response[attr]

        # Second, try in JWT
        #if self.jwt is not None and attr in self.jwt:
            #return self.jwt[attr]

        # Finally, try for attributes within "claim"'s JWT attributes
        #if self.jwt is not None and "claims" in self.jwt and attr in self.jwt["claims"]:
            #return self.jwt["claims"][attr]

        #return None