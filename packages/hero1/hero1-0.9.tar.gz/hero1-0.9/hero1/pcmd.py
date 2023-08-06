import hero1.hero1
from hero1.command_pb2 import CmdType, Cmd
import json
import time
#from ldproto import read_ld, write_ld
import struct


from hero1.bodyinfo_pb2 import *
s = None

def recv_ack():
  while True:
    c = CmdInfo()
    c.ParseFromString(s.recv(1024))
    if c.head == Head.ack:
        c = c.ack
        print(f'ACK:{c.code} {c.info}')
        return
    else:
        print('Unexpected:', c)

def send2(c):
  global s
  bs = c.SerializeToString()
  head_bytes = struct.pack('<L', Head.generic)  
  len_bytes = struct.pack('<L', len(bs))
  print(f'size:4 + {len(bs)}')
  s.sendall(head_bytes + len_bytes + bs)

def send_obj(c):
  global s
  bs = c.SerializeToString()
  head_bytes = struct.pack('<L', Head.bodyinfo)  
  len_bytes = struct.pack('<L', len(bs))
  #print(f'size:4 + {len(bs)}')
  s.sendall(head_bytes + len_bytes + bs)


def addS(cmd, s):
  c = Cmd()
  c.cmd = CmdType.INIT
  c.strings.append(cmd)
  c.strings.append(s)
  c.ints.append(0)
  c.ints.append(0)
  c.ints.append(0)
  c.ints.append(0)
  c.ints.append(0)  
  send2(c)

def init(s):
  addS('init', s)
  recv_ack()  

def addIa(cmd, i):
  c = Cmd()
  c.cmd = CmdType.INIT
  c.strings.append(cmd)
  c.strings.append('')
  c.ints.append(i)
  c.ints.append(0)
  c.ints.append(0)
  c.ints.append(0)
  c.ints.append(0)  
  send2(c)
  recv_ack()  

def addOC(o):
  global s
  c = Cmd()
  c.cmd = CmdType.INIT
  c.strings.append(o['name'])
  c.strings.append(o['type'])
  c.ints.append(round(o['id']))
  c.ints.append(round(o['x']))
  c.ints.append(round(o['y']))
  c.ints.append(round(o['width']))
  c.ints.append(round(o['height']))
  send2(c)

def getType(name):
  if name == 'dynamic':
    return BodyType.dynamic
  elif name == 'static':
    return BodyType.static
  else:
    return BodyType.kinematic

def add_body(o):
  match o['name']:
    case 'fruit'|'trampoline':
      bi = BodyInfo()
      bi.bid = o['id']
      bi.name = o['name']
      bi.shape = BodyShape.rectangle
      bi.x = o['x']
      bi.y = o['y']
      bi.width = o['width']
      bi.height = o['height']
      bi.restitution = 0
      bi.friction = 0
      bi.density = 1.0
      bi.isSensor = True if 'type' not in o else getType(o['type']) != BodyType.dynamic
      bi.categoryBits = 0x0001
      bi.maskBits = 0xFFFF
      bi.fixedRotation = True
      bi.type = BodyType.static if 'type' not in o else getType(o['type']) 
      bi.skin = o['skin']
      bi.trackable = True if 'trackable' not in o else o['trackable']
      send_obj(bi)
    case 'actor':
      bi = BodyInfo()
      bi.bid = o['id']
      bi.name = o['name']
      bi.shape = BodyShape.actor
      bi.x = o['x']
      bi.y = o['y']
      bi.width = o['width']
      bi.height = o['height']
      bi.restitution = 0
      bi.friction = 0
      bi.density = 1.0
      bi.isSensor = False
      bi.categoryBits = 0x1000
      bi.maskBits = 0x00FF
      bi.fixedRotation = True
      bi.type = BodyType.dynamic
      bi.skin = o['skin']
      bi.trackable = True if 'trackable' not in o else o['trackable']   
      send_obj(bi)      
      pass
    case 'void':
      bi = BodyInfo()
      bi.bid = o['id']
      bi.name = o['name']
      bi.shape = BodyShape.rectangle
      bi.x = o['x']
      bi.y = o['y']
      bi.width = o['width']
      bi.height = o['height']
      bi.restitution = 0
      bi.friction = 0.2
      bi.density = 0.0
      bi.isSensor = False
      bi.categoryBits = 0x0001
      bi.maskBits = 0xFFFF
      bi.fixedRotation = True
      bi.type = BodyType.static
      bi.skin = o['skin']
      bi.trackable = True if 'trackable' not in o else o['trackable']     
      send_obj(bi)
    case 'box':
      bi = BodyInfo()
      bi.bid = o['id']
      bi.name = o['name']
      bi.shape = BodyShape.rectangle
      bi.x = o['x']
      bi.y = o['y']
      bi.width = o['width']
      bi.height = o['height']
      bi.restitution = 0
      bi.friction = 0.0
      bi.density = 0.0
      bi.isSensor = False
      bi.categoryBits = 0x0001
      bi.maskBits = 0xFFFF
      bi.fixedRotation = True
      bi.type = BodyType.static
      bi.skin = o['skin']
      bi.trackable = True if 'trackable' not in o else o['trackable']    
      send_obj(bi)      
    case _:
      addOC(o)  

def set_bodyskin(bid, bskin, btype = BodySkinType.loop, bextra = BodySkinExtra.right):
  global s
  info = BodySkinInfo()
  info.bid = bid
  info.skin = bskin
  info.type = btype
  info.extra = bextra
  bs = info.SerializeToString()
  head_bytes = struct.pack('<L', Head.bodystatus)  
  len_bytes = struct.pack('<L', len(bs))
  print(f'size:4 + {len(bs)}')
  s.sendall(head_bytes + len_bytes + bs)

def set_bodyop(bid, op, x, y):
  global s
  info = BodyOpInfo()
  info.bid = bid
  info.op = op
  info.x = x
  info.y = y
  bs = info.SerializeToString()
  head_bytes = struct.pack('<L', Head.bodyop)  
  len_bytes = struct.pack('<L', len(bs))
  print(f'size:4 + {len(bs)}')
  s.sendall(head_bytes + len_bytes + bs)

def set_setting(info):
  global s
  bs = info.SerializeToString()
  head_bytes = struct.pack('<L', Head.setting)  
  len_bytes = struct.pack('<L', len(bs))
  print(f'size:4 + {len(bs)}')
  s.sendall(head_bytes + len_bytes + bs)  

def set_init(info):
  global s
  bs = info.SerializeToString()
  head_bytes = struct.pack('<L', Head.init)  
  len_bytes = struct.pack('<L', len(bs))
  print(f'size:8 + {len(bs)}')
  s.sendall(head_bytes + len_bytes + bs)  
  recv_ack()

def set_query(info):
  global s
  bs = info.SerializeToString()
  head_bytes = struct.pack('<L', Head.query)  
  len_bytes = struct.pack('<L', len(bs))
  print(f'size:8 + {len(bs)}')
  s.sendall(head_bytes + len_bytes + bs)  


def addOa(o):
  addO(o)
  recv_ack()

def recv_cmd():
  c = CmdInfo()
  c.ParseFromString(s.recv(1024))
  return c


def cmdS(cmd, s):
  c = Cmd()
  c.cmd = CmdType.COMMAND2
  c.strings.append(cmd)
  c.strings.append(s)
  send2(c)

def cmdSa(cmd, s):
  cmdS(cmd, s)
  recv_ack()  

def cmdF2(cmd, x, y):
  c = Cmd()
  c.cmd = CmdType.COMMAND2
  c.strings.append(cmd)
  c.floats.append(x)
  c.floats.append(y)
  send2(c)

def cmdF2S(cmd, x, y, opt):
  c = Cmd()
  c.cmd = CmdType.COMMAND2
  c.strings.append(cmd)
  c.strings.append(opt)
  c.floats.append(x)
  c.floats.append(y)
  send2(c)

def cmdI(cmd, v):
  c = Cmd()
  c.cmd = CmdType.COMMAND2
  c.strings.append(cmd)
  c.ints.append(v)
  send2(c)    

def cmdIF2(cmd, i, f1, f2):
  c = Cmd()
  c.cmd = CmdType.COMMAND2
  c.strings.append(cmd)
  c.ints.append(i)
  c.floats.append(f1)
  c.floats.append(f2)
  send2(c)    

def cmdOnly(cmd):
  c = Cmd()
  c.cmd = CmdType.COMMAND2
  c.strings.append(cmd)
  send2(c)    
