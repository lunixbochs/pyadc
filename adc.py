import socket
import base32
import uuid
from ConfigParser import SafeConfigParser

import tiger # http://github.com/lunixbochs/pytiger

def print_r(obj, tabs=0, newline=True):
	if type(obj) in (list, tuple, set, frozenset):
		for entry in obj:
			print_r(entry, tabs+1)
	
	elif type(obj) == dict:
		for entry in sorted(obj):
			print '%s%s:' % ('\t'*tabs, entry),
			print_r(obj[entry], tabs+1, False)
	else:
		print '%s%s' % (newline and '\t'*tabs or '', obj)

class Connection:
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.queue = []
		self.buffer = ''
	
	def connect(self):
		self.sock = s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((self.host, self.port))
	
	def send(self, msg):
		print '>> %s' % msg
		self.sock.send(msg+chr(0x0a))
	
	def recv(self):
		if not self.queue:
			while not '\n' in self.buffer:
				self.buffer += self.sock.recv(1024)
			
			messages, self.buffer = self.buffer.rsplit('\n', 1)
			self.queue = messages.split('\n')

		return self.queue.pop(0)

class File: # will hash a file and store full path and metadata
	pass

class Share: # will be responsible for keeping a list of Files
	pass

class Client:
	def __init__(self, configFile):
		self.config = config = SafeConfigParser()
		config.read(configFile)
		host = config.get('server', 'host')
		port = config.getint('server', 'port')

		pid = tiger.hash(uuid.uuid1().hex).replace('00', '01')
		self.pid = base32.encode(pid)
		self.cid = base32.encode(tiger.hash(pid))
		self.inf = {
			'ID': self.cid,
			'PD': self.pid,
			'SF': 0, # number of shared files
			'SS': 1, # size of shared files in bytes
			'NI': 'daemon', # nickname
			'VE': 'pyadc 0.1', # client version
			'US': 0, # maximum upload speed, bytes/second
			# 'DS': 0, # maximum download speed, bytes/second
			'FS': 0, # number of free upload slots
			'SL': 0, # maximum number of open slots
			'HN': 0, # number of hubs where user is normal
			'HR': 0, # number of hubs where user is registered and normal
			'HO': 0, # number of hubs where user is op and normal
			'SU': 'ADC0,TCP4', # list of capabilities
			'U4': 0, # udp ipv4 port
		}

		self.conn = Connection(host, port)
		self.clients = {}
		self.info = {}

		self.logged_in = False

	def run(self):
		self.conn.connect()
		self.conn.send('HSUP ADBASE ADTIGR ')
		while True:
			self.parse(self.conn.recv())
	
	def parse(self, msg):
		if not msg: return
		byte, msg = msg[0], msg[1:]

		args = None
		argc = 0
		if ' ' in msg:
			msg, args = msg.split(' ', 1)
			if ' ' in args:
				args = args.split(' ')
				argc = len(args)
			else:
				args = (args,)
				argc = 1

		if byte == 'B':
			self.handleBroadcast(msg, args, argc)
		elif byte == 'I':
			self.handleInfo(msg, args, argc)
		elif byte == 'F':
			self.handleFeature(msg, args, argc)
		else:
			print '<< unhandled message:'
			print '<<', (byte, msg, args)
	
	def sendInfo(self):
		inf = ' '.join('%s%s' % (field, str(self.inf[field]).replace(' ', '\s')) for field in self.inf)
		self.conn.send('BINF %s %s' % (self.sid, inf))
	
	def handleBroadcast(self, msg, args, argc):
		print '<< Broadcast:', msg, args
		if msg == 'INF' and argc >= 2:
			sid = args[0]
			if not sid in self.clients: self.clients[sid] = {}

			for arg in args[1:]:
				field, info = arg[:2], arg[2:]
				self.clients[sid][field] = info.replace('\s', ' ')
		
		print_r(self.clients)

	def handleInfo(self, msg, args, argc):
		print '<< Info:', msg, args
		if msg == 'SID' and argc >= 1:
			self.sid = args[0]
		elif msg == 'INF' and argc >= 1:
			for arg in args:
				field, info = arg[:2], arg[2:]
				self.info[field] = info.replace('\s', ' ')

			if self.logged_in == False:
				self.sendInfo()

	def handleFeature(self, msg, args, argc):
		print '<< Feature:', msg, args

	def handleClient(self, msg, args, argc):
		print '<< Client:', msg, args

if __name__ == '__main__':
	import sys, os

	config = None
	if len(sys.argv) >= 2:
		config = sys.argv[1]

	if not (config and os.path.isfile(config)):
		if os.path.isfile('adc.conf'):
			config = 'adc.conf'
		else:
			print './adc.conf does not exist and no other config specified'
			print 'Usage: %s [path/to/config]' % sys.argv[0]
			sys.exit(1)

	adc = Client(config)
	adc.run()
