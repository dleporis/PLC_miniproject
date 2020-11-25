import socket

# figxed length header
HEADERSIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1234))

while True:

    full_msg = ''
    new_msg_recieving = True
    while True:
        msg = s.recv(16) #buffer
        if new_msg_recieving:
            print(f"new message length {msg[:HEADERSIZE]}")
            msglen = int(msg[:HEADERSIZE])
            new_msg_recieving = False

        full_msg += msg.decode("utf-8") 
        # print(msg.decode("utf-8")) # display the last recieved msg part

        if len(full_msg) - HEADERSIZE == msglen:
            print("full msg recieved")
            print(full_msg[HEADERSIZE:])
            new_msg_recieving = True
            full_msg = ''

    print(full_msg)