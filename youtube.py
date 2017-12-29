from os import path
from sys import exit
from time import sleep
from core.tor import Tor
from random import randint
from subprocess import call
from core.queue import Queue
from threading import Thread
from core.browser import Browser
from argparse import ArgumentParser
from commands import getoutput as shell

class Views(Browser, Tor):

 def __init__(self, urllist, visits, min, max):

  self.bots = 5 # max amount of bots to use
  self.count = 0 # returning bots
  self.ip = None
  self.alive = True
  self.targets = {} # {url: visits}
  self.recentIPs = Queue(10)

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

  call('clear')
  print ''
  print '  +------ Youtube Views ------+'
  print '  [-] Url: {}{}{}'.format(g, url, n)
  print '  [-] Proxy IP: {}{}{}'.format(b, self.ip, n)
  print '  [-] Visits: {}{}{}'.format(y, self.targets[url], n)

 def visit(self, url):
  try:
   if self.watch(url):
    views = self.targets[url]
    self.targets[url] = views + 1
  except:pass
  finally:self.count -= 1

 def connection(self):
  try:
   br = self.createBrowser()
   br.open('https://example.com', timeout=2.5)
   br.close()
  except:
   print 'Error: Unable to access the internet'
   self.exit()

 def exit(self):
  self.alive = False
  self.stopTor()

 def run(self):
  ndex = 0
  while all([self.alive, len(self.targets)]):
   urls = [] # tmp list of the urls that are being visited
   self.restartTor()
   if not self.ip:continue

   for _ in range(self.bots):
    try:
     url = [_ for _ in self.targets][ndex]
    except IndexError:return
    view = self.targets[url]
    if view >= self.visits:
     del self.targets[url]
     continue

    if url in urls:continue # prevent wrapping
    ndex = ndex+1 if ndex < len(self.targets)-1 else 0
    Thread(target=self.visit, args=[url]).start()
    urls.append(url)
    self.count += 1
    sleep(1)

   while all([self.count, self.alive]):
    for url in urls:
     try:
      self.display(url)
      [sleep(1) for _ in range(7) if all([self.count, self.alive])]
     except:
      self.exit()

if __name__ == '__main__':

 # arguments
 args = ArgumentParser()
 args.add_argument('visits',help='The amount of visits ex: 300')
 args.add_argument('urllist',help='Youtube videos url list')
 args.add_argument('min',help='Minimum watch time in seconds ex: 38')
 args.add_argument('max',help='Maximum watch time in seconds ex: 65')
 args = args.parse_args()

 youtube_views = Views(args.urllist, args.visits, args.min, args.max)

 # does tor exists?
 if not path.exists('/usr/sbin/tor'):
  try:youtube_views.installTor()
  except KeyboardInterrupt:exit('Exiting ...')
  if all([not path.exists('/usr/sbin/tor'), youtube_views.alive]):
   exit('Please Install Tor')

 try:youtube_views.run()
 except Exception as error:
  print 'Error:',error
  youtube_views.exit()
