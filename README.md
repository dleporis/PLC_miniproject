# PLC_miniproject
Mini project description
Create two programs:

* A PLC program (TCP client) that controls the physical system
* A PC program (TCP server) that monitors the behavior of the physical system. The programming language is arbitrary.

The programs must perform the following operations:

- [ ] Read the pallet RFID tag when a pallet moves to the module you are working on
      (we are not sure if our functionality currently fullfills this)
- [ ] Send the RFID info to a PC via TCP/IP as an XML-encoded string (TODO)
- [ ] The PC program shall decode the information and display the relevant information on screen during program execution
- [ ] The PC program shall return an estimated processing time to the PLC via TCP/IP (check the .csv according to the RFID tag)
- [ ] The PLC shall simulate the physical processing time by letting the pallet wait for the returned time.
- [ ] The decoded data shall be stored in a file on the PC, so that it can be analyzed later.

The "estimated processing time" is given a priori as a CSV-file (see under PLC-workshop lecture) and will have to be read into memory before realtime execution on the PC,.
- [x] estimated processing time.CSV is loaded
- [ ] get the estimated processing time of a specific carrier-process_station combination whenever needed

In the mini-project you are allowed to design and develop your code as a group, but it shall be documented in a small, individual report, containing:

* Background for the project (description of the hardware, software, etc.)
* Description and documentation of your solution
* A brief discussion where the project is related to modern manufacturing systems (MES, ERP, PLC's, etc.)

The report may not exceed 6 pages. It will be used as a basis for the oral examination, and must therefore be uploaded to Digital Eksamen individually by each student no later than January 3rd. 
