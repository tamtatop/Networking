from Name import *
import Parse
import ipaddress

A_TYPE = 1
NS_TYPE = 2
CNAME_TYPE = 5
SOA_TYPE = 6
MX_TYPE = 15
TXT_TYPE = 16
AAAA_TYPE = 28

class Rdata:

	def __init__(self, rdata):
		self.rdata = rdata

	@classmethod
	def bytes_to_rdata(cls, packet, rdata_type, start_byte):
		rdata = None
		if rdata_type is A_TYPE:
			rdata = cls._parse_A(packet, start_byte)
		elif rdata_type is NS_TYPE:
			rdata = cls._parse_NS_or_CNAME(packet, start_byte)
		elif rdata_type is CNAME_TYPE:
			rdata = cls._parse_NS_or_CNAME(packet, start_byte)
		elif rdata_type is SOA_TYPE:
			rdata = cls._parse_SOA(packet, start_byte)
		elif rdata_type is MX_TYPE:
			rdata = cls._parse_MX(packet, start_byte)
		elif rdata_type is TXT_TYPE:
			rdata = cls._parse_TXT(packet, start_byte)
		elif rdata_type is AAAA_TYPE:
			rdata = cls._parse_AAAA(packet, start_byte)

		return cls(rdata)

	@classmethod
	def _parse_A(cls, packet, start_byte):
		address = packet[start_byte : start_byte + Parse.FOUR_BYTES]
		ip_address = ipaddress.IPv4Address(address)
		return ip_address

	@classmethod
	def _parse_AAAA(cls, packet, start_byte):
		address = packet[start_byte : start_byte + Parse.SIXTEEN_BYTES]
		ip_address = ipaddress.IPv6Address(address)
		return ip_address

	@classmethod
	def _parse_NS_or_CNAME(cls, packet, start_byte):
		return Name.bytes_to_name(packet, start_byte)[0]

	@classmethod
	def _parse_SOA(cls, packet, start_byte):
		m_name, cur_position = Name.bytes_to_name(packet, start_byte)
		r_name, cur_position = Name.bytes_to_name(packet, cur_position)
		serial, cur_position = Parse.parse_n_bytes(packet, Parse.FOUR_BYTES, cur_position)
		refresh, cur_position = Parse.parse_n_bytes(packet, Parse.FOUR_BYTES, cur_position)
		retry, cur_position = Parse.parse_n_bytes(packet, Parse.FOUR_BYTES, cur_position)
		expire, cur_position = Parse.parse_n_bytes(packet, Parse.FOUR_BYTES, cur_position)
		minimum, end_position = Parse.parse_n_bytes(packet, Parse.FOUR_BYTES, cur_position)
		return m_name, r_name, serial, refresh, retry, expire, minimum

	@classmethod
	def _parse_MX(cls, packet, start_byte):
		preference, cur_position = Parse.parse_n_bytes(packet, Parse.TWO_BYTES, start_byte)
		exchange, _ = Name.bytes_to_name(packet, cur_position)
		return preference, exchange 

	@classmethod
	def _parse_TXT(cls, packet, start_byte):
		size, cur_position = Parse.parse_n_bytes(packet, Parse.ONE_BYTE, start_byte)
		text = packet[cur_position:cur_position+size]
		return text

	def rdata_to_bytes(self, rdata_type):
		ans = b''
		if rdata_type is A_TYPE:
			ans = self._pack_A_or_AAAA()
		elif rdata_type is NS_TYPE:
			ans = self._pack_NS_or_CNAME()
		elif rdata_type is CNAME_TYPE:
			ans = self._pack_NS_or_CNAME()
		elif rdata_type is SOA_TYPE:
			ans = self._pack_SOA()
		elif rdata_type is MX_TYPE:
			ans = self._pack_MX()
		elif rdata_type is TXT_TYPE:
			ans = self._pack_TXT()
		elif rdata_type is AAAA_TYPE:
			ans = self._pack_A_or_AAAA()
		return ans

	def _pack_A_or_AAAA(self):
		return self.rdata.packed

	def _pack_NS_or_CNAME(self):
		return self.rdata.name_to_bytes()

	def _pack_SOA(self):
		ans = b''
		m_name, r_name, serial, refresh, retry, expire, minimum = self.rdata
		ans += m_name.name_to_bytes() + r_name.name_to_bytes()
		ans += struct.pack('!IIIII', serial, refresh, retry, expire, minimum)
		print("ans: ", ans)
		return ans

	def _pack_MX(self):
		ans = b''
		preference, exchange = self.rdata
		ans += struct.pack('!H', preference)
		ans += exchange.name_to_bytes()
		return ans

	def _pack_TXT(self):
		ans = b''
		ans += struct.pack('!B', len(self.rdata))
		ans += self.rdata
		return ans

	@classmethod
	def str_to_rdata(cls, input_val, rdata_type):
		rdata = None
		if rdata_type is A_TYPE:
			rdata = cls._A_str_to_rdata(input_val)
		elif rdata_type is NS_TYPE:
			rdata = cls._NS_or_CNAME_str_to_rdata(input_val)
		elif rdata_type is CNAME_TYPE:
			rdata = cls._NS_or_CNAME_str_to_rdata(input_val)
		elif rdata_type is SOA_TYPE:
			rdata = cls._SOA_str_to_rdata(input_val)
		elif rdata_type is MX_TYPE:
			rdata = cls._MX_str_to_rdata(input_val)
		elif rdata_type is TXT_TYPE:
			rdata = cls._TXT_str_to_rdata(input_val)
		elif rdata_type is AAAA_TYPE:
			rdata = cls._AAAA_str_to_rdata(input_val)

		return cls(rdata)
	
	@classmethod
	def _A_str_to_rdata(cls, input_val):
		return ipaddress.IPv4Address(input_val)

	@classmethod
	def _AAAA_str_to_rdata(cls, input_val):
		return ipaddress.IPv6Address(input_val)

	@classmethod
	def _NS_or_CNAME_str_to_rdata(cls, input_val):
		return Name(input_val.encode())

	@classmethod
	def _MX_str_to_rdata(cls, input_val):
		preference, exchange_name = input_val
		exchange = Name(exchange_name.encode())
		return int(preference), exchange

	@classmethod
	def _SOA_str_to_rdata(cls, input_val):
		inputs = input_val.split(' ')
		return Name(inputs[0].encode()), Name(inputs[1].encode()), int(inputs[2]), int(inputs[3]), int(inputs[4]), int(inputs[5]), int(inputs[6])

	@classmethod
	def _TXT_str_to_rdata(cls, input_val):
		return input_val.encode()


	def __repr__(self):
		return f'''
		{self.rdata}
'''


