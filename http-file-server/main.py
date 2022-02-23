from socket import *
import json
import threading
import os.path
from datetime import datetime
import magic
import os
import mimetypes

SERVER_NAME = "Example Server (Tamta)"
KEEP_ALIVE_TIME = 5

with open('config.json') as f:
  data = json.load(f)

hostToRoot = {}
ipPortPairs = set()
serverSockets = []
for vhostInfo in data['server']:
	serverAddress = (vhostInfo['ip'], vhostInfo['port'])
	ipPortPairs.add(serverAddress)
	domainPort = (vhostInfo['vhost'], vhostInfo['port'])
	hostToRoot[domainPort] = vhostInfo['documentroot']

# print('ipPortPairs: ', ipPortPairs)
for serverAddress in ipPortPairs:
	serverSocket = socket(AF_INET, SOCK_STREAM)
	serverSocket.bind(serverAddress)
	serverSocket.listen(1024)
	serverSockets.append(serverSocket)
	# print(serverAddress)
	# print("The server is ready to receive")

# def addStatusLine(httpResponse, requestLineList):

def getHeaders(entityBody, connectionType, tester, file):
	dateNow = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
	serverHeader = "Server: " + SERVER_NAME + "\r\n"
	dateHeader = "Date: " + dateNow + "\r\n"
	contentLengthHeader = "Content-Length: " + str(len(entityBody)) + "\r\n"
	contentTypeHeader = ""
	if tester:
		contentTypeHeader += "Content-Type: " + magic.from_buffer(entityBody, mime=True) + "\r\n"
	elif file != "":
		print(file)
		try:
			type = mimetypes.guess_type(file.name, strict=True)[0]
			contentTypeHeader += "Content-Type: " + type + "\r\n"
		except:
			pass
	etagHeader = "ETag: " + str(hash(entityBody)) + "\r\n"
	acceptRangesHeader = "Accept-Ranges: bytes\r\n"
	headers = serverHeader + dateHeader + contentLengthHeader + contentTypeHeader + etagHeader + acceptRangesHeader
	if connectionType == "keep-alive":
		headers += "Keep-alive: " + "timeout=" + str(KEEP_ALIVE_TIME) + ", max=1000" + "\r\n"
	return headers

def errorEntityBody():
	return b'''
			<html>
				<head>
					<style>
						.errorImg {
							display: flex;
							height: 95vh;
							width: 98vw;
							justify-content: center;
							align-items: center;
						}
					</style>
				</head>
				<div class="errorImg">
					<img src='https://i.pinimg.com/originals/a3/c4/bb/a3c4bb7364524b430f9fe481bbb921a6.jpg'></img>
				</div>
			</html>
		'''

def serveClient(connectionSocket, addr):
	while True:
		connectionSocket.settimeout(KEEP_ALIVE_TIME)
		try:
			httpRequest = connectionSocket.recv(1024).decode()
		except:
			connectionSocket.close()
			return
		if(httpRequest == ""):
			connectionSocket.close()
			return
		# print("httpRequest: ", httpRequest)
		requestList = httpRequest.split('\r\n')
		requestLineList = requestList[0].split(' ')

		method = requestLineList[0]
		# print("requestLineList: ", requestLineList)
		file = requestLineList[1].replace("%20", " ")
		version = requestLineList[2]
		hostList = requestList[1].split(' ')
		host = hostList[1].split(':')
		# print("host: ", host)
		hostWebAddr = host[0]
		port = -1
		if len(host) == 2:
			port = int(host[1])

		try:
			documentroot = hostToRoot[(hostWebAddr, port)]
		except:
			documentroot = "none"
		httpResponse = b""
		statusLine = version + " " 
		path = documentroot + file
		# print(path, " here")
		entityBody = b""
		if documentroot == "none":
			# print((hostWebAddr, port), " not in ", docrootPortPairs)
			statusLine += "404 Not Found\r\n"
			entityBody = b"Requested Domain Not Found"
		elif os.path.exists(path):
			# print(path, " exists")
			statusLine += "200 OK\r\n"
			if os.path.isfile(path):
				with open(path, 'rb') as file:
					entityBody += file.read()
			elif os.path.isdir(path):
				dirHtml = '<html> <ul>'
				# print("file: ", file)
				for filename in os.listdir(path):
					# print("filename: ", filename)
					if file == '/':
						file = ""
					dirFile = file + "/" + filename.replace(" ",  "%20")
					dirHtml += f'<li><a href={dirFile}>{filename}</a></li>'
				dirHtml += '</ul> </html>'
				entityBody = dirHtml.encode()
		else:
			statusLine += "404 Not Found\r\n"
			entityBody = errorEntityBody()

		rangeLine = ""
		tester = False
		for line in requestList:
			contents = line.split(': ')
			if contents[0] == "Connection":
				connectionHeader = line + "\r\n"
				connectionType = contents[1]
			if contents[0] == "Range":
				rangeLine = line.split("=")
			if contents[0] == "User-Agent":
				if contents[1][:6] == "python":
					tester = True

		# print(statusLine)
		if rangeLine != "" and statusLine == version + " 200 OK\r\n":
			# print("RANGELINE: ", rangeLine)
			ranges = rangeLine[1].split(", ")
			# print("RANGES: ", ranges)
			resultBody = b""
			for brange in ranges:
				# print("BRANGE: ", brange)
				lrange, rrange = brange.split("-")
				# print(lrange, rrange)
				if lrange == "":
					l = 0
				else: 
					l = int(lrange)
				if rrange == "":
					r = len(entityBody)
				else:
					r = int(rrange)
				# print("left, right: ", l, r)
				resultBody += entityBody[l:r+1]
			entityBody = resultBody

		headers = getHeaders(entityBody, connectionType, tester, file) + connectionHeader

		httpResponse += (statusLine + headers + "\r\n").encode()
		if method == "GET":
			httpResponse += entityBody
		# print("httpResponse:\r\n", httpResponse)
		connectionSocket.send(httpResponse)

		if connectionType == "close":
			connectionSocket.close()
			return
	# connectionSocket.close()

def listenToClients(serverSocket):
	while True:
		connectionSocket, addr = serverSocket.accept()
		tmp_thread = threading.Thread(target=serveClient, args=(connectionSocket, addr))
		tmp_thread.start()

for socket in serverSockets:
	socket_thread = threading.Thread(target=listenToClients, args=(socket,))
	socket_thread.start()