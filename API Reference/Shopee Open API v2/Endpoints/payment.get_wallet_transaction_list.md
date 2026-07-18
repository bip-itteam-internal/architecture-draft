# payment.get_wallet_transaction_list

- Path: `/api/v2/payment/get_wallet_transaction_list`
- Method: GET
- Auth: shop
- Deskripsi: Use this API to get the transaction records of wallet. Only applicable for local shops
- Sumber: open.shopee.com/documents/v2/payment.get_wallet_transaction_list?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `page_no` | int | ya | Specifies the starting entry of data to return in the current call. Default is 0. if data is more than one page, the offset can be some entry to start next call. |
| `page_size` | int | ya | If many transactions are available to retrieve, you may need to call GetTransactionList multiple times to retrieve all the data. Each result set is returned as a page of entries. Default is 40. Use the Pagination filters to control the maximum number of entries (<= 100) to retrieve per page (i.e., per call), the offset number to start next call. This integer value is usUed to specify the maximum number of entries to return in a single ""page"" of data. |
| `create_time_from` | int | tidak | The create_time_from field is the starting date range. The maximum date range that may be specified with the create_time_from and create_time_to fields is 15 days. |
| `create_time_to` | int | tidak | The create_time_to field is the ending date range. The maximum date range that may be specified with the create_time_from and create_time_to fields is 15 days. |
| `wallet_type` | string | tidak | This field indicates the wallet type. |
| `transaction_type` | string | tidak | Transaction type APIs: ESCROW_VERIFIED_ADD = 101; // Escrow has been verified and paid to seller ESCROW_VERIFIED_MINUS = 102; // Escrow has been verified and charged from seller as escrow amount is negative WITHDRAWAL_CREATED = 201; // The seller has created a withdrawal, so it’s deducted from balance WITHDRAWAL_COMPLETED = 202; // The withdrawal has been completed, so the ongoing amount decreases. WITHDRAWAL_CANCELLED = 203; // The withdrawal has been canceled, so the amount is added back to the seller balance. Ongoing amount decreases as well. ADJUSTMENT_ADD = 401; // One adjustment item has been paid to seller ADJUSTMENT_MINUS = 402; // One adjustment item has been charged from seller FBS_ADJUSTMENT_ADD = 404; //One adjustment item related to Shopee fulfillment order is added to seller FBS_ADJUSTMENT_MINUS = 405; // One adjustment item related to Shopee fulfillment order is deducted from seller ADJUSTMENT_CENTER_ADD = 406; // One adjustment item has been added to seller wallet ADJUSTMENT_CENTER_DEDUCT = 407; // One adjustment item has been deducted from seller wallet FSF_COST_PASSING_DEDUCT = 408; FSF cost passing for canceled/invalid orders PERCEPTION_VAT_TAX_DEDUCT = 409; Extra charge for perception regime VAT tax (Argentina) PERCEPTION_TURNOVER_TAX_DEDUCT = 410; Extra charge for perception regime turnover tax (Argentina) PAID_ADS_CHARGE = 450; // Paid ads are charged from seller PAID_ADS_REFUND = 451; // Paid ads are refunded to seller FAST_ESCROW_DISBURSE = 452; // ADD. // The first disbursement of fast escrow has been paid to seller AFFILIATE_ADS_SELLER_FEE = 455; // DEDUCT // Affiliate ads seller fee is charged from seller AFFILIATE_ADS_SELLER_FEE_REFUND = 456; // ADD // Affiliate ads seller fee is refunded to seller FAST_ESCROW_DEDUCT = 458; // Fast escrow is deducted from seller balance in the event of return and refund FAST_ESCROW_DISBURSE_REMAIN = 459; // The second disbursement of fast escrow has been paid to seller AFFILIATE_FEE_DEDUCT = 460; // Affiliate MKT fee is charged from seller for using affiliate MKT services |
| `money_flow` | string | tidak | It's to indicate whether user wants to only return : MONEY_IN = addition MONEY_OUT = Deduction if not specified, we will return all Note special case for TW JKO Pay, we will ignore Money_flow |
| `transaction_tab_type` | string | tidak | NOTE: Only 1 'transaction tab type' value should be passed in. Passing in more than 1 value (eg: comma separated values) will return default response. This is because the request param treats the value passed in as a single string. This to indicates the updated filtering type that client can use to specify which transaction type we want to return. it will have : Default wallet_order_income wallet_adjustment_filter wallet_wallet_payment wallet_refund_from_order wallet_withdrawals fast_escrow_repayment fast_pay seller_loan corporate_loan pix_transactions_filter open_finance_transactions_filter Note for BR, wallet txn type that linked to pix_transactions_filter and open_finance_transactions_filter are classified as default type tab instead. therefore for Open API client who wants to query these 2 trx can put default as the filter in this type |

## Response

| field | tipe | keterangan |
|---|---|---|
| `response` | object |  |
| `response.transaction_list` | object[] |  |
| `response.transaction_list[].status` | string | The status of the transaction，available values: FAILED,COMPLETED,PENDING,INITIAL. |
| `response.transaction_list[].transaction_type` | string | The type of transaction. |
| `response.transaction_list[].txn_title` | string | The transaction title sent by client (Adjustment Center) for adjustments, Only for ID local sellers for now. |
| `response.transaction_list[].amount` | float | The amount of transaction. |
| `response.transaction_list[].current_balance` | float | The current balance of this account. |
| `response.transaction_list[].create_time` | int | The create time of the transaction. |
| `response.transaction_list[].order_sn` | string | Shopee's unique identifier for an order. |
| `response.transaction_list[].refund_sn` | string | The serial number of return. |
| `response.transaction_list[].withdrawal_type` | string | The type of withdrawal. |
| `response.transaction_list[].transaction_fee` | float | This field indicates the transaction fee. |
| `response.transaction_list[].description` | string | The detailed description of TOPUP SUCCESS and TOPUP FAILED. |
| `response.transaction_list[].buyer_name` | string | The name of buyer. |
| `response.transaction_list[].pay_order_list` | object[] |  |
| `response.transaction_list[].pay_order_list[].order_sn` | string | Shopee's unique identifier for an order. |
| `response.transaction_list[].pay_order_list[].shop_name` | string | Name of the shop. |
| `response.transaction_list[].shop_name` | string | Name of the shop. |
| `response.transaction_list[].withdrawal_id` | int | Withdrawal ID when transaction type is withdraw_created, withdrawal_completed, withdrawal_cancelled. |
| `response.transaction_list[].reason` | string | The reason for ADJUSTMENT_ADD and ADJUSTMENT_MINUS. |
| `response.transaction_list[].root_withdrawal_id` | int | Use this field to indicate the event where a withdrawal is split into several withdrawals due to the withdrawal limit. |
| `response.transaction_list[].transaction_tab_type` | string | Description: A new response parameter added after: https://confluence.shopee.io/display/SPCT/%5BPRD%5D+%5BOpen+API%5D+Update+on+New+Open+API+to+fetch+Seller+wallet+Transaction This returns the updated transaction tab types that client can use to specify which transaction types they want to return. It will have the following tab types Default wallet_order_income wallet_adjustment_filter wallet_wallet_payment wallet_refund_from_order wallet_withdrawals fast_escrow_repayment fast_pay seller_loan corporate_loan pix_transactions_filter open_finance_transactions_filter Note for BR, currently in SOP live configuration, wallet txn type that linked to pix_transactions_filter and open_finance_transactions_filter are classified as default type tab instead. therefore for Open API client who wants to query these 2 txn can put default as the filter in this type |
| `response.transaction_list[].money_flow` | string | New response parameter provided after: https://confluence.shopee.io/display/SPCT/%5BPRD%5D+%5BOpen+API%5D+Update+on+New+Open+API+to+fetch+Seller+wallet+Transaction It's to indicate the money flow MONEY_IN = addition MONEY_OUT = deduction if not specified in request, will return both Note special case for TW JKO Pay, we will ignore Money_flow |
| `response.transaction_list[].outlet_shop_name` | string | The outlet shop name where this outlet transaction came from. (In the Original Instant Mart concept, outlet transactions are redirected to Mart.) |
| `response.more` | boolean |  |
| `request_id` | string |  |
| `message` | string |  |
| `error` | string |  |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
