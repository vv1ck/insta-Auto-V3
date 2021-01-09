import requests
import json
import hashlib
import hmac
import urllib
import uuid
import time

#Headers
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class SentryBlockException(Exception):
  pass

class InstagramAPI:
    API_URL = 'https://i.instagram.com/api/v1/'
    DEVICE_SETTINGS = {'manufacturer': 'OnePlus',
                       'model': 'ONEPLUS A3015',
                       'android_version': 25,
                       'android_release': '8.0'}
    USER_AGENT = 'Instagram 85.0.0.21.100 Android ({android_version}/{android_release}; 380dpi; 1080x1920; {manufacturer}; {model}; OnePlus3T; qcom; en_US)'.format(**DEVICE_SETTINGS)
    IG_SIG_KEY = '19ce5f445dbfd9d29c59dc2a78c616a7fc090a8e018b9267bc4240a30244c53b'
    SIG_KEY_VERSION = '4'
    
    def __init__(self, username, password, debug=False, IGDataPath=None):
        m = hashlib.md5()
        m.update(username.encode('utf-8') + password.encode('utf-8'))
        self.device_id = self.generateDeviceId(m.hexdigest())
        self.setUser(username, password)
        self.isLoggedIn = False
        self.LastResponse = None
        self.s = requests.Session()

    def setUser(self, username, password):
        self.username = username
        self.password = password
        self.uuid = self.generateUUID(True)

    def get_id(self, username):
      global USERNAME_ID
      url = "https://www.instagram.com/web/search/topsearch/?context=blended&query="+username+"&rank_token=0.3953592318270893&count=1"
      response = requests.get(url)
      respJSON = response.json()
      try:
        USERNAME_ID = str( respJSON['users'][0].get("user").get("pk") )
      except:
        return "Unexpected error"
#joker
    def login(self, force=False):
        if (not self.isLoggedIn or force):
            if (self.SendRequest('si/fetch_headers/?challenge_type=signup&guid=' + self.generateUUID(False), None, True)):

                data = {'phone_id': self.generateUUID(True),
                        '_csrftoken': self.LastResponse.cookies['csrftoken'],
                        'username': self.username,
                        'guid': self.uuid,
                        'device_id': self.device_id,
                        'password': self.password,
                        'login_attempt_count': '0'}
                if (self.SendRequest('accounts/login/', self.generateSignature(json.dumps(data)), True)):

                    self.isLoggedIn = True
                    self.username_id = self.LastJson["logged_in_user"]["pk"]
                    self.rank_token = "%s_%s" % (self.username_id, self.uuid)
                    self.token = self.LastResponse.cookies["csrftoken"]
                    print("Login success!\n")
                    return True

    def logout(self):
        logout = self.SendRequest('accounts/logout/')
#vv1ck
    def finishTwoFactorAuth(self, verification_code, two_factor_identifier, force=False):
      if (not self.isLoggedIn or force):
        data = {'_csrftoken': self.LastResponse.cookies['csrftoken'],
                 'username': self.username,
                 'guid': self.uuid,
                 'device_id': self.device_id,
                 'verification_method': '1',
                 'verification_code': verification_code,
                 'two_factor_identifier': two_factor_identifier}
      if (self.SendRequest('accounts/two_factor_login/', self.generateSignature(json.dumps(data)), True)):
        self.isLoggedIn = True
        self.username_id = self.LastJson["logged_in_user"]["pk"]
        self.rank_token = "%s_%s" % (self.username_id, self.uuid)
        self.token = self.LastResponse.cookies["csrftoken"]
        print("Login success with two factor authentication!\n")
        return True
    #vv1ck
    def completeCheckpoint1(self, force=False):
      global USER_AGENT
      global USERNAME_ID
      print(USERNAME_ID)
      URLSEND = 'https://i.instagram.com/integrity/checkpoint/checkpoint_logged_out_main/'+USERNAME_ID+'/?next=instagram%3A%2F%2Fcheckpoint%2Fdismiss'
      
      headers = {
      'Origin': 'https://i.instagram.com',
      'Connection': 'keep-alive',
      'Proxy-Connection': 'keep-alive',
      'Accept-Language': 'en-en',
      'Referer': 'https://i.instagram.com/integrity/checkpoint/checkpoint_logged_out_main/'+USERNAME_ID+'/?next=instagram%3A%2F%2Fcheckpoint%2Fdismiss',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
      }
      payload = {
      '_csrftoken': self.LastResponse.cookies['csrftoken'],
      'email': 'Verify by email'}
      r = requests.post(URLSEND, headers=headers, data=payload)
      r.status_code

    def completeCheckpoint2(self, AUTHCODE, force=False):
      URLSEND = 'https://i.instagram.com/integrity/checkpoint/checkpoint_logged_out_main/'+USERNAME_ID+'/?next=instagram%3A%2F%2Fcheckpoint%2Fdismiss'
      headers2 = {
      'Origin': 'https://i.instagram.com',
      'Connection': 'keep-alive',
      'Proxy-Connection': 'keep-alive',
      'Accept-Language': 'en-en',
      'Referer': 'https://i.instagram.com/integrity/checkpoint/checkpoint_logged_out_main/'+USERNAME_ID+'/?next=instagram%3A%2F%2Fcheckpoint%2Fdismiss',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
      }
      payload2 = {
      'csrfmiddlewaretoken': self.LastResponse.cookies['csrftoken'],
      'response_code': AUTHCODE}
      r2 = requests.post(URLSEND, headers=headers2, data=payload2)      
      r2.status_code


    def getPendingFollowRequests(self):
        return self.SendRequest('friendships/pending?')

    def approve(self, userId):
        data = json.dumps({
        '_uuid'         : self.uuid,
        '_uid'          : self.username_id,
        'user_id'       : userId,
        '_csrftoken'    : self.token
        })
        return self.SendRequest('friendships/approve/'+ str(userId) + '/', self.generateSignature(data))

    def generateSignature(self, data, skip_quote=False):
        if not skip_quote:
            try:
                parsedData = urllib.parse.quote(data)
            except AttributeError:
                parsedData = urllib.quote(data)
        else:
            parsedData = data
        return 'ig_sig_key_version=' + self.SIG_KEY_VERSION + '&signed_body=' + hmac.new(self.IG_SIG_KEY.encode('utf-8'), data.encode('utf-8'), hashlib.sha256).hexdigest() + '.' + parsedData

    def generateDeviceId(self, seed):
        volatile_seed = "12345"
        m = hashlib.md5()
        m.update(seed.encode('utf-8') + volatile_seed.encode('utf-8'))
        return 'android-' + m.hexdigest()[:16]

    def generateUUID(self, type):
        generated_uuid = str(uuid.uuid4())
        if (type):
            return generated_uuid
        else:
            return generated_uuid.replace('-', '')

    def SendRequest(self, endpoint, post=None, login=False):
        verify = False  # don't show request warning

        if (not self.isLoggedIn and not login):
            raise Exception("Not logged in!\n")

        self.s.headers.update({'Connection': 'close',
                               'Accept': '*/*',
                               'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                               'Cookie2': '$Version=1',
                               'Accept-Language': 'en-US',
                               'User-Agent': self.USER_AGENT})

        while True:
            try:
                if (post is not None):
                    response = self.s.post(self.API_URL + endpoint, data=post, verify=verify)
                else:
                    response = self.s.get(self.API_URL + endpoint, verify=verify)
                break
            except Exception as e:
                print('Except on SendRequest (wait 60 sec and resend): ' + str(e))
                time.sleep(60)

        if response.status_code == 200:
            self.LastResponse = response
            self.LastJson = json.loads(response.text)
            return True
        else:
            print("Request return " + str(response.status_code) + " error!")
            # joker
            try:
                self.LastResponse = response
                self.LastJson = json.loads(response.text)
                print(self.LastJson)
                if 'error_type' in self.LastJson and self.LastJson['error_type'] == 'sentry_block':
                    raise SentryBlockException(self.LastJson['message'])
            except SentryBlockException:
                raise
            except:
                pass
            return False
