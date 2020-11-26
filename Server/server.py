import socket
import time
import xml.etree.ElementTree as etree
# https://www.tutorialspoint.com/the-elementtree-xml-api-in-python


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

# figxed length header
HEADERSIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
s.bind((socket.gethostname(), 1234)) # localhost, port name
s.listen(5) #queue of 5 msgs


# arbitrary variables just for testing
station_id = 13
rfid = 8
estim_process_time = 52680836 #ptf.get_est_proc_time(rfid, station_id)


info_to_send = {'time_stamp':'aaa','age':21,'sal':5000}

# make xml
root = etree.Element("server_response")

time_stamp = etree.Element("time_stamp")
root.append(time_stamp)
time_stamp.text = f"{time.time()}"


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
msg = etree.tostring(root, encoding='utf-8', method='xml')
xml_header = """<?xml version="1.0" encoding="UTF-8"?>"""
#xml_header_str = xml_header.decode('utf-8')
print(xml_header)
msg = xml_header + msg
print(msg)

while True:
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been estabilished")
    
    msg = "Welcome to the server!"
    print(msg)
    msg = f'{len(msg):<{HEADERSIZE}}'+msg # check f-string formatting
    
    clientsocket.send(bytes(msg, "utf-8"))

    while True:
        time.sleep(3)
        msg = f"The time is {time.time()}"
        msg = f'{len(msg):<{HEADERSIZE}}'+msg
        clientsocket.send(bytes(msg, "utf-8"))
