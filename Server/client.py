import socket
from random import *
import time
import xml.etree.ElementTree as etree

# figxed length header
HEADERSIZE = 10
# STATION NUMBER
STATIONID = 12

junction_state = "straight"

# setup TCP communication
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1234))

while True:
    print("ha")
    full_msg = ''
    new_msg_recieving = True
    while True:
        print("haha")
        # check the sensors
        is_new_carrier_here = randint(1, 1000)
        if is_new_carrier_here == 1:
            arrived_rfid = randint(1, 15)
            arrived_time_stamp = time.time()
            '''
            <arrival>
                <station>
                    <ID>10</ID>
                </station>
                <carrier>
                    <RFID>1</RFID>
                </carrier>
                <request>estim_time</request>
                <request>command</request>
            </arrival>
            '''
            # make xml msg to server
            root = etree.Element("arrival")

            time_stamp_elem = etree.Element("time_stamp")
            root.append(time_stamp_elem)
            time_stamp_elem.text = f"{arrived_time_stamp}"


            station_elem = etree.Element("station")
            root.append(station_elem)
            station_id_elem = etree.SubElement(station_elem, "ID")
            station_id_elem.text = f"{STATIONID}"

            carrier_elem = etree.Element("carrier")
            root.append(carrier_elem)
            carrier_id_elem = etree.SubElement(carrier_elem, "RFID")
            carrier_id_elem.text = f"{arrived_rfid}"

            request_elem = etree.Element("request")
            root.append(request_elem)
            request_elem.text = "estim_time"

            request_elem = etree.Element("request")
            root.append(request_elem)
            request_elem.text = "commands"

            tree = etree.ElementTree(root)
            send_msg = etree.tostring(root, encoding="unicode", method="xml")
            print("request:")
            print(send_msg)

        #check for messages
        msg = s.recv(16) #buffer
        if new_msg_recieving:
            print(f"new message length {msg[:HEADERSIZE]}")
            msglen = int(msg[:HEADERSIZE])
            new_msg_recieving = False

        full_msg += msg.decode("utf-8") 
        # print(msg.decode("utf-8")) # display the last recieved msg part

        if len(full_msg) - HEADERSIZE == msglen:
            
            full_msg_cleaned = full_msg [HEADERSIZE:]
            print("full msg recieved:")
            print(full_msg_cleaned)
            

            prefix = "<server_response>"
            suffix = "</server_response>"   
            if full_msg_cleaned.startswith(prefix) == False or full_msg_cleaned.endswith(suffix) == False:
                new_msg_recieving = True
                full_msg = ''
                continue
            else:
                tree = etree.ElementTree(etree.fromstring(full_msg_cleaned))
                root = tree.getroot()
                children = root.getchildren()
                print(children)
                '''
                [<Element 'time_stamp' at 0x0000023EF5EDD908>, <Element 'station' at 0x0000023EF61E4D18>,
                <Element 'carrier' at 0x0000023EF624E228>, <Element 'estim_time' at 0x0000023EF6258958>, 
                <Element 'command' at 0x0000023EF62589A8>, <Element 'command' at 0x0000023EF6258A98>]
                '''
                for time_stamp_elem in root.iter("time_stamp"):
                    server_send_time_stamp = time_stamp_elem.text

                for station_elem in root.iter("station"):
                    for station_id_elem in station_elem.iter("ID"):
                        station_id = station_id_elem.text

                for carrier_elem in root.iter("carrier"):
                    for rfid_elem in carrier_elem.iter("RFID"):
                        rfid = rfid_elem.text

                for estim_time_elem in root.iter("estim_time"):
                    estim_time = estim_time_elem.text

                # save these values into log
                for command_elem in root.iter("command"):
                    for cmd_elem in command_elem.iter("cmd"):
                        cmd = cmd_elem.text
                        print("cmd")
                        print(cmd)
                    for val_elem in command_elem.iter("val"):
                        val = val_elem.text
                        print("val")
                        print(val)
                    # execute commands
                    if cmd == "junction":
                        if val == junction_state:
                            print (f"keep junction in {junction_state} position")
                        else:
                            print(f"switch junction to {val} position")
                            junction_state = val
                    elif cmd == "wait":
                        print(f"set timer for {val} ms, and then release the carrier")
                
            new_msg_recieving = True
            full_msg = ''
