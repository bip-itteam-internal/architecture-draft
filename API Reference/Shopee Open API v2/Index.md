# Shopee Open API v2 — Endpoint Index

Total **367 endpoint** / 15 modul. Digenerate 2026-07-18 dari `QuoVadis86/shopee-sdk`.

> Index saja. Parameter request/response TIDAK ada di sini —
> lihat `Endpoints/` atau ambil detailnya sesuai alur di README.
> Kolom `method` diturunkan dari SDK, sifatnya indikatif.

## Modul

`ads` (20) · `ams` (49) · `auth` (3) · `br` (4) · `global_product` (33) · `logistics` (50) · `media` (18) · `order` (16) · `partner` (7) · `payment` (16) · `product` (50) · `promotion` (66) · `returns` (8) · `shop` (23) · `warehouse` (4)

## ads

| method | path | doc |
|---|---|---|
| GET | `/api/v2/ads/check_create_gms_product_campaign_eligibility` | https://open.shopee.com/documents/v2/ads.check_create_gms_product_campaign_eligibility?module=&type=1 |
| POST | `/api/v2/ads/create_gms_product_campaign` | https://open.shopee.com/documents/v2/ads.create_gms_product_campaign?module=&type=1 |
| POST | `/api/v2/ads/create_manual_product_ads` | https://open.shopee.com/documents/v2/ads.create_manual_product_ads?module=&type=1 |
| POST | `/api/v2/ads/edit_gms_item_product_campaign` | https://open.shopee.com/documents/v2/ads.edit_gms_item_product_campaign?module=&type=1 |
| POST | `/api/v2/ads/edit_gms_product_campaign` | https://open.shopee.com/documents/v2/ads.edit_gms_product_campaign?module=&type=1 |
| POST | `/api/v2/ads/edit_manual_product_ad_keywords` | https://open.shopee.com/documents/v2/ads.edit_manual_product_ad_keywords?module=&type=1 |
| POST | `/api/v2/ads/edit_manual_product_ads` | https://open.shopee.com/documents/v2/ads.edit_manual_product_ads?module=&type=1 |
| GET | `/api/v2/ads/get_ads_facil_shop_rate` | https://open.shopee.com/documents/v2/ads.get_ads_facil_shop_rate?module=&type=1 |
| GET | `/api/v2/ads/get_all_cpc_ads_daily_performance` | https://open.shopee.com/documents/v2/ads.get_all_cpc_ads_daily_performance?module=&type=1 |
| GET | `/api/v2/ads/get_all_cpc_ads_hourly_performance` | https://open.shopee.com/documents/v2/ads.get_all_cpc_ads_hourly_performance?module=&type=1 |
| GET | `/api/v2/ads/get_create_product_ad_budget_suggestion` | https://open.shopee.com/documents/v2/ads.get_create_product_ad_budget_suggestion?module=&type=1 |
| GET | `/api/v2/ads/get_gms_campaign_performance` | https://open.shopee.com/documents/v2/ads.get_gms_campaign_performance?module=&type=1 |
| GET | `/api/v2/ads/get_gms_item_performance` | https://open.shopee.com/documents/v2/ads.get_gms_item_performance?module=&type=1 |
| GET | `/api/v2/ads/get_product_campaign_daily_performance` | https://open.shopee.com/documents/v2/ads.get_product_campaign_daily_performance?module=&type=1 |
| GET | `/api/v2/ads/get_product_campaign_hourly_performance` | https://open.shopee.com/documents/v2/ads.get_product_campaign_hourly_performance?module=&type=1 |
| GET | `/api/v2/ads/get_product_level_campaign_id_list` | https://open.shopee.com/documents/v2/ads.get_product_level_campaign_id_list?module=&type=1 |
| GET | `/api/v2/ads/get_product_level_campaign_setting_info` | https://open.shopee.com/documents/v2/ads.get_product_level_campaign_setting_info?module=&type=1 |
| GET | `/api/v2/ads/get_product_recommended_roi_target` | https://open.shopee.com/documents/v2/ads.get_product_recommended_roi_target?module=&type=1 |
| GET | `/api/v2/ads/get_recommended_item_list` | https://open.shopee.com/documents/v2/ads.get_recommended_item_list?module=&type=1 |
| GET | `/api/v2/ads/get_recommended_keyword_list` | https://open.shopee.com/documents/v2/ads.get_recommended_keyword_list?module=&type=1 |

## ams

| method | path | doc |
|---|---|---|
| POST | `/api/v2/ams/add_all_products_to_open_campaign` | https://open.shopee.com/documents/v2/ams.add_all_products_to_open_campaign?module=&type=1 |
| POST | `/api/v2/ams/batch_add_products_to_open_campaign` | https://open.shopee.com/documents/v2/ams.batch_add_products_to_open_campaign?module=&type=1 |
| POST | `/api/v2/ams/batch_edit_products_open_campaign_setting` | https://open.shopee.com/documents/v2/ams.batch_edit_products_open_campaign_setting?module=&type=1 |
| POST | `/api/v2/ams/batch_get_products_suggested_rate` | https://open.shopee.com/documents/v2/ams.batch_get_products_suggested_rate?module=&type=1 |
| POST | `/api/v2/ams/batch_remove_products_open_campaign_setting` | https://open.shopee.com/documents/v2/ams.batch_remove_products_open_campaign_setting?module=&type=1 |
| POST | `/api/v2/ams/create_new_targeted_campaign` | https://open.shopee.com/documents/v2/ams.create_new_targeted_campaign?module=&type=1 |
| POST | `/api/v2/ams/delete_video` | https://open.shopee.com/documents/v2/ams.delete_video?module=&type=1 |
| POST | `/api/v2/ams/edit_affiliate_list_of_targeted_campaign` | https://open.shopee.com/documents/v2/ams.edit_affiliate_list_of_targeted_campaign?module=&type=1 |
| POST | `/api/v2/ams/edit_all_products_open_campaign_setting` | https://open.shopee.com/documents/v2/ams.edit_all_products_open_campaign_setting?module=&type=1 |
| POST | `/api/v2/ams/edit_product_list_of_targeted_campaign` | https://open.shopee.com/documents/v2/ams.edit_product_list_of_targeted_campaign?module=&type=1 |
| POST | `/api/v2/ams/edit_video_info` | https://open.shopee.com/documents/v2/ams.edit_video_info?module=&type=1 |
| GET | `/api/v2/ams/get_affiliate_performance` | https://open.shopee.com/documents/v2/ams.get_affiliate_performance?module=&type=1 |
| GET | `/api/v2/ams/get_auto_add_new_product_toggle_status` | https://open.shopee.com/documents/v2/ams.get_auto_add_new_product_toggle_status?module=&type=1 |
| GET | `/api/v2/ams/get_campaign_key_metrics_performance` | https://open.shopee.com/documents/v2/ams.get_campaign_key_metrics_performance?module=&type=1 |
| GET | `/api/v2/ams/get_content_performance` | https://open.shopee.com/documents/v2/ams.get_content_performance?module=&type=1 |
| GET | `/api/v2/ams/get_conversion_report` | https://open.shopee.com/documents/v2/ams.get_conversion_report?module=&type=1 |
| GET | `/api/v2/ams/get_cover_list` | https://open.shopee.com/documents/v2/ams.get_cover_list?module=&type=1 |
| GET | `/api/v2/ams/get_managed_affiliate_list` | https://open.shopee.com/documents/v2/ams.get_managed_affiliate_list?module=&type=1 |
| GET | `/api/v2/ams/get_metric_trend` | https://open.shopee.com/documents/v2/ams.get_metric_trend?module=&type=1 |
| GET | `/api/v2/ams/get_open_campaign_added_product` | https://open.shopee.com/documents/v2/ams.get_open_campaign_added_product?module=&type=1 |
| GET | `/api/v2/ams/get_open_campaign_batch_task_result` | https://open.shopee.com/documents/v2/ams.get_open_campaign_batch_task_result?module=&type=1 |
| GET | `/api/v2/ams/get_open_campaign_not_added_product` | https://open.shopee.com/documents/v2/ams.get_open_campaign_not_added_product?module=&type=1 |
| GET | `/api/v2/ams/get_open_campaign_performance` | https://open.shopee.com/documents/v2/ams.get_open_campaign_performance?module=&type=1 |
| GET | `/api/v2/ams/get_optimization_suggestion_product` | https://open.shopee.com/documents/v2/ams.get_optimization_suggestion_product?module=&type=1 |
| GET | `/api/v2/ams/get_overview_performance` | https://open.shopee.com/documents/v2/ams.get_overview_performance?module=&type=1 |
| GET | `/api/v2/ams/get_performance_data_update_time` | https://open.shopee.com/documents/v2/ams.get_performance_data_update_time?module=&type=1 |
| GET | `/api/v2/ams/get_product_performance` | https://open.shopee.com/documents/v2/ams.get_product_performance?module=&type=1 |
| GET | `/api/v2/ams/get_product_performance_list` | https://open.shopee.com/documents/v2/ams.get_product_performance_list?module=&type=1 |
| GET | `/api/v2/ams/get_recommended_affiliate_list` | https://open.shopee.com/documents/v2/ams.get_recommended_affiliate_list?module=&type=1 |
| GET | `/api/v2/ams/get_shop_performance` | https://open.shopee.com/documents/v2/ams.get_shop_performance?module=&type=1 |
| GET | `/api/v2/ams/get_shop_suggested_rate` | https://open.shopee.com/documents/v2/ams.get_shop_suggested_rate?module=&type=1 |
| GET | `/api/v2/ams/get_targeted_campaign_addable_product_list` | https://open.shopee.com/documents/v2/ams.get_targeted_campaign_addable_product_list?module=&type=1 |
| GET | `/api/v2/ams/get_targeted_campaign_list` | https://open.shopee.com/documents/v2/ams.get_targeted_campaign_list?module=&type=1 |
| GET | `/api/v2/ams/get_targeted_campaign_performance` | https://open.shopee.com/documents/v2/ams.get_targeted_campaign_performance?module=&type=1 |
| GET | `/api/v2/ams/get_targeted_campaign_settings` | https://open.shopee.com/documents/v2/ams.get_targeted_campaign_settings?module=&type=1 |
| GET | `/api/v2/ams/get_user_demographics` | https://open.shopee.com/documents/v2/ams.get_user_demographics?module=&type=1 |
| GET | `/api/v2/ams/get_validation_list` | https://open.shopee.com/documents/v2/ams.get_validation_list?module=&type=1 |
| GET | `/api/v2/ams/get_validation_report` | https://open.shopee.com/documents/v2/ams.get_validation_report?module=&type=1 |
| GET | `/api/v2/ams/get_video_detail` | https://open.shopee.com/documents/v2/ams.get_video_detail?module=&type=1 |
| GET | `/api/v2/ams/get_video_detail_audience_distribution` | https://open.shopee.com/documents/v2/ams.get_video_detail_audience_distribution?module=&type=1 |
| GET | `/api/v2/ams/get_video_detail_metric_trend` | https://open.shopee.com/documents/v2/ams.get_video_detail_metric_trend?module=&type=1 |
| GET | `/api/v2/ams/get_video_detail_performance` | https://open.shopee.com/documents/v2/ams.get_video_detail_performance?module=&type=1 |
| GET | `/api/v2/ams/get_video_detail_product_performance` | https://open.shopee.com/documents/v2/ams.get_video_detail_product_performance?module=&type=1 |
| GET | `/api/v2/ams/get_video_list` | https://open.shopee.com/documents/v2/ams.get_video_list?module=&type=1 |
| GET | `/api/v2/ams/get_video_performance_list` | https://open.shopee.com/documents/v2/ams.get_video_performance_list?module=&type=1 |
| GET | `/api/v2/ams/query_affiliate_list` | https://open.shopee.com/documents/v2/ams.query_affiliate_list?module=&type=1 |
| POST | `/api/v2/ams/remove_all_products_open_campaign_setting` | https://open.shopee.com/documents/v2/ams.remove_all_products_open_campaign_setting?module=&type=1 |
| POST | `/api/v2/ams/update_auto_add_new_product_setting` | https://open.shopee.com/documents/v2/ams.update_auto_add_new_product_setting?module=&type=1 |
| POST | `/api/v2/ams/update_basic_info_of_targeted_campaign` | https://open.shopee.com/documents/v2/ams.update_basic_info_of_targeted_campaign?module=&type=1 |

## auth

| method | path | doc |
|---|---|---|
| POST | `/api/v2/auth/access_token/get` | https://open.shopee.com/documents/v2/auth.access_token/get?module=&type=1 |
| POST | `/api/v2/auth/get_token_by_resend_code` | https://open.shopee.com/documents/v2/auth.get_token_by_resend_code?module=&type=1 |
| POST | `/api/v2/auth/token/get` | https://open.shopee.com/documents/v2/auth.token/get?module=&type=1 |

## br

| method | path | doc |
|---|---|---|
| GET | `/api/v2/br/query_br_shop_block_status` | https://open.shopee.com/documents/v2/br.query_br_shop_block_status?module=&type=1 |
| GET | `/api/v2/br/query_br_shop_enrollment_status` | https://open.shopee.com/documents/v2/br.query_br_shop_enrollment_status?module=&type=1 |
| GET | `/api/v2/br/query_br_shop_invoice_error` | https://open.shopee.com/documents/v2/br.query_br_shop_invoice_error?module=&type=1 |
| GET | `/api/v2/br/query_br_sku_block_status` | https://open.shopee.com/documents/v2/br.query_br_sku_block_status?module=&type=1 |

## global_product

| method | path | doc |
|---|---|---|
| POST | `/api/v2/global_product/add_global_item` | https://open.shopee.com/documents/v2/global_product.add_global_item?module=&type=1 |
| POST | `/api/v2/global_product/add_global_model` | https://open.shopee.com/documents/v2/global_product.add_global_model?module=&type=1 |
| POST | `/api/v2/global_product/cancel_video_upload` | https://open.shopee.com/documents/v2/global_product.cancel_video_upload?module=&type=1 |
| POST | `/api/v2/global_product/create_publish_task` | https://open.shopee.com/documents/v2/global_product.create_publish_task?module=&type=1 |
| POST | `/api/v2/global_product/delete_global_item` | https://open.shopee.com/documents/v2/global_product.delete_global_item?module=&type=1 |
| POST | `/api/v2/global_product/delete_global_model` | https://open.shopee.com/documents/v2/global_product.delete_global_model?module=&type=1 |
| GET | `/api/v2/global_product/get_attribute_tree` | https://open.shopee.com/documents/v2/global_product.get_attribute_tree?module=&type=1 |
| GET | `/api/v2/global_product/get_brand_list` | https://open.shopee.com/documents/v2/global_product.get_brand_list?module=&type=1 |
| GET | `/api/v2/global_product/get_category` | https://open.shopee.com/documents/v2/global_product.get_category?module=&type=1 |
| GET | `/api/v2/global_product/get_global_item_id` | https://open.shopee.com/documents/v2/global_product.get_global_item_id?module=&type=1 |
| GET | `/api/v2/global_product/get_global_item_info` | https://open.shopee.com/documents/v2/global_product.get_global_item_info?module=&type=1 |
| GET | `/api/v2/global_product/get_global_item_limit` | https://open.shopee.com/documents/v2/global_product.get_global_item_limit?module=&type=1 |
| ? | `/api/v2/global_product/get_global_item_list` | https://open.shopee.com/documents/v2/global_product.get_global_item_list?module=&type=1 |
| GET | `/api/v2/global_product/get_global_model_list` | https://open.shopee.com/documents/v2/global_product.get_global_model_list?module=&type=1 |
| GET | `/api/v2/global_product/get_local_adjustment_rate` | https://open.shopee.com/documents/v2/global_product.get_local_adjustment_rate?module=&type=1 |
| GET | `/api/v2/global_product/get_publish_task_result` | https://open.shopee.com/documents/v2/global_product.get_publish_task_result?module=&type=1 |
| GET | `/api/v2/global_product/get_publishable_shop` | https://open.shopee.com/documents/v2/global_product.get_publishable_shop?module=&type=1 |
| GET | `/api/v2/global_product/get_published_list` | https://open.shopee.com/documents/v2/global_product.get_published_list?module=&type=1 |
| GET | `/api/v2/global_product/get_recommend_attribute` | https://open.shopee.com/documents/v2/global_product.get_recommend_attribute?module=&type=1 |
| GET | `/api/v2/global_product/get_shop_publishable_status` | https://open.shopee.com/documents/v2/global_product.get_shop_publishable_status?module=&type=1 |
| GET | `/api/v2/global_product/get_size_chart_detail` | https://open.shopee.com/documents/v2/global_product.get_size_chart_detail?module=&type=1 |
| GET | `/api/v2/global_product/get_size_chart_list` | https://open.shopee.com/documents/v2/global_product.get_size_chart_list?module=&type=1 |
| GET | `/api/v2/global_product/get_variations` | https://open.shopee.com/documents/v2/global_product.get_variations?module=&type=1 |
| GET | `/api/v2/global_product/get_video_upload_result` | https://open.shopee.com/documents/v2/global_product.get_video_upload_result?module=&type=1 |
| GET | `/api/v2/global_product/search_global_attribute_value_list` | https://open.shopee.com/documents/v2/global_product.search_global_attribute_value_list?module=&type=1 |
| POST | `/api/v2/global_product/set_sync_field` | https://open.shopee.com/documents/v2/global_product.set_sync_field?module=&type=1 |
| POST | `/api/v2/global_product/update_global_item` | https://open.shopee.com/documents/v2/global_product.update_global_item?module=&type=1 |
| POST | `/api/v2/global_product/update_global_model` | https://open.shopee.com/documents/v2/global_product.update_global_model?module=&type=1 |
| POST | `/api/v2/global_product/update_local_adjustment_rate` | https://open.shopee.com/documents/v2/global_product.update_local_adjustment_rate?module=&type=1 |
| POST | `/api/v2/global_product/update_price` | https://open.shopee.com/documents/v2/global_product.update_price?module=&type=1 |
| POST | `/api/v2/global_product/update_size_chart` | https://open.shopee.com/documents/v2/global_product.update_size_chart?module=&type=1 |
| POST | `/api/v2/global_product/update_stock` | https://open.shopee.com/documents/v2/global_product.update_stock?module=&type=1 |
| POST | `/api/v2/global_product/update_tier_variation` | https://open.shopee.com/documents/v2/global_product.update_tier_variation?module=&type=1 |

## logistics

| method | path | doc |
|---|---|---|
| POST | `/api/v2/logistics/batch_ship_order` | https://open.shopee.com/documents/v2/logistics.batch_ship_order?module=&type=1 |
| POST | `/api/v2/logistics/batch_update_tpf_warehouse_tracking_status` | https://open.shopee.com/documents/v2/logistics.batch_update_tpf_warehouse_tracking_status?module=&type=1 |
| GET | `/api/v2/logistics/check_polygon_update_status` | https://open.shopee.com/documents/v2/logistics.check_polygon_update_status?module=&type=1 |
| POST | `/api/v2/logistics/create_booking_shipping_document` | https://open.shopee.com/documents/v2/logistics.create_booking_shipping_document?module=&type=1 |
| POST | `/api/v2/logistics/create_shipping_document` | https://open.shopee.com/documents/v2/logistics.create_shipping_document?module=&type=1 |
| POST | `/api/v2/logistics/create_shipping_document_job` | https://open.shopee.com/documents/v2/logistics.create_shipping_document_job?module=&type=1 |
| POST | `/api/v2/logistics/delete_address` | https://open.shopee.com/documents/v2/logistics.delete_address?module=&type=1 |
| POST | `/api/v2/logistics/delete_special_operating_hour` | https://open.shopee.com/documents/v2/logistics.delete_special_operating_hour?module=&type=1 |
| GET | `/api/v2/logistics/get_address_list` | https://open.shopee.com/documents/v2/logistics.get_address_list?module=&type=1 |
| GET | `/api/v2/logistics/get_booking_shipping_document_data_info` | https://open.shopee.com/documents/v2/logistics.get_booking_shipping_document_data_info?module=&type=1 |
| GET | `/api/v2/logistics/get_booking_shipping_document_parameter` | https://open.shopee.com/documents/v2/logistics.get_booking_shipping_document_parameter?module=&type=1 |
| GET | `/api/v2/logistics/get_booking_shipping_document_result` | https://open.shopee.com/documents/v2/logistics.get_booking_shipping_document_result?module=&type=1 |
| GET | `/api/v2/logistics/get_booking_shipping_parameter` | https://open.shopee.com/documents/v2/logistics.get_booking_shipping_parameter?module=&type=1 |
| GET | `/api/v2/logistics/get_booking_tracking_info` | https://open.shopee.com/documents/v2/logistics.get_booking_tracking_info?module=&type=1 |
| GET | `/api/v2/logistics/get_booking_tracking_number` | https://open.shopee.com/documents/v2/logistics.get_booking_tracking_number?module=&type=1 |
| GET | `/api/v2/logistics/get_channel_list` | https://open.shopee.com/documents/v2/logistics.get_channel_list?module=&type=1 |
| GET | `/api/v2/logistics/get_courier_delivery_channel_list` | https://open.shopee.com/documents/v2/logistics.get_courier_delivery_channel_list?module=&type=1 |
| GET | `/api/v2/logistics/get_courier_delivery_detail` | https://open.shopee.com/documents/v2/logistics.get_courier_delivery_detail?module=&type=1 |
| GET | `/api/v2/logistics/get_courier_delivery_tracking_number_list` | https://open.shopee.com/documents/v2/logistics.get_courier_delivery_tracking_number_list?module=&type=1 |
| GET | `/api/v2/logistics/get_courier_delivery_waybill` | https://open.shopee.com/documents/v2/logistics.get_courier_delivery_waybill?module=&type=1 |
| GET | `/api/v2/logistics/get_detail` | https://open.shopee.com/documents/v2/logistics.get_detail?module=&type=1 |
| GET | `/api/v2/logistics/get_mart_packaging_info` | https://open.shopee.com/documents/v2/logistics.get_mart_packaging_info?module=&type=1 |
| POST | `/api/v2/logistics/get_mass_shipping_parameter` | https://open.shopee.com/documents/v2/logistics.get_mass_shipping_parameter?module=&type=1 |
| POST | `/api/v2/logistics/get_mass_tracking_number` | https://open.shopee.com/documents/v2/logistics.get_mass_tracking_number?module=&type=1 |
| GET | `/api/v2/logistics/get_operating_hour_restrictions` | https://open.shopee.com/documents/v2/logistics.get_operating_hour_restrictions?module=&type=1 |
| GET | `/api/v2/logistics/get_operating_hours` | https://open.shopee.com/documents/v2/logistics.get_operating_hours?module=&type=1 |
| GET | `/api/v2/logistics/get_pause_status` | https://open.shopee.com/documents/v2/logistics.get_pause_status?module=&type=1 |
| GET | `/api/v2/logistics/get_shipping_document_data_info` | https://open.shopee.com/documents/v2/logistics.get_shipping_document_data_info?module=&type=1 |
| GET | `/api/v2/logistics/get_shipping_document_job_status` | https://open.shopee.com/documents/v2/logistics.get_shipping_document_job_status?module=&type=1 |
| POST | `/api/v2/logistics/get_shipping_document_parameter` | https://open.shopee.com/documents/v2/logistics.get_shipping_document_parameter?module=&type=1 |
| GET | `/api/v2/logistics/get_shipping_document_result` | https://open.shopee.com/documents/v2/logistics.get_shipping_document_result?module=&type=1 |
| GET | `/api/v2/logistics/get_shipping_parameter` | https://open.shopee.com/documents/v2/logistics.get_shipping_parameter?module=&type=1 |
| GET | `/api/v2/logistics/get_tracking_info` | https://open.shopee.com/documents/v2/logistics.get_tracking_info?module=&type=1 |
| GET | `/api/v2/logistics/get_tracking_number` | https://open.shopee.com/documents/v2/logistics.get_tracking_number?module=&type=1 |
| GET | `/api/v2/logistics/get_tracking_number_list` | https://open.shopee.com/documents/v2/logistics.get_tracking_number_list?module=&type=1 |
| GET | `/api/v2/logistics/get_transit_warehouse_list` | https://open.shopee.com/documents/v2/logistics.get_transit_warehouse_list?module=&type=1 |
| GET | `/api/v2/logistics/get_unbind_order_list` | https://open.shopee.com/documents/v2/logistics.get_unbind_order_list?module=&type=1 |
| GET | `/api/v2/logistics/get_waybill` | https://open.shopee.com/documents/v2/logistics.get_waybill?module=&type=1 |
| POST | `/api/v2/logistics/mass_ship_order` | https://open.shopee.com/documents/v2/logistics.mass_ship_order?module=&type=1 |
| POST | `/api/v2/logistics/set_address_config` | https://open.shopee.com/documents/v2/logistics.set_address_config?module=&type=1 |
| POST | `/api/v2/logistics/set_mart_packaging_info` | https://open.shopee.com/documents/v2/logistics.set_mart_packaging_info?module=&type=1 |
| POST | `/api/v2/logistics/set_pause_status` | https://open.shopee.com/documents/v2/logistics.set_pause_status?module=&type=1 |
| POST | `/api/v2/logistics/ship_booking` | https://open.shopee.com/documents/v2/logistics.ship_booking?module=&type=1 |
| POST | `/api/v2/logistics/ship_order` | https://open.shopee.com/documents/v2/logistics.ship_order?module=&type=1 |
| POST | `/api/v2/logistics/update_address` | https://open.shopee.com/documents/v2/logistics.update_address?module=&type=1 |
| POST | `/api/v2/logistics/update_channel` | https://open.shopee.com/documents/v2/logistics.update_channel?module=&type=1 |
| POST | `/api/v2/logistics/update_operating_hours` | https://open.shopee.com/documents/v2/logistics.update_operating_hours?module=&type=1 |
| POST | `/api/v2/logistics/update_self_collection_order_logistics` | https://open.shopee.com/documents/v2/logistics.update_self_collection_order_logistics?module=&type=1 |
| POST | `/api/v2/logistics/update_shipping_order` | https://open.shopee.com/documents/v2/logistics.update_shipping_order?module=&type=1 |
| POST | `/api/v2/logistics/update_tracking_status` | https://open.shopee.com/documents/v2/logistics.update_tracking_status?module=&type=1 |

## media

| method | path | doc |
|---|---|---|
| POST | `/api/v2/media/add_item_list` | https://open.shopee.com/documents/v2/media.add_item_list?module=&type=1 |
| POST | `/api/v2/media/create_session` | https://open.shopee.com/documents/v2/media.create_session?module=&type=1 |
| POST | `/api/v2/media/delete_item_list` | https://open.shopee.com/documents/v2/media.delete_item_list?module=&type=1 |
| POST | `/api/v2/media/delete_show_item` | https://open.shopee.com/documents/v2/media.delete_show_item?module=&type=1 |
| GET | `/api/v2/media/get_item_count` | https://open.shopee.com/documents/v2/media.get_item_count?module=&type=1 |
| GET | `/api/v2/media/get_item_list` | https://open.shopee.com/documents/v2/media.get_item_list?module=&type=1 |
| GET | `/api/v2/media/get_item_set_item_list` | https://open.shopee.com/documents/v2/media.get_item_set_item_list?module=&type=1 |
| GET | `/api/v2/media/get_item_set_list` | https://open.shopee.com/documents/v2/media.get_item_set_list?module=&type=1 |
| GET | `/api/v2/media/get_latest_comment_list` | https://open.shopee.com/documents/v2/media.get_latest_comment_list?module=&type=1 |
| GET | `/api/v2/media/get_like_item_list` | https://open.shopee.com/documents/v2/media.get_like_item_list?module=&type=1 |
| GET | `/api/v2/media/get_recent_item_list` | https://open.shopee.com/documents/v2/media.get_recent_item_list?module=&type=1 |
| GET | `/api/v2/media/get_session_detail` | https://open.shopee.com/documents/v2/media.get_session_detail?module=&type=1 |
| GET | `/api/v2/media/get_session_item_metric` | https://open.shopee.com/documents/v2/media.get_session_item_metric?module=&type=1 |
| GET | `/api/v2/media/get_session_metric` | https://open.shopee.com/documents/v2/media.get_session_metric?module=&type=1 |
| GET | `/api/v2/media/get_show_item` | https://open.shopee.com/documents/v2/media.get_show_item?module=&type=1 |
| POST | `/api/v2/media/update_item_list` | https://open.shopee.com/documents/v2/media.update_item_list?module=&type=1 |
| POST | `/api/v2/media/update_session` | https://open.shopee.com/documents/v2/media.update_session?module=&type=1 |
| POST | `/api/v2/media/update_show_item` | https://open.shopee.com/documents/v2/media.update_show_item?module=&type=1 |

## order

| method | path | doc |
|---|---|---|
| POST | `/api/v2/order/cancel_order` | https://open.shopee.com/documents/v2/order.cancel_order?module=&type=1 |
| GET | `/api/v2/order/get_booking_detail` | https://open.shopee.com/documents/v2/order.get_booking_detail?module=&type=1 |
| GET | `/api/v2/order/get_booking_list` | https://open.shopee.com/documents/v2/order.get_booking_list?module=&type=1 |
| GET | `/api/v2/order/get_buyer_invoice_info` | https://open.shopee.com/documents/v2/order.get_buyer_invoice_info?module=&type=1 |
| GET | `/api/v2/order/get_estimate_cancel_value` | https://open.shopee.com/documents/v2/order.get_estimate_cancel_value?module=&type=1 |
| GET | `/api/v2/order/get_fbs_invoices_result` | https://open.shopee.com/documents/v2/order.get_fbs_invoices_result?module=&type=1 |
| GET | `/api/v2/order/get_order_detail` | https://open.shopee.com/documents/v2/order.get_order_detail?module=&type=1 |
| GET | `/api/v2/order/get_order_list` | https://open.shopee.com/documents/v2/order.get_order_list?module=&type=1 |
| GET | `/api/v2/order/get_package_detail` | https://open.shopee.com/documents/v2/order.get_package_detail?module=&type=1 |
| GET | `/api/v2/order/get_pending_buyer_invoice_order_list` | https://open.shopee.com/documents/v2/order.get_pending_buyer_invoice_order_list?module=&type=1 |
| GET | `/api/v2/order/get_shipment_list` | https://open.shopee.com/documents/v2/order.get_shipment_list?module=&type=1 |
| GET | `/api/v2/order/get_warehouse_filter_config` | https://open.shopee.com/documents/v2/order.get_warehouse_filter_config?module=&type=1 |
| POST | `/api/v2/order/search_package_list` | https://open.shopee.com/documents/v2/order.search_package_list?module=&type=1 |
| POST | `/api/v2/order/set_note` | https://open.shopee.com/documents/v2/order.set_note?module=&type=1 |
| POST | `/api/v2/order/split_order` | https://open.shopee.com/documents/v2/order.split_order?module=&type=1 |
| POST | `/api/v2/order/unsplit_order` | https://open.shopee.com/documents/v2/order.unsplit_order?module=&type=1 |

## partner

| method | path | doc |
|---|---|---|
| GET | `/api/v2/partner/get_app_push_config` | https://open.shopee.com/documents/v2/partner.get_app_push_config?module=&type=1 |
| GET | `/api/v2/partner/get_bound_whs_info` | https://open.shopee.com/documents/v2/partner.get_bound_whs_info?module=&type=1 |
| GET | `/api/v2/partner/get_lost_push_message` | https://open.shopee.com/documents/v2/partner.get_lost_push_message?module=&type=1 |
| GET | `/api/v2/partner/get_merchants_by_partner` | https://open.shopee.com/documents/v2/partner.get_merchants_by_partner?module=&type=1 |
| GET | `/api/v2/partner/get_shopee_ip_ranges` | https://open.shopee.com/documents/v2/partner.get_shopee_ip_ranges?module=&type=1 |
| GET | `/api/v2/partner/get_shops_by_partner` | https://open.shopee.com/documents/v2/partner.get_shops_by_partner?module=&type=1 |
| POST | `/api/v2/partner/set_app_push_config` | https://open.shopee.com/documents/v2/partner.set_app_push_config?module=&type=1 |

## payment

| method | path | doc |
|---|---|---|
| GET | `/api/v2/payment/get_billing_transaction_info` | https://open.shopee.com/documents/v2/payment.get_billing_transaction_info?module=&type=1 |
| GET | `/api/v2/payment/get_escrow_detail` | https://open.shopee.com/documents/v2/payment.get_escrow_detail?module=&type=1 |
| POST | `/api/v2/payment/get_escrow_detail_batch` | https://open.shopee.com/documents/v2/payment.get_escrow_detail_batch?module=&type=1 |
| GET | `/api/v2/payment/get_escrow_list` | https://open.shopee.com/documents/v2/payment.get_escrow_list?module=&type=1 |
| GET | `/api/v2/payment/get_income_detail` | https://open.shopee.com/documents/v2/payment.get_income_detail?module=&type=1 |
| GET | `/api/v2/payment/get_income_overview` | https://open.shopee.com/documents/v2/payment.get_income_overview?module=&type=1 |
| GET | `/api/v2/payment/get_income_report` | https://open.shopee.com/documents/v2/payment.get_income_report?module=&type=1 |
| GET | `/api/v2/payment/get_income_statement` | https://open.shopee.com/documents/v2/payment.get_income_statement?module=&type=1 |
| GET | `/api/v2/payment/get_item_installment_status` | https://open.shopee.com/documents/v2/payment.get_item_installment_status?module=&type=1 |
| GET | `/api/v2/payment/get_payment_method_list` | https://open.shopee.com/documents/v2/payment.get_payment_method_list?module=&type=1 |
| GET | `/api/v2/payment/get_payout_detail` | https://open.shopee.com/documents/v2/payment.get_payout_detail?module=&type=1 |
| GET | `/api/v2/payment/get_payout_info` | https://open.shopee.com/documents/v2/payment.get_payout_info?module=&type=1 |
| GET | `/api/v2/payment/get_shop_installment_status` | https://open.shopee.com/documents/v2/payment.get_shop_installment_status?module=&type=1 |
| GET | `/api/v2/payment/get_wallet_transaction_list` | https://open.shopee.com/documents/v2/payment.get_wallet_transaction_list?module=&type=1 |
| POST | `/api/v2/payment/set_item_installment_status` | https://open.shopee.com/documents/v2/payment.set_item_installment_status?module=&type=1 |
| POST | `/api/v2/payment/set_shop_installment_status` | https://open.shopee.com/documents/v2/payment.set_shop_installment_status?module=&type=1 |

## product

| method | path | doc |
|---|---|---|
| POST | `/api/v2/product/add_item` | https://open.shopee.com/documents/v2/product.add_item?module=&type=1 |
| POST | `/api/v2/product/add_kit_item` | https://open.shopee.com/documents/v2/product.add_kit_item?module=&type=1 |
| POST | `/api/v2/product/add_model` | https://open.shopee.com/documents/v2/product.add_model?module=&type=1 |
| POST | `/api/v2/product/add_ssp_item` | https://open.shopee.com/documents/v2/product.add_ssp_item?module=&type=1 |
| POST | `/api/v2/product/boost_item` | https://open.shopee.com/documents/v2/product.boost_item?module=&type=1 |
| POST | `/api/v2/product/delete_item` | https://open.shopee.com/documents/v2/product.delete_item?module=&type=1 |
| POST | `/api/v2/product/delete_model` | https://open.shopee.com/documents/v2/product.delete_model?module=&type=1 |
| GET | `/api/v2/product/get_aitem_by_pitem_id` | https://open.shopee.com/documents/v2/product.get_aitem_by_pitem_id?module=&type=1 |
| GET | `/api/v2/product/get_all_vehicle_list` | https://open.shopee.com/documents/v2/product.get_all_vehicle_list?module=&type=1 |
| GET | `/api/v2/product/get_attribute_tree` | https://open.shopee.com/documents/v2/product.get_attribute_tree?module=&type=1 |
| GET | `/api/v2/product/get_boosted_list` | https://open.shopee.com/documents/v2/product.get_boosted_list?module=&type=1 |
| GET | `/api/v2/product/get_brand_list` | https://open.shopee.com/documents/v2/product.get_brand_list?module=&type=1 |
| GET | `/api/v2/product/get_category` | https://open.shopee.com/documents/v2/product.get_category?module=&type=1 |
| GET | `/api/v2/product/get_comment` | https://open.shopee.com/documents/v2/product.get_comment?module=&type=1 |
| GET | `/api/v2/product/get_direct_item_list` | https://open.shopee.com/documents/v2/product.get_direct_item_list?module=&type=1 |
| GET | `/api/v2/product/get_direct_shop_recommended_price` | https://open.shopee.com/documents/v2/product.get_direct_shop_recommended_price?module=&type=1 |
| GET | `/api/v2/product/get_item_base_info` | https://open.shopee.com/documents/v2/product.get_item_base_info?module=&type=1 |
| GET | `/api/v2/product/get_item_content_diagnosis_result` | https://open.shopee.com/documents/v2/product.get_item_content_diagnosis_result?module=&type=1 |
| GET | `/api/v2/product/get_item_extra_info` | https://open.shopee.com/documents/v2/product.get_item_extra_info?module=&type=1 |
| GET | `/api/v2/product/get_item_limit` | https://open.shopee.com/documents/v2/product.get_item_limit?module=&type=1 |
| ? | `/api/v2/product/get_item_list` | https://open.shopee.com/documents/v2/product.get_item_list?module=&type=1 |
| GET | `/api/v2/product/get_item_list_by_content_diagnosis` | https://open.shopee.com/documents/v2/product.get_item_list_by_content_diagnosis?module=&type=1 |
| GET | `/api/v2/product/get_item_promotion` | https://open.shopee.com/documents/v2/product.get_item_promotion?module=&type=1 |
| GET | `/api/v2/product/get_item_violation_info` | https://open.shopee.com/documents/v2/product.get_item_violation_info?module=&type=1 |
| GET | `/api/v2/product/get_kit_item_info` | https://open.shopee.com/documents/v2/product.get_kit_item_info?module=&type=1 |
| GET | `/api/v2/product/get_kit_item_limit` | https://open.shopee.com/documents/v2/product.get_kit_item_limit?module=&type=1 |
| GET | `/api/v2/product/get_main_item_list` | https://open.shopee.com/documents/v2/product.get_main_item_list?module=&type=1 |
| GET | `/api/v2/product/get_mart_item_by_outlet_item_id` | https://open.shopee.com/documents/v2/product.get_mart_item_by_outlet_item_id?module=&type=1 |
| GET | `/api/v2/product/get_mart_item_mapping_by_id` | https://open.shopee.com/documents/v2/product.get_mart_item_mapping_by_id?module=&type=1 |
| GET | `/api/v2/product/get_model_list` | https://open.shopee.com/documents/v2/product.get_model_list?module=&type=1 |
| POST | `/api/v2/product/get_product_certification_rule` | https://open.shopee.com/documents/v2/product.get_product_certification_rule?module=&type=1 |
| GET | `/api/v2/product/get_recommend_attribute` | https://open.shopee.com/documents/v2/product.get_recommend_attribute?module=&type=1 |
| GET | `/api/v2/product/get_size_chart_detail` | https://open.shopee.com/documents/v2/product.get_size_chart_detail?module=&type=1 |
| GET | `/api/v2/product/get_size_chart_list` | https://open.shopee.com/documents/v2/product.get_size_chart_list?module=&type=1 |
| GET | `/api/v2/product/get_ssp_info` | https://open.shopee.com/documents/v2/product.get_ssp_info?module=&type=1 |
| GET | `/api/v2/product/get_ssp_list` | https://open.shopee.com/documents/v2/product.get_ssp_list?module=&type=1 |
| GET | `/api/v2/product/get_variations` | https://open.shopee.com/documents/v2/product.get_variations?module=&type=1 |
| GET | `/api/v2/product/get_vehicle_list_by_compatibility_detail` | https://open.shopee.com/documents/v2/product.get_vehicle_list_by_compatibility_detail?module=&type=1 |
| GET | `/api/v2/product/get_weight_recommendation` | https://open.shopee.com/documents/v2/product.get_weight_recommendation?module=&type=1 |
| POST | `/api/v2/product/publish_item_to_outlet_shop` | https://open.shopee.com/documents/v2/product.publish_item_to_outlet_shop?module=&type=1 |
| GET | `/api/v2/product/search_attribute_value_list` | https://open.shopee.com/documents/v2/product.search_attribute_value_list?module=&type=1 |
| GET | `/api/v2/product/search_unpackaged_model_list` | https://open.shopee.com/documents/v2/product.search_unpackaged_model_list?module=&type=1 |
| POST | `/api/v2/product/unlist_item` | https://open.shopee.com/documents/v2/product.unlist_item?module=&type=1 |
| POST | `/api/v2/product/update_item` | https://open.shopee.com/documents/v2/product.update_item?module=&type=1 |
| POST | `/api/v2/product/update_kit_item` | https://open.shopee.com/documents/v2/product.update_kit_item?module=&type=1 |
| POST | `/api/v2/product/update_model` | https://open.shopee.com/documents/v2/product.update_model?module=&type=1 |
| POST | `/api/v2/product/update_price` | https://open.shopee.com/documents/v2/product.update_price?module=&type=1 |
| POST | `/api/v2/product/update_sip_item_price` | https://open.shopee.com/documents/v2/product.update_sip_item_price?module=&type=1 |
| POST | `/api/v2/product/update_stock` | https://open.shopee.com/documents/v2/product.update_stock?module=&type=1 |
| POST | `/api/v2/product/update_tier_variation` | https://open.shopee.com/documents/v2/product.update_tier_variation?module=&type=1 |

## promotion

| method | path | doc |
|---|---|---|
| POST | `/api/v2/promotion/add_add_on_deal` | https://open.shopee.com/documents/v2/promotion.add_add_on_deal?module=&type=1 |
| POST | `/api/v2/promotion/add_add_on_deal_main_item` | https://open.shopee.com/documents/v2/promotion.add_add_on_deal_main_item?module=&type=1 |
| POST | `/api/v2/promotion/add_add_on_deal_sub_item` | https://open.shopee.com/documents/v2/promotion.add_add_on_deal_sub_item?module=&type=1 |
| POST | `/api/v2/promotion/add_bundle_deal` | https://open.shopee.com/documents/v2/promotion.add_bundle_deal?module=&type=1 |
| POST | `/api/v2/promotion/add_bundle_deal_item` | https://open.shopee.com/documents/v2/promotion.add_bundle_deal_item?module=&type=1 |
| POST | `/api/v2/promotion/add_discount` | https://open.shopee.com/documents/v2/promotion.add_discount?module=&type=1 |
| POST | `/api/v2/promotion/add_discount_item` | https://open.shopee.com/documents/v2/promotion.add_discount_item?module=&type=1 |
| POST | `/api/v2/promotion/add_follow_prize` | https://open.shopee.com/documents/v2/promotion.add_follow_prize?module=&type=1 |
| POST | `/api/v2/promotion/add_item_list` | https://open.shopee.com/documents/v2/promotion.add_item_list?module=&type=1 |
| POST | `/api/v2/promotion/add_shop_category` | https://open.shopee.com/documents/v2/promotion.add_shop_category?module=&type=1 |
| POST | `/api/v2/promotion/add_shop_flash_sale_items` | https://open.shopee.com/documents/v2/promotion.add_shop_flash_sale_items?module=&type=1 |
| POST | `/api/v2/promotion/add_top_picks` | https://open.shopee.com/documents/v2/promotion.add_top_picks?module=&type=1 |
| POST | `/api/v2/promotion/add_voucher` | https://open.shopee.com/documents/v2/promotion.add_voucher?module=&type=1 |
| POST | `/api/v2/promotion/create_shop_flash_sale` | https://open.shopee.com/documents/v2/promotion.create_shop_flash_sale?module=&type=1 |
| POST | `/api/v2/promotion/delete_add_on_deal` | https://open.shopee.com/documents/v2/promotion.delete_add_on_deal?module=&type=1 |
| POST | `/api/v2/promotion/delete_add_on_deal_main_item` | https://open.shopee.com/documents/v2/promotion.delete_add_on_deal_main_item?module=&type=1 |
| POST | `/api/v2/promotion/delete_add_on_deal_sub_item` | https://open.shopee.com/documents/v2/promotion.delete_add_on_deal_sub_item?module=&type=1 |
| POST | `/api/v2/promotion/delete_bundle_deal` | https://open.shopee.com/documents/v2/promotion.delete_bundle_deal?module=&type=1 |
| POST | `/api/v2/promotion/delete_bundle_deal_item` | https://open.shopee.com/documents/v2/promotion.delete_bundle_deal_item?module=&type=1 |
| POST | `/api/v2/promotion/delete_discount` | https://open.shopee.com/documents/v2/promotion.delete_discount?module=&type=1 |
| POST | `/api/v2/promotion/delete_discount_item` | https://open.shopee.com/documents/v2/promotion.delete_discount_item?module=&type=1 |
| POST | `/api/v2/promotion/delete_follow_prize` | https://open.shopee.com/documents/v2/promotion.delete_follow_prize?module=&type=1 |
| POST | `/api/v2/promotion/delete_item_list` | https://open.shopee.com/documents/v2/promotion.delete_item_list?module=&type=1 |
| POST | `/api/v2/promotion/delete_shop_category` | https://open.shopee.com/documents/v2/promotion.delete_shop_category?module=&type=1 |
| POST | `/api/v2/promotion/delete_shop_flash_sale` | https://open.shopee.com/documents/v2/promotion.delete_shop_flash_sale?module=&type=1 |
| POST | `/api/v2/promotion/delete_shop_flash_sale_items` | https://open.shopee.com/documents/v2/promotion.delete_shop_flash_sale_items?module=&type=1 |
| POST | `/api/v2/promotion/delete_sip_discount` | https://open.shopee.com/documents/v2/promotion.delete_sip_discount?module=&type=1 |
| POST | `/api/v2/promotion/delete_top_picks` | https://open.shopee.com/documents/v2/promotion.delete_top_picks?module=&type=1 |
| POST | `/api/v2/promotion/delete_voucher` | https://open.shopee.com/documents/v2/promotion.delete_voucher?module=&type=1 |
| POST | `/api/v2/promotion/end_add_on_deal` | https://open.shopee.com/documents/v2/promotion.end_add_on_deal?module=&type=1 |
| GET | `/api/v2/promotion/get_add_on_deal` | https://open.shopee.com/documents/v2/promotion.get_add_on_deal?module=&type=1 |
| GET | `/api/v2/promotion/get_add_on_deal_list` | https://open.shopee.com/documents/v2/promotion.get_add_on_deal_list?module=&type=1 |
| GET | `/api/v2/promotion/get_add_on_deal_main_item` | https://open.shopee.com/documents/v2/promotion.get_add_on_deal_main_item?module=&type=1 |
| GET | `/api/v2/promotion/get_add_on_deal_sub_item` | https://open.shopee.com/documents/v2/promotion.get_add_on_deal_sub_item?module=&type=1 |
| GET | `/api/v2/promotion/get_bundle_deal` | https://open.shopee.com/documents/v2/promotion.get_bundle_deal?module=&type=1 |
| GET | `/api/v2/promotion/get_bundle_deal_item` | https://open.shopee.com/documents/v2/promotion.get_bundle_deal_item?module=&type=1 |
| GET | `/api/v2/promotion/get_bundle_deal_list` | https://open.shopee.com/documents/v2/promotion.get_bundle_deal_list?module=&type=1 |
| GET | `/api/v2/promotion/get_discount` | https://open.shopee.com/documents/v2/promotion.get_discount?module=&type=1 |
| GET | `/api/v2/promotion/get_discount_list` | https://open.shopee.com/documents/v2/promotion.get_discount_list?module=&type=1 |
| GET | `/api/v2/promotion/get_follow_prize_detail` | https://open.shopee.com/documents/v2/promotion.get_follow_prize_detail?module=&type=1 |
| GET | `/api/v2/promotion/get_follow_prize_list` | https://open.shopee.com/documents/v2/promotion.get_follow_prize_list?module=&type=1 |
| GET | `/api/v2/promotion/get_item_criteria` | https://open.shopee.com/documents/v2/promotion.get_item_criteria?module=&type=1 |
| GET | `/api/v2/promotion/get_item_list` | https://open.shopee.com/documents/v2/promotion.get_item_list?module=&type=1 |
| GET | `/api/v2/promotion/get_shop_category_list` | https://open.shopee.com/documents/v2/promotion.get_shop_category_list?module=&type=1 |
| GET | `/api/v2/promotion/get_shop_flash_sale` | https://open.shopee.com/documents/v2/promotion.get_shop_flash_sale?module=&type=1 |
| GET | `/api/v2/promotion/get_shop_flash_sale_items` | https://open.shopee.com/documents/v2/promotion.get_shop_flash_sale_items?module=&type=1 |
| GET | `/api/v2/promotion/get_shop_flash_sale_list` | https://open.shopee.com/documents/v2/promotion.get_shop_flash_sale_list?module=&type=1 |
| GET | `/api/v2/promotion/get_sip_discounts` | https://open.shopee.com/documents/v2/promotion.get_sip_discounts?module=&type=1 |
| GET | `/api/v2/promotion/get_time_slot_id` | https://open.shopee.com/documents/v2/promotion.get_time_slot_id?module=&type=1 |
| GET | `/api/v2/promotion/get_top_picks_list` | https://open.shopee.com/documents/v2/promotion.get_top_picks_list?module=&type=1 |
| GET | `/api/v2/promotion/get_voucher` | https://open.shopee.com/documents/v2/promotion.get_voucher?module=&type=1 |
| GET | `/api/v2/promotion/get_voucher_list` | https://open.shopee.com/documents/v2/promotion.get_voucher_list?module=&type=1 |
| POST | `/api/v2/promotion/set_sip_discount` | https://open.shopee.com/documents/v2/promotion.set_sip_discount?module=&type=1 |
| POST | `/api/v2/promotion/update_add_on_deal` | https://open.shopee.com/documents/v2/promotion.update_add_on_deal?module=&type=1 |
| POST | `/api/v2/promotion/update_add_on_deal_main_item` | https://open.shopee.com/documents/v2/promotion.update_add_on_deal_main_item?module=&type=1 |
| POST | `/api/v2/promotion/update_add_on_deal_sub_item` | https://open.shopee.com/documents/v2/promotion.update_add_on_deal_sub_item?module=&type=1 |
| POST | `/api/v2/promotion/update_bundle_deal` | https://open.shopee.com/documents/v2/promotion.update_bundle_deal?module=&type=1 |
| POST | `/api/v2/promotion/update_bundle_deal_item` | https://open.shopee.com/documents/v2/promotion.update_bundle_deal_item?module=&type=1 |
| POST | `/api/v2/promotion/update_discount` | https://open.shopee.com/documents/v2/promotion.update_discount?module=&type=1 |
| POST | `/api/v2/promotion/update_discount_item` | https://open.shopee.com/documents/v2/promotion.update_discount_item?module=&type=1 |
| POST | `/api/v2/promotion/update_follow_prize` | https://open.shopee.com/documents/v2/promotion.update_follow_prize?module=&type=1 |
| POST | `/api/v2/promotion/update_shop_category` | https://open.shopee.com/documents/v2/promotion.update_shop_category?module=&type=1 |
| POST | `/api/v2/promotion/update_shop_flash_sale` | https://open.shopee.com/documents/v2/promotion.update_shop_flash_sale?module=&type=1 |
| POST | `/api/v2/promotion/update_shop_flash_sale_items` | https://open.shopee.com/documents/v2/promotion.update_shop_flash_sale_items?module=&type=1 |
| POST | `/api/v2/promotion/update_top_picks` | https://open.shopee.com/documents/v2/promotion.update_top_picks?module=&type=1 |
| POST | `/api/v2/promotion/update_voucher` | https://open.shopee.com/documents/v2/promotion.update_voucher?module=&type=1 |

## returns

| method | path | doc |
|---|---|---|
| POST | `/api/v2/returns/cancel_dispute` | https://open.shopee.com/documents/v2/returns.cancel_dispute?module=&type=1 |
| GET | `/api/v2/returns/get_available_solutions` | https://open.shopee.com/documents/v2/returns.get_available_solutions?module=&type=1 |
| GET | `/api/v2/returns/get_return_detail` | https://open.shopee.com/documents/v2/returns.get_return_detail?module=&type=1 |
| GET | `/api/v2/returns/get_return_dispute_reason` | https://open.shopee.com/documents/v2/returns.get_return_dispute_reason?module=&type=1 |
| GET | `/api/v2/returns/get_return_list` | https://open.shopee.com/documents/v2/returns.get_return_list?module=&type=1 |
| GET | `/api/v2/returns/get_reverse_tracking_info` | https://open.shopee.com/documents/v2/returns.get_reverse_tracking_info?module=&type=1 |
| GET | `/api/v2/returns/get_shipping_carrier` | https://open.shopee.com/documents/v2/returns.get_shipping_carrier?module=&type=1 |
| GET | `/api/v2/returns/query_proof` | https://open.shopee.com/documents/v2/returns.query_proof?module=&type=1 |

## shop

| method | path | doc |
|---|---|---|
| GET | `/api/v2/shop/get_authorised_reseller_brand` | https://open.shopee.com/documents/v2/shop.get_authorised_reseller_brand?module=&type=1 |
| GET | `/api/v2/shop/get_br_shop_onboarding_info` | https://open.shopee.com/documents/v2/shop.get_br_shop_onboarding_info?module=&type=1 |
| GET | `/api/v2/shop/get_late_orders` | https://open.shopee.com/documents/v2/shop.get_late_orders?module=&type=1 |
| GET | `/api/v2/shop/get_listings_with_issues` | https://open.shopee.com/documents/v2/shop.get_listings_with_issues?module=&type=1 |
| GET | `/api/v2/shop/get_merchant_info` | https://open.shopee.com/documents/v2/shop.get_merchant_info?module=&type=1 |
| GET | `/api/v2/shop/get_merchant_prepaid_account_list` | https://open.shopee.com/documents/v2/shop.get_merchant_prepaid_account_list?module=&type=1 |
| GET | `/api/v2/shop/get_merchant_warehouse_list` | https://open.shopee.com/documents/v2/shop.get_merchant_warehouse_list?module=&type=1 |
| GET | `/api/v2/shop/get_merchant_warehouse_location_list` | https://open.shopee.com/documents/v2/shop.get_merchant_warehouse_location_list?module=&type=1 |
| GET | `/api/v2/shop/get_metric_source_detail` | https://open.shopee.com/documents/v2/shop.get_metric_source_detail?module=&type=1 |
| GET | `/api/v2/shop/get_penalty_point_history` | https://open.shopee.com/documents/v2/shop.get_penalty_point_history?module=&type=1 |
| GET | `/api/v2/shop/get_profile` | https://open.shopee.com/documents/v2/shop.get_profile?module=&type=1 |
| GET | `/api/v2/shop/get_punishment_history` | https://open.shopee.com/documents/v2/shop.get_punishment_history?module=&type=1 |
| GET | `/api/v2/shop/get_shop_holiday_mode` | https://open.shopee.com/documents/v2/shop.get_shop_holiday_mode?module=&type=1 |
| GET | `/api/v2/shop/get_shop_info` | https://open.shopee.com/documents/v2/shop.get_shop_info?module=&type=1 |
| GET | `/api/v2/shop/get_shop_list_by_merchant` | https://open.shopee.com/documents/v2/shop.get_shop_list_by_merchant?module=&type=1 |
| GET | `/api/v2/shop/get_shop_notification` | https://open.shopee.com/documents/v2/shop.get_shop_notification?module=&type=1 |
| GET | `/api/v2/shop/get_shop_performance` | https://open.shopee.com/documents/v2/shop.get_shop_performance?module=&type=1 |
| GET | `/api/v2/shop/get_shop_toggle_info` | https://open.shopee.com/documents/v2/shop.get_shop_toggle_info?module=&type=1 |
| GET | `/api/v2/shop/get_total_balance` | https://open.shopee.com/documents/v2/shop.get_total_balance?module=&type=1 |
| GET | `/api/v2/shop/get_warehouse_detail` | https://open.shopee.com/documents/v2/shop.get_warehouse_detail?module=&type=1 |
| GET | `/api/v2/shop/get_warehouse_eligible_shop_list` | https://open.shopee.com/documents/v2/shop.get_warehouse_eligible_shop_list?module=&type=1 |
| POST | `/api/v2/shop/set_shop_holiday_mode` | https://open.shopee.com/documents/v2/shop.set_shop_holiday_mode?module=&type=1 |
| POST | `/api/v2/shop/update_profile` | https://open.shopee.com/documents/v2/shop.update_profile?module=&type=1 |

## warehouse

| method | path | doc |
|---|---|---|
| GET | `/api/v2/warehouse/get_current_inventory` | https://open.shopee.com/documents/v2/warehouse.get_current_inventory?module=&type=1 |
| GET | `/api/v2/warehouse/get_expiry_report` | https://open.shopee.com/documents/v2/warehouse.get_expiry_report?module=&type=1 |
| GET | `/api/v2/warehouse/get_stock_aging` | https://open.shopee.com/documents/v2/warehouse.get_stock_aging?module=&type=1 |
| GET | `/api/v2/warehouse/get_stock_movement` | https://open.shopee.com/documents/v2/warehouse.get_stock_movement?module=&type=1 |
