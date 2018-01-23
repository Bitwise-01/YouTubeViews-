from os import path
from sys import exit
from time import sleep
from lib.spyder import IP
from random import randint
from subprocess import call
from platform import system
from lib.queue import Queue
from threading import Thread
from lib.browser import Browser
from argparse import ArgumentParser
from requests import get as urlopen

class Views(Browser):

 def __init__(self, urllist, visits, min, max):

  self.bots = 5 # max amount of bots to use
  self.count = 0 # returning bots
  self.ip = None
  self.alive = True
  self.targets = {} # {url: visits}
  self.ip_usage = 0
  self.ip_fails = 0
  self.max_fails = 3
  self.max_usage = 3
  self.proto = 'https'
  self.recentIPs = Queue(15)
  self.requesting_ip = False

  self.min = int(min)
  self.max = int(max)
  self.visits = int(visits)

  if not path.exists(urllist):
   exit('Error: Unable to locate `{}`'.format(urllist))

  # read the url list
  with open(urllist, 'r') as f:
   try:
    for url in [_ for _ in f.read().split('\n') if _]:
     self.targets[url] = 0 # initial view
   except Exception as err:exit('Error:', err)

 def display(self, url):
  n = '\033[0m'  # null ---> reset
  r = '\033[31m' # red
  g = '\033[32m' # green
  y = '\033[33m' # yellow
  b = '\033[34m' # blue

  call([cls])
  print ''
  print '  +------ Youtube Views ------+'
  print '  [-] Url: {}{}{}'.format(g, url, n)
  print '  [-] Proxy IP: {}{}{}'.format(b, self.ip['ip'], n)
  print '  [-] Visits: {}{}{}'.format(y, self.targets[url], n)
  if not self.alive:self.exit()

 def visit(self, url):
  try:
   if self.watch(url):
    views = self.targets[url]
    self.targets[url] = views + 1
  except:pass
  finally:
   try:
    sleep(1)
    self.count -= 1
   except:pass

 def connection(self):
  connected = False
  for _ in xrange(3):
   try:

    if not self.alive:self.exit()
    urlopen('https://example.com')
    connected = True
    break
   except:pass
  if not connected:
   print 'Error: No Connection!'
   self.exit()

 def change_ip(self, ip):
  if not ip:
   self.connection()
   return
  else:
   if not ip in self.recentIPs.queue:
    self.set_ip(ip)

 def updateIp(self):
  if not self.alive:return
  if self.requesting_ip:return
  self.requesting_ip = True
  self.change_ip(IP(self.proto).get_ip())
  self.requesting_ip = False

 def set_ip(self, ip):
  self.ip = ip
  self.ip_usage = 0
  self.ip_fails = 0
  self.recentIPs.put(ip)

 def exit(self):
  self.alive = False
  exit()

 def run(self):
  ndex = 0
  while all([self.alive, len(self.targets)]):
   try:
    urls = [] # tmp list of the urls that are being visited
    if any([not self.ip, self.ip_fails >= self.max_fails, self.ip_usage >= self.max_usage]):
     self.updateIp()
     if not self.ip:
      call([cls])
      print 'Working on obtaining a clean IP ...'
     sleep(5)
     continue
   except KeyboardInterrupt:self.exit()

   for _ in range(self.bots):
    try:
     url = [_ for _ in self.targets][ndex]
    except IndexError:return
    except KeyboardInterrupt:self.exit()

    view = self.targets[url]
    if view >= self.visits:
     del self.targets[url]
     continue

    # if url in urls:continue # prevent wrapping
    # if not self.ip:continue
    # if self.ip_fails >= self.max_fails:continue
    if any([url in urls, not self.ip, self.ip_fails >= self.max_fails]):continue
    ndex = ndex+1 if ndex < len(self.targets)-1 else 0
    Thread(target=self.visit, args=[url]).start()

    urls.append(url)
    self.count += 1
    self.ip_usage += 1
    try:sleep(1)
    except:self.exit()

   while all([self.count, self.alive]):
    for url in urls:
     try:
      self.display(url)
      if not self.alive:self.exit()
      if self.ip_fails >= self.max_fails:
       self.count = 0
      [sleep(1) for _ in range(7) if all([self.count, self.alive])]
     except KeyboardInterrupt:self.exit()
     except:pass
   else:pass
    # if self.ip_usage >= self.max_usage:
     # self.ip = None


if __name__ == '__main__':

 # arguments
 args = ArgumentParser()
 args.add_argument('visits',help='The amount of visits ex: 300')
 args.add_argument('urllist',help='Youtube videos url list')
 args.add_argument('min',help='Minimum watch time in seconds ex: 38')
 args.add_argument('max',help='Maximum watch time in seconds ex: 65')
 args = args.parse_args()

 cls = 'cls' if system() == 'Windows' else 'clear'
 youtube_views = Views(args.urllist, args.visits, args.min, args.max)
 youtube_views.run()
