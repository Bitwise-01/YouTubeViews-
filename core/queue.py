
class Queue(object):

 def __init__(self, size):
  self.queue = []
  self.max_size = size

 def put(self, item):
  if len(self.queue) == self.max_size:
   self.queue.pop(0)
  else:
   self.queue.append(item)
