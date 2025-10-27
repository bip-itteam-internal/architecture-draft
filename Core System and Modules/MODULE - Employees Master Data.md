## Description

This master data manage every employees data including additional linked documents or data from other system into this master data system. 

Rename ideas since this has it's own back-end and databases
- ~~**"Employee module"** following the usage of this system~~
- **"Employee service"** following micro-services naming convention

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
- ~~UUID/GUID~~
	- ~~Easy creation but accessing this would be nightmare and probably slow? The default one is 128-bit but we can start from 16-bit and step that up if collision happen~~
- ~~Snowflake (custom-uuid)~~
	- ~~Whatever bit-size data that has a structure from the system, the usual size is 64-bit with this composition: 1-bit signed, 41-bit timestamp, 10-bit from database/system creation, 12-bit randoms or from millisecond~~ 

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

- Employee ID (unique)
	- Each division has its own employee ID
	- Employee ID are being composed by: BIP (count, probation month count, etc)
- Department or division
- Position or title
- Employment type
- NPWP number
- Payment bank details
- Additional documents
	- Signed contract
	- Probation start
	- Probation end
	- Warning notices

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

## Database Structures

Since we re going with MongoDB NoSQL database so we need to identify what do we can do within the database

### Consideration

- Multiple collection within 1 database, as MongoDB has hard limit of 16MB of each documents/entry in the collection
	- If that is accessed frequently by the system
	- If it hold binary documents like images, PDF and others
	- If it doesn't make sense to do embedded information on the entry
		- Embedded documents is basically sub-object within the object like JSON `outer_object.inner_object.entry` and so on
- Reference with MongoDB build-in `_id` as primary key
	- If it is 1:1 reference and will never changes the other collection can match the `_id` field with the main reference object
	- If it is many to many relation it is better to leave the object `_id` as default and add new entry like `_employee_reference` and give it the main reference to that object

### Database Collection Graph and Relation

This will be attached in the future...

### Database Documents/Entries

This is the example on the database document or entries going to looks like if it was in 1 massive wrapper after all join query has been done

#### Personal Data

```JSON
{ // Personal information collections
	"_id": ObjectId(MongoDB_ID_Assignment),
	"employee_id": "0032-03-27102025", // Natural keys (PK)
	
	"full_name": "Aurelia Mara",
	"gender": "Female", // Enums to string
	"religion": "Islam", // Enums to string
	"marital_status": "Single", // Enums to string
	"phone_number": "081234567890",
	"email_address": "aurelia_mara@example.com",
	"home_address": "Jl. Merdeka No. 99, Bandung, Indonesia",
	
	// This still missing some information from the examples like: NIK, No. KK, since we dont know if we want to expose those, and what are the use of those information with-in the system
}
```

Documents being split to save spaces and since those information aren't frequently needed

```JSON
{ // Personal document collections
	"_id": ObjectId(MongoDB_ID_Assignment),
	"employee_id": "0032-03-27102025", // Natural keys (FK)
	
	"documents": [ // Easily expandable if needed
		{
			"type": "photo_ktp",
			"filename": "aurelia_mara_ktp.jpg",
			"file_data": BinData(0, "<binary data>"), 
		},
		{
			"type": "photo_kk",
			"filename": "aurelia_mara_kk.jpg",
			"file_data": BinData(0, "<binary data>"), 
		},
		{
			"type": "photo_npwp",
			"filename": "aurelia_mara_npwp.jpg",
			"file_data": BinData(0, "<binary data>"), 
		}
	]
}
```

#### Work Data

```JSON
{ // Work information collections
	"_id": ObjectId(MongoDB_ID_Assignment),
	"employee_id": "0032-03-27102025", // Natural keys (FK)
	
	"department": "IT", // Enums to string
	"position": "Supervisior", // Enums to string, this doesn't really do anything for now, since we have our own system authentication
	"employment_type": "Fulltime", // Enums to string
	
	"fingerprint_number": 211, // This is required as we might fallback to attendance using fingerprint
	
	"probation": {
		start_date: ISODate(),
		end_date: ISODate()
	},
	
	"npwp_number": "6788.4642738.973", // Optional
	"bpjs_number": "39932016910944", // Optional
	
	// Since all employee are forced to have Mandiri Bank account, but what if it changes? Is this better then? Since we account for changes that might happen in the future?
	// Pick one from below
	"mandiri_account_number": "930419413752", // Optional
	// "bank_details": { // Optional
		// "bank_name": "Bank Mandiri",
		// "account_number": "930419413752",
		// "account_holder": "Aurelia Mara"
	// }
}
```

Documents being split to save spaces and since those information aren't frequently needed

```JSON
{ // Work document collections
	"_id": ObjectId(MongoDB_ID_Assignment),
	"employee_id": "0032-03-27102025", // Natural keys (FK)
	
	"documents": [ // Easily expandable if needed
		{
			"type": "signed_contract",
			"filename": "aurelia_mara_contract.pdf",
			"file_data": BinData(0, "<binary data>"), 
		},
		{
			"type": "probation_report",
			"filename": "aurelia_mara_probation.pdf",
			"file_data": BinData(0, "<binary data>"), 
		}
	]
}
```

#### Work Schedule Data

This being separated since this will have more frequent access

```JSON
{ // Work schedule collections
	"_id": ObjectId(MongoDB_ID_Assignment),
	"employee_id": "0032-03-27102025", // Natural keys (FK)
	
	// We shouldn't really mess much in here, we want to include work schedule but we need reference into their department schedule and shift, since hard embedding it in here would really bad and hard to change later on
	// Therefore this should work for now, until we enstablish attendance system

	"work_schedule": "BIP-REGULAR", // Natural keys (FK) reference to company work schedule collections
	"exception": {} // This may be needed later on for Hybrid type and such
}
```

#### Company Work Schedule

This is reference for the Work Schedule Data
This will have its own collections in Employee Master Data and Attendance Data and will be synced properly between the two

```JSON
{ // Company work schedule collections (This is bad, but will do for now)
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "BIP-REGULAR", // Natural keys (PK)	

	// Below are bad since what if it has this and that exception? If so then this need to write the exception and explain it before passing into front-end
	// "work_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
	// "work_hours": { "start": "09:00", "end": "17:00" },

	// This is better in structures, but still yikes also this can be change to array if necessary
	"schedule": {
		"monday":    {"start": "08:00", "end": "17:00"},
		"tuesday":   {"start": "08:00", "end": "17:00"},
		"wednesday": {"start": "08:00", "end": "17:00"},
		"thursday":  {"start": "08:00", "end": "17:00"},
		"friday":    {"start": "08:00", "end": "17:00"},
		"saturday":  {"start": "08:00", "end": "13:00"}, // 5 hours
		"sunday":    null
	}
},
// Below are for Office boy
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "OFFICEBOY-REGULAR", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "06:30", "end": "17:00"},
		"tuesday":   {"start": "06:30", "end": "17:00"},
		"wednesday": {"start": "06:30", "end": "17:00"},
		"thursday":  {"start": "06:30", "end": "17:00"},
		"friday":    {"start": "06:30", "end": "17:00"},
		"saturday":  {"start": "06:30", "end": "14:00"}, // 5 hours
		"sunday":    null
	}
},
// Below are shift for Host Live
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "HOSTLIVE-SHIFT-A", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "05:00", "end": "13:00"},
		"tuesday":   {"start": "05:00", "end": "13:00"},
		"wednesday": {"start": "05:00", "end": "13:00"},
		"thursday":  {"start": "05:00", "end": "13:00"},
		"friday":    {"start": "05:00", "end": "13:00"},
		"saturday":  {"start": "05:00", "end": "13:00"},
		"sunday":    null
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "HOSTLIVE-SHIFT-B", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "13:00", "end": "21:00"},
		"tuesday":   {"start": "13:00", "end": "21:00"},
		"wednesday": {"start": "13:00", "end": "21:00"},
		"thursday":  {"start": "13:00", "end": "21:00"},
		"friday":    {"start": "13:00", "end": "21:00"},
		"saturday":  {"start": "13:00", "end": "21:00"},
		"sunday":    null
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "HOSTLIVE-SHIFT-C", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "17:00", "end": "01:00"},
		"tuesday":   {"start": "17:00", "end": "01:00"},
		"wednesday": {"start": "17:00", "end": "01:00"},
		"thursday":  {"start": "17:00", "end": "01:00"},
		"friday":    {"start": "17:00", "end": "01:00"},
		"saturday":  {"start": "17:00", "end": "01:00"},
		"sunday":    null
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "HOSTLIVE-SHIFT-D", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "01:00", "end": "09:00"},
		"tuesday":   {"start": "01:00", "end": "09:00"},
		"wednesday": {"start": "01:00", "end": "09:00"},
		"thursday":  {"start": "01:00", "end": "09:00"},
		"friday":    {"start": "01:00", "end": "09:00"},
		"saturday":  {"start": "01:00", "end": "09:00"},
		"sunday":    null
	}
},
// Below are shift for Security
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "SECURITY-SHIFT-A", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "07:00", "end": "19:00"},
		"tuesday":   {"start": "07:00", "end": "19:00"},
		"wednesday": {"start": "07:00", "end": "19:00"},
		"thursday":  {"start": "07:00", "end": "19:00"},
		"friday":    {"start": "07:00", "end": "19:00"},
		"saturday":  {"start": "07:00", "end": "19:00"},
		"sunday":    null
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "SECURITY-SHIFT-B", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "19:00", "end": "07:00"},
		"tuesday":   {"start": "19:00", "end": "07:00"},
		"wednesday": {"start": "19:00", "end": "07:00"},
		"thursday":  {"start": "19:00", "end": "07:00"},
		"friday":    {"start": "19:00", "end": "07:00"},
		"saturday":  {"start": "19:00", "end": "07:00"},
		"sunday":    null
	}
},
// Below are for Production
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "PRODUCTION-SHIFT-A", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "08:00", "end": "16:00"},
		"tuesday":   {"start": "08:00", "end": "16:00"},
		"wednesday": {"start": "08:00", "end": "16:00"},
		"thursday":  {"start": "08:00", "end": "16:00"},
		"friday":    {"start": "08:00", "end": "16:00"},
		"saturday":  {"start": "08:00", "end": "13:00"}, // 5 hours
		"sunday":    null
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "PRODUCTION-SHIFT-B", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "16:00", "end": "00:00"},
		"tuesday":   {"start": "16:00", "end": "00:00"},
		"wednesday": {"start": "16:00", "end": "00:00"},
		"thursday":  {"start": "16:00", "end": "00:00"},
		"friday":    {"start": "16:00", "end": "00:00"},
		"saturday":  {"start": "16:00", "end": "21:00"}, // 5 hours
		"sunday":    null
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "PRODUCTION-SHIFT-C", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "00:00", "end": "08:00"},
		"tuesday":   {"start": "00:00", "end": "08:00"},
		"wednesday": {"start": "00:00", "end": "08:00"},
		"thursday":  {"start": "00:00", "end": "08:00"},
		"friday":    {"start": "00:00", "end": "08:00"},
		"saturday":  {"start": "00:00", "end": "05:00"}, // 5 hours
		"sunday":    null
	}
},
// Below are for Inventory
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "INVENTORY-SHIFT-A", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "08:00", "end": "16:00"},
		"tuesday":   {"start": "08:00", "end": "16:00"},
		"wednesday": {"start": "08:00", "end": "16:00"},
		"thursday":  {"start": "08:00", "end": "16:00"},
		"friday":    {"start": "08:00", "end": "16:00"},
		"saturday":  {"start": "08:00", "end": "13:00"}, // 5 hours
		"sunday":    null
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "INVENTORY-SHIFT-B", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "16:00", "end": "00:00"},
		"tuesday":   {"start": "16:00", "end": "00:00"},
		"wednesday": {"start": "16:00", "end": "00:00"},
		"thursday":  {"start": "16:00", "end": "00:00"},
		"friday":    {"start": "16:00", "end": "00:00"},
		"saturday":  {"start": "16:00", "end": "21:00"}, // 5 hours
		"sunday":    null
	}
}
```

#### System Authentication Data

```JSON
{ // System authentication collections
	"_id": ObjectId(MongoDB_ID_Assignment),
	"employee_id": "0032-03-27102025", // Natural keys (FK)
	
	"username": "aurelia_mara",
	"password": "hash+salt...", // Encrypted
	"passkey": { // Optional
		"pin": "hash+salt..." // Encrypted
	},
	"system_roles": { // This is easily expandable
		"it": "Supervisor" // Enums as string
	}
}
```

#### Metadata

Since all of the example above has no metadata for date of creation, update or who created, updated the data, or even the current status of the data is active or not, this will be in future discussed of what is needed and what is not
