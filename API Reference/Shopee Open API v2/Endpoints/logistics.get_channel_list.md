# logistics.get_channel_list

- Path: `/api/v2/logistics/get_channel_list`
- Method: GET
- Auth: shop
- Deskripsi: Use this api to get all supported logistic channels.
- Sumber: open.shopee.com/documents/v2/logistics.get_channel_list?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

_Tidak ada parameter request selain common params._

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object | Detail informations you are querying. |
| `response.logistics_channel_list` | object[] | The list of logistics channel. |
| `response.logistics_channel_list[].logistics_channel_id` | int64 | The identity of logistic channel. |
| `response.logistics_channel_list[].logistics_channel_name` | string | The name of logistic channel. |
| `response.logistics_channel_list[].cod_enabled` | boolean | This is to indicate whether this logistic channel supports COD |
| `response.logistics_channel_list[].enabled` | boolean | Whether this logistic channel is enabled on shop level. |
| `response.logistics_channel_list[].fee_type` | string | SIZE_SELECTION SIZE_INPUT FIXED_DEFAULT_PRICE CUSTOM_PRICE |
| `response.logistics_channel_list[].size_list` | object[] | Only for fee_type is SIZE_SELECTION |
| `response.logistics_channel_list[].size_list[].size_id` | string | The identity of size. |
| `response.logistics_channel_list[].size_list[].name` | string | The name of size. |
| `response.logistics_channel_list[].size_list[].default_price` | float | The pre-defined shipping fee for the specific size. |
| `response.logistics_channel_list[].weight_limit` | object | The weight limit for this logistic channel. |
| `response.logistics_channel_list[].weight_limit.item_max_weight` | float | The max weight for an item on this logistic channel.If the value is 0 or null, that means there is no limit. |
| `response.logistics_channel_list[].weight_limit.item_min_weight` | float | The min weight for an item on this logistic channel. If the value is 0 or null, that means there is no limit. |
| `response.logistics_channel_list[].item_max_dimension` | object | The dimension limit for this logistic channel. |
| `response.logistics_channel_list[].item_max_dimension.height` | float | The max height limit. |
| `response.logistics_channel_list[].item_max_dimension.width` | float | The max width limit. |
| `response.logistics_channel_list[].item_max_dimension.length` | float | The max length limit. |
| `response.logistics_channel_list[].item_max_dimension.unit` | string | The unit for the limit. |
| `response.logistics_channel_list[].item_max_dimension.dimension_sum` | float | The sum of the item's dimension |
| `response.logistics_channel_list[].volume_limit` | object | The limit of item volume. |
| `response.logistics_channel_list[].volume_limit.item_max_volume` | float | The max volume for an item on this logistic channel.If the value is 0 or null, that means there is no limit for the item weight. |
| `response.logistics_channel_list[].volume_limit.item_min_volume` | float | The min volume for an item on this logistic channel. If the value is 0 or null, that means there is no limit for the item weight. |
| `response.logistics_channel_list[].logistics_description` | string | For checkout channels, this field indicates its corresponding fulfillment channels. |
| `response.logistics_channel_list[].force_enable` | boolean | Indicates whether the logistic channel is force enabled on Shop Level. If true, sellers cannot close this channel. |
| `response.logistics_channel_list[].mask_channel_id` | int64 | Indicate the parent logistic channel ID. If it’s 0, it indicates the channel is a checkout(masked) channel; if it’s not 0, indicate the channel is a fulfillment channel and has a checkout channel(checkout channel’s channel_id equals this mask_channel_id) on top of it. Multiple channels may share the same mask_channel_id. |
| `response.logistics_channel_list[].block_seller_cover_shipping_fee` | boolean | Indicate whether the channel is blocked to use seller cover shipping fee function. if the channel does not allow sellers to cover shipping fee, then the block_seller_cover_shipping_fee field will return true, otherwise it will return false. |
| `response.logistics_channel_list[].support_cross_border` | boolean | Indicate whether this channel support cross border shipping. |
| `response.logistics_channel_list[].seller_logistic_has_configuration` | boolean | Indicate If seller has set the Seller logistics configuration if set will return true, otherwise it will return false or null. |
| `response.logistics_channel_list[].logistics_capability` | object | The capability of one logistic channel. |
| `response.logistics_channel_list[].logistics_capability.seller_logistics` | boolean | Indicate If it's a Seller logistics channel, if it's a Seller logistics channel will return true, otherwise it will return false. |
| `response.logistics_channel_list[].preprint` | boolean | Indicate whether this channel support pre-print AWB |
| `response.logistics_channel_list[].service_type_identifier` | string | This parameter specifies the delivery service type of logistics channel. Applicable values: - instant - same_day - null |
| `response.logistics_channel_list[].auto_call_driver_setting` | object |  |
| `response.logistics_channel_list[].auto_call_driver_setting.auto_call_driver_eligible` | boolean | Indicate whether this channel is eligible for Auto Call Driver. |
| `response.logistics_channel_list[].auto_call_driver_setting.auto_call_driver_enabled` | boolean | Indicate whether Auto Call Driver is currently enabled for this channel |
| `response.logistics_channel_list[].auto_call_driver_setting.preparation_time` | int32 | The current valid preparation time for this channel, in minutes. |
| `response.logistics_channel_list[].auto_call_driver_setting.preparation_time_limit` | object | The preparation time range allowed for this channel. Note: When calling v2.logistics.update_channel to set the Preparation Time for the channel, the time must not exceed this range. |
| `response.logistics_channel_list[].auto_call_driver_setting.preparation_time_limit.min_preparation_time` | int32 | The minimum allowable preparation time, in minutes. |
| `response.logistics_channel_list[].auto_call_driver_setting.preparation_time_limit.max_preparation_time` | int32 | The maximum allowable preparation time, in minutes. |
| `response.logistics_channel_list[].support_pause` | boolean | Indicates whether this channel supports the pause operation (Pausing allows the shop to temporarily prevent buyers from placing orders through this logistics channel). - true: This channel is affected by the pause function. - false: This channel is not affected by the pause function. Note: Please first call v2.logistics.get_pause_status to get the current pause status of logistics channels under the shop. If is_paused = true, then call v2.logistics.get_channel_list and identify the range of channels affected by the pause function through support_pause = true. |
| `response.logistics_channel_list[].compulsory_channel` | boolean | Indicates if the channel is compulsory. If the value is true, at least one such channel must be enabled. |
| `response.logistics_channel_list[].channel_relation_rules` | object[] | Indicate the related rules & channels of this logistic channel. |
| `response.logistics_channel_list[].channel_relation_rules[].related_enabled_channels` | int64[] | Channels that will be auto-enabled in the same request if this channel is enabled. |
| `response.logistics_channel_list[].channel_relation_rules[].related_dependent_block_channels` | int64[] | Channels that must be disabled before or while disabling this parent channel. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
