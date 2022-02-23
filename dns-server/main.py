import sys
from socket import *
from Packet import Packet
from easyzone import easyzone
from Rdata import *
import copy
from Question import *
import glob
from ResourceRecord import *

ROOT_SERVER_IPS = ['192.58.128.30', '192.228.79.201', '192.33.4.12', '199.7.91.13', '192.203.230.10', '192.5.5.241', '192.112.36.4', '128.63.2.53', '192.36.148.17', '192.58.128.30', '193.0.14.129', '199.7.83.42', '202.12.27.33']
DNS_PORT = 53

MAXIMUM_PACKET_SIZE = 2048

saved_responses = {}
zones = []

TYPES_TO_STR = {
	A_TYPE : 'A',
	NS_TYPE : 'NS',
	CNAME_TYPE : 'CNAME',
	SOA_TYPE : 'SOA',
	MX_TYPE : 'MX',
	TXT_TYPE : 'TXT',
	AAAA_TYPE : 'AAAA'
}

def run_dns_server(CONFIG, IP, PORT):

	save_zones()

	serverSocket = socket(AF_INET, SOCK_DGRAM)
	serverSocket.bind((IP, int(PORT)))
	
	cur_root = 0
	while True:
		request_bytes, client_address = serverSocket.recvfrom(MAXIMUM_PACKET_SIZE)
		request_packet = Packet.bytes_to_packet(request_bytes)

		local_response = local_query(request_packet)
		if local_response != None:
			serverSocket.sendto(local_response, client_address)
			continue

		recursive_answer = recursive_query(request_packet, ROOT_SERVER_IPS[cur_root], cur_root)
		while recursive_answer == None:
			cur_root +=1
			recursive_answer = recursive_query(request_packet, ROOT_SERVER_IPS[cur_root], cur_root)

		serverSocket.sendto(recursive_answer.packet_to_bytes(), client_address)

def save_zones():
	for file_path in glob.glob(CONFIG + "*.conf"):
		file_name = file_path[7:-5]
		z = easyzone.zone_from_file(file_name, file_path) 
		zones.append(z)

def local_query(request_packet):
	q_name = request_packet.questions[0].q_name.name.decode()
	q_type = TYPES_TO_STR[request_packet.questions[0].q_type]
	values = []
	for z in zones:
		if q_name in z.names:
			for value in z.names[q_name].records(q_type).items:
				values.append(value)
			ttl = z.names[q_name].ttl

	if len(values) == 0:
		return None
	response_packet = _make_response_packet(request_packet, values, ttl)
	return response_packet.packet_to_bytes()


def _make_response_packet(request_packet, values, ttl):
	q_name = request_packet.questions[0].q_name
	q_type = request_packet.questions[0].q_type
	q_class = request_packet.questions[0].q_class
	
	answers = []
	for value in values:
		rdata = Rdata.str_to_rdata(value, q_type)
		rr = ResourceRecord(q_name, q_type, q_class, int(ttl), 0, rdata)
		answers.append(rr)

	request_packet.header.qr = 1
	request_packet.header.ancount = len(answers)
	request_packet.answers = answers
	return request_packet



def recursive_query(request_packet, ip, cur_root):
	request_packet.header.rd = 1
	request_bytes = request_packet.packet_to_bytes()

	sock = socket(AF_INET, SOCK_DGRAM) 
	sock.sendto(request_bytes, (ip, DNS_PORT))
	sock.settimeout(0.5)
	
	try:
		dnsrespone, _ = sock.recvfrom(MAXIMUM_PACKET_SIZE)
	except:
		return None

	response_packet = Packet.bytes_to_packet(dnsrespone)

	if response_packet.header.rcode != 0:
		return None

	request_question = response_packet.questions[0]
	if request_question in saved_responses:
		return saved_responses[request_question]

	for answer in response_packet.answers:
		if _is_answer_to_request(answer, response_packet):
			saved_responses[request_packet.questions[0]] = response_packet
			return response_packet

	doContinue = False
	for answer in response_packet.authority:
		# search for ns's ip
		if answer.rr_type == NS_TYPE:
			ns_name = answer.rdata.rdata
			for rr in response_packet.additional_information:
				if _rr_is_authority_servers_ip(rr, ns_name):
					ip = rr.rdata.rdata
					# get answer form lower level server
					response = recursive_query(request_packet, ip.exploded, cur_root)

					# jump to another ns if this one returns none
					if response == None:
						doContinue = True
						break
					else:
						return response
			if doContinue:
				doContinue = False
				continue

			# if we can't get name server's ip from "additional information", ask root
			ns_request = _request_for_ip(request_packet, ns_name, cur_root)
			root_ip = ROOT_SERVER_IPS[cur_root]
			ns_ip_response = recursive_query(ns_request, root_ip, cur_root)

			if ns_ip_response == None:
				continue
			for rr in ns_ip_response.answers:
				if _rr_is_authority_servers_ip(rr, ns_name):
					ip = rr.rdata.rdata
					response = recursive_query(request_packet, ip.exploded, cur_root)
					if response == None:
						break
					else:
						return response

	return response_packet

def _is_answer_to_request(answer, packet):
	return answer.rr_name.name == packet.questions[0].q_name.name and answer.rr_type == packet.questions[0].q_type

def _rr_is_authority_servers_ip(rr, ns_name):
	return rr.rr_name.name == ns_name.name and rr.rr_type == A_TYPE

def _request_for_ip(request_packet, ns_name, cur_root):
	ns_request = copy.deepcopy(request_packet)
	ns_request.questions[0].q_name = ns_name
	ns_request.questions[0].q_type = A_TYPE
	return ns_request

# do not change!
if __name__ == '__main__':
	CONFIG = sys.argv[1]
	IP = sys.argv[2]
	PORT = sys.argv[3]
	run_dns_server(CONFIG, IP, PORT)
