## Description

*This is the main application/platform that going to be a portal to access all system and features*

## Features

- Login page
	- Login with username and password, passkey are unavailable on web application
- Base dashboard with portal to access other system (BASE - Landing Page)
	- Base dashboard page will include base information or status of the employee
	- Portal access to other system will be display with modular portal interface possibly with tile-based dashboard
- **PRIORITY:** HRIS Manager to be able to input into Employee Master Data, since this is hard dependencies to make APP - Mobile Application login and registration features

## Implemented Features

1. Login page with username and password
2. HRIS managing employee master data
3. HRIS monitoring and editing employee attendance data
4. HRIS managing holiday lists

## Unimplemented Features

1. HRIS warning for employee that suit this category:
	- Partially filled employee data
	- Employee is not registered in myBharata mobile application
	- Employee is nearing their contract end period
	- Employee absent from their attendance without any notes
2. IT to manage employee system roles
3. IT to reset employee accounts
4. Helpdesk for all the system viewable by anyone

## Dependencies

- [x] [[CORE - API Master Gateway]]