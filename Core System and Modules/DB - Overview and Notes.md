## Description

This is just plain overview of how the database going to looks like and some notes for those information

In database there is going to be a lot of collection and some of the collection aren't natively owned by said database, therefore those collection need to be fetched from their database if possible on each server restart

Example can be seen below

![[database-collection-ownership-example.png]]

This is required to enforce ownership to each database properly and only update those who are the owner, other can fetch the data collection regularly or immediately if needed as the system see it fit

Also benefit of this method is multi-database lookup or query aren't necesarry anymore since they have their own information on the collection required for it. If one of the services down the other can still work just fine using the previous collection data fetched

## List of Databases and their Collections

**Employee Master Data**
- Personal data
- Personal documents
- Work data
- Work documents
- Work schedule
- System authentication
- Company work schedule (Synced from Attendance Data)

**Attendance Data**
- Attendance
- Company work schedule
- Company holiday
- Work schedule (Synced from Employee Master Data)