import struct
from Name import *
from Rdata import *

class ResourceRecord:

	def __init__(self, rr_name, rr_type, rr_class, ttl, rdlength, rdata):
		self.rr_name = rr_name
		self.rr_type = rr_type
		self.rr_class = rr_class
		self.ttl = ttl
		self.rdlength = rdlength
		self.rdata = rdata

	@classmethod
	def bytes_to_resource_record(cls, packet, rrs_num, start_byte):
		rr_name,  cur_position = Name.bytes_to_name(packet, start_byte)
		rr_type, cur_position = Parse.parse_n_bytes(packet, Parse.TWO_BYTES, cur_position)
		rr_class, cur_position = Parse.parse_n_bytes(packet, Parse.TWO_BYTES, cur_position)
		ttl, cur_position = Parse.parse_n_bytes(packet, Parse.FOUR_BYTES, cur_position)
		rdlength, cur_position = Parse.parse_n_bytes(packet, Parse.TWO_BYTES, cur_position)
		rdata = Rdata.bytes_to_rdata(packet, rr_type, cur_position)
		end_position = cur_position + rdlength
		return cls(rr_name, rr_type, rr_class, ttl, rdlength, rdata), end_position


	def resource_record_to_bytes(self):
		ans = b''
		ans += self.rr_name.name_to_bytes()
		rdata_bytes = self.rdata.rdata_to_bytes(self.rr_type)
		ans += struct.pack('!HHIH', self.rr_type, self.rr_class, self.ttl, len(rdata_bytes))
		ans += rdata_bytes
		return ans

	def __repr__(self):
		return f'''
	NAME: {self.rr_name}
	TYPE: {self.rr_type}
	CLASS: {self.rr_class}
	TTL: {self.ttl}
	RDLENGTH: {self.rdlength}
	RDATA: {self.rdata}
'''