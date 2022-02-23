import struct
import Parse

class Header:
	"""docstring for Header"""

	HEADER_SIZE_IN_BYTES = 12

	def __init__(self, packet_id, qr, opcode, aa, tc, rd ,ra, z, rcode, qdcount, ancount, nscount, arcount):
		self.packet_id = packet_id
		self.qr = qr
		self.opcode = opcode
		self.aa = aa
		self.tc = tc
		self.rd = rd
		self.ra = ra
		self.z = z
		self.rcode = rcode
		self.qdcount = qdcount
		self.ancount = ancount
		self.nscount = nscount
		self.arcount = arcount

	@classmethod
	def bytes_to_header(cls, packet):
		packet_id = struct.unpack('!H', packet[0:2])[0]
		qr = Parse.get_bits(packet[2], 7, 1)
		opcode = Parse.get_bits(packet[2], 3, 4)
		aa = Parse.get_bits(packet[2], 2, 1)
		tc = Parse.get_bits(packet[2], 1, 1)
		rd = Parse.get_bits(packet[2], 0, 1)

		ra = Parse.get_bits(packet[3], 7, 1)
		z = Parse.get_bits(packet[3], 4, 3)
		rcode = Parse.get_bits(packet[3], 0, 4)

		qdcount, ancount, nscount, arcount = struct.unpack('!HHHH', packet[4:12])
		return cls(packet_id, qr, opcode, aa, tc, rd ,ra, z, rcode, qdcount, ancount, nscount, arcount)

	def header_to_bytes(self, qdcount, ancount, nscount, arcount):
		ans = b''
		ans += struct.pack('!H', self.packet_id)

		flags_1 = Parse.set_bits(self.qr, 7) + Parse.set_bits(self.opcode, 3) + Parse.set_bits(self.aa, 2) + Parse.set_bits(self.tc, 1) + self.rd
		flags_2 = Parse.set_bits(self.ra, 7) + Parse.set_bits(self.z, 4) + Parse.set_bits(self.rcode, 0)

		ans += struct.pack('!BB', flags_1, flags_2) 
		ans += struct.pack('!HHHH', qdcount, ancount, nscount, arcount)
		return ans

	def __repr__(self):
		return f'''
ID: {self.packet_id}
QR: {self.qr}
OPCODE: {self.opcode}
AA: {self.aa}
TC: {self.tc}
RD: {self.rd}
RA: {self.ra}
Z: {self.z}
RCODE: {self.rcode}
QDCOUNT: {self.qdcount}
ANCOUNT: {self.ancount}
NSCOUNT: {self.nscount}
ARCOUNT: {self.arcount}
'''



