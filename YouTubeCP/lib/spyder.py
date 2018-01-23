from requests import get as urlopen

class IP(object):
 ''' Provides clean IP addresses '''

 def __init__(self, proto):
  self.ip_url = 'https://gimmeproxy.com/api/getProxy?protocol=http'
  self.ip_check = 'https://ip-api.io/json/{}'
  self.proto = proto

 def format(self, data):
  if any([not data['websites']['amazon'], not data['supportsHttps']]):return
  return {'ip': data['ip'], 'ipPort': data['ipPort']}

 def fetch_ip(self):
  try:
   data = urlopen(self.ip_url).json()
   return self.format(data) if 'ipPort' in data else None
  except:pass

 def examine_ip(self, ip):
  try:
   stat = urlopen(self.ip_check.format(ip)).json()['suspicious_factors']
   return not all([stat['is_proxy'], stat['is_suspicious'], stat['is_tor_node'], stat['is_spam']])
  except:pass

 def get_ip(self):
  ip = self.fetch_ip()
  if not ip:return
  if self.examine_ip(ip['ip']):
   return ip
