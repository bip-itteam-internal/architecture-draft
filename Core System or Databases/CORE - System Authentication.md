## Description

*This is the system authentication that will respond back result status, this will hold 1 database for each base system to store employees reference, their role and password in their system respectively*

*Creation of single middle-ware that could be rerouted to all system authentication based on their current system would be beneficial to the whole system as managing it will be easier and centralized*
## Consideration

- Multiple databases for each base system VS single database for all
	- Multiple databases will make the reroute and make the role assignment easier
	- Single database would make the replicate and backup easier

## Requirements

- [ ] Database to hold system authentication data for each base system
	- Employee ID (reference)
	- Role in their system
	- Password and additional authentication if necessary
- [ ] Centralized middle-ware

## Dependencies

- [ ] [[CORE - Employees Master Data]]