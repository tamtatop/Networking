from Header import *
from Question import *
from ResourceRecord import *

class Packet:
	"""docstring for Packet"""

	def __init__(self, header, questions, answers, authority, additional_information):
		self.header = header
		self.questions = questions
		self.answers = answers
		self.authority = authority
		self.additional_information = additional_information
		
	@classmethod
	def bytes_to_packet(cls, byte_string):
		questions = []
		answers = []
		authority = []
		additional_information = []
		header = Header.bytes_to_header(byte_string)
		cur_position = header.HEADER_SIZE_IN_BYTES

		cur_position = cls._group_questions(questions, byte_string, header.qdcount, cur_position)

		cur_position = cls._group_resource_records(answers, byte_string, header.ancount, cur_position)
		cur_position =  cls._group_resource_records(authority, byte_string, header.nscount, cur_position)
		cur_position =  cls._group_resource_records(additional_information, byte_string, header.arcount, cur_position)		
		

		return cls(header, questions, answers, authority, additional_information)

	@classmethod
	def _group_questions(cls, questions_group, byte_string, question_number, cur_position):
		for question in range(question_number):
			question, cur_position = Question.bytes_to_question(byte_string, question_number, cur_position)
			questions_group.append(question)
		return cur_position

	@classmethod
	def _group_resource_records(cls, rrs_group, byte_string, rr_number, cur_position):
		for resource_record in range(rr_number):
			resource_record, cur_position = ResourceRecord.bytes_to_resource_record(byte_string, rr_number, cur_position)
			if resource_record.rdata.rdata is not None:
				rrs_group.append(resource_record)
		return cur_position

	@classmethod
	def generate_response_packet(cls, request_packet):
		pass

	def packet_to_bytes(self):
		ans = b''
		ans += self.header.header_to_bytes(len(self.questions), len(self.answers), len(self.authority), len(self.additional_information))
		ans += self._question_group_to_bytes(self.questions)
		ans += self._rr_group_to_bytes(self.answers) + self._rr_group_to_bytes(self.authority) + self._rr_group_to_bytes(self.additional_information)
		return ans

	def _question_group_to_bytes(self, question_group):
		ans = b''
		for question in question_group:
			ans += question.question_to_bytes()
		return ans

	def _rr_group_to_bytes(self, rr_group):
		ans = b''
		for rr in rr_group:
			ans += rr.resource_record_to_bytes()
		return ans


	def __repr__(self):
		return f'''

HEADER: {self.header}
QUESTIONS: {self.questions}
ANSWERS: {self.answers}
AUTHORITY: {self.authority}
ADDITIONAL INFORMATION: {self.additional_information}

'''









