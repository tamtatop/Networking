import struct
import Parse

OFFSET_PREFIX = 0b11 << 14
COMPRESSION_POINTER_SIZE = 2
COMPRESSION_POINTER_PREFIX = 0b11

class Name:

	def __init__(self, name):
		self.name = name

	@classmethod
	def bytes_to_name(cls, packet, cur_position):
		name_end_byte = None
		name = b""
		while True:
			size = packet[cur_position]
			if size == 0:
				cur_position += 1
				break
			if Parse.get_bits(size, 6, COMPRESSION_POINTER_SIZE) == COMPRESSION_POINTER_PREFIX:
				if cls._has_not_jumped(name_end_byte):
					name_end_byte = cur_position + COMPRESSION_POINTER_SIZE
				offset = struct.unpack('!H', packet[cur_position : cur_position + COMPRESSION_POINTER_SIZE])[0] -  OFFSET_PREFIX
				cur_position = offset
			else:
				cur_position += 1
				name += packet[cur_position:cur_position+size] + b"."
				cur_position += size

		if cls._has_not_jumped(name_end_byte):
			name_end_byte = cur_position

		return cls(name), name_end_byte

	@classmethod
	def _has_not_jumped(cls, name_end_byte):
		return name_end_byte is None

	def name_to_bytes(self):
		ans = b''
		name_parts = self.name.split(b'.')[:-1]
		for part in name_parts:
			ans += struct.pack('!B', len(part))
			ans += part
		ans += struct.pack('!B', 0)
		return ans

	def __hash__(self):
		return hash(self.name)

	def __eq__(self, other):
		if isinstance(other, Name):
			return self.name == other.name
		return NotImplemented

	def __repr__(self):
		return f'''{self.name}'''




