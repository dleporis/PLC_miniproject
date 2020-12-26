VAR_GLOBAL
	

	///////////////////////////
	// Inputs
	///////////////////////////
	
	xBG20		AT %IX1.0	: BOOL;	// Stopper released
	xBG21		AT %IX1.1	: BOOL;	// Carrier available
	xBG22		AT %IX1.2	: BOOL;	// Carrier ID bit 0
	xBG23		AT %IX1.3	: BOOL;	// Carrier ID bit 1
	xBG24		AT %IX1.4	: BOOL;	// Carrier ID bit 2
	xEmg		AT %IX0.0	: BOOL;	// Emergency stop
	
	///////////////////////////
	// Outputs
	///////////////////////////	
	
	xMB20		AT %QX1.0	: BOOL;	// Release stopper
	xQA1_LEFT	AT %QX0.5	: BOOL;	// Conveyor to the left
	xQA1_RIGHT	AT %QX0.4	: BOOL;	// Conveyor to the right
	xQA1_SLOW	AT %QX0.6	: BOOL;	// Conveyor Slow
	xQA1_STOP	AT %QX0.7	: BOOL;	// Conveyor Stop
	
	
END_VAR
