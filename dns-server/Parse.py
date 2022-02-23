import struct

ONE_BYTE = 1
TWO_BYTES = 2
FOUR_BYTES = 4
EIGHT_BYTES = 8
SIXTEEN_BYTES = 16

def get_bits(byte, start, size):
	return (byte >> start) & ((1 << size) - 1)

def set_bits(bits, start):
	return (bits << start)

# returns parsed int and position after parsing
def parse_n_bytes(packet, n, cur_position):
	if n is ONE_BYTE:
		parser = '!B'
	elif n is TWO_BYTES:
		parser = '!H'
	elif n is FOUR_BYTES:
		parser = '!I'
	elif n is EIGHT_BYTES:
		parser = '!Q'

	parsed_int = struct.unpack(parser, packet[cur_position:cur_position+n])[0]
	position_after_parsing = cur_position + n
	return parsed_int, position_after_parsing