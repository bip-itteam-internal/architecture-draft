## Description

*This database kept record of attendance from employees, therefore this need reference link into employee data and their work schedule to assign proper status, based on this [employee schedule and shift details](https://docs.google.com/document/d/1W0MOCEPyoodp_09atBVe_PGDhSaoMgfxN2SCvpMVyHY/edit?tab=t.0)*

## Features

- Automated attendance data creation based on employee shift with cron job 2 hours prior before their shift began
- Employee get their newest attendance data sorted from datetime and their proper shift
- Employee self-service to clock-in and clock-out endpoint (limited to modifing the entry, no creation needed)
- Employee can see then is the national holiday set by HRIS
- Employee can see their work schedules in yearly calendar (low priority)
- HRIS additional forced flagging and document insertion to the entries (low priority)

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
- Attendance for employee that are inside rolling shift should have additional information on their employee work schedule, and we need some function resolvement to get their proper work schedule, since it is dynamics
	- Rolling shift changed per-week basis like Host live schedule
	- Rolling shift change per-self repetition basis like Security schedule with 2 day work and 1 day off, repetition disregarding anything else 

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

### Company Work Schedule

```JSON
{ // Company work schedule collections (This is bad, but will do for now)
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "BIP-REGULAR", // Natural keys (PK)	

	// Below are bad since what if it has this and that exception? If so then this need to write the exception and explain it before passing into front-end
	// "work_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
	// "work_hours": { "start": "09:00", "end": "17:00" },

	// This is better in structures, but still yikes also this can be change to array if necessary
	"schedule": {
		"monday":    {"start": "08:00", "end": "17:00"},
		"tuesday":   {"start": "08:00", "end": "17:00"},
		"wednesday": {"start": "08:00", "end": "17:00"},
		"thursday":  {"start": "08:00", "end": "17:00"},
		"friday":    {"start": "08:00", "end": "17:00"},
		"saturday":  {"start": "08:00", "end": "13:00"}, // 5 hours
		"sunday":    null
	}
},
// Below are for Office boy
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "OFFICEBOY-REGULAR", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "06:30", "end": "17:00"},
		"tuesday":   {"start": "06:30", "end": "17:00"},
		"wednesday": {"start": "06:30", "end": "17:00"},
		"thursday":  {"start": "06:30", "end": "17:00"},
		"friday":    {"start": "06:30", "end": "17:00"},
		"saturday":  {"start": "06:30", "end": "14:00"}, // 5 hours
		"sunday":    null
	}
},
// Below are shift for Host Live
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "HOSTLIVE-SHIFT-A", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "05:00", "end": "13:00"},
		"tuesday":   {"start": "05:00", "end": "13:00"},
		"wednesday": {"start": "05:00", "end": "13:00"},
		"thursday":  {"start": "05:00", "end": "13:00"},
		"friday":    {"start": "05:00", "end": "13:00"},
		"saturday":  {"start": "05:00", "end": "13:00"},
		"sunday":    null
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "HOSTLIVE-SHIFT-B", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "13:00", "end": "21:00"},
		"tuesday":   {"start": "13:00", "end": "21:00"},
		"wednesday": {"start": "13:00", "end": "21:00"},
		"thursday":  {"start": "13:00", "end": "21:00"},
		"friday":    {"start": "13:00", "end": "21:00"},
		"saturday":  {"start": "13:00", "end": "21:00"},
		"sunday":    null
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "HOSTLIVE-SHIFT-C", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "17:00", "end": "01:00"},
		"tuesday":   {"start": "17:00", "end": "01:00"},
		"wednesday": {"start": "17:00", "end": "01:00"},
		"thursday":  {"start": "17:00", "end": "01:00"},
		"friday":    {"start": "17:00", "end": "01:00"},
		"saturday":  {"start": "17:00", "end": "01:00"},
		"sunday":    null
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "HOSTLIVE-SHIFT-D", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "01:00", "end": "09:00"},
		"tuesday":   {"start": "01:00", "end": "09:00"},
		"wednesday": {"start": "01:00", "end": "09:00"},
		"thursday":  {"start": "01:00", "end": "09:00"},
		"friday":    {"start": "01:00", "end": "09:00"},
		"saturday":  {"start": "01:00", "end": "09:00"},
		"sunday":    null
	}
},
// Below are shift for Security
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "SECURITY-SHIFT-A", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "07:00", "end": "19:00"},
		"tuesday":   {"start": "07:00", "end": "19:00"},
		"wednesday": {"start": "07:00", "end": "19:00"},
		"thursday":  {"start": "07:00", "end": "19:00"},
		"friday":    {"start": "07:00", "end": "19:00"},
		"saturday":  {"start": "07:00", "end": "19:00"},
		"sunday":    null
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "SECURITY-SHIFT-B", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "19:00", "end": "07:00"},
		"tuesday":   {"start": "19:00", "end": "07:00"},
		"wednesday": {"start": "19:00", "end": "07:00"},
		"thursday":  {"start": "19:00", "end": "07:00"},
		"friday":    {"start": "19:00", "end": "07:00"},
		"saturday":  {"start": "19:00", "end": "07:00"},
		"sunday":    null
	}
},
// Below are for Production
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "PRODUCTION-SHIFT-A", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "08:00", "end": "16:00"},
		"tuesday":   {"start": "08:00", "end": "16:00"},
		"wednesday": {"start": "08:00", "end": "16:00"},
		"thursday":  {"start": "08:00", "end": "16:00"},
		"friday":    {"start": "08:00", "end": "16:00"},
		"saturday":  {"start": "08:00", "end": "13:00"}, // 5 hours
		"sunday":    null
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "PRODUCTION-SHIFT-B", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "16:00", "end": "00:00"},
		"tuesday":   {"start": "16:00", "end": "00:00"},
		"wednesday": {"start": "16:00", "end": "00:00"},
		"thursday":  {"start": "16:00", "end": "00:00"},
		"friday":    {"start": "16:00", "end": "00:00"},
		"saturday":  {"start": "16:00", "end": "21:00"}, // 5 hours
		"sunday":    null
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "PRODUCTION-SHIFT-C", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "00:00", "end": "08:00"},
		"tuesday":   {"start": "00:00", "end": "08:00"},
		"wednesday": {"start": "00:00", "end": "08:00"},
		"thursday":  {"start": "00:00", "end": "08:00"},
		"friday":    {"start": "00:00", "end": "08:00"},
		"saturday":  {"start": "00:00", "end": "05:00"}, // 5 hours
		"sunday":    null
	}
},
// Below are for Inventory
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "INVENTORY-SHIFT-A", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "08:00", "end": "16:00"},
		"tuesday":   {"start": "08:00", "end": "16:00"},
		"wednesday": {"start": "08:00", "end": "16:00"},
		"thursday":  {"start": "08:00", "end": "16:00"},
		"friday":    {"start": "08:00", "end": "16:00"},
		"saturday":  {"start": "08:00", "end": "13:00"}, // 5 hours
		"sunday":    null
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "INVENTORY-SHIFT-B", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "16:00", "end": "00:00"},
		"tuesday":   {"start": "16:00", "end": "00:00"},
		"wednesday": {"start": "16:00", "end": "00:00"},
		"thursday":  {"start": "16:00", "end": "00:00"},
		"friday":    {"start": "16:00", "end": "00:00"},
		"saturday":  {"start": "16:00", "end": "21:00"}, // 5 hours
		"sunday":    null
	}
}
```