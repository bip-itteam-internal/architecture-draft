## Description

*This is the landing page of the application that include portals to other systems this is currently exclusively implemented for website*

## Features

Since we have the basic information of the employee, we could create some good to have information for them in this landing page, see below

- Personal information checks (read-only)
- Calendar with their work schedule and shift
	- Which also include company pre-determine mass leaves or national holiday
- Status of their current attendance (this required HRIS - Attendance System)
- Status of their Warning Notice (SP in Indonesian which mean Surat Peringatan) and how much do they currently held
	- Need more information regarding this abolishment, as each one has lifetime of 6 month before it is being abolished

Portal list will be displayed in the left hand side of the screen, listed with all possible feature from each active system based on their role in the system, example below
- HR Manager logging in into the APP - Website and now in BASE - Landing Page, they can see the feature for Manage Employee under the HRIS title on the left hand side, which when clicked will bring them into that feature immediately, images of this example will be attached soon

![[landing-page-example.png]]

On the left hand side, the title like: HRIS, Manufacturer and IT aren't clickable and only for indication, the only clickable is the features below the title of those

This is able to be implemented in both Mobile and Web application, although the UX on the mobile may suffer from this hidden left hand tab list

## Requirements

- [x] Employees master data (look up reference)
- [x] Role information from the employee master data
	- [ ] Features status from available system (for maintenance flags, as you don't want to hide this in the front-end, you want to flag this unavailable at the moment)
- [x] Unified portal to others services or system

## Dependencies

- [x] [[CORE - API Master Gateway]]
