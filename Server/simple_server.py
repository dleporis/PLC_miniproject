import xml.etree.ElementTree as ET
import csv
import socket
import sys
import time

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('172.20.66.78', 1234)
print('starting up on %s port %s' % server_address)
sock.bind(server_address)

#give the station number
print("station:")
station = int(input())


# Wait for a connection and connect
sock.listen(1)
connection, client_address = sock.accept()
print('connection from', client_address)

# Receive the data
while True:
    data = connection.recv(64)
    data1=data.decode('utf-8')
            
    if data:
        print('received: ' + data1)
                
        #make an xml file from the input
        f = open("xmldata.xml", "w")
        f.write(data1)
        f.close()
