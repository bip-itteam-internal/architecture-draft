## Description

*Creation of single API Gateway that could be rerouted to all system authentication based on their current system would be beneficial to the whole system as managing it will be easier and centralized*

## Requirements

- [ ] Handle authentication
- [ ] Centralized API Gateway to other module on the system

## Forwarded Request

Below are the valid endpoint, propagated calls or forwarded request from this gateway
List of exposed endpoint on each module will be discussed later on

- [ ] [[MODULE - Employees Master Data]]
- [ ] [[MODULE - Attendance Data]]

### Consideration - Gateway Authorization to Module Endpoint

API Gateway and each module shared a matching secret **INTERNAL-KEY**, this key only supplied when request from API Gateway are forwarded to module
Each module endpoint will validate this gateway **INTERNAL-KEY** with its own, if the provide 
key is missing or incorrect it will result in error unauthorized

The database are internal and not exposed, it has to be setup properly in docker to communicate with the API Gateway correctly

![[gateway-example.png]]

Read more about [mTLS](https://www.cloudflare.com/learning/access-management/what-is-mutual-tls/) the more secure method of authorization 

## Endpoint Lists

*To be defined per-module in future sections*