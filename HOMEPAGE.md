## Notices

*Everything in here is is a quick overview and a rough idea on how the system looks like and how it interact with one another, this required more open discussion together*

## What is CORE System?

CORE system are basically Databases with API endpoints that accommodate required access to other system, need more discussion on this as well

This database will be partitioned from the CORE - Employee Master Data to others CORE system with foreign keys

### Consideration

- What kind of database to use
	- Multiple database for each CORE system (NoSQL)
		- NoSQL database mean everything is flexible
		- Reroute and role assignment on each system would be easier
		- Clear differentiation between CORE system
		- Other system still able to function if their dependencies are met
		- Foreign keys connection need to be carried out manually by back-end for example: CORE - Employee Master Data as Single Source of Truth, which means any inconsistency will be discarded and return as error
	- Single database with multiple table representing each CORE system
		- SQL database mean everything is strict
		- Replication and backup is easier compare to multiple databases
- To have 1 read/write database and 2 read-only database (for each database)
- Database replicate for daily/hourly backups
- Database redundancy if required so failed access into the main could be redirected to alternative active database (low-priority as this is quite tricky to implement)

## What is BASE System?

BASE system are base landing page and authentication for users to be able to use said system, by default the BASE system are empty, but will be filled with features by time

## System Creation Sequence

This is still an assumption/prediction and required further confirmation

| Seq. | System Name                  | Status   |
| ---- | ---------------------------- | -------- |
| 1    | CORE - Employees Master Data | Drafting |
| 2    | CORE - System Authentication | Drafting |
| 3    | HRIS - BASE System           | ...      |
| 4    | HRIS - Attendance System     | ...      |
| ...  | ...                          | ...      |

### About system lists, priorities and technical architectures

Below this will be system list and their priority, so we can aim to create the core system and dependencies that is required to create the other system

Technical architecture of the said system will be discussed later on in details

## Examples

### Example case

Employee wanted to login into HRIS system and access their attendance view

1. Go and login the main company application portal (not discussed or mention yet in this draft documents)
2. Select go into HRIS
3. Select attendance feature and click view my attendance options

![[usecase-example.png]]

Main portal will accommodate as the HUB of the application to other systems

### Example request

This is type of request that we will probably have 
1. Single-fetch database request
	- This is where you fetch single database information, normal and straight forward
2. Multi-fetch database request
	- This is where you fetch 2 or more database, middle-ware has to make sure all fetch are successful and return processed or cleaned version of the data
- Single-fetch chained/propagate request
	- Request into database endpoints, and that endpoint will chain/propagate to another required database as cross-validation for example and cleaning the data before returning to the middle-ware

Image example below for (2) and (3) on how the data flow will looks like

![[endpoint-example.png]]