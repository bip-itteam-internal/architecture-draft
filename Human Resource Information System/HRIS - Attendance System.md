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

## Features

* Clock-in/out anywhere (Mobile App)
* 3 Layer clock-in/out (face, location, and fencing)
* Real-time attendance logs

## Requirements

- [ ] Employees master data (look up reference)
- [ ] Read and write access to attendance database

## Dependencies

- [ ] [[BASE - Landing Page]]

*This will insert attendance data to MODULE - Attendance Data as it is needed for record keeping that will be used by HRIS - Payroll and because some employee have different work schedule*
