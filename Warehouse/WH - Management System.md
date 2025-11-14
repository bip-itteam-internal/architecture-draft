## Description

*This dashboard listed all goods stored in the warehouse in details so everything is organized and easy to keep track*

[Example of this system](https://docs.google.com/spreadsheets/d/12L5OKViT2LnQECT6ldUBkjK-xablpcZO/edit?gid=1015075572#gid=1015075572)

## Features

- Dashboard
	- Overview of everything that is stored in warehouse
- View and search
	- To keep track of goods count and placement within the warehouse
- Creation of new Stock Keeping Unit entry and barcode
	- This is needed as new goods will eventually come to the warehouse and has to be tracked properly

## Pending Details

- [ ] Does warehouse itself able to execute dispatch order? This might be needed if we have 2 or more warehouses to send goods back and front for organizing or somethings
- [ ] Would we implement dispatch order? so order from Finance department can be carried immediately from the system?
- [ ] How does inbound request from other system being placed or processed?
- [ ] How does outbound request from other system being placed or processed?

## Requirements

- [ ] Employees master data (look up reference, this will be used to link which entry are created by whom)

## Dependencies

- [ ] [[BASE - Landing Page]]
- [ ] [[[...] - Warehouse Master Data]]
- [ ] Logging system
	- [ ] [[WH - Inbound (Receiving)]]
	- [ ] [[WH - Outbound (Sending)]]
- [ ] Other system that able to request to this system
