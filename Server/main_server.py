import os
import csv
import sys
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
        self.file_name = os.path.join(self.path, filename)

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

    def get_est_proc_time(self, carrier_RFID, station_ID):
        '''
        find the estimated processing time
        '''
        estimated_process_time = self.csv_data[carrier_RFID - 1][ station_ID - 1]
        return estimated_process_time

def create_table(curs):
    curs.execute("CREATE TABLE IF NOT EXISTS dataProdStation(StationID INTEGER, rfid INTEGER, arrivalUnixEpoch REAL, arrivalDateTime TEXT, EstimProcessTime REAL)")

def dynamic_data_entry(sql_connection, cur, stat_id, rfid, unix, est_procc_t):
    date = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
    cur.execute("INSERT INTO dataProdStation(StationID, rfid, arrivalUnixEpoch, arrivalDateTime, EstimProcessTime) VALUES (?, ?, ?, ?, ?)",(stat_id, rfid, unix, date, est_procc_t))
    sql_connection.commit()

def response_handler(arr_time_stamp, station_id, rf_id, estim_process_time):
    
    print('\n{:-^70}'.format('Server response info - summary'))
    print ("{:<15} {:<10} {:<25} {:<15}".format('Station ID','RFID','Time stamp','Estimated processing time'))
    print ("{:<15} {:<10} {:<25} {:<15}".format(station_id, rf_id, arr_time_stamp, estim_process_time))
    
    # make SQLite database
    conn = sqlite3.connect('PLC_data.db')
    c = conn.cursor()
    create_table(c) # if not exists
    # add to the log
    dynamic_data_entry(conn, c, station_id, rf_id, arr_time_stamp, estim_process_time)
    # close the database
    c.close()
    conn.close()

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
    tree = etree.ElementTree(etree.fromstring(recieved_xml_string))
    root = tree.getroot()
    
    for station_elem in root.iter("station"):
        station_id_recieved = station_elem.text

    for carrier_elem in root.iter("carrier"):
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
    s.bind((socket.gethostname(), 65431))
    s.listen(1)
    clientsocket, address = s.accept()
    # now our endpoint knows about the OTHER endpoint.
    print(f"Connection from {address} has been established.")

    while True:
        msg = clientsocket.recv(64)
        msg_decoded = msg.decode('utf-8')
        if new_msg:
            print('received: ' + msg_decoded)
            
            #parse data from xml
            station_id_recv, rfid_recv = xml_string_parser(msg_decoded)
            
            # get a unix epoch time stamp
            carrier_arr_time_stamp = time.time()
            
            #summarise
            print('\n{:-^70}'.format('Carrier arrival - summary'))
            print ("{:<15} {:<10} {:<15}".format('Station ID','RFID','Arrival time stamp'))
            print ("{:<15} {:<10} {:<15}".format(station_id_recv, rfid_recv, carrier_arr_time_stamp))
            
            # get estimated process time
            estimated_process_time = ptf.get_est_proc_time(rfid_recv, station_id_recv)
            
            server_response_simple_string = response_handler(carrier_arr_time_stamp, station_id_recv, rfid_recv, estimated_process_time)
            clientsocket.send(bytes(server_response_simple_string, "utf-8"))
            print("\nWaiting for client requests...")
            new_msg = True
            full_recieved_from_client = ""
