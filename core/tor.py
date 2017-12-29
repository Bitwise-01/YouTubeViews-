import socket, socks
from time import sleep
from commands import getoutput as shell

class Tor(object):

 def __init__(self):
  super(Tor, self).__init__()

 def restartTor(self, num=3):
  shell('service tor restart')
  sleep(1.5)
  self.updateIp(num)

 def stopTor(self):
  shell('service tor stop')

 def installTor(self):
  self.connection()
  if not self.alive:return
  print 'Installing Tor ...'
  shell('echo "deb http://http.kali.org/kali kali-rolling main contrib non-free" > /etc/apt/sources.list \
         && apt-get update && apt-get install tor -y && apt autoremove -y')

 def getIp(self):
  try:
   ip = None
   br = self.createBrowser()
   ip = br.open('https://api.ipify.org/?format=text', timeout=1.5).read()
   br.close()
  except:pass
  finally:
   if not self.alive:self.exit()
   return ip

 def updateIp(self, recur=3):
  if not self.alive:self.exit()
  socks.socket.setdefaulttimeout(5)
  socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9050, True)
  socket.socket = socks.socksocket

  try:
   ip = self.getIp()
   if all([not ip, recur]):
    print 'Error: Network unreachable'
    reset_counts = 2
    for _ in range(30):
     if not self.alive:return
     ip = self.getIp()
     if ip:break
     else:
      if reset_counts:
       reset_counts -= 1
       shell('service network-manager restart')
      sleep(1)
    if not ip:self.restartTor(recur-1)
   if all([not ip, not recur]):self.connection()

   if ip in self.recentIPs.queue:self.restartTor()
   else:
    self.ip = ip
    self.recentIPs.put(ip)

  except:pass
