## Description

This database will hold everything about notification for all services includng articles intended for mobile and website

## Features

This service will be able to manage all notification third-party usage like: 
- Push WhatsApp notification request to personal or groups
- Push FCM notication for single and multiple tokens
*(This all already ready to be used on shared-library and some are already in-use by some services, merging them all together is better than each service need to setup each time for their own usage)*

Database will hold information as follow:
- History for FCM notification for mobile and website
- Articles created from division regarding their update that impacted their own department, other department or the whole company, viewable on mobile and website

Need futher disscusion on how does this will reside in here, as this is better suited to reside in HRIS database
- Payroll document are saved in here for each employee, and easily viewable (required to verify PIN or password)

## Consideration

Images for articles need to be on fixed size so it didnt break for FCM notification on mobile, specification below:
- Width and length: 1024x512 px
- Filesize: below 1MB recommended to be below 300KB

## Data Structures

All structures below are just baseline and can be change as requirement needs

### Notification

Personal notification required employee ID to know who is this notification are for, this will also present on bulk notification, this only reserved for important notification
Therefore daily notification like clock-in and maybe some articles information are not saved into this collection

```json
{ // Notification collection
	"_id": ObjectId(MongoDB_ID_Assignment),
	"employee_id": "0032-03-27102025", // Natural keys (FK)
	
	"title": "Notification title",
	"body": "Notification body or message",
	"image": "Servable imageURL from minIO",
}
```

### Article

```json
{ // Notification collection
	"_id": ObjectId(MongoDB_ID_Assignment),
	
	"title": "Article title",
	"content": "Article content in markdown styles",
	"author_department": "String enums", // Who is publishing thiss articles?
	"pubslihed_at": Datetime, // Will be used as default sorting
	
	// Additional attachment
	"image": "Servable imageURL from minIO",
	"video": "Servable videoURL from minIO",
	"file": "Servable file from minIO",
	
	"summary": "Content summary will be used to push FCM notification",
	"pinned": true, // To be pinned on top of articles page
	
	// Engagement metrics, there is no limiter so employee can spam it, we dont really care for now
	"view_count": int,
	"like_count": int,
	"reaction": Object, // Object of emoticon and their used value in int
}
```

Articles are viewable by all department, it is fine to publish some notification for 1 department on here, since the other can just ignore it
On articles publish, it will automatically use article title and summary to push FCM notification