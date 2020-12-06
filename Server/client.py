import socket
from random import *
import time
import datetime
import xml.etree.ElementTree as etree

def xml_string_writer(time_stamp, station_id, rfid):
    '''
    <arrival>
        <timestamp>timestamp</timestamp>
        <station>
            <ID>10</ID>
        </station>
        <carrier>
            <RFID>1</RFID>
        </carrier>
        """
        NO <request>estim_time</request>
        NO <request>command</request>
        """
    </arrival>
    '''
    # make xml msg to server
    root = etree.Element("arrival")

    time_stamp_elem = etree.Element("time_stamp")
    root.append(time_stamp_elem)
    time_stamp_elem.text = f"{time_stamp}"


    station_elem = etree.Element("station")
    root.append(station_elem)
    station_id_elem = etree.SubElement(station_elem, "ID")
    station_id_elem.text = f"{station_id}"

    carrier_elem = etree.Element("carrier")
    root.append(carrier_elem)
    carrier_id_elem = etree.SubElement(carrier_elem, "RFID")
    carrier_id_elem.text = f"{rfid}"

    """
    request_elem = etree.Element("request")
    root.append(request_elem)
    request_elem.text = "estim_time"

    request_elem = etree.Element("request")
    root.append(request_elem)
    request_elem.text = "commands"
    """

    tree = etree.ElementTree(root)
    xml_string = etree.tostring(root, encoding="unicode", method="xml")
    print("request:")
    print(xml_string)
    return xml_string

def xml_string_parser(recieved_xml_string):
    prefix = "<server_response>"
    suffix = "</server_response>"   
    if recieved_xml_string.startswith(prefix) == False or recieved_xml_string.endswith(suffix) == False:
        new_msg_recieving = True
        #full_msg = ''
        print("prefix or suffix not found")
        #continue
    else:
        tree = etree.ElementTree(etree.fromstring(recieved_xml_string))
        root = tree.getroot()
        children = root.getchildren()
        print(children)
        '''
        [<Element 'time_stamp' at 0x0000023EF5EDD908>, <Element 'station' at 0x0000023EF61E4D18>,
        <Element 'carrier' at 0x0000023EF624E228>, <Element 'estim_time' at 0x0000023EF6258958>, 
        <Element 'command' at 0x0000023EF62589A8>, <Element 'command' at 0x0000023EF6258A98>]
        '''
        for time_stamp_elem in root.iter("time_stamp"):
            server_time_stamp = time_stamp_elem.text

        for station_elem in root.iter("station"):
            for station_id_elem in station_elem.iter("ID"):
                station_id_recieved = station_id_elem.text

        for carrier_elem in root.iter("carrier"):
            for rfid_elem in carrier_elem.iter("RFID"):
                rfid_recieved = rfid_elem.text

        for estim_time_elem in root.iter("estim_time"):
            estim_time_recieved = estim_time_elem.text


        print(f"Server sent the response at {server_time_stamp} s")
        print(f"The commands are for the station with ID: {station_id_recieved}")
        if station_id_recieved == STATIONID:
            print("The command station ID matches the actual station ID")
        else:
            print("The command station ID doesn't match the actual station ID")
            print(f"The command station ID is {station_id_recieved}, while the actual station ID is {STATIONID}")
            return

        print(f"The commands are for the carrier with RFID: {rfid_recieved}")
        print(f"The estimated processing time is: {estim_time_recieved}")

        for command_elem in root.iter("command"):
            for cmd_elem in command_elem.iter("cmd"):
                cmd = cmd_elem.text
            for val_elem in command_elem.iter("val"):
                val = val_elem.text
            print(f"Command: {cmd} with value {val}")
            
            # execute commands
            print("\nCommand execution:")
            if cmd == "junction":
                if val == junction_state:
                    print (f"Keep junction in {junction_state} position")
                else:
                    print(f"Switch junction to {val} position")
                    junction_state = val
            elif cmd == "wait":
                print(f"set timer for {val} ms, and then release the carrier")
                time.sleep(val/1000)
                print(f"Carrier {rfid_recieved} released")

if __name__ == "__main__":
    # CONSTANTS
    # figxed length header
    HEADERSIZE = 10
    # STATION NUMBER
    STATIONID = 12

    junction_state = "straight" # other possible states: left, right, straight
        
    # setup TCP communication
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), 1234))
    #serversocket, address = s.accept()
    #print(f"Connection from {address} has been estabilished")

    '''
    #Aligning the text and specifying a width:
    
    '{:<30}'.format('left aligned')
    'left aligned                  '
    
    '{:>30}'.format('right aligned')
    '                 right aligned'
    
    '{:^30}'.format('centered')
    '           centered           '
    
    '{:*^30}'.format('centered')  # use '*' as a fill char
    '***********centered***********'
    '''

    while True:
        full_msg = ''
        new_msg = True # Todo: find meaning of this
        new_carrier_here = False
        while True:
            if new_carrier_here == False:
                input("Press any key for the carrier to aproach the station...")
                print("Carrier approaching...")
                time.sleep(0.2)
                print("Slowing down conveyor belt...")
                time.sleep(2)

                print("Carrier stopped...")
                new_carrier_here = True
                arrived_time_stamp = time.time()
                arrived_time_utc = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(arrived_time_stamp))
                time.sleep(0.2)
                
                print("Reading RFID...")
                arrived_rfid = randint(1, 15)
                time.sleep(0.2)
                print(f"The carier with RFID {arrived_rfid} arrived at time {arrived_time_stamp} s from EPOCH, which is {arrived_time_utc} in UTC.")
                
                # make and send the xml message
                client_request_string = xml_string_writer(arrived_time_stamp, STATIONID, arrived_rfid)
                msg_send = f'{len(client_request_string):<{HEADERSIZE}}'+client_request_string # check f-string formatting
                s.send(bytes(msg_send, "utf-8"))
                
               
            #check for messages
            msg = s.recv(16) #buffer
            if new_msg:
                print(f"new message length {msg[:HEADERSIZE]}")
                msglen = int(msg[:HEADERSIZE])
                new_msg = False

            full_msg += msg.decode("utf-8") 
            # print(msg.decode("utf-8")) # display the last recieved msg part

            if len(full_msg) - HEADERSIZE == msglen:
                
                full_msg_cleaned = full_msg [HEADERSIZE:]
                print("full msg recieved:")
                print(full_msg_cleaned)
                
                xml_string_parser(full_msg_cleaned)
                print ("Wait for another carrier...")
                new_carrier_here = False
                new_msg = True
                full_msg = ''
