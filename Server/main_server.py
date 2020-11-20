import os
import pandas as pd
import numpy as np
import socketserver

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
        
        # load csv with panda
        self.data_frame = pd.read_csv(self.file_name) #import csv
        self.data_frame.info()
        print (self.data_frame)

        self.processing_times_array = self.data_frame.select_dtypes(include=int).to_numpy()
        print (self.processing_times_array) # whole array
        
        '''
        # help regarding the processing_times_array
        print(processing_times_array[0,0]) # Carrier#1 Station#01
        print(processing_times_array[0,1]) # Carrier#1 Station#02
        # ...
        print(processing_times_array[15,15]) # Carrier#16 Station#16
        '''
        
    def get_est_proc_time(self, carrier_RFID, station_ID):
        # find the estimated processing time
        carrier_RFID = 1 # later will be extracted from XML recieved from the PLC
        station_ID = 10 # this is the station at smartlab we operate, change manually, we will not automate this during the miniproject
        estimated_process_time = self.processing_times_array[carrier_RFID - 1, station_ID - 1]
        print("Estimated process time: ", estimated_process_time)
        return estimated_process_time
    
    
class Handler_TCPServer(socketserver.BaseRequestHandler):
    """
    The TCP Server class for demonstration.

    Note: We need to implement the Handle method to exchange data
    with TCP client.

    """

    def handle(self):
        # self.request - TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} sent:".format(self.client_address[0]))
        print(self.data)
        # just send back ACK for data arrival confirmation
        self.request.sendall("ACK from TCP Server".encode())
        
        
    
    
if __name__ == '__main__':
    ptf = ProcessingTimesFinder('processing_times_table.csv')
    
    HOST, PORT = "172.20.66.102", 65432 # change the port according to the needs

    # Init the TCP server object, bind it to the localhost on 9999 port
    tcp_server = socketserver.TCPServer((HOST, PORT), Handler_TCPServer)

    # Activate the TCP server.
    # To abort the TCP server, press Ctrl-C.
    tcp_server.serve_forever()
    
    RFID = 1
    estim_processing_time = ptf.get_est_proc_time(RFID, 10)
    
    
