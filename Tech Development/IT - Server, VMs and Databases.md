
*Akses ke server on-site dan VM tercantum di bawah ini, semua password root sama dengan user, namun harap JANGAN menggunakan root sebagai default*

## Server

**Server - Windows Server (RAID5/HyperV)**
- Local IP: 10.10.10.15
- Username: administrator, devops
- Password: Hijau+99!

## VM (Virtual Machine dan VPS)

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

## MongoDB ERP Production

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