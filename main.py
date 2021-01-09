
import os

package = "halo"
package2 = "replit"

try:
    import package
except:
    os.system("pip install "+ package)

try:
    import package2
except:
    os.system("pip install "+ package2)


from multiprocessing import Process
import sys

from colorama import Fore
from InstagramAPI import InstagramAPI
from halo import Halo
import time
import json
from contextlib import contextmanager
from colorama import init
import replit
init(autoreset=True)
username = ''
password = ''
number = 0
spinner = Halo(text='\nFollowers accepted: ' + str(number), spinner='dots')



@contextmanager
def hide():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

def getPendingFollowRequests(self):
  return self.SendRequest('friendships/pending?')

def approve(self, userId):
  data = json.dumps({'_uuid':self.uuid, 
   '_uid':self.username_id, 
   'user_id':userId, 
   '_csrftoken':self.token})
  return self.SendRequest('friendships/approve/' + str(userId) + '/', self.generateSignature(data))

def getPendingInfo(insta):
  idsUser = []
  if getPendingFollowRequests(insta):
    info = insta.LastJson
    for i in info['users']:
      idsUser.append(i['pk'])
    return (idsUser)

def usernameInput():
  username = input("Username:\n")
  return username

def passwordInput():  
  password = input("Password:\n")
  return password


replit.clear()
print('Instagram follow request accepter, get in touch with me at @__clapped__ if you have any questions\n')
print('<<<THIS IS A ' + Fore.GREEN + 'FREE' + Fore.RESET + ' ACCEPTER, IF YOU WERE CHARGED FOR THIS YOU HAVE BEEN SCAMMED>>>')
username = usernameInput()
password = passwordInput()
insta = InstagramAPI(username, password)

while insta.isLoggedIn == False:
  global select
  with hide():
    insta.login()
  try:
    if insta.LastJson['two_factor_required']:
      print(Fore.RED + 'Instagram Login has failed')
      print(Fore.RED + 'Two factor authentication error!')
      authID = insta.LastJson['two_factor_info']['two_factor_identifier']
      authcode = input('Please input SMS code here: \n')
      insta.finishTwoFactorAuth(authcode, authID)
  except:
    pass
  try:
    while 'challenge_required' in insta.LastJson['message']:
      print(Fore.RED + 'Instagram Login has failed')
      print(Fore.RED + 'Challenge required error!')
      input('Please open the Instagram app and click "This was me" on the popup, This occurs because this program runs on servers based in Mountain View, California' + Fore.GREEN + '\nPress enter/return to continue after doing so')
      with hide():
        insta.login()
  except:
    pass
  if insta.isLoggedIn == False:
    print(Fore.RED + 'Instagram Login has failed.')
    username = usernameInput()
    password = passwordInput()
    insta = InstagramAPI(username, password)

replit.clear()

spinner.start()

while __name__ == '__main__':
  try:
    userid = getPendingInfo(insta)
  except:
    pass
  if userid:
    for app in userid:
      p = Process(target=approve, args=(insta, app))
      p.start()
      number+=1
      spinner.start('\rFollowers accepted: ' + str(number))