## Notes

*This system name is misleading as this didn't manage fully for Internal Inventory and external inventory altogether. This only manage inventory used form purchase/procurement for production and sales of said products*

## Consideration

Can this be merged with internal inventory? As both will probably have a lot of feature the same, we could put it in here and add additional tags for items that is being used internally. 

Might be undesiredable if internal inventory aren't natively managed by GA

## Features

- Dashboard
	- Overview of everything excellent for reporting to stakeholders
	- Summary in details: purchases, sales, stocks and profits
	- Volume activity or stock changes
- Purchases (Why this feature in here?)
	- Normal purchase/procurement for product, with vendor/supplier details
	- Because GA (General Affairs) has a petty cash fund used for expenses that are consumed within one month — for example, purchasing office supplies, cleaning equipment, or submitting requests for items not exceeding 2 million rupiah per month.
	- If so then Finance are still the sole owner of purchasing system, and GA are able request and see their accepted procurement entries
- Sales (Why this feature in here?)
	- Normal sales for product, but no information on where the product being sold to
	- I agree, better to move this feature to it's own module (eg: move to Finance System)
* OCR Document
	* dokumen fisik yang ada bisa di scan berbentuk gambar yang nantinya diupload ke sistem 
	* OCR akan membaca dokumen tersebut dan bisa dimanfaatkan untuk kebutuhan lain
	* misal: pencarian title dokumen, isi dokumen, nomor tertentu di dalam dokumen

## Issues that might come from other departments

- Finance
	- Purchase/procurement order is required to validate the entry
	- Sales order is required to validate the entry
- Warehouse
	- Additional document to validate said product is being moved around inbound/outbound of the warehouse

## Requirements

- [ ] Warehouse master data (look up reference)
- [ ] Purchase data from finance
- [ ] Sales data from finance

## Dependencies

- [ ] [[Unlisted - Warehouse Master Data]]
