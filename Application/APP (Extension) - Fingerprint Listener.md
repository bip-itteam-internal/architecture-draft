## Description

This application responsible to listen and sent out command to the fingerprint machine
[Check out the application repository](https://github.com/bip-itteam-internal/fingerprint-listener)

This extension/middleware provides:
- Fingerprint event push into ERP system
- ERP request to export fingerprint data directly from the machines which will be push to HR WhatsApp message from IT WooWa chatbot
- ERP request to sync the fingerprint machine time

Application are build on Python with [pyzk](https://github.com/fananimi/pyzk) library, since it already link all the SDK into one place, and has the support for other series as well.

## Fingerprint devices

Currently we have 2 fingerprint devices:
- **X105 Solution** (on the Cipari's main office building, ground floor on the main door enterance)
- **X305 Solution** (on Tinggarjaya's warehouse, specific details on where it placed are unknown)

Which mean both of those devices need to have the same user data, since those data are need to be sync with the ERP system, any additional devices need to be cloned

## Fingerprint device specifications

Below are the device specification and notes regarding the devices since they are being used heavily and therefore some quirks are expected

### X105 Solution 

![[x105.jpg]]
![[specification.png]]

#### Current status and information

Status and information below are captured at 18 December 2025

Connection/communication to the network
- IP address: 10.10.10.201
- Subnet mask: 255.255.255.0
- Gateway: 10.10.10.1

Image description
- (A): Device machine information
- (B): Device current allocated spaces

| Image (A)              | Image (B)                 |
| ---------------------- | ------------------------- |
| ![[machine-info.jpeg]] | ![[allocated-space.jpeg]] |

#### Known issues

- Fingerprint device port 4370 is restricted to 1 connection
	- Which mean if we want to yield this to the server for custom fingerprint event listener then HR will not able to access it via the solution application
- Fingerprint device onboard memory are reseted after 3 days without power? How does this happen? are the CMOS battery faulty or what is happening with the device?
	- Which mean the connection/communication information will be reseted as well, therefore need manually be set to be on the correct network again 

### X305 Solution

Currently I have never look nor inspected the device that is being used on Tinggarjaya's warehouse, so this will be empty for the time being 

## Additional information

This application are currently limited to 1 devices, since it is easier to make. Therefore if we listen to 2 or more devices the number of active application will grow the same number

The application already have good disaster recovery, killing itself when error are found, heartbeat checks if the connection are lost.
But more testing are always needed since this is related to the hardware devices

## Dependencies

- [x] [[CORE - API Master Gateway]]
- [x] [[DB - Attendance Data]]