import struct
from Name import *
import Parse

class Question:
	
	def __init__(self, q_name, q_type, q_class):
		self.q_name = q_name
		self.q_type = q_type
		self.q_class = q_class

	@classmethod
	def bytes_to_question(cls, packet, questions_num, start_byte):
		q_name,  cur_position = Name.bytes_to_name(packet, start_byte)
		q_type, cur_position = Parse.parse_n_bytes(packet, Parse.TWO_BYTES, cur_position)
		q_class, end_position = Parse.parse_n_bytes(packet, Parse.TWO_BYTES, cur_position)
		return cls(q_name, q_type, q_class), end_position

	def question_to_bytes(self):
		ans = b''
		ans += self.q_name.name_to_bytes()
		ans += struct.pack('!HH', self.q_type, self.q_class)
		return ans

	def __key(self):
		return (self.q_name, self.q_type, self.q_class)

	def __hash__(self):
		return hash(self.__key())

	def __eq__(self, other):
		if isinstance(other, Question):
			return self.__key() == other.__key()
		return NotImplemented



	def __repr__(self):
		return f'''
	QNAME: {self.q_name}
	QTYPE: {self.q_type}
	QCLASS: {self.q_class}
'''








