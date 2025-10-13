## Description

*This is the main application/platform that going to be a portal to access all system and features*

Where does this application will be accessible from? Currently we're working on 2 platform:
- Mobile application
- Web application

## Features

- Login page
	- Login with username and password, or with additional passkey that have been setup on the registration page
	- More information on passkey can be seen in Employee Master Data
- Registration page or on-boarding
	- This reside within the login page, where additional click for "New employees" is required, below are the registration flow:
		1. Information regarding the employee already being filled by the HRD and knowing the Employee ID are required for the next step
		2. Insert unregistered Employee ID and it will show the full name of that employees (to make sure the employees and their account is match)
		3. Requirement to fill new username, password and pick 1 options for 2nd verification (phone number or email, this is read-only data taken from MODULE - Employee Master Data)
		4. Additional setup for alternative method of login with PIN or Bio-metrics passkey (based on device capabilities) this step is skip-able
- Base dashboard with portal to access other system
	- Base dashboard page will include base information or status of the employee
	- Portal access to other system will be display with modular portal interface possibly with tile-based dashboard

## Dependencies

- [ ] [[CORE - API Master Gateway]]