## Description

*Creation of single API Gateway that could be rerouted to all system authentication based on their current system would be beneficial to the whole system as managing it will be easier and centralized*

[Read more into our implementation of this API Master Gateway](https://github.com/bip-itteam-internal/api-gateway-test)

## Requirements

- [x] Handle authentication
- [x] Pass forward the payload to be used by the module on the system
- [x] Centralized API Gateway to other module on the system
- [x] Login and logout features (data taken from Employee Master Data in the collections of System Authentication)
- [x] Registration from first time user that login with employee ID and temporary password given by HRD
- [ ] Simplification of reroute request and internal request for easy development

## Forwarded Request / Reroute

Below are the valid endpoint, propagated calls or forwarded request from this gateway
List of exposed endpoint on each module will be discussed later on

- [ ] [[DB - Overview and Notes]]
- [ ] [[DB - Employees Master Data]]
- [ ] [[DB - Attendance Data]]

Others that is not urgent
- [ ] [[DB - Notification Center]]

List of unknown modules as per 10/17/25

- [ ] [[Unlisted - Internal Inventory]]
- [ ] [[Unlisted - Warehouse Master Data]]
- [ ] [[Unlisted - Purchase Master Data]]
- [ ] [[Unlisted - Sales Master Data]]
- [ ] [[Unlisted - Dynamic Task Tracker]]

### Gateway Authorization to Module Endpoint

API Gateway and each module shared a matching secret **INTERNAL-KEY**, this key only supplied when request from API Gateway are forwarded to module
Each module endpoint will validate this gateway **INTERNAL-KEY** with its own, if the provide 
key is missing or incorrect it will result in error unauthorized

The database are internal and not exposed, it has to be setup properly in docker to communicate with the API Gateway correctly

![[gateway-example.png]]

Read more about [mTLS](https://www.cloudflare.com/learning/access-management/what-is-mutual-tls/) the more secure method of authorization 

There is a discussion to imporve this into **INTERNAL-KEY-V2** where it will only be set and validated from internal to internal requests, therefore blocking any routes access with "/internal" automatically if it called from API-Gateway

## JWT Payload Structure / Custom Headers

Additional JWT payload for easier look up into here instead of querying the database for those most reused information, this information is being passed around as additional headers

```JSON
{
	"employee_id": "0032-03-27102025",
	"username": "aurelia_mara",
	"system_roles": {
		"it": "supervisor",
		"hris": "manager",
		"finance": "staff",
	}
}
```

This header are being used to check for self-services routes and also to set metadata into database on data creation/modification

## Public Endpoint Lists

*To be defined per-module in future sections*