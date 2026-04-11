## Database Backups

Backup are carried out for important databases, weekly on Monday at 4:15am

Currently this backup reside only on the local machine project directory, this should be improved to upload the backups into cloud services, so we have something for fallback incase the local machine or VM crashes and unable to be recovered

## Collection Synchronization

In database there is going to be a lot of collection and some of the collection aren't natively owned by said database, therefore those collection need to be fetched from their database if possible on each server restart, cron based or by subscription based action

Example can be seen below

![[database-collection-ownership-example.png]]

This is required to enforce ownership to each database properly and only update those who are the owner, other can fetch the data collection regularly or immediately if needed as the system see it fit

Also benefit of this method is multi-database lookup or query aren't necesarry anymore since they have their own information on the collection required for it. If one of the services down the other can still work just fine using the previous collection data fetched

## Database Replication

Database replication is required if we want to expose our database for external usages for other application, where it will only have **READ** access

Currently this only active for **Employee-MongoDB** and the slave/secondary cluster being used by **Task Management**

The replication rules explicitly state that the cluster cannot be change for the primary as we currently dont have dynamic cluster picker for those action

## List of Databases and their Collections

**Employee-MongoDB**
- PersonalData
- PersonalDocs
- WorkData
- WorkDocs
- WorkSchedule
- SystemAuthentication
- CompanyWorkSchedule (Sync from Attendance-Service)
- CompanyHoliday

**Attendance-MongoDB**
- AttendanceEntries
- CompanyWorkSchedule
- CompanyGroupRotation
- CompanyHoliday
- CompanyWifi
- FingerprintExport
- Guestbook
- WorkSchedule (Sync from Employee-Service)
- LeaveRequest

**Notification-MongoDB**
- Inbox
- Article
- Splash
