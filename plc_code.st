PROGRAM PLC_PRG
VAR
	state			:	INT := 0;
	stationID		:	UINT:= 12;
	TCPclient		:	DC_ECP.TcpClientByteStream;
	timer			:	TON;
	RFID			:	dc_ecp.Dtm425;
	rfidData		:	dc_ecp.st_CPF_RfidData;
	carrierID		:	UINT;
	wait_var		:	TIME := TIME#1s0ms;
	junction		:	WSTRING := 'left';
	send_xml_string	:	WSTRING;
	wait_string: WSTRING;
	send_xml_string_length : DINT;	// double int
	pstData: INT;
END_VAR	

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
	IO.xQA1_LEFT := TRUE; // make the conveyor going to the left run
	
	IO.xMB20 := FALSE; // stopper not released
	RFID.ClearError(); // clear the RFID sensor memory
	TCPclient.Connect(sIP:='172.20.66.102', uiPort:=65432); // connect to the Server on PC
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
	IF IO.xBG22 = TRUE THEN
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
		// todo format the XML string, insert the timestamp, stationID and carrierID.
		// formatting of the time in s ms according to the estimated processing time
		// delimitation of messages, in python we have a header with a string length
		//xml server response parsing
		
		send_xml_string := "<arrival><timestamp>timestamp</timestamp><station><ID>10</ID></station><carrier><RFID>1</RFID></carrier></arrival>";
		send_xml_string := stu.StrConcatA(pstFrom:= send_xml_string, pstTo:= send_xml_string, iBufferSize:= 10);
		stu.StrConcatA
		send_xml_string_length := StrLenW(pstData := send_xml_string );
		
		dc_ecp.TcpClientByteStream();
		state := 8;
	END_IF
	
	8: //wait for the tcp being ready, and send the RFID data
	IF TCPclient.xReady THEN
		TCPclient.Send(pToSend:=ADR(rfidData.uiCarrierID), uiSizeToSend:=SIZEOF(rfidData.uiCarrierID));
		state := 9;
	END_IF
	
	9: //wait to receive te server response
	IF TCPclient.xReady THEN
		TCPclient.Receive(pToReceive:=ADR(rfidData.uiCarrierID), uiSizeToReceive:=SIZEOF(rfidData.uiCarrierID));
		
		wait_string := "TIME#1s0ms";
		wait_var := STRING_TO_TIME(wait_string);
		// PROCESS DATA RECEIVED HERE!
		state := 10;
	END_IF

	10: // initialization of timer
		
		timer(IN := TRUE, PT := wait_var); // find how to insert wait time here
		state := 11;
		
	11: // wait for the timer, then release the carrier
	IF timer.Q = TRUE THEN
		timer(IN := FALSE); // reset the timer
		IO.xMB20 := TRUE; // stopper released, releasing the carrier
		IF junction = 'left' THEN
			// switch junction to left
		END_IF
		IF junction = 'right' THEN
			// switch junction to right
		END_IF
		state := 12;
	END_IF
	
	12: //wait for carrier to pass
	IF IO.xBG21 = FALSE THEN
		IO.xMB20 := FALSE; // stopper not released
		state := 1;
	END_IF
	
END_CASE
TCPclient();
RFID();
