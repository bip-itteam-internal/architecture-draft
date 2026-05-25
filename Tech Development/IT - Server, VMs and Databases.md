
*Access to the on-site server and VMs are listed below, all root access password is the same with the user, but please DO NOT use the root as default*

## Servers

**Server - Windows Server (RAID5/HyperV)**
- Local IP: 10.10.10.15
- Username: administrator, devops
- Password: Hijau+99!

## VMs (Virtual Machines and VPS)

**VM - DevOps Ubuntu**
- Local IP: 10.10.10.37
- Username: devops_ubuntu
- Password: Hijau+99

**VM - CI/CD Runner**
- Local IP: 10.10.10.8
- Username: cicd
- Password: Hijau@99!

**VM - ERP Development**
- Local IP: 10.10.10.121
- Username: erp
- Password: Hijau+99

**VM - ERP Production**
- Local IP: 10.10.10.120
- Username: erp
- Password: Hijau+99

**VM - ERP Testing
- Local IP: 10.10.10.122
- Username: erp
- Password: Hijau+99

**VM - Finance Production**
- Local IP: 10.10.10.38
- Username: financeprodapi
- Password: Hijau+99

**VM - Network Monitor**
- Local IP: 10.10.10.3
- Username: netmon
- Password: Hijau@99!

## ERP Production MongoDBs

- **Employee (Primary Replication):** 
	- mongodb://erp-mongo:{password}@10.10.10.120:32783/employee_db?authSource=admin&directConnection=true

- **Attendance:** 
	- mongodb://erp-mongo:{password}@10.10.10.120:32785/attendance_db?authSource=admin

- **Notification:** 
	- mongodb://erp-mongo:{password}@10.10.10.120:32786/notification_db?authSource=admin

- **Insentive:** 
	- mongodb://erp-mongo:{password}@10.10.10.120:32787/insentive_db?authSource=admin

- **Integration:** 
	- mongodb://erp-mongo:{password}@10.10.10.120:32789/integration_db?authSource=admin