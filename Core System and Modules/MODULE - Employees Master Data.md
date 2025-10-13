## Description

This master data manage every employees data including additional linked documents or data from other system into this master data system. 

Rename ideas since this has it's own back-end and databases
- **"Employee module"** following the usage of this system
- ~~**"Employee service"** following micro-services naming convention~~

## Pending Details

- [ ] Who are responsible for this master data accuracy and completeness?
	- This will be HRD Manager responsibilities

## Data Structures

*All data below need to be rechecked and reconfirmed*

### Consideration 

This database need something that will be used for UUID and act as Foreign Keys as well, pick one below what is best for this system:
- ~~Auto increment like standard SQL~~
	- ~~This is hard to get right as this need to be sync with the latest data insertion, even if we Single Source of Truth this is still tricky to sync~~
- Natural keys
	- Use something that is already from data below, possibly Employee ID
- UUID/GUID
	- Easy creation but accessing this would be nightmare and probably slow? The default one is 128-bit but we can start from 16-bit and step that up if collision happen
- Snowflake (custom-uuid)
	- Whatever bit-size data that has a structure from the system, the usual size is 64-bit with this composition: 1-bit signed, 41-bit timestamp, 10-bit from database/system creation, 12-bit randoms or from millisecond 

### Personal Data

- Full name
- Gender
- Religion
- Martial status
- Telephone number
- Email address
- Home address
- Additional documents
	- Photo KTP
	- Photo KK

*We only want usable data that is useful to the system, therefore additional information and data can be stored as images or scanned document that is stored in bytes and even encrypt them if needed*

### Work Data

- Employee ID
- Department or division
- Position or title
- Employment type
- NPWP number
- Payment bank details
- Additional documents
	- Probation start
	- Probation end

#### Attendance Data

*This data information could placed somewhere else if necessary, this will be reference look up to determine attendance automated status*

- Work type (onsite full-time, onsite shift-based or remote)
- Work days
- Work hours (start and end hour)

*Work days and hours are required as some department didn't follow the conventional attendance system, example: security/manufacturer as they follow their shift-based, live hosts as they start later on the day. etc*

### System Authentication Roles

*This data include employee role on all system for the employee personal work information or other work-related system that is required for the employee to do their work*

*This information below is crucial and will be completed during the new employee on-boarding process with HRD side-by-side*

- Username
- Password (hashed)
- Passkey (exclusive to mobile based on device capabilities)
	- PIN (hashed)
	- Bio-metrics (this credentials are saved locally on device per-application)
- Roles (on their subsystem)
	- Using object notation so it is easier to access, lookup are also faster as you can access it directly, example: `user.system_roles.hris`
	- Obviously this will be enum type in their respective system

#### System Roles Example

```json
system_roles: {
	hris: "Manager",
	manufacturer: "Clerk",
	warehouse: "Auditor"
}
```
