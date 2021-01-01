PROGRAM PLC_PRG
VAR
	state 			:   DINT := 0;
	stationID		:	UINT:= 9;
	TCPclient		:	dc_ecp.TcpClientByteStream;
	timer			:	TON;
	RFID			:	dc_ecp.Dtm425;
	rfidData		:	dc_ecp.st_CPF_RfidData;
	carrierID		:	UINT;
	wait_var		:	INT;
	send_xml_wstring	:	WSTRING;
	send_xml_string	:	STRING;
	wait_wstring: WSTRING;
	wait_string: STRING;
	send_xml_string_length : DINT;	// double int
	pstData: INT;
	dateandtime: DTU.GetDateAndTime;
	StrLenA: INT;
	time_stamp: DATE_AND_TIME;
	str_length: UINT;
	headersize: UINT := 10;
	length_length: UINT;
	wstring_mode: BOOL := FALSE;
	input : WORD;
	realitime: WORD;
END_VAR
