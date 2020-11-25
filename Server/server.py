import socket
import time

# figxed length header
HEADERSIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
s.bind((socket.gethostname(), 1234)) # localhost, port name
s.listen(5) #queue of 5 msgs

while True:
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been estabilished")
    
    
    msg = "Welcome to the server!"
    msg = f'{len(msg):<{HEADERSIZE}}'+msg # check f-string formatting
    
    clientsocket.send(bytes(msg, "utf-8"))

    while True:
        time.sleep(3)
        msg = f"The time is {time.time()}"
        msg = f'{len(msg):<{HEADERSIZE}}'+msg
        clientsocket.send(bytes(msg, "utf-8"))
