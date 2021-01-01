		
	///////////////////////////
	// Inputs
	///////////////////////////
	
	//xBG20		AT %IX1.0	: BOOL;	// Stopper released
	//xBG21		AT %IX1.1	: BOOL;	// Carrier available
	//xBG22		AT %IX1.2	: BOOL;	// Carrier ID bit 0
	//xBG23		AT %IX1.3	: BOOL;	// Carrier ID bit 1
	//xBG24		AT %IX1.4	: BOOL;	// Carrier ID bit 2
	//xEmg		AT %IX0.0	: BOOL;	// Emergency stop
	
	///////////////////////////
	// Outputs
	///////////////////////////	
	
	//xMB20		AT %QX1.0	: BOOL;	// Release stopper
	//xQA1_LEFT	AT %QX0.5	: BOOL;	// Conveyor going to the left
	//xQA1_RIGHT	AT %QX0.4	: BOOL;	// Conveyor going to the right
	//xQA1_SLOW	AT %QX0.6	: BOOL;	// Conveyor Slow
	//xQA1_STOP	AT %QX0.7	: BOOL;	// Conveyor Stop

CASE state OF
	
	0: //initialisation
	IO.xQA1_RIGHT := TRUE; // make the conveyor going to the right run
	// to make a loop

	IO.xMB20 := FALSE; // stopper not released
	RFID.ClearError(); // clear the RFID sensor memory
	TCPclient.Connect(sIP:='172.20.66.48', uiPort:=65431); // connect to the Server on PC
	state := 1;
	
	1: //wait for RFID to clear
	IF RFID.xReady THEN
		RFID.Connect(usiNodeId := 32, usiNetworkId := 0, usiChannel := 1); // connect to the RFID sensor
		state := 2;
	END_IF
	
	2: //wait for RFID to connect
	IF RFID.xReady THEN
		state := 3;
	END_IF
	
	3: //wait for TCP connect
	IF TCPclient.xConnected AND TCPclient.xReady THEN
		state := 4;
	END_IF
	
	4: //wait for carrier to approach
	IF IO.xBG24 = TRUE THEN
		xQA1_SLOW := TRUE; // slow down the conveyor
		state := 5;
	END_IF
	
	5: //wait for carrier to arrive
	IF IO.xBG21 = TRUE THEN
		xQA1_SLOW := FALSE; // make conveyor fast again
		state := 6;
	END_IF
	
	6: //read the RFID tag
	RFID.ReadTag(uiStartAddress:=0,uiDataLength:=SIZEOF(rfidData), pData:=ADR(rfidData));
	state := 7;
	
	7: //wait for RFID read being finished 
	IF RFID.xReady THEN
		carrierID := rfidData.uiCarrierID;
		// todo format the XML string, insert the timestamp, stationID and carrierID. ok
		// formatting of the time in s ms according to the estimated processing time
		// delimitation of messages, in python we have a header with a string length  
		// xml server response parsing ans: send back the wait time only, no xml
		
		
		state := 8;
	END_IF
	
	8: // make a string to send 
		//time_stamp := dateandtime.dtDateAndTime;
		// problem: it is possible to make only strings 81 char or shorter
		//send_xml_string := "<arrival><station>10</station><carrier>8</carrier></arrival>";
		
		
		
		send_xml_string := dc_ecp.CONCAT('<arrival><station>',UINT_TO_STRING(stationID));
		send_xml_string := dc_ecp.CONCAT(send_xml_string,'</station><carrier>');
		send_xml_string := dc_ecp.CONCAT(send_xml_string,UINT_TO_STRING(carrierID));
		send_xml_string := dc_ecp.CONCAT(send_xml_string,'</carrier></arrival>');
		
		//str_length := SIZEOF(send_xml_string);
		//length_length := SIZEOF(UINT_TO_STRING(str_length));
		//header_size - length_length;
		//send_xml_string := dc_ecp.CONCAT(UINT_TO_STRING(length), send_xml_string);
		//dc_ecp.TcpClientByteStream();
		state := 9;
	
	9: //wait for the tcp being ready, and send the RFID data
	IF TCPclient.xReady THEN
		//TCPclient.SendAndReceive(pToSend:=ADR(send_xml_string), uiSizeToSend:=SIZEOF(send_xml_string), pToReceive:=ADR(wait_string), uiSizeToReceive:=SIZEOF(wait_string));
		IF wstring_mode = TRUE THEN
			send_xml_wstring := STRING_TO_WSTRING(send_xml_string);
			TCPclient.Send(pToSend:=ADR(send_xml_wstring), uiSizeToSend:=SIZEOF(send_xml_wstring));
		ELSE
			TCPclient.Send(pToSend:=ADR(send_xml_string), uiSizeToSend:=SIZEOF(send_xml_string));
		END_IF
		state := 10;
	END_IF
	
	10: //wait to receive te server response
	IF TCPclient.xReady THEN
			TCPclient.Receive(pToReceive:=ADR(input), uiSizeToReceive:= SIZEOF(input);
			realitime := dc_ecp.SwapWORD(input);
			wait_var := WORD_TO_INT(realitime);
			//wait_string := dc_ecp.CONCAT('T#', wait_string);
			//wait_string := dc_ecp.CONCAT(wait_string, 'MS');
			
			//wait_var := STRING_TO_TIME(wait_string);
		// wait_string will be in a format: 'T#4065ms'
		// PROCESS DATA RECEIVED HERE!
		state := 11;
	END_IF

	11: // initialization of timer
		
		timer(IN := TRUE, PT := INT_TO_TIME(wait_var));
		state := 12;
		
	12: // wait for the timer, then release the carrier
	IF timer.Q = TRUE THEN
		timer(IN := FALSE); // reset the timer
		IO.xMB20 := TRUE; // stopper released, releasing the carrier
		state := 13;
	END_IF
	
	13: //wait for carrier to pass
	IF IO.xBG21 = FALSE THEN
		IO.xMB20 := FALSE; // stopper not released
		state := 1;
	END_IF
	
END_CASE
RFID();
timer();
TCPclient();
