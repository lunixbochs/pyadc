from ctypes import c_ubyte
alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'

def encode(string):
	src = [ord(c) for c in string]

	base32 = ''
	i = 0
	index = 0
	while i < len(src):
		if index > 3:
			word = src[i] & (255 >> index)
			index = (index + 5) % 8
			word <<= index
			if i + 1 < len(src):
				word |= src[i+1] >> (8 - index)
			
			i += 1
		else:
			word = (src[i] >> (8 - (index + 5))) & 31
			index = (index + 5) % 8
			if index == 0:
				i += 1
		
		assert word < 32
		base32 += alphabet[word]

	return base32

def decode(string):
	string = string.upper()
	src = [ord(c) for c in string]

	buflen = len(string)*2
	result = (c_ubyte * buflen)()

	i = 0
	index = 0
	offset = 0
	while i < len(src):
		ref = alphabet.find(string[i])
		
		if ref == -1: continue

		if index <= 3:
			index = (index + 5) % 8
			if index == 0:
				result[offset] |= ref
				offset += 1
				if offset == buflen:
					break
			else:
				result[offset] |= ref << (8 - index)
		else:
			index = (index + 5) % 8
			result[offset] |= (ref >> index)
			offset += 1
			if offset == buflen:
				break
			result[offset] |= ref << (8 - index)
		
		i += 1

	return ''.join(chr(c) for c in result).strip('\x00')