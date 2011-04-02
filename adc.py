import socket

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
	def __init__(self, host, port):
		self.conn = Connection(host, port)
		self.sid = None

	def run(self):
		self.conn.connect()
		self.conn.send('HSUP ADBASE ADTIGR ')
		while True:
			self.parse(self.conn.recv())
	
	def parse(self, msg):
		if not msg: return
		byte, msg = msg[0], msg[1:]
		if byte == 'I':
			self.handleInfo(msg)
		elif byte == 'F':
			self.handleFeature(msg)
		else:
			print 'unhandled message:'
			print '->', byte, '=>', msg
	
	def handleInfo(self, msg):
		print 'Info:', msg

	def handleFeature(self, msg):
		print 'Feature:', msg

	def handleClient(self, msg):
		print 'Client:', msg

if __name__ == '__main__':
	host = ''
	port = 0
	
	adc = Client(host, port)
	adc.run()