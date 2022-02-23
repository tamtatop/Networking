import sys
import getopt

import Checksum
import BasicSender

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
PACKET_MSG_SIZE = 1400
WINDOW_SIZE = 7
TIMEOUT = 0.5

class Sender(BasicSender.BasicSender):

	def __init__(self, dest, port, filename, debug=False, sackMode=False):
		super(Sender, self).__init__(dest, port, filename, debug)
		self.sackMode = sackMode
		self.debug = debug
		self.packets = list()
		self.base = 0
		self.sent_base = 0
		self.packets_received = list()

	# Main sending loop.
	def start(self):
		# add things here
		self.generate_packets()
		self.packets_received = [False]*len(self.packets)
		self.go_back_n_algo()
		

	def go_back_n_algo(self):
		ack_repeated = 0
		while True:
			if(self.base == len(self.packets)):
				break
			self.send_window()
			received = self.receive(TIMEOUT)

			if received == None:
				self.sent_base = self.base
				continue

			if not Checksum.validate_checksum(received):
				continue

			msg_type, resp_seqno, _, ack_checksum = self.split_packet(received)
			if self.sackMode:
				self.save_received_packets_sack(resp_seqno)
				resp_seqno = resp_seqno.split(";")[0]
			
			if int(resp_seqno) > self.base:
				self.base = int(resp_seqno)
				ack_repeated = 0
			elif int(resp_seqno) == self.base:
				ack_repeated += 1
				if ack_repeated == 4:
					self.send(self.packets[self.base])
					ack_repeated = 0

	def save_received_packets_sack(self, sack_seqno):
		rec_packets = sack_seqno.split(";")[1]
		if rec_packets == "":
			return
		rec_packets_list = rec_packets.split(",")
		for packet_index in rec_packets_list:
			self.packets_received[int(packet_index)] = True

	def send_window(self):
		for i in range(WINDOW_SIZE):
			seqno = self.base + i
			if seqno == len(self.packets):
				break
			if seqno >= self.sent_base and not self.packets_received[seqno]:
				self.send(self.packets[self.base + i])
				self.sent_base = seqno + 1

	def generate_packets(self):
		msg_type = "syn"
		first_packet = self.make_packet(msg_type, 0, "")
		self.packets.append(first_packet)
		msg_type = "dat"
		while msg_type != "fin":
			seqno = len(self.packets)
			data = self.infile.read(PACKET_MSG_SIZE)
			if len(data) < PACKET_MSG_SIZE:
				msg_type = "fin"
			packet = self.make_packet(msg_type, seqno, data)
			self.packets.append(packet)

'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
	def usage():
		print "BEARS-TP Sender"
		print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
		print "-p PORT | --port=PORT The destination port, defaults to 33122"
		print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
		print "-d | --debug Print debug messages"
		print "-h | --help Print this usage message"
		print "-k | --sack Enable selective acknowledgement mode"


	try:
		opts, args = getopt.getopt(sys.argv[1:],
								   "f:p:a:dk", ["file=", "port=", "address=", "debug=", "sack="])
	except:
		usage()
		exit()

	port = 33122
	dest = "localhost"
	filename = None
	debug = False
	sackMode = False

	for o, a in opts:
		if o in ("-f", "--file="):
			filename = a
		elif o in ("-p", "--port="):
			port = int(a)
		elif o in ("-a", "--address="):
			dest = a
		elif o in ("-d", "--debug="):
			debug = True
		elif o in ("-k", "--sack="):
			sackMode = True

	s = Sender(dest, port, filename, debug, sackMode)
	try:
		s.start()
	except (KeyboardInterrupt, SystemExit):
		exit()