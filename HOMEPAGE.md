## Notices

*Everything in here is is a quick overview and a rough idea on how the system looks like and how it interact with one another, this required more open discussion together*

## What is ERP system looks like?

Currently everything are still in mono repository, this will be moved out with git submodules down the line when it sees fit

Interaction between the services can be interpreted like image below
![[erp-request-nutshell.png]]

### What does the API Gateway do?

It is our entry point for request, which also handle JWT authentication and routes check for open/restricted routes propagation

### Explanation of the API Gateway routes structures

By default API Gateway doesn't have their own routes, and only foward the request to internal services accordingly *(with the exception of authenticaction since it will be post-processed by the API Gateway themself for JWT creation)*

![[api-gateway-routes.png]]

Routes structure lists (full details):
- **/public** - Stand for public routes, which freely accessable for anyone
- **/health** - This is heartbeat check for services that will always resolve to `/api/:service/` and sent back the information back
- **/api** - Stand for normal api calls, this will calll internal services with the requirement of JWT authentication and/or unique `access-key` if requested to one of the open route services *(more explation can be read below)*
- **/auth** - Stand for authentication, this route will always call into `/api/employee` under the hood and grab employee data and sign it with JWT on API Gateway
- **/ext** - Stand for extension or external routes, with direct access (no JWT authentication) into services or webhooks *(currently heavily utilized for fingerprint integration)*
- **/onboarding** - Being used for public access (minimal) information and helper function call/check for onboarding via mobile application 
- **/debug** and **/dev** - Debug and development routes respectively, only available on dev/staging environment

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
    ├── common (Common stuff for model, function and others that being ref often)
    │   ├── env.go
    │   ├── header.go
    │   ├── metadata.go
    │   ├── response.go
    │   ├── roles.go
    │   └── struct.go
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




## Using pre-existing ERP authentication for external apps

Sometimes we are unable to build on top of the ERP because of restriction or we have standalone prototype we want to share directly but it is need authentication

Therefore you can use the existing authentication on ERP for your external apps like below, just call the function and then save it as header for JWT, and validate it for each page access accordingly

Sequence diagram are show below

![[erp-external-auth-use-case.svg]]
