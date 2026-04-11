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
- **X609 Solution** (on Tinggarjaya's warehouse, specific details on where it placed are unknown)

Which mean both of those devices need to have the same user data, since those data are need to be sync with the ERP system, any additional devices need to be cloned

## Fingerprint device specifications

Below are the device specification and notes regarding the devices since they are being used heavily and therefore some quirks are expected

### X105 Solution 

![[x105.jpg]]
![[Additional documents/Fingerprint Machine X105/specification.png]]

#### Current status and information

- **Platform**: JZ4725_TFT
- **Firmware**: Ver 6.60 Jun 23 2015
- **Serial Number**: OID6090586090601114
- **MAC Address**: 00:17:61:94:4C:B8
- **IP Address**: 10.10.10.201
- **Subnet Mask**: 255.255.255.0
- **Gateway**: 10.10.10.1

#### Known issues

- Fingerprint device port 4370 is restricted to 1 connection
	- Which mean if we want to yield this to the server for custom fingerprint event listener then HR will not able to access it via the solution application
- Fingerprint device onboard memory are reseted after 3 days without power? How does this happen? are the CMOS battery faulty or what is happening with the device?
	- Which mean the connection/communication information will be reseted as well, therefore need manually be set to be on the correct network again 

### X609 Solution

This previously used in Tinggarjaya Warehouses, but now are not used anymore and can be utilized for something

Since this device is better than we currently using, we could use this on the main office and update employee ID card with embedded RFID and display the ERP's QR code in the future

![[x609.jpg]]
![[Additional documents/Fingerprint Machine X609/specification.png]]

#### Current status and information

- **Platform**: ZLM60_TFT
- **Firmware**: Ver 6.60 Apr 13 2022
- **Serial Number**: JHG3235300134
- **MAC Address**: 00:17:61:10:40:48
- **IP Address**: 
- **Subnet Mask**: 
- **Gateway**: 10.10.10.1

## Additional information

This application are currently limited to 1 devices, since it is easier to make. Therefore if we listen to 2 or more devices the number of active application will grow the same number

The application already have good disaster recovery, killing itself when error are found, heartbeat checks if the connection are lost.
But more testing are always needed since this is related to the hardware devices

## Dependencies

- [x] [[CORE - API Master Gateway]]
- [x] [[Microservices - Attendance Service]]