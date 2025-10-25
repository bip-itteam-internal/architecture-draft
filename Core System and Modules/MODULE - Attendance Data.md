## Description

*This database kept record of attendance from employees, therefore this need reference link into employee data and their work schedule to assign proper status*

## Data Structures

*All data below need to be rechecked and reconfirmed*

- Employee ID (reference)
- Attendance date (this entry has to be created automatically each day)
	- Clock-in timestamp
	- Clock-out timestamp
- Status (example: on-time, late, alpha, sick, vacation, holiday)
	- Automated system check for on-time, late and alpha
	- Manual flagging from HRD for sick, vacation, holiday, etc
		- This manual flags will invalidate all information below
- Automated leave hour
	- Calculated automatically if late (starting hour - clock-in hour)
- Leave hour
	- Adjustment by HRD if the employee able to leave the job for X hour, this required additional documents as verification
- Overtime hour
	- Adjustment by HRD if the employee working X hour overtime, this required additional document as verification

### Consideration

- Clock-in/out limitation by Wifi MAC Address, since we want to limit from where the employee can clock-in/out (handled by front-end)
	- Why MAC Address and not just SSID? Since SSID can easily be replicated with Hotspot, but not with MAC Address which would be harder to do
	- But is this viable? As this access into MAC Address would be categozied into sensitive details under normal circumstances
- Work hour calculation for Payroll system
	- Normal working hour
	- Overtime working hour

## Database Structures

We have our own independent database exclusively for attendance

### Attendance Data

``` JSON  
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"employee_id": "0032-03-27102025", // Natural keys (FK)
	
	"date": ISODate(),
	"clock_in": Timestamp,
	"clock_out": Timestamp,
	
	"status": "on-time", // Enums to string
	
	"late_hour": 0, // Decrement to normal working hour
	"leave_hour": 2, // Decrement to normal working hour	
	"overtime_hour": 2,
	
	// Do we need to set normal working hour that will be used for payroll right now? If so then add the normal working hour but this need to be check into the 'work_data' or said employee id and into 'company_work_schedule' collection to get how long does they work for the day
	// We need a better way to deal with this issues later on (this is required for payroll calculation)
	
	"documents": [ // Easily expandable if needed
		{ // The type is important as this will be the one being used as 'search' or lookup into the specifict documents
			"type": "leave_document",
			"filename": "aurelia_mara_leave.jpg",
			"file_data": BinData(0, "<binary data>"), 
		},
		{
			"type": "overtime_document",
			"filename": "aurelia_mara_overtime.jpg",
			"file_data": BinData(0, "<binary data>"), 
		},
	]
}
```