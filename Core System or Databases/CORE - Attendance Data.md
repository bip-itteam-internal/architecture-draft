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

- Work hour calculation for Payroll system
	- Normal working hour
	- Overtime working hour

## Dependencies

- [ ] [[CORE - Employees Master Data]]