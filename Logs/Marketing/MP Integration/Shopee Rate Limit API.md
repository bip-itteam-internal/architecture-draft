# Shopee API Rate Limit Increase — Response to OpenAPI Team

**Partner ID:** 2032638 (Ads Bharata)  
**Response Date:** 2026-06-23  
**Reference Period:** 2026-06-20 – 2026-06-22 (3 days)

---

## 1. Detailed Request Information for Each API

### 1.1 v2.ads.get_gms_item_performance

**Purpose:**  
This API is called to retrieve item-level GMS (Gross Merchandise Sales) performance data for each seller shop connected to our ERP platform. The data covers metrics such as GMV, clicks, impressions, CPC, and ROI per product item per campaign. It is used to generate daily performance reports for our merchant clients.

**Method:** `POST`  
**Endpoint:** `https://partner.shopeemobile.com/api/v2/ads/get_gms_item_performance`

**Query Parameters (URL):**

| Parameter | Type | Description |
|---|---|---|
| `partner_id` | string | Application Partner ID |
| `timestamp` | int64 | Unix timestamp at time of request |
| `access_token` | string | Shop's OAuth access token |
| `shop_id` | int64 | Target shop ID |
| `sign` | string | HMAC-SHA256 signature |

**Request Body (JSON):**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `campaign_id` | int64 | Yes | Campaign ID. Use `0` to retrieve all campaigns |
| `start_date` | string | Yes | Report start date in `DD-MM-YYYY` format |
| `end_date` | string | Yes | Report end date in `DD-MM-YYYY` format |
| `offset` | int64 | Yes | Pagination offset (starts at 0) |
| `limit` | int64 | Yes | Number of records per page (max: 100) |

---

### 1.2 v2.ads.get_gms_campaign_performance

**Purpose:**  
This API is called to retrieve campaign-level GMS performance data for each seller shop. The data covers campaign-wide metrics such as total GMV, broad ROI, clicks, CPC, and conversion rates. It is used alongside item-level data to provide complete campaign performance dashboards for our merchant clients.

**Method:** `POST`  
**Endpoint:** `https://partner.shopeemobile.com/api/v2/ads/get_gms_campaign_performance`

**Query Parameters (URL):**

| Parameter | Type | Description |
|---|---|---|
| `partner_id` | string | Application Partner ID |
| `timestamp` | int64 | Unix timestamp at time of request |
| `access_token` | string | Shop's OAuth access token |
| `shop_id` | int64 | Target shop ID |
| `sign` | string | HMAC-SHA256 signature |

**Request Body (JSON):**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `campaign_id` | int64 | Yes | Campaign ID. Use `0` to retrieve all campaigns |
| `start_date` | string | Yes | Report start date in `DD-MM-YYYY` format |
| `end_date` | string | Yes | Report end date in `DD-MM-YYYY` format |

---

## 2. Current Usage Metrics

**Job Schedule:** Daily automated sync at **02:00 WIB (UTC+07:00)**  
**Sync Window per Run:** Last 3 days of data per execution  
**Concurrency Architecture:** Maximum 3 shops running simultaneously, maximum 5 concurrent requests per shop  
**Connected Shops (observed):** 8 shops (shop IDs: 898309034, 940147456, 914603669, 823286268, 1005619049, 1440882595, 1726433082, 908963392)

### Usage Summary (2026-06-20 to 2026-06-22)

| Metric | `get_gms_item_performance` | `get_gms_campaign_performance` | Combined |
|---|---|---|---|
| **Total calls (3 days)** | 36 | 28 | **64** |
| **Average calls per day** | 12 | ~10 | **~22** |
| **Active call window** | 02:00:00–02:00:02 WIB | 02:00:01–02:00:03 WIB | ~3–4 seconds |
| **Current QPS (peak)** | ~7 calls/sec | ~4 calls/sec | **~10–11 calls/sec** |
| **Average RPM (during window)** | ~12 RPM | ~10 RPM | **~22 RPM** |
| **Peak volume per run** | ~12 calls | ~10 calls | **~22 calls** |
| **Success calls (3 days)** | 18 | 16 | 34 |
| **Failed calls (3 days)** | 18 | 12 | 30 |
| **Success rate** | 50% | 57.1% | — |

> **Key Note:** All API calls are concentrated within a **2–4 second burst window** at 02:00 WIB due to parallel execution across multiple shops. Despite the low absolute call volume (~22 calls/day total), the daily call limit is reached before all shops can be synced. This directly impacts the completeness of our merchant performance data.

---

## 3. Full API Request & Response Details

> **Note:** `access_token` and `sign` parameters are masked for security. All other values are actual data retrieved from the Shopee Open Platform API Access Log (Partner ID: 2032638, period: 2026-06-20 to 2026-06-22).

---

### 3.1 v2.ads.get_gms_item_performance

#### Example A — Successful Response

| Field | Value |
|---|---|
| **Request Time** | `2026-06-22 02:00:00 (UTC+07:00 / WIB)` |
| **request_id** | `e3e3e7f354c821f70efbe856385d300` |
| **shop_id** | `823286268` |
| **HTTP Status** | `200` |

**Full cURL Request:**

```bash
curl --location --request POST \
'https://partner.shopeemobile.com/api/v2/ads/get_gms_item_performance?partner_id=2032638&shop_id=823286268&timestamp=1782068400&access_token=<access_token>&sign=<sign>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "campaign_id": 0,
  "start_date": "20-06-2026",
  "end_date": "20-06-2026",
  "offset": 0,
  "limit": 100
}'
```

**Full Response Body:**

```json
{
  "error": "",
  "message": "",
  "warning": "",
  "request_id": "e3e3e7f354c821f70efbe856385d300",
  "response": {
    "campaign_id": 445729906,
    "has_next_page": false,
    "total": 12,
    "result_list": [
      {
        "item_id": 18359703872,
        "report": {
          "broad_cir": 0.2,
          "broad_gmv": 1188000,
          "broad_order": 12,
          "broad_order_amount": 12,
          "broad_roi": 0.2,
          "clicks": 264,
          "expense": 0,
          "cpc": 0,
          "cpdc": 0,
          "cr": 0,
          "direct_cr": 0,
          "direct_cir": 0,
          "direct_order": 0,
          "direct_order_amount": 0,
          "direct_roi": 0,
          "impression": 0
        }
      }
    ]
  }
}
```

---

#### Example B — Failed Response (Daily Limit Reached)

| Field | Value |
|---|---|
| **Request Time** | `2026-06-21 02:00:02 (UTC+07:00 / WIB)` |
| **request_id** | `e3e3e7f354b40442d084e9a48e52600` |
| **shop_id** | `898309034` |
| **HTTP Status** | `429` |

**Full cURL Request:**

```bash
curl --location --request POST \
'https://partner.shopeemobile.com/api/v2/ads/get_gms_item_performance?partner_id=2032638&shop_id=898309034&timestamp=1781982002&access_token=<access_token>&sign=<sign>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "campaign_id": 0,
  "start_date": "18-06-2026",
  "end_date": "18-06-2026",
  "offset": 0,
  "limit": 100
}'
```

**Full Response Body:**

```json
{
  "error": "error_limit",
  "message": "The total API call number made by your APP has reached the daily API call limit, please try again after 00:00 (UTC+08:00)",
  "warning": null,
  "request_id": "e3e3e7f354b40442d084e9a48e52600",
  "response": null
}
```

---

### 3.2 v2.ads.get_gms_campaign_performance

#### Example A — Successful Response

| Field | Value |
|---|---|
| **Request Time** | `2026-06-21 02:00:01 (UTC+07:00 / WIB)` |
| **request_id** | `e3e3e7f354b4042e3b89894864076d00` |
| **shop_id** | `940147456` |
| **HTTP Status** | `200` |

**Full cURL Request:**

```bash
curl --location --request POST \
'https://partner.shopeemobile.com/api/v2/ads/get_gms_campaign_performance?partner_id=2032638&shop_id=940147456&timestamp=1781982001&access_token=<access_token>&sign=<sign>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "campaign_id": 0,
  "start_date": "19-06-2026",
  "end_date": "19-06-2026"
}'
```

**Full Response Body:**

```json
{
  "error": "",
  "message": "",
  "warning": "",
  "request_id": "e3e3e7f354b4042e3b89894864076d00",
  "response": {
    "campaign_id": 446801171,
    "report": {
      "broad_cir": 0,
      "broad_gmv": 2541500,
      "broad_order": 23,
      "broad_order_amount": 27,
      "broad_roi": 5.87,
      "clicks": 307,
      "expense": 1881014855,
      "cpc": 1881014855,
      "cpdc": 0,
      "cr": 0,
      "direct_cr": 0,
      "direct_cir": 0,
      "direct_order": 0,
      "direct_order_amount": 0,
      "direct_roi": 0,
      "impression": 0
    }
  }
}
```

---

#### Example B — Failed Response (Daily Limit Reached)

| Field | Value |
|---|---|
| **Request Time** | `2026-06-22 02:00:02 (UTC+07:00 / WIB)` |
| **request_id** | `e3e3e7f354c8221574e3dd81daec0f00` |
| **shop_id** | `1005619049` |
| **HTTP Status** | `429` |

**Full cURL Request:**

```bash
curl --location --request POST \
'https://partner.shopeemobile.com/api/v2/ads/get_gms_campaign_performance?partner_id=2032638&shop_id=1005619049&timestamp=1782068402&access_token=<access_token>&sign=<sign>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "campaign_id": 0,
  "start_date": "19-06-2026",
  "end_date": "19-06-2026"
}'
```

**Full Response Body:**

```json
{
  "error": "error_limit",
  "message": "The total API call number made by your APP has reached the daily API call limit, please try again after 00:00 (UTC+08:00)",
  "warning": null,
  "request_id": "e3e3e7f354c8221574e3dd81daec0f00",
  "response": null
}
```

---

## 4. Additional Context — Why Rate Limit Increase is Needed

Our application is a multi-tenant ERP platform serving multiple Shopee merchant accounts. Each merchant's shop requires individual API calls because:

1. **Access token is shop-scoped** — each shop has its own `access_token`, requiring separate API calls per shop
2. **Daily sync covers 3 days** — to ensure data completeness and handle late-updated metrics, we sync the last 3 days per run
3. **Growing merchant base** — we currently have **8 connected shops**, and the number is expected to grow

With the current daily limit, approximately **50% of API calls fail** before all shops can be synced. This means merchants on our platform receive incomplete performance data, directly impacting their ability to optimize advertising spend on Shopee.

We are requesting a rate limit increase to support our current and projected merchant volume without data gaps.

---

*All request_id values and timestamps above can be verified in the API Access Log of Partner ID 2032638 on the Shopee Open Platform Console.*
