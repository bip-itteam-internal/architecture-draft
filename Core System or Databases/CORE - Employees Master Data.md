## Notes

*CORE System structure and functionality is still work in progress*

## Description

*This master data manage every employees data including additional linked documents or data from other system into this master data system*

## Pending Details

- [ ] Who are responsible for this master data accuracy and completeness?

## Data Structures

*All data below need to be rechecked and reconfirmed*

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
- Payment bank details

#### Attendance Data

*This data information could placed somewhere else if necessary, this will be reference look up to determine attendance automated status*

- Work type (onsite full-time, onsite shift-based or remote)
- Work days
- Work hours (start and end hour)

*Work days and hours are required as some department didn't follow the conventional attendance system, example: security/manufacturer as they follow their shift-based, live hosts as they start later on the day. etc*