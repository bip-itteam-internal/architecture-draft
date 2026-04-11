## Notes

*This system is required for automated attendance that will benefit HRIS - Payroll
This system should be moved from HRIS system to Extension or something else*

## Background

* Attendance system is semi-automatic right now. We have fingerprint reader machine (Solution X105) that is connected to a network. HR can pull attendance logs everyday. (There's attempt to do cron job regulary pull the logs but never successful).
	* How will the data from fingerprint reader machine (Solution X105) be integrated to here?
		- We can use their SDK and create our own script (https://drive.google.com/file/d/1MSV_OdJRTjIlcrKOrw1t0bbpT3vS4GoF/view?usp=sharing) or 3rd party (there are some open source script) to pull attendance data every day
		- Store them in a "Raw Database"
		- Fingerprint machine is a "Fallback" in case it's needed
	- Looking at the SDK we could create a middleware listener, where it will pass the signal from fingerprint machine into the ERP website on attendance services with special routes for fingerprint automated clock-in/out
	- The listener application will be build on Python with [pyzk](https://github.com/fananimi/pyzk) library, since it already link all the SDK into one place, and has the support for other series as well. The repository will be shared in here later on 
- Read more about the fingerprint machine application and their usages on **APP (Extension) - Fingerprint Listener**
* After many consideration, we decided to do Mobile App as a attendance gate. Mobile App will be installed on every employee and they can do clock-in or clock-out anywhere within the radius. (50 m)
* There are 3 layer security to clock-in/out: Face recognition, Geolocation, and Geofencing (must connected to local WIFI)
	* If the system are only available in local network then Geolocation and Geofencing information is redundant
* Every clock-in/out data stored in "Attendance Logs" database which is as real-time as possible.

## Consideration

Since we're going with MongoDB it is good to [read about this](https://www.mongodb.com/docs/manual/data-modeling/design-antipatterns/reduce-collections/) before jumping into designing the database structure

## Use-case Diagram

Attendance can be done with 2 method as per February 2026, either from fingerprint machine validation or mobile application, website are currently disabled

![[attendance-use-case.png]]

## Features

This is feature that is bind and owned by HRIS for attendances
- View attendance in real-time
- Change attendance entry statush
- Add additional comments to attendance entries
- Add additional documents to attendance entries
- Export attendance report

**(Finished)** Additional milestones
 - Connect fingerprint machine with C/C# application listener to enter data into DB using curl calling specific routes
 - This is connected with Python script with collective open-source module for 

Additional features
 - We might want to consider using hybrid/remote work environment, therefore employee need to clock-in/out with mobile application outsite the company network

## Requirements

- [x] Employees master data (look up reference)
- [x] Read and write access to attendance database

## Dependencies

- [x] [[Microservices - Attendance Service]]

*This will insert attendance data to MODULE - Attendance Data as it is needed for record keeping that will be used by HRIS - Payroll and because some employee have different work schedule*
