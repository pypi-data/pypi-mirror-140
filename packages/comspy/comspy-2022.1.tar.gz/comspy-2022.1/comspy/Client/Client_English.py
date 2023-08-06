#!/usr/bin/python3

import socket
import sys
import time
import threading

def client():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	host = socket.gethostname()

	port = int(input("Please enter the communication port number(0~65535):"))

	try:
		s.connect((host, port))
		while True:
			msg = s.recv(2048)
			print(msg.decode('utf-8'))

			while True:
				msg = s.recv(1024)
				if msg.decode('utf-8') != "\r":
					print("Received message:"+msg.decode('utf-8'))
					if msg.decode('utf-8') == "QUIT\r":
						print("The other party broke off this communication")
						s.close()
						exit()
	except ConnectionResetError:
	    print("Error ConnectionResetError was reported, possibly because the remote host forced down an existing connection")
	    exit()
	except ConnectionRefusedError:
	    print("Error ConnectionRefusedError was reported, possibly because the target computer actively rejected it")
	    exit()
	except ConnectionAbortedError:
	    print("Error ConnectionAbortedError was reported, possibly because software on the host aborted an established connection")
	    exit()
	except BrokenPipeError:
	    print("BrokenPipeError was reported")
	    exit()

def start():
    threading.Thread(target=client).start()


	

