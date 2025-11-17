## Description

*This dashboard will help Human Resource to manage employees from the start to end of their careers on this company*

[Example of this system](https://docs.google.com/spreadsheets/d/14dDRxTWME4N4-TY42BPZFFaXYQOTTZxV/edit?gid=1164498077#gid=1164498077)

## Features

-  Task tracker (on all subsystems)
	- Overview of everything that include current, ongoing and finished analysis
	- This task might ended sooner than expected
- Dashboard
	- Overview of everything excellent for reporting to stakeholders
- Details
	- View of attrition in details viewed per departments
- Demographics
	- Information in details regarding termination gender, type and reasons (additional easy lookup for departure per departments)

## Subsystems

- Talent acquisition
- Interview
	- This is per-person
	- This is byproduct from talent acquisition which mean this could have multiple entry at once
	- Link this information to talent acquisition
- On-boarding
	- This is per-person
	- Might close ongoing talent acquisition is needed
- Retention
	- In motion at fixed-time possibly per-month
- Remote management (Currently deactivated)
- Work review
	- In motion at fixed-time possibly per-month
- Conflict management
	- Link to employees, one conflict might link to more than one employees
- Off-boarding
	- Return of company's assets (check listed assets under employees master data)
	- Administration clearance (check into Finance department)
	- Account deactivation (check into IT department)

## Requirements

- [ ] Task tracker creation based on subsystems
	- The flows of all segments are static documents
- [ ] Employees master data (look up reference)
- [ ] Employee current assets lists
- [ ] Employee administration clearance
- [ ] Employee account status

## Dependencies

- [ ] [[BASE - Landing Page]]
- [ ] [[[...] - Internal Inventory]]
	- This is required for on-boarding, remote management and off-boarding
- [ ] [[GA - Dynamic Task Tracker]]
