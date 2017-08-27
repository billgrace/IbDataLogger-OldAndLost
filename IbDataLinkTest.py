#!/usr/local/bin/python3

import sys
import socket

LocalIpAddress = "192.168.1.45"
DistantIpAddress = "73.254.166.172"
BorisPortNumber = 55554
StatusPortNumber = 56781

def Main():
	if 2 == len(sys.argv):
		if "1" == sys.argv[1]:
			print("1 => Boris local")
			Boris(LocalIpAddress)
		elif "2" == sys.argv[1]:
			print("2 => Boris distant")
			Boris(DistantIpAddress)
		elif "3" == sys.argv[1]:
			print("3 => Status local")
			StatusRequest(LocalIpAddress)
		elif "4" == sys.argv[1]:
			print("4 => Status Distant")
			StatusRequest(DistantIpAddress)
		else:
			ShowCommandLineUsage()
	else:
		ShowCommandLineUsage()

def ShowCommandLineUsage():
		print("One parameter: 1=> localBoris, 2=> distantBoris, 3=> localStatus, 4=> distantStatus")

def StatusRequest(IpAddress):
	if(DistantIpAddress == IpAddress):
		print("Distant Status.")
	else:
		print("Local Status.")

	print ("Sending to IP address: " + str(IpAddress) + " using port: " + str(StatusPortNumber))

	outgoingMessage = bytes([0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00])
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((IpAddress, StatusPortNumber))
	s.send(outgoingMessage)
	incomingMessage = s.recv(1024)
	s.close()
	print ("sent: status request to " + IpAddress + ":" + str(StatusPortNumber) + ", received: ")
	for incomingByte in incomingMessage:
		print(format(incomingByte, '02x'), " ", end="")
	print("")
	print("...")

def Boris(IpAddress):
	if(DistantIpAddress == IpAddress):
		print("Distant Boris.")
	else:
		print("Local Boris.")

	print ("Sending to IP address: " + str(IpAddress) + " using port: " + str(BorisPortNumber))

	outgoingMessage = "Boris?"
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("0.0.0.0", BorisPortNumber))
	s.connect((IpAddress, BorisPortNumber))
	s.send(outgoingMessage.encode())
	incomingMessage = s.recv(1024).decode()
	print ("sent: " + outgoingMessage + " to " + IpAddress + ":" + str(PortNumber) + ", received: " + incomingMessage)
	s.close()

if __name__ == '__main__':
	Main()
