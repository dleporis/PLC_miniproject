import socket
import time
import xml.etree.ElementTree as etree
# https://www.tutorialspoint.com/the-elementtree-xml-api-in-python

def xml_string_writer(time_stamp, station_id, rfid, estim_process_time):
    # make xml
    root = etree.Element("server_response")

    time_stamp = etree.Element("time_stamp")
    root.append(time_stamp)
    time_stamp.text = f"{time_stamp}"

    station = etree.Element("station")
    root.append(station)
    station_id_elem = etree.SubElement(station, "ID")
    station_id_elem.text = f"{station_id}"

    carrier = etree.Element("carrier")
    root.append(carrier)
    carrier_id_elem = etree.SubElement(carrier, "RFID")
    carrier_id_elem.text = f"{rfid}"

    estim_time_elem = etree.Element("estim_time")
    root.append(estim_time_elem)
    estim_time_elem.text = f"{estim_process_time}"

    # decide on commands
    wait_time = estim_process_time
    if rfid <= 5:
        side = "left"
        wait_time = wait_time + 2 # 2 seconds
    elif rfid > 5:
        side = "straight"

    make_xml_cmd("wait", wait_time)
    make_xml_cmd("junction", side)
    #indent_xml(root)

    tree = etree.ElementTree(root)
    msg = etree.tostring(root, encoding="unicode", method="xml")
    return msg

def xml_string_parser(recieved_xml_string):
    '''
    Parsing of the folowing XML protocol
    <arrival>
        <timestamp>timestamp</timestamp>
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

    prefix = "<arrival>"
    suffix = "</arrival>"   
    if recieved_xml_string.startswith(prefix) == False or recieved_xml_string.endswith(suffix) == False:
        new_msg_recieving = True
        print("prefix or suffix not found")
        #full_msg = ''
        #continue
    else:
        tree = etree.ElementTree(etree.fromstring(recieved_xml_string))
        root = tree.getroot()
        children = root.getchildren()
        print(children)

        for time_stamp_elem in root.iter("time_stamp"):
            carrier_arrival_time_stamp = time_stamp_elem.text

        for station_elem in root.iter("station"):
            for station_id_elem in station_elem.iter("ID"):
                station_id_recieved = station_id_elem.text

        for carrier_elem in root.iter("carrier"):
            for rfid_elem in carrier_elem.iter("RFID"):
                rfid_recieved = rfid_elem.text
        return carrier_arrival_time_stamp, station_id_recieved, rfid_recieved


def make_xml_cmd(command_type, value):
    command_elem = etree.Element("command")
    root.append(command_elem)
    cmd_type_elem = etree.SubElement(command_elem, "cmd")
    cmd_type_elem.text = f"{command_type}"
    cmd_value_elem = etree.SubElement(command_elem, "val")
    cmd_value_elem.text = f"{value}"

def indent_xml(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent_xml(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


if __name__ == "__main__":

    # figxed length header
    HEADERSIZE = 10

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
    s.bind((socket.gethostname(), 1234)) # localhost, port name
    s.listen(5) #queue of 5 msgs


    # arbitrary variables just for testing
    station_id_recv = 12
    rfid_recv = 8
    estimated_process_time = 52680836 #ptf.get_est_proc_time(rfid, station_id)

    while True:
        clientsocket, address = s.accept()
        # now our endpoint knows about the OTHER endpoint.
        print(f"Connection from {address} has been established.")

        msg = "Welcome to the server!"
        msg = f"{len(msg):<{HEADERSIZE}}"+msg

        clientsocket.send(bytes(msg,"utf-8"))


        full_recieved_from_client = ''
        new_msg = True
        while True:
            msg = s.recv(16)

            if new_msg:
                print("new msg len:",msg[:HEADERSIZE])
                msglen = int(msg[:HEADERSIZE])
                new_msg = False

            print(f"full message length: {msglen}")

            full_recieved_from_client += msg.decode("utf-8")

            print(len(full_recieved_from_client))


            if len(full_recieved_from_client)-HEADERSIZE == msglen:
                print("Full client message recieved")
                print(full_recieved_from_client[HEADERSIZE:])
                recieved_from_client_cleaned = full_recieved_from_client [HEADERSIZE:]
                carrier_arr_time_stamp, station_id_recv, rfid_recv = xml_string_parser(recieved_from_client_cleaned)
                
                '{:*^30}'.format('Carrier arrival') # use '*' as a fill char
                
                print(f"Station ID: {station_id_recv}\tRFID: {rfid_recv}\tArrived at: {station_id_recv}\tEstimated processing time: {estimated_process_time}")
                # save to log here
                
                # write server response
                server_time_stamp = time.time()
                server_response_xml_string = xml_string_writer(time_stamp, station_id_recieved, rfid_recieved, estimated_process_time)
                msg = f'{len(server_response_xml_string):<{HEADERSIZE}}'+server_response_xml_string # check f-string formatting
                print("Send HEADER + message:")
                print(msg)
                clientsocket.send(bytes(msg, "utf-8"))

                new_msg = True
                full_recieved_from_client = ""
