# logistics.get_operating_hour_restrictions

- Path: `/api/v2/logistics/get_operating_hour_restrictions`
- Method: GET
- Auth: shop
- Deskripsi: This API is designed to retrieve all restrictions related to inputting operating hours for the v2.logistics.update_operating_hours function. This API ensures that user are aware of any limitations or conditions that may affect their operating hours.
- Sumber: open.shopee.com/documents/v2/logistics.get_operating_hour_restrictions?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

_Tidak ada parameter request selain common params._

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.regular_operating_hour_restrictions` | object | The restrictions for Pickup Operating Hours / Preferred Pickup Hours |
| `response.regular_operating_hour_restrictions.minimum_working_days_in_week` | int64 | Minimum number of days the seller needs to designate as working days per week (including Monday to Sunday, but excluding public holidays from the count). |
| `response.regular_operating_hour_restrictions.working_day_config` | object | The restrictions specific to each day |
| `response.regular_operating_hour_restrictions.working_day_config.monday` | object | The restrictions specific for Monday |
| `response.regular_operating_hour_restrictions.working_day_config.monday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.regular_operating_hour_restrictions.working_day_config.monday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.regular_operating_hour_restrictions.working_day_config.monday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.monday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.monday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.monday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.monday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.regular_operating_hour_restrictions.working_day_config.tuesday` | object | The restrictions specific for Tuesday |
| `response.regular_operating_hour_restrictions.working_day_config.tuesday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.regular_operating_hour_restrictions.working_day_config.tuesday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.regular_operating_hour_restrictions.working_day_config.tuesday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.tuesday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.tuesday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.tuesday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.tuesday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.regular_operating_hour_restrictions.working_day_config.wednesday` | object | The restrictions specific for Wednesday |
| `response.regular_operating_hour_restrictions.working_day_config.wednesday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.regular_operating_hour_restrictions.working_day_config.wednesday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.regular_operating_hour_restrictions.working_day_config.wednesday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.wednesday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.wednesday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.wednesday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.wednesday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.regular_operating_hour_restrictions.working_day_config.thursday` | object | The restrictions specific for Thursday |
| `response.regular_operating_hour_restrictions.working_day_config.thursday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.regular_operating_hour_restrictions.working_day_config.thursday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.regular_operating_hour_restrictions.working_day_config.thursday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.thursday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.thursday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.thursday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.thursday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.regular_operating_hour_restrictions.working_day_config.friday` | object | The restrictions specific for Friday |
| `response.regular_operating_hour_restrictions.working_day_config.friday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.regular_operating_hour_restrictions.working_day_config.friday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.regular_operating_hour_restrictions.working_day_config.friday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.friday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.friday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.friday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.friday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.regular_operating_hour_restrictions.working_day_config.saturday` | object | The restrictions specific for Saturday |
| `response.regular_operating_hour_restrictions.working_day_config.saturday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.regular_operating_hour_restrictions.working_day_config.saturday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.regular_operating_hour_restrictions.working_day_config.saturday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.saturday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.saturday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.saturday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.saturday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.regular_operating_hour_restrictions.working_day_config.sunday` | object | The restrictions specific for Sunday |
| `response.regular_operating_hour_restrictions.working_day_config.sunday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.regular_operating_hour_restrictions.working_day_config.sunday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.regular_operating_hour_restrictions.working_day_config.sunday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.sunday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.sunday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.sunday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.sunday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.regular_operating_hour_restrictions.working_day_config.public_holiday` | object | The restrictions specific for public holiday |
| `response.regular_operating_hour_restrictions.working_day_config.public_holiday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.regular_operating_hour_restrictions.working_day_config.public_holiday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.regular_operating_hour_restrictions.working_day_config.public_holiday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.public_holiday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.public_holiday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.public_holiday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.regular_operating_hour_restrictions.working_day_config.public_holiday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.instant_operating_hour_restrictions` | object | The restrictions for Instant Operating Hours |
| `response.instant_operating_hour_restrictions.minimum_working_days_in_week` | int64 | Minimum number of days the seller needs to designate as working days per week (including Monday to Sunday, but excluding public holidays from the count). |
| `response.instant_operating_hour_restrictions.working_day_config` | object | The restrictions specific to each day |
| `response.instant_operating_hour_restrictions.working_day_config.monday` | object | The restrictions specific for Monday |
| `response.instant_operating_hour_restrictions.working_day_config.monday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.instant_operating_hour_restrictions.working_day_config.monday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.instant_operating_hour_restrictions.working_day_config.monday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.monday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.monday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.monday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.monday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.instant_operating_hour_restrictions.working_day_config.tuesday` | object | The restrictions specific for Tuesday |
| `response.instant_operating_hour_restrictions.working_day_config.tuesday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.instant_operating_hour_restrictions.working_day_config.tuesday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.instant_operating_hour_restrictions.working_day_config.tuesday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.tuesday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.tuesday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.tuesday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.tuesday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.instant_operating_hour_restrictions.working_day_config.wednesday` | object | The restrictions specific for Wednesday |
| `response.instant_operating_hour_restrictions.working_day_config.wednesday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.instant_operating_hour_restrictions.working_day_config.wednesday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.instant_operating_hour_restrictions.working_day_config.wednesday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.wednesday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.wednesday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.wednesday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.wednesday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.instant_operating_hour_restrictions.working_day_config.thursday` | object | The restrictions specific for Thursday |
| `response.instant_operating_hour_restrictions.working_day_config.thursday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.instant_operating_hour_restrictions.working_day_config.thursday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.instant_operating_hour_restrictions.working_day_config.thursday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.thursday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.thursday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.thursday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.thursday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.instant_operating_hour_restrictions.working_day_config.friday` | object | The restrictions specific for Friday |
| `response.instant_operating_hour_restrictions.working_day_config.friday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.instant_operating_hour_restrictions.working_day_config.friday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.instant_operating_hour_restrictions.working_day_config.friday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.friday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.friday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.friday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.friday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.instant_operating_hour_restrictions.working_day_config.saturday` | object | The restrictions specific for Saturday |
| `response.instant_operating_hour_restrictions.working_day_config.saturday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.instant_operating_hour_restrictions.working_day_config.saturday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.instant_operating_hour_restrictions.working_day_config.saturday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.saturday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.saturday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.saturday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.saturday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.instant_operating_hour_restrictions.working_day_config.sunday` | object | The restrictions specific for Sunday |
| `response.instant_operating_hour_restrictions.working_day_config.sunday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.instant_operating_hour_restrictions.working_day_config.sunday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.instant_operating_hour_restrictions.working_day_config.sunday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.sunday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.sunday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.sunday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.sunday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.instant_operating_hour_restrictions.working_day_config.public_holiday` | object | The restrictions specific for public holiday |
| `response.instant_operating_hour_restrictions.working_day_config.public_holiday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.instant_operating_hour_restrictions.working_day_config.public_holiday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.instant_operating_hour_restrictions.working_day_config.public_holiday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.public_holiday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.public_holiday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.public_holiday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.instant_operating_hour_restrictions.working_day_config.public_holiday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.special_operating_hour_restrictions` | object | The restrictions for Special Operating Hours |
| `response.special_operating_hour_restrictions.special_day` | object |  |
| `response.special_operating_hour_restrictions.special_day.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.special_operating_hour_restrictions.special_day.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.special_operating_hour_restrictions.special_day.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.special_operating_hour_restrictions.special_day.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.special_operating_hour_restrictions.special_day.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.special_operating_hour_restrictions.special_day.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.special_operating_hour_restrictions.special_day.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.shop_collection_operating_hour_restrictions` | object | The restrictions for Shop Collection Operating Hours |
| `response.shop_collection_operating_hour_restrictions.minimum_working_days_in_week` | int64 | Minimum number of days the seller needs to designate as working days per week (including Monday to Sunday, but excluding public holidays from the count). |
| `response.shop_collection_operating_hour_restrictions.working_day_config` | object | The restrictions specific to each day |
| `response.shop_collection_operating_hour_restrictions.working_day_config.monday` | object | The restrictions specific for Monday |
| `response.shop_collection_operating_hour_restrictions.working_day_config.monday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.monday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.monday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.monday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.monday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.monday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.monday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.tuesday` | object | The restrictions specific for Tuesday |
| `response.shop_collection_operating_hour_restrictions.working_day_config.tuesday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.tuesday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.tuesday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.tuesday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.tuesday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.tuesday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.tuesday.operating_24_hour_toggle` | string | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.wednesday` | object | The restrictions specific for Wednesday |
| `response.shop_collection_operating_hour_restrictions.working_day_config.wednesday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.wednesday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.wednesday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.wednesday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.wednesday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.wednesday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.wednesday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.thursday` | object | The restrictions specific for Thursday |
| `response.shop_collection_operating_hour_restrictions.working_day_config.thursday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.thursday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.thursday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.thursday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.thursday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.thursday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.thursday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.friday` | object | The restrictions specific for Friday |
| `response.shop_collection_operating_hour_restrictions.working_day_config.friday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.friday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.friday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.friday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.friday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.friday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.friday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.saturday` | object | The restrictions specific for Saturday |
| `response.shop_collection_operating_hour_restrictions.working_day_config.saturday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.saturday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.saturday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.saturday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.saturday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.saturday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.saturday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.sunday` | object | The restrictions specific for Sunday |
| `response.shop_collection_operating_hour_restrictions.working_day_config.sunday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.sunday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.sunday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.sunday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.sunday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.sunday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.sunday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.public_holiday` | object | The restrictions specific for Public Holiday |
| `response.shop_collection_operating_hour_restrictions.working_day_config.public_holiday.mandatory` | boolean | If the value is true, this day must be marked as open. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.public_holiday.minimum_operating_hour` | int64 | Minimum number of hours required for the seller to operate on that day. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.public_holiday.minimum_start_time` | string | The start hour for that day should not be set earlier than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.public_holiday.maximum_start_time` | string | The start hour for that day should not be set later than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.public_holiday.minimum_end_time` | string | The end hour for that day should not be set earlier than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.public_holiday.maximum_end_time` | string | The end hour for that day should not be set later than this time. |
| `response.shop_collection_operating_hour_restrictions.working_day_config.public_holiday.operating_24_hour_toggle` | boolean | If the toggle value is true, the user can set the start_time to 00:00 and the end_time to 23:59 to indicate that the shop is operating 24 hours a day. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
