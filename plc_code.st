CASE state OF
	
	0:
	IO.xQA1_RIGHT := TRUE;
	IO.xMB20 := FALSE;
	RFID.ClearError();
	TCPclient.Connect(sIP:='172.20.66.102', uiPort:=65432);
	state := 1;
	
	1: //wait for RFID to clear
	IF RFID.xReady THEN
		RFID.Connect(usiNodeId := 32, usiNetworkId := 0, usiChannel := 1);
		state := 2;
	END_IF
	
	2: //wait for RFID to connect
	IF RFID.xReady THEN
		state := 3;
	END_IF
	
	3: //wait for TCP connect
	IF tcpclient.xConnected AND tcpclient.xReady THEN
		state := 4;
	END_IF
	
	4: //wait for carrier
	IF IO.xBG21 = TRUE THEN
		IO.xMB20 := TRUE;
		state := 5;
	END_IF
	
	5: //read the RFID tag;
	RFID.ReadTag(uiStartAddress:=0,uiDataLength:=SIZEOF(rfidData), pData:=ADR(rfidData));
	state := 6;
	
	6: //wait for RFID read
	IF RFID.xReady THEN
		IF rfidData.uiCarrierID > 8 THEN
			//TCPclient.Send(pToSend:=ADR(rfidData.uiCarrierID), uiSizeToSend:=SIZEOF(rfidData.uiCarrierID));
			state := 7;
		END_IF
	END_IF
	
	7: //wait for send
	IF TCPclient.xReady THEN
		//TCPclient.Receive(pToReceive:=ADR(rfidData.uiCarrierID), uiSizeToReceive:=SIZEOF(rfidData.uiCarrierID));
		TCPclient.Send(pToSend:=ADR(rfidData.uiCarrierID), uiSizeToSend:=SIZEOF(rfidData.uiCarrierID));
		state := 8;
	END_IF
	
	//8: //wait to receive
	//IF TCPclient.xReady THEN
	//	//PROCESS DATA RECEIVED HERE!
	//	IO.xMB20 := TRUE;
	//	state := 9;
	//END_IF
	
	8: //wait for carrier to pass
	IF IO.xBG21 = FALSE THEN
		IO.xMB20 := FALSE;
		TCPclient.Receive(pToReceive:=ADR(dataIn), uiSizeToReceive:=SIZEOF(dataIn));
		state := 1;
	END_IF
	
	//10: //release pallet 1-8
	//IO.xMB20 := TRUE;
	//state := 30;
	
	//20: //release pallet 9-16
	//timer(IN:=TRUE, pt:=T#2S);
	//state := 21;
	
	//21: //wait for timer
	//IF timer.Q THEN
	//	IO.xMB20 := TRUE;
	//	state := 30;
	//END_IF
	//30: //wait for carrier to pass`	
	//IF IO.xBG21 = FALSE THEN
	//	IO.xMB20 := FALSE;
	//	state := 4;
	//END_IF
END_CASE
TCPclient();
RFID();
