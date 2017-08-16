# Date: 08/16/2017
# Distro: Kali Linux
# Author: Ethical-H4CK3R
# Description: YouTube Views Bot
#
#

import os
import time
import random
import urllib
import argparse
import threading
import subprocess
from platform import platform
from core.tor import TorManager
from core.browser import Browser

class Instagram(TorManager,Browser):
 def __init__(self,urllist,views,minWatch,maxWatch):
  self.url = None
  self.urls = []
  self.cache = {} # each url has its amount of visits {url:visits}
  self.views = views
  self.urllist = urllist
  self.lock = threading.Lock()
  self.minWatch = eval(minWatch)
  self.maxWatch = eval(maxWatch)

  self.ip = None # current ip address
  self.index = 0 # going through url list
  self.done = False # done with visits
  self.wait = False # wait for connection
  self.alive = True # is bruter still running
  self.counts = eval(self.views) # the max visits per link

  self.attemptlist = [] # temporary storage; holds a max of 5 passwords
  self.recentIps = [] # temporary storage; holds a max of 5 ip addresses

  Browser.__init__(self)
  TorManager.__init__(self)

  self.n = '\033[0m'  # null ---> reset
  self.r = '\033[31m' # red
  self.g = '\033[32m' # green
  self.y = '\033[33m' # yellow
  self.b = '\033[34m' # blue

 def kill(self):
  if not any([not self.done,self.alive]):return
  self.alive = False
  self.done = True
  print '\n  [-] Exiting {}...{}'.format(self.g,self.n)
  try:self.stopTor()
  finally:exit()

 def manageIps(self,rec=2):
  ip = self.getIp()
  if ip:
   if ip in self.recentIps:
    self.updateIp()
    self.manageIps()
   self.ip = ip
   self.recentIps.append(ip)
  else:
   if rec:
    self.updateIp()
    self.manageIps(rec-1)
   else:
    self.connectionHandler()

 def readUrls(self):
  with open(self.urllist,'r') as urlfile:
   for url in urlfile:
    url = url.replace('\n','')
    self.cache[url] = 0
   self.urls = [url for url in self.cache.keys()]

 def status(self):
  done = [visit >= self.counts for visit in self.cache.values()]
  self.done = True if all(done) else False
  if self.done:self.kill()

 def getUrl(self):
  self.status()
  self.urls = [url for url in self.urls if self.cache[url] < self.counts]
  self.index = self.index+1 if self.index < len(self.urls)-1 else 0
  if self.urls[self.index] == self.url:self.getUrl()
  return self.urls[self.index]

 def modifylist(self):
  if len(self.recentIps) == 256:
   del self.recentIps[0]

  if len(self.recentIps) > 256:
   while len(self.recentIps) > 255:
    del self.recentIps[0]

 def changeIp(self):
  self.createBrowser()
  self.updateIp()

  self.manageIps()
  self.modifylist()
  self.deleteBrowser()

 def setTries(self):
  self.status()
  self.url = self.getUrl()
  while all([not self.done,self.alive]):
   while all([self.alive,len(self.attemptlist)]):pass
   if not len(self.attemptlist):
    self.url = self.getUrl()
    self.attemptlist.append(1)

  # wait for left overs
  while self.alive:
   if not len(self.attemptlist):
    self.alive = False

 def connectionHandler(self):
  if self.wait:return
  self.wait = True
  print '\n  [-] Waiting For Connection {}...{}'.format(self.g,self.n)
  while all([self.alive,self.wait]):
   try:
    self.updateIp()
    urllib.urlopen('https://wtfismyip.com/text')
    self.wait = False
    break
   except IOError:
    time.sleep(1.5)
  self.manageIps()

 def attempt(self,attempt):
  with self.lock:
   self.status()
   self.createBrowser()
   html = self.watch()
   self.deleteBrowser()
   if html:
    self.cache[self.url]+=1
    del self.attemptlist[0]

 def run(self):
  self.readUrls()
  threading.Thread(target=self.setTries).start()
  self.display()
  time.sleep(1.3)
  while self.alive:
   bot = None # workers

   for attempt in self.attemptlist:
    bot = threading.Thread(target=self.attempt,args=[attempt])
    bot.start()
   self.status()

  # wait for bot
   if bot:
    while all([self.alive,bot.is_alive()]):pass
    if self.alive:
     self.changeIp()

 def display(self):
  ip = self.ip if self.ip else ''
  attempts = self.cache[self.url]+1 if self.url else ''

  subprocess.call(['clear'])
  print ''
  print '  +------ Youtube Views ------+'
  print '  [-] Url: {}{}{}'.format(self.g,self.url,self.n)
  print '  [-] Proxy IP: {}{}{}'.format(self.b,ip,self.n)
  print '  [-] Visits: {}{}{}'.format(self.y,attempts,self.n)

  if not ip:
   print '\n  [-] Obtaining Proxy IP {}...{}'.format(self.g,self.n)
   self.changeIp()
   time.sleep(1.3)
   self.display()

def main():
 # assign arugments
 args = argparse.ArgumentParser()
 args.add_argument('visits',help='The amount of visits')
 args.add_argument('urllist',help='Youtube videos url list')
 args.add_argument('min',help='Minimum watch time in seconds ex: 38')
 args.add_argument('max',help='Maximum watch time in seconds ex: 65')
 args = args.parse_args()

 # assign variables
 engine = Instagram(args.urllist,args.visits,args.min,args.max)

 # does tor exists?
 if not os.path.exists('/usr/sbin/tor'):
  try:engine.installTor()
  except KeyboardInterrupt:engine.kill('Exiting {}...{}'.format(self.g,self.n))
  if not os.path.exists('/usr/sbin/tor'):
   engine.kill('Please Install Tor'.format(engine.y,engine.r,engine.n))

 # start
 try:engine.run()
 finally:engine.kill()

if __name__ == '__main__':
 if not 'kali' in platform():
  exit('Kali Linux required')

 if os.getuid():
  exit('root access required')
 else:
  main()
