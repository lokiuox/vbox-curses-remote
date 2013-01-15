#!/usr/bin/env python3

import socket
import libssh2
import os

def open_session(user, host, port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((host,port))

	# Create a new SSH session using that socket and login as
	session = libssh2.Session()
	session.startup(sock)
	session.userauth_publickey_fromfile(user, os.getenv("HOME") + "/.ssh/id_rsa.pub", os.getenv("HOME") + "/.ssh/id_rsa")

	return session

def remote_cmd(session, rcmd):

	channel = session.channel()
	channel.execute(rcmd)

	stdout = ""
#	stderr = ""

	while not channel.eof:
		data = channel.read(1024)
		if data:
			stdout += data.decode("utf-8")

#		data = channel.read(1024, libssh2.STDERR)
#		if data:
#			stderr += data.decode("utf-8")
 
	#print(stderr)
	return stdout

