## Notes

*This system is required for automated attendance that will benefit HRIS - Payroll*

## Background

* Attendance system is semi-automatic right now. We have fingerprint reader machine (Solution X105) that is connected to a network. HR can pull attendance logs everyday. (There's attempt to do cron job regulary pull the logs but never successful).
	* - How will the data from fingerprint reader machine (Solution X105) be integrated to here?
		- We can use their SDK and create our own script (https://drive.google.com/file/d/1MSV_OdJRTjIlcrKOrw1t0bbpT3vS4GoF/view?usp=sharing) or 3rd party (there are some open source script) to pull attendance data every day
		- Store them in a "Raw Database"
		- Fingerprint machine is a "Fallback" in case it's needed
* After many consideration, we decided to do Mobile App as a attendance gate. Mobile App will be installed on every employee and they can do clock-in or clock-out anywhere within the radius. (50 m)
* There are 3 layer security to clock-in/out: Face recognition, Geolocation, and Geofencing (must connected to local WIFI)
	* If the system are only available in local network then Geolocation and Geofencing information is redundant
* Every clock-in/out data stored in "Attendance Logs" database which is as real-time as possible.

## Consideration

Since we're going with MongoDB it is good to [read about this](https://www.mongodb.com/docs/manual/data-modeling/design-antipatterns/reduce-collections/) before jumping into designing the database structure

## Features

* Clock-in/out anywhere (Mobile App)
* 3 Layer clock-in/out (face, location, and fencing)
* Real-time attendance logs

This is feature that is bind and owned by HRIS for attendances
- View attendance in real-time
- Change attendance entry status
- Add additional comments to attendance entries
- Add additional documents to attendance entries
- Export attendance report

Additional milestones
 - Connect fingerprint machine with C application listener to enter data into DB using curl calling specific routes

## Repository

- FE: [Backlog · HRIS](https://github.com/orgs/bip-itteam-internal/projects/4)
- BE: -

## Requirements

- [ ] Employees master data (look up reference)
- [ ] Read and write access to attendance database

## Dependencies

- [ ] [[DB - Attendance Data]]

*This will insert attendance data to MODULE - Attendance Data as it is needed for record keeping that will be used by HRIS - Payroll and because some employee have different work schedule*
