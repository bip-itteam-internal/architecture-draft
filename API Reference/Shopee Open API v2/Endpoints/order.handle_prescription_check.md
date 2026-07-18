# order.handle_prescription_check

- Path: `/api/v2/order/handle_prescription_check`
- Method: POST
- Auth: shop
- Deskripsi: Use this API to approve or reject a prescription
- Sumber: open.shopee.com/documents/v2/order.handle_prescription_check?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `order_sn` | string | ya | Shopee's unique identifier for an order. |
| `is_approved` | boolean | ya | Approve or reject the prescription. Available values: TRUE, FALSE. |
| `reject_reason_code` | int | tidak | Reject reason code. Available values: 1 = Invalid Prescription (counterfeit/incorrect format) 2 = Incorrect Dosage 3 = No Prescription 4 = Unclear Image 5 = Free Text |
| `items` | object[] | tidak | The list of invalid items that make the prescription get rejected |
| `pharmacist_name` | string | tidak | Full name of the pharmacist. Required for PH and ID Prescription Orders. |
| `free_text` | string | tidak | The reason for rejecting the prescription. Only usable when the reject_reason_code = 5. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `response` | object | Detail informations you are querying. |
| `response.is_success` | boolean | This is to indicate whether the request has been executed successfully. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
