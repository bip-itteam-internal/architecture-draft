## Description

*This database kept record of attendance from employees, therefore this need reference link into employee data and their work schedule to assign proper status, based on this [employee schedule and shift details](https://docs.google.com/document/d/1W0MOCEPyoodp_09atBVe_PGDhSaoMgfxN2SCvpMVyHY/edit?tab=t.0)*

## Features

- **(Complete)** Automated attendance data creation based on employee shift with cron job 2 hours prior before their shift began
- **(Complete)** Employee get their newest attendance data sorted from datetime and their proper shift
- **(Complete)** Employee self-service to clock-in and clock-out endpoint (limited to modifing the entry, no creation needed)
- **(Complete)** Employee can see their work schedules in the current month, including holiday that being set by HRIS in calendar (low priority)
- Send out FCM notification to device to remind them of their work schedules
- HRIS additional forced flagging and document insertion to the entries (low priority)

## Cron Scheduler

Cron schedule play a vital role in thiss daatabase system, as it is the one responsible for attendance data creation based on work schedule of the employee, this system/engine is already automated running for each 30mins

Information that is essential for cron scheduler:
1. Company work schedule (Static collection) 
2. Company group rotation (Static collection) 
3. Company holiday (set by HRIS)
4. Work schedule (fetched from employee database)

Minor information used by FCM notification:
1. Active FCM token (fetched from employee database)

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

Read more below in **Company Group Rotation** for data structures and features needed to support shift/group-based schedules

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

### Attendance Entries

``` JSON  
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"employee_id": "0032-03-27102025", // Natural keys (FK)
	
	"date": ISODate(),
	"clock_in": Timestamp,
	"clock_out": Timestamp,
	
	"date_realtime": ISODate(), // This is going to be the sort mechanism for managing realtime attendance, this will be updated on status changes
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
// Actual based takes for off-duty employee, don't question this decision..
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "OFF-DUTY", // Natural keys (PK)
	"schedule": {
		"monday":    null,
		"tuesday":   null,
		"wednesday": null,
		"thursday":  null,
		"friday":    null,
		"saturday":  null,
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
		"sunday":    {"start": "05:00", "end": "13:00"}
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
		"sunday":    {"start": "13:00", "end": "21:00"}
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "HOSTLIVE-SHIFT-C", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "21:00", "end": "05:00"},
		"tuesday":   {"start": "21:00", "end": "05:00"},
		"wednesday": {"start": "21:00", "end": "05:00"},
		"thursday":  {"start": "21:00", "end": "05:00"},
		"friday":    {"start": "21:00", "end": "05:00"},
		"saturday":  {"start": "21:00", "end": "05:00"},
		"sunday":    {"start": "21:00", "end": "05:00"}
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
		"sunday":    {"start": "07:00", "end": "19:00"}
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
		"sunday":    {"start": "19:00", "end": "07:00"}
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

### Company Group Rotation

This information is required as we need to change the group shift rotation or rolling shift accordingly, which mean some employee aren;t bounded to their schedule but to their group-schedule instead, which will be annoying to deal with...

1. **Host live groups**, rotated per-week basis, with 4 groups total (3 active work and 1 offwork group at any given week) 
	- **Array structures:** A, B, C, null
	- **Index changes:** 7 days
2. **Security groups**, rotated per-self completion, with 3 groups total (2 active work and 1 offwork group at any given day)
	- **Array structures:** A, B, null
	- **Index changes:** array completion and reset into the first index

Therefore we will need 1 helper function to be aware on this difference in static-based employee schedules and the shift/group-based (or whatever name it yourself) schedules and pass it into resolver function for date/attendance pickup or lookup

Also as this shift/group-based have differances in resolving themself, one is changed statically based on time and the other is based on their own completion, then we will have 2 resolver function

```JSON
// Host-live rolling schedules
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	
	"group_id": "HOSTLIVE-GROUP-1",
	"schedule_rotation": [
		"HOSTLIVE-SHIFT-A", 
		"HOSTLIVE-SHIFT-B", 
		"HOSTLIVE-SHIFT-C", 
		"OFF-DUTY"
	],
	"schedule_rotated_in_x_days": 7,
	
	"starting_date": ISODate(),
	"starting_schedule": "HOSTLIVE-SHIFT-A",
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	
	"group_id": "HOSTLIVE-GROUP-2",
	"schedule_rotation": [
		"HOSTLIVE-SHIFT-A", 
		"HOSTLIVE-SHIFT-B", 
		"HOSTLIVE-SHIFT-C", 
		"OFF-DUTY"
	],
	"schedule_rotated_in_x_days": 7,
	
	"starting_date": ISODate(),
	"starting_schedule": "HOSTLIVE-SHIFT-B",
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	
	"group_id": "HOSTLIVE-GROUP-3",
	"schedule_rotation": [
		"HOSTLIVE-SHIFT-A", 
		"HOSTLIVE-SHIFT-B", 
		"HOSTLIVE-SHIFT-C", 
		"OFF-DUTY"
	],
	"schedule_rotation_days": 7,
	
	"starting_date": ISODate(),
	"starting_schedule": "HOSTLIVE-SHIFT-C",
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	
	"group_id": "HOSTLIVE-GROUP-4",
	"schedule_rotation": [
		"HOSTLIVE-SHIFT-A",
		"HOSTLIVE-SHIFT-B", 
		"HOSTLIVE-SHIFT-C", 
		"OFF-DUTY"
	],
	"schedule_rotated_in_x_days": 7,
	
	"starting_date": ISODate(),
	"starting_schedule": null,
},

// Security rolling schedules
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	
	"group_id": "SECURITY-GROUP-1",
	"schedule_rotation": ["SECURITY-SHIFT-A", "SECURITY-SHIFT-B", "OFF-DUTY"],
	"schedule_rotated_in_x_days": 1,
	
	"starting_schedule": "SECURITY-SHIFT-A",
	"starting_date": ISODate(),
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	
	"group_id": "SECURITY-GROUP-2",
	"schedule_rotation": ["SECURITY-SHIFT-A", "SECURITY-SHIFT-B", "OFF-DUTY"],
	"schedule_rotated_in_x_days": 1,
	
	"starting_date": ISODate(),
	"starting_schedule": "SECURITY-SHIFT-B",
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	
	"group_id": "SECURITY-GROUP-3",
	"schedule_rotation": ["SECURITY-SHIFT-A", "SECURITY-SHIFT-B", "OFF-DUTY"],
	"schedule_rotated_in_x_days": 1,
	
	"starting_date": ISODate(),
	"starting_schedule": null,
}

// Production rolling schedules
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"group_id": "PRODUCTION-GROUP-1",
	"schedule_rotation": [
	   "PRODUCTION-SHIFT-A", 
	   "PRODUCTION-SHIFT-C", 
	   "PRODUCTION-SHIFT-B"
	],
	schedule_rotated_in_x_days: 7,
	starting_date: ISODate(),
	starting_schedule: "PRODUCTION-SHIFT-A"
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"group_id": "PRODUCTION-GROUP-2",
	"schedule_rotation": [
	   "PRODUCTION-SHIFT-A", 
	   "PRODUCTION-SHIFT-C", 
	   "PRODUCTION-SHIFT-B"
	],
	schedule_rotated_in_x_days: 7,
	starting_date: ISODate(),
	starting_schedule: "PRODUCTION-SHIFT-C"
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"group_id": "PRODUCTION-GROUP-3",
	"schedule_rotation": [
	   "PRODUCTION-SHIFT-A", 
	   "PRODUCTION-SHIFT-C", 
	   "PRODUCTION-SHIFT-B"
	],
	schedule_rotated_in_x_days: 7,
	starting_date: ISODate(),
	starting_schedule: "PRODUCTION-SHIFT-B"
},
 
// Warehouse rolling schedules
// This is still wrong as there is 3 groups and 2 groups will be at shift A at any given time, which mean we should ref by index instead of string to the array
 {
	"_id": ObjectId(MongoDB_ID_Assignment),
	"group_id": "WAREHOUSE-GROUP-1",
	"schedule_rotation": [
	   "WAREHOUSE-SHIFT-A", 
	   "WAREHOUSE-SHIFT-A", 
	   "WAREHOUSE-SHIFT-B"
	],
	schedule_rotated_in_x_days: 7,
	starting_date: ISODate(),
	starting_schedule: "WAREHOUSE-SHIFT-A"
},
 {
	"_id": ObjectId(MongoDB_ID_Assignment),
	"group_id": "WAREHOUSE-GROUP-2",
	"schedule_rotation": [
	   "WAREHOUSE-SHIFT-A", 
	   "WAREHOUSE-SHIFT-A", 
	   "WAREHOUSE-SHIFT-B"
	],
	schedule_rotated_in_x_days: 7,
	starting_date: ISODate(),
	starting_schedule: "WAREHOUSE-SHIFT-B"
},
```

### Company Holiday Date

```JSON
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	
	"date": ISODate(),
	"note": "additional notes regarding the holiday" // String normal inserted
}
```
