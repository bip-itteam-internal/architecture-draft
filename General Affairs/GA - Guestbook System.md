## Description

Digitalized version of the current manually handled company's guestbook, currently aren't fully fledge system but we're on it, check out the [GitHub repository](https://github.com/bip-itteam-internal/guestbook-system)

This system is fully owned by GA Security and they have full control over it

## Features

- Public web application which responsible to send guestbook entries to ERP system
	- Security show guestbook QR code to the visitor for them to fill out the guestbook
	- Request are valid if the token send match the active token on the ERP system, which being rotated each day on 4 in the morning
- View of the guestbook are available to GA/Security and all HR roles

- (On-progress) For employee that is late and need to fill out guestbook we have faster option to do so with the help of mobile application, explaination below;
	- Employee come late, and clock in on the gate
	- Security request the employee to show their employee data QR
	- Security select 'scan late employee QR' option and simply scan the QR
	- The details are filled automatically and passed to the guestbook


## Preview

Since this application is mobile-first we dont really care now support better view for desktop

![[Pasted image 20260307112209.png]]