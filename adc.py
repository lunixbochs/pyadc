import socket
from ConfigParser import SafeConfigParser

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
		self.sock.send(msg+'\n')
	
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

		self.conn = Connection(host, port)
		self.info = {}

	def run(self):
		self.conn.connect()
		self.conn.send('HSUP ADBASE ADTIGR ')
		while True:
			self.parse(self.conn.recv())
	
	def parse(self, msg):
		if not msg: return
		byte, msg = msg[0], msg[1:]

		args = None
		if ' ' in msg:
			msg, args = msg.split(' ', 1)

		if byte == 'I':
			self.handleInfo(msg, args)
		elif byte == 'F':
			self.handleFeature(msg, args)
		else:
			print 'unhandled message:'
			print '->', byte, '=>', msg
	
	def handleInfo(self, msg, args=None):
		argv = args.split(' ')
		argc = len(argv)

		print 'Info:', msg, args
		if msg == 'SID' and argc >= 1:
			self.sid = argv[0]
		if msg == 'INF' and argc >= 1:
			for arg in argv:
				field, info = arg[:2], arg[2:]
				self.info[field] = info.replace('\\s', ' ')
			
			print self.info

	def handleFeature(self, msg, args=None):
		print 'Feature:', msg, args

	def handleClient(self, msg, args=None):
		print 'Client:', msg, args

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