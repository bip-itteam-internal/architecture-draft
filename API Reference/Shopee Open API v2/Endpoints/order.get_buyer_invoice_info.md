# order.get_buyer_invoice_info

- Path: `/api/v2/order/get_buyer_invoice_info`
- Method: POST
- Auth: shop
- Deskripsi: API to obtain buyer submitted invoice info for VN, TH and PH local sellers only.
- Sumber: open.shopee.com/documents/v2/order.get_buyer_invoice_info?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `queries` | object[] | ya |  |

## Response

| field | tipe | keterangan |
|---|---|---|
| `invoice_info_list` | object[] |  |
| `invoice_info_list[].order_sn` | string | Shopee's unique identifier for an order. |
| `invoice_info_list[].invoice_type` | string | Type of invoice requested: {1: personal, 2: company, 3: household}. |
| `invoice_info_list[].invoice_detail` | object | Invoice info submitted by buyer. Might be masked, e.g. A****b, depending on order status. |
| `invoice_info_list[].invoice_detail.name` | string | Buyer name (has value when invoice_type is personal, household, or company) - VN, TH, PH only |
| `invoice_info_list[].invoice_detail.email` | string | Buyer email address (has value when invoice_type is personal and household) - VN, TH, PH only |
| `invoice_info_list[].invoice_detail.phone_number` | string | Buyer phone number - TH only |
| `invoice_info_list[].invoice_detail.tax_id` | string | has value when invoice_type is personal and household. - VN, TH, PH only |
| `invoice_info_list[].invoice_detail.address` | string | Buyer address in format "Street & number, city, zipcode, any additional info provided by buyer" (has value when invoice_type is personal and household) - PH, VN only |
| `invoice_info_list[].invoice_detail.id_card_address` | string | Same function as the address, only having a different field name for TH.Buyer address in format "Street & number, city, zipcode, any additional info provided by buyer" (only has value when invoice_type is personal). |
| `invoice_info_list[].invoice_detail.address_breakdown` | object | Buyer address breakdown. - TH, PH only |
| `invoice_info_list[].invoice_detail.address_breakdown.region` | string | Return region value - PH, TH only |
| `invoice_info_list[].invoice_detail.address_breakdown.state` | string | Return value - TH: Province |
| `invoice_info_list[].invoice_detail.address_breakdown.city` | string | Return value - TH: District |
| `invoice_info_list[].invoice_detail.address_breakdown.town` | string | Return value - TH: Sub district |
| `invoice_info_list[].invoice_detail.address_breakdown.postcode` | string | Return value - TH: Postal code - PH: Postal code |
| `invoice_info_list[].invoice_detail.address_breakdown.detailed_address` | string | Return value - PH: Additional details, i.e. street name, building - TH: Additional details, i.e. house number |
| `invoice_info_list[].invoice_detail.address_breakdown.additional_info` | string | Return value: - Empty for PH, TH |
| `invoice_info_list[].invoice_detail.address_breakdown.full_address` | string | - only has value when invoice_type is personal - Buyer address in format "detailed_address, town, district, state, postcode, additional_info" for all regions --- for TH: leave the 'additional_info' as empty |
| `invoice_info_list[].invoice_detail.company_head_office` | string | - return value for TH only (only has value when invoice_type is company) |
| `invoice_info_list[].invoice_detail.company_name` | string | - Only return value when invoice type is company - VN, TH, PH only |
| `invoice_info_list[].invoice_detail.company_branch_name` | string | - Only return value when invoice type is company - TH only |
| `invoice_info_list[].invoice_detail.company_branch_id` | string | - Only return value when invoice type is company - TH only |
| `invoice_info_list[].invoice_detail.company_type` | string | - Only return value when invoice type is company - TH only |
| `invoice_info_list[].invoice_detail.company_email` | string | - Only return value when invoice type is company - VN, TH, PH only |
| `invoice_info_list[].invoice_detail.company_tax_id` | string | - Only return value when invoice type is company - VN, TH, PH only |
| `invoice_info_list[].invoice_detail.company_address` | string | Buyer address in format "Street & number,city, zipcode, any additional info provided by buyer" (only has value when invoice_type is company) - VN, TH only |
| `invoice_info_list[].invoice_detail.company_address_breakdown` | object | Company address breakdown - PH, TH only |
| `invoice_info_list[].invoice_detail.company_address_breakdown.company_region` | string | Return region value - PH, TH only |
| `invoice_info_list[].invoice_detail.company_address_breakdown.company_state` | string | Return value - PH: Province - TH: Province |
| `invoice_info_list[].invoice_detail.company_address_breakdown.company_city` | string | Return value - PH: City |
| `invoice_info_list[].invoice_detail.company_address_breakdown.company_district` | string | Return value - PH: Barangay - TH: District |
| `invoice_info_list[].invoice_detail.company_address_breakdown.company_town` | string | Return value - TH: Sub district |
| `invoice_info_list[].invoice_detail.company_address_breakdown.company_postcode` | string | Return postal code - TH, PH only |
| `invoice_info_list[].invoice_detail.company_address_breakdown.company_detailed_address` | string | Return value - PH: Detailed address - TH: Detailed address |
| `invoice_info_list[].invoice_detail.company_address_breakdown.company_additional_info` | string | Return value: - Empty for PH, TH |
| `invoice_info_list[].invoice_detail.company_address_breakdown.company_full_address` | string | Concatenation of company address breakdown - only has value when invoice_type is company |
| `invoice_info_list[].invoice_detail.household_address_breakdown` | object | Household address breakdown -Only for VN |
| `invoice_info_list[].invoice_detail.household_address_breakdown.household_region` | string | Region of the household address. |
| `invoice_info_list[].invoice_detail.household_address_breakdown.household_state` | string | State of the household address. |
| `invoice_info_list[].invoice_detail.household_address_breakdown.household_city` | string | City of the household address. |
| `invoice_info_list[].invoice_detail.household_address_breakdown.household_province` | string | Province of the household address. |
| `invoice_info_list[].invoice_detail.household_address_breakdown.household_district` | string | District of the household address. |
| `invoice_info_list[].invoice_detail.household_address_breakdown.household_town` | string | Town of the household address. |
| `invoice_info_list[].invoice_detail.household_address_breakdown.household_barangay` | string | Barangay of the household address. |
| `invoice_info_list[].invoice_detail.household_address_breakdown.household_postcode` | string | Postal code of the household address. |
| `invoice_info_list[].invoice_detail.household_address_breakdown.household_detailed_address` | string | Detailed street address of the household. |
| `invoice_info_list[].invoice_detail.household_address_breakdown.household_additional_info` | string | Additional address information provided by the buyer. |
| `invoice_info_list[].invoice_detail.household_address_breakdown.household_full_address` | string | Full formatted household address. |
| `invoice_info_list[].error` | string | Error in retrieving the receipt setting of a particular order. |
| `invoice_info_list[].is_requested` | boolean | To identify order with and without buyer request, applicable to PL. |
| `request_id` | string | Request id for debugging purposes |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
