import os
import csv
import sys
# import pandas as pd
import sqlite3
import socket
import time
import datetime
import xml.etree.ElementTree as etree
# https://www.tutorialspoint.com/the-elementtree-xml-api-in-python

rfid_dictionary =	{
  1280: 5,
  2048: 8
}

class ProcessingTimesFinder():

    def __init__(self, filename):
        ## read csv
        self.path = os.path.dirname(__file__) #find the directory of this source file
        '''
        #check if the directory is correct
        path = os.getcwd() # get current working directory
        print(path)
        '''
        
        self.file_name = os.path.join(self.path, filename)
        '''
        # load csv with panda
        self.data_frame = pd.read_csv(self.file_name) #import csv
        self.data_frame.info()
        print (self.data_frame)

        self.processing_times_array = self.data_frame.select_dtypes(include=int).to_numpy()
        print (self.processing_times_array) # whole array
        '''

        self.station_ids = []
        self.carrier_ids = []
        self.csv_data = []

        with open('processing_times_table.csv', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar=',')
            for index, row in enumerate(spamreader, start=0):
                if index == 0:
                    self.station_ids = row
                    print('\n{:-^100}'.format('Carrier RFID (row 1 - 16) x Station ID (row 1 - 16) matrix'))
                else:
                    self.carrier_ids.append(row.pop(0))
                    self.csv_data.append(row)
                    print(row)

        '''
        # help regarding the processing_times_array
        print(processing_times_array[0,0]) # Carrier#1 Station#01
        print(processing_times_array[0,1]) # Carrier#1 Station#02
        # ...
        print(processing_times_array[15,15]) # Carrier#16 Station#16
        '''
        
    def get_est_proc_time(self, carrier_RFID, station_ID):
        '''
        find the estimated processing time
        '''
        estimated_process_time = self.csv_data[carrier_RFID - 1][ station_ID - 1]
        return estimated_process_time

def create_table(curs):
    curs.execute("CREATE TABLE IF NOT EXISTS dataProdStation(StationID INTEGER, rfid INTEGER, arrivalUnix REAL, arrivalStamp TEXT, EstimProcessTime REAL, command1 TEXT, value1 REAL, command2 TEXT, value2 TEXT)")

def dynamic_data_entry(sql_connection, cur, stat_id, rfid, unix, est_procc_t):
    date = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
    cur.execute("INSERT INTO dataProdStation(StationID, rfid, arrivalUnixEpoch, arrivalDateTime, EstimProcessTime) VALUES (?, ?, ?, ?, ?)",
            (stat_id, rfid, unix, date, est_procc_t))
    sql_connection.commit()

def minimalistic_response_handler(arr_time_stamp, station_id, rf_id, estim_process_time):

def response_handler(arr_time_stamp, station_id, rf_id, estim_process_time):
    
    # make xml
    root = etree.Element("server_response")

    time_stamp_elem = etree.Element("time_stamp")
    root.append(time_stamp_elem)
    time_stamp_elem.text = f"{time_stamp}"

    station = etree.Element("station")
    root.append(station)
    station_id_elem = etree.SubElement(station, "ID")
    station_id_elem.text = f"{station_id}"

    carrier = etree.Element("carrier")
    root.append(carrier)
    carrier_id_elem = etree.SubElement(carrier, "RFID")
    carrier_id_elem.text = f"{rf_id}"

    estim_time_elem = etree.Element("estim_time")
    root.append(estim_time_elem)
    estim_time_elem.text = f"{estim_process_time}"
    
    # decide on commands
    #wait_time = estim_process_time
    """
    if rf_id <= 5:
        side = "left"
    elif rf_id > 5:
        side = "right"

    def make_xml_cmd(command_type, value):
        command_elem = etree.Element("command")
        root.append(command_elem)
        cmd_type_elem = etree.SubElement(command_elem, "cmd")
        cmd_type_elem.text = f"{command_type}"
        cmd_value_elem = etree.SubElement(command_elem, "val")
        cmd_value_elem.text = f"{value}"
    """
    """
    wait_cmd_str = "wait"
    junction_cmd_str = "junction"
    make_xml_cmd(wait_cmd_str, wait_time)
    make_xml_cmd(junction_cmd_str, side)
    """
    print('\n{:-^70}'.format('Server response info - summary'))
    print ("{:<15} {:<10} {:<25} {:<15}".format('Station ID','RFID','Time stamp','Estimated processing time'))
    print ("{:<15} {:<10} {:<25} {:<15}".format(station_id, rf_id, arr_time_stamp, estim_process_time))
    # print(f"Station ID: {station_id}\t\tRFID: {rfid}\t\tCommands sent at: {time_stamp}\t\tEstimated processing time: {estim_process_time}")
    """
    print('\n{:-^70}'.format('Server response commands - summary'))
    print ("{:<15} {:<10}".format('Command','Value'))
    print ("{:<15} {:<10}".format(wait_cmd_str, wait_time))
    print ("{:<15} {:<10}".format(junction_cmd_str, side))
    """
    
    # make SQLite database
    conn = sqlite3.connect('PLC_data.db')
    c = conn.cursor()
    create_table(c) # if not exists
    # add to the log
    dynamic_data_entry(conn, c, station_id, rf_id, arr_time_stamp, estim_process_time)
    # close the database
    c.close()
    conn.close()

    #indent_xml(root)

    #tree = etree.ElementTree(root)
    #msg = etree.tostring(root, encoding="unicode", method="xml")
    msg = f"T#{estim_process_time}ms"
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
    <arrival><station>10</station><carrier>8</carrier></arrival>
    '''
    """
    prefix = "<arrival>"
    suffix = "</arrival>"   
    if recieved_xml_string.startswith(prefix) == False or recieved_xml_string.endswith(suffix) == False:
        new_msg_recieving = True
        print("prefix or suffix not found")
        #full_msg = ''
        #continue
    else:
    """
    tree = etree.ElementTree(etree.fromstring(recieved_xml_string))
    root = tree.getroot()
    # children = root.getchildren()
    # print(children) # prints out the list of the root children
    """
    for time_stamp_elem in root.iter("time_stamp"):
        carrier_arrival_time_stamp = time_stamp_elem.text
    """
    for station_elem in root.iter("station"):
        #for station_id_elem in station_elem.iter("ID"):
            #station_id_recieved = station_id_elem.text
        station_id_recieved = station_elem.text

    for carrier_elem in root.iter("carrier"):
        #for rfid_elem in carrier_elem.iter("RFID"):
            #rfid_recieved = rfid_elem.text
        rfid_recieved = carrier_elem.text
        rfid_recieved_sticker = rfid_dictionary[int(rfid_recieved)]
    return int(station_id_recieved), rfid_recieved_sticker


if __name__ == "__main__":
    print(sys.version)
    print(sys.executable)
    print('\n{:-^70}'.format('Server startup'))

    # initialize ProcessingTimesFinder
    ptf = ProcessingTimesFinder('processing_times_table.csv')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to the port
    #server_address = ('172.20.66.48', 65432)
    s.bind((socket.gethostname(), 65431))
    s.listen(1)
    clientsocket, address = s.accept()
    # now our endpoint knows about the OTHER endpoint.
    print(f"Connection from {address} has been established.")

    # arbitrary variables just for testing
    #station_id_recv = 12
    #rfid_recv = 8
    

    while True:
        '''
        msg = "Welcome to the server!"
        msg = f"{len(msg):<{HEADERSIZE}}"+msg
        clientsocket.send(bytes(msg,"utf-8"))
        '''

        full_recieved_from_client = ''
        new_msg = True
        while True:
            msg = clientsocket.recv(64)
            msg_decoded = msg.decode('utf-8')
            if new_msg:
                print('received: ' + msg_decoded)
                """
                # print("Message length:",msg[:HEADERSIZE])
                msglen = int(msg[:HEADERSIZE])
                new_msg = False

                # print(f"full message length: {msglen}")

                full_recieved_from_client += msg.decode("utf-8")
                # print(len(full_recieved_from_client))


                if len(full_recieved_from_client)-HEADERSIZE == msglen:
                    print('\n{:*^70}'.format(''))
                    print('{:*^70}'.format('Full client message recieved'))

                    recieved_from_client_cleaned = full_recieved_from_client [HEADERSIZE:]
                    print(f"Message length: {msglen}")
                    print("Full msg recieved:")
                    print(recieved_from_client_cleaned)
                """
                station_id_recv, rfid_recv = xml_string_parser(msg_decoded)
                carrier_arr_time_stamp = time.time()
                print('\n{:-^70}'.format('Carrier arrival - summary'))
                print ("{:<15} {:<10} {:<15}".format('Station ID','RFID','Arrival time stamp'))
                
                print ("{:<15} {:<10} {:<15}".format(station_id_recv, rfid_recv, carrier_arr_time_stamp))
                # print(f"Station ID: {station_id_recv}\t\tRFID: {rfid_recv}\t\tArrived at: {carrier_arr_time_stamp}")
                
                # get estimated process time
                # estimated_process_time = 112233445566 # test
                print(f"rfid_recv: {rfid_recv}")
                print(f"station_id_recv: {station_id_recv}")
                estimated_process_time = ptf.get_est_proc_time(rfid_recv, station_id_recv)
                # save to log here
                
                # write server response
                
                #server_response_xml_string = response_handler(carrier_arr_time_stamp, station_id_recv, rfid_recv, estimated_process_time)
                """
                print('\n{:-^70}'.format('Send response message to the client'))
                print(server_response_xml_string)
                msg = f'{len(server_response_xml_string):<{HEADERSIZE}}'+server_response_xml_string # check f-string formatting
                clientsocket.send(bytes(msg, "utf-8"))
                
                """
                server_response_xml_string = response_handler(carrier_arr_time_stamp, station_id_recv, rfid_recv, estimated_process_time)
                clientsocket.send(bytes(server_response_xml_string, "utf-8"))
                print("\nWaiting for client requests...")
                new_msg = True
                full_recieved_from_client = ""
