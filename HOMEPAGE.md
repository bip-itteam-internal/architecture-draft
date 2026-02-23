## Notices

*Everything in here is is a quick overview and a rough idea on how the system looks like and how it interact with one another, this required more open discussion together*

## What is ERP system looks like?

Currently everything are still in mono repository, this will be moved out with git submodules down the line when it sees fit

Interaction between the services can be interpreted like image below
![[erp-request-nutshell.png]]

### What does the API Gateway do?

It is our entry point for request, which also handle JWT authentication and routes check for open/restricted routes propagation

### What does the Orchestrator do?

Orchestrator is basically our wrapper for event-based action, for example some request might required to call 2 different services, this system will do it for you for processing required data to do so

The orchestrator we currently have are: **HRIS** and **IT**

### What does the Service do?

Service are the end-point that interact and connected with their own databases, this ensure the easy way of developing certain services, and if its ended up broken it is fine, since only said service are affected

We have 2 type of services:
- **Open route services** - request can be made from outsite and required access/service keys, if the keys aren't provided it will fallback using JWT authentication
- **Restricted services** - request must be validated using JWT authentication

## Type of Requests

There is total of 3 type of request for ERP system, where it is numbered as well, explained below:

1. **Direct request to services** - Where you request something directly to the services, example `/api/employee/status` or `/api/file/preview`

2. **Request to orchestrator** - Where you request to orchestrator to do business action to the various system, example `/api/hris/employee/create` where it will create the said employee data to the `employee-service` and upload the files to `file-service` and update the newest schedule to `attendance-service`

3. **Direct request to services that dependand to another services** - This is moving into dangerous territory, where the action is vague and unclear since that is internal service-to-service calls. This is fine as long as it is not critical, example `/api/attendance/team-today?department=X` will fetch employees data based on department to `/api/employee-list` and use that information to get latest entry of that department employee attendance. **If you create this request and the flow are confusing then it means it is time move it to orchestrator**

## Glances to the Repository structure

Below are glances to the code repository with notes on it

```
├── .env (Everything in here, need to sort this out)
├── docker-compose.yml (Main entry point and duct tape for all services)
├── Makefile (Shorten common commands, ask Pero about this)
│
├── api-gateway (Manages authenticcation and routes to existing services)
│
├── orchestrator (Manages request for multiple services at once)
│   ├── hris
│   └── it
│
├── services (ERP services, some are restricted other are open)
│   ├── attendance (Restricted)
│   ├── employee (Restricted)
│   ├── file (Open-routes and restricted)
│   └── notification (Open-routes and restricted)
│
└── shared-library (All things point into shared-library to not declare something twice, this is out duct tape for all the services. Need to move this into proper go include if needed)
    │
	├── auth (JWT authentication)
    ├── database (Currently exclusive to MongoDB)
    ├── routes (Handles gateway and internal routing)
    │
    ├── type (Common stuff for model, function and others that being ref often)
    │   └── common.go
    │
    ├── models (Models declaration for all services)
    │   ├── attendance
    │   ├── employee
    │   ├── inventory
    │   └── notification
    │
    ├── notification (WhatsApp and FCM library)
    ├── minio (File server)
    ├── logs
    └── validation
```

## Where do I start?

Before starting it is recommended to familiar yourself with the shared-library files, api gateway and then to the services/orchestrator boilderplate files

To start create new services you can do below:
1. Create new folder for your service
2. Run `go mod init 'service-name'` inside that new folder
3. Adjust this command to suit your path to link the shared-library to your new services `go mod edit -replace github.com/bharata/shared-library=../../shared-library` and after that run `go get github.com/bharata/shared-library@v0.0.0`
4. (Copy template of other services) Create `main.go` for your service
5. (Copy template of other services) Create `dockerfile` for your service
6. (Copy template of other services) Edit the `docker-compose.yml`, with the required stuff intended for your services
7. Add your service-module-url to `api-gateway/main.go` on hashmap `InternalURL`
8. Add new variables if you create it to `.env`

These action above can be automated using shell script, but for now we dont have it nor we have any boilderplate template, so everything is manual for now

## TODO

1. Split this into git submodules, or even just make them as seperate repository
2. Forget about shared-library shares and just push it as standalone repository where we can include it easily to each services
3. Split docker-compose and env variables to each services properly with their own slices

























# --- Below this are OUTDATED information, you might waste your time reading stuff in below ---

## What is APP?

APP or application are the basic platform and landing page that will be web and/or mobile application, this is the portal to access another BASE System within the application

## What is CORE System?

CORE system are the main API Gateway to other MODULE on the system, currently there is only one: CORE - API Master Gateway

## What is MODULE?

MODULE system are basically Databases with API endpoints that accommodate required access to other system, this access is restricted

This database will be partitioned from the CORE - Employee Master Data to others CORE system with foreign keys

### Consideration

- What kind of database to use
	- Multiple database for each MODULE system (NoSQL)
		- NoSQL database mean everything is flexible
		- Reroute and role assignment on each system would be easier
		- Clear differentiation between MODULE system
		- Other system still able to function if their dependencies are met
		- Foreign keys connection need to be carried out manually by back-end for example: MODULE - Employee Master Data as Single Source of Truth, which means any inconsistency will be discarded and return as error
	- ~~Single database with multiple table representing each MODULE system~~
		- ~~SQL database mean everything is strict~~
		- ~~Replication and backup is easier compare to multiple databases~~
- To have 1 read/write database and 2 read-only database (for each database)
- Database replicate for daily/hourly backups
- Database redundancy if required so failed access into the main could be redirected to alternative active database (low-priority as this is quite tricky to implement)

### Internal Reroute

This is internal reroute from one module to another, already implemented under [shared-library](https://github.com/bip-itteam-internal/api-gateway-test) which mean, one module can request to another without the restriction of authentication on API Master Gateway and only need to provide Internal Keys, which all of the module had, this is really beneficial since we can do multi-module query easily for either update or read

## What is BASE System?

BASE system are base landing page after logging in, they can see their own basic employee information and portal to go into another system features that they have role for (this is done from the front-end when they acquire logging info with user roles in it)

## System Creation Sequence

This is still an assumption/prediction and required further confirmation

| Seq. | System Name                    | Status       |
| ---- | ------------------------------ | ------------ |
| 2    | CORE - API Master Gateway      | Polishing    |
| 1    | MODULE - Employees Master Data | Implementing |
| 3    | APP - Web Application          | Implementing |
| 3    | APP - Mobile Application       | Implementing |
| 4    | BASE - Landing Page            | Designing    |
| ...  | ...                            | ...          |

### About system lists, priorities and technical architectures

Below this will be system list and their priority, so we can aim to create the core system and dependencies that is required to create the other system

Technical architecture of the said system will be discussed later on in details

## Examples

### Example case

Employee wanted to login into HRIS system and access their attendance view

1. Go and login the main company application portal (APP - Main Application) from their platform respectively
2. Select go into HRIS
3. Select attendance feature and click view my attendance options

![[usecase-example.png]]

Main portal will accommodate as the HUB of the application to other systems

### Example request (Outdated)

**This is still in here since it is a good reference on how the API Master Gateway Reroute and Internal Reroute works**

This is type of request that we will probably have 
1. Single-fetch database request
	- This is where you fetch single database information, normal and straight forward
2. Multi-fetch database request
	- This is where you fetch 2 or more database, middle-ware has to make sure all fetch are successful and return processed or cleaned version of the data
- Single-fetch chained/propagate request
	- Request into database endpoints, and that endpoint will chain/propagate to another required database as cross-validation for example and cleaning the data before returning to the middle-ware

Image example below for (2) and (3) on how the data flow will looks like

![[endpoint-example.png]]

Example images above are out-dated as we now using API Master Gateway authorization as the middleware on requests