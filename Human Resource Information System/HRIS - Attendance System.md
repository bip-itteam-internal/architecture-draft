**Personal Note**
*This system is required for automated attendance that will benefit [[HRIS - Payroll]]*

Background
* Attendance system is semi-automatic right now. We have fingerprint reader machine (Solution X105) that is connected to a network. HR can pull attendance logs everyday. (There's attempt to do cron job regulary pull the logs but never successful).
* After many consideration, we decided to do Mobile App as a attendance gate. Mobile App will be installed on every employee and they can do clock-in or clock-out anywhere within the radius. (50 m)
* There are 3 layer security to clock-in/out: Face recognition, Geolocation, and Geofencing (must connected to local WIFI)
* Every clock-in/out data stored in "Attendance Logs" database which is as real-time as possible.

Features
* Clock-in/out anywhere (Mobile App)
* 3 Layer clock-in/out (face, location, and fencing)
* Real-time attendance logs

Requirement 
- [ ] Employees master data (look up reference)

This will link back information to [[CORE - Employees Master Data]] as it is needed for record keeping that will be used by [[HRIS - Payroll]] and because some employee have different work schedule
