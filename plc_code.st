CASE state OF

	0: // initialization
		IO.xQA1_RIGHT := TRUE; // make the conveyor run
		IO.xQA1_SLOW := FALSE; // the conveyor moves fast
		IO.xMB20 := FALSE; // the piston engaging stopper release is inactive
		state := 1; // move to state 1

	1: // wait for carrier to approach, and slow down the conveyor
		IF IO.xBG24 = TRUE THEN // the carier approaches, sensor activated
			IO.xQA1_SLOW = TRUE; // slow down the conveyor
			state := 2;
		END_IF

	2: // wait for carrier to arrive to stopper
		IF IO.xBG21 = TRUE THEN // the carier arrived
			state := 3;
		END_IF

	3: // initialization of timer
		timer(IN := TRUE, PT := T#2S);
		state := 4;

	4: // wait for the timer, then release the carrier
		IF timer.Q = TRUE THEN
			timer(IN := FALSE); // reset the timer
			IO.xMB20 := TRUE; // engage the stopper piston, thus releasing the carrier
			state := 5;
		END_IF

	5: // wait for the carrier to pass
		IF IO.xBG21 = FALSE THEN // the carrier left
			state := 6;
		END_IF

	6: // initialization of timer
		timer(IN := TRUE, PT := T#2S);
		state := 7;

	7: // wait for the timer, then put the stopper back in place
		IF timer.Q = TRUE THEN
			timer(IN := FALSE); // reset the timer
			IO.xMB20 := FALSE; // disengage the stopper piston, thus keeping it in a stop position
			IO.xQA1_SLOW = FALSE; // speed up the conveyor
			state := 1;
		END_IF
END_CASE
timer();


CASE state OF

	0: //init
	IO.xQA1_RIGHT:=TRUE;
	//IO.xQA1_SLOW:=FALSE;
	IO.xMB20:=FALSE;
	RFID.ClearError();
	state := 1;

	1:
	IF RFID.xReady THEN
		RFID.Connect();
		state := 2;
	END_IF

	2:
	IF RFID.xReady AND RFID.xConnected THEN
		state := 3;
	END_IF

	3:
	IF IO.xBG21 = TRUE THEN
		IO.xMB20:=TRUE;
		state := 4; //activates the timer
	END_IF

	//2: // stop and release the tray when it arrived
	//IF IO.xBG21 = TRUE THEN
		//insert the timer here
		//IO.xMB20 := TRUE;
		//state := 3;
	//END_IF

	//2:
	//timer(IN:=TRUE, PT:=T#2S);
	////IO.xMB20:=TRUE;
	//state:= 3;

	//3: // wait for the tray to leave and speed up
	//IF IO.xBG21 = FALSE THEN
		//IO.xMB20 := FALSE;
		//IO.xQA1_SLOW:=FALSE;
		//state := 1;
	//END_IF
	4:
	RFID.ReadTag(uiStartAddress := 0, uiDataLenght := SIZEOF(rfidData), ADR(rfidData));
		state := 5;

	5:
	IF RFID.xReady THEN
		IF rfidData.uiCarrierID <= 8 THEN
			state := 10;
		ELSE
			state := 20;
		END_IF
	END_IF

	10:
	IO.xMB20 := TRUE;
	state := 30;

	20:
	timer(IN:= TRUE, PT := T#2S);
	state := 21;

	21:
	IF timer.Q THEN
		io.xMB20 := TRUE;
		state := 30;
	END_IF
	30:
	IF IO.xBG21 = FALSE THEN
		IO.xMB20 := FALSE;
		state := 3;
	END_IF

END_CASE
timer();
RFID();
