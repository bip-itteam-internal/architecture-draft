# product.get_item_base_info

- Path: `/api/v2/product/get_item_base_info`
- Method: GET
- Auth: shop
- Deskripsi: Use this api to get basic info of item by item_id list.
- Sumber: open.shopee.com/documents/v2/product.get_item_base_info?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_id_list` | int64[] | ya | item_id list; limit [0,50] Contoh: `[34001,34002]` |
| `need_tax_info` | boolean | tidak | if true will response tax_info Contoh: `true` |
| `need_complaint_policy` | boolean | tidak | if true will response complaint_policy Contoh: `true` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.item_list` | object[] |  |
| `response.item_list[].item_id` | int64 | Shopee's unique identifier for an item. |
| `response.item_list[].category_id` | int32 | Shopee's unique identifier for a category. |
| `response.item_list[].item_name` | string | Name of the item in local language. |
| `response.item_list[].description` | string | if description_type is normal , Description information will be returned through this field，else description will be empty |
| `response.item_list[].item_sku` | string | An item SKU (stock keeping unit) is an identifier defined by a seller, sometimes called parent SKU. Item SKU can be assigned to an item in Shopee Listings. |
| `response.item_list[].create_time` | timestamp | Timestamp that indicates the date and time that the item was created. |
| `response.item_list[].update_time` | timestamp | Timestamp that indicates the last time that there was a change in value of the item, such as price/stock change. |
| `response.item_list[].attribute_list` | object[] |  |
| `response.item_list[].attribute_list[].attribute_id` | int32 | The Identify of each category. |
| `response.item_list[].attribute_list[].original_attribute_name` | string | The name of each attribute. |
| `response.item_list[].attribute_list[].is_mandatory` | boolean | This is to indicate whether this attribute is mandantory. |
| `response.item_list[].attribute_list[].attribute_value_list` | object[] |  |
| `response.item_list[].attribute_list[].attribute_value_list[].value_id` | int32 | Unique identifier for value of this item attribute. |
| `response.item_list[].attribute_list[].attribute_value_list[].original_value_name` | string | Value name of this item attribute. |
| `response.item_list[].attribute_list[].attribute_value_list[].value_unit` | string | Value unit of this item attribute. |
| `response.item_list[].price_info` | object[] | If the item has models, price_info will not be returned. Please get the price of each model through the get_model_list api |
| `response.item_list[].price_info[].currency` | string | The three-digit code representing the currency unit used for the item in Shopee Listings. |
| `response.item_list[].price_info[].original_price` | float | The original price of the item in the listing currency. |
| `response.item_list[].price_info[].current_price` | float | The current price of the item in the listing currency. If product under a onging promotion, current_price will be the promotion price |
| `response.item_list[].price_info[].inflated_price_of_original_price` | float | The After-tax original price of the item in the listing currency. |
| `response.item_list[].price_info[].inflated_price_of_current_price` | float | The After-tax current price of the item in the listing currency. |
| `response.item_list[].price_info[].sip_item_price` | float | The price of the item in sip.If item is for CNSC primary shop, this field will not be returned |
| `response.item_list[].price_info[].sip_item_price_source` | string | source of sip' price. ( auto or manual).If item is for CNSC SIP primary shop, this field will not be returned |
| `response.item_list[].price_info[].local_price` | float | The original price multiplied by the local adjustment rate equals the local price. The local price is denominated in the local currency and is rounded to two decimal places. |
| `response.item_list[].price_info[].local_promotion_price` | float | During the promotion period, the CB price is multiplied by the local adjustment rate. Once the promotion starts, the price remains unchanged. During the promotion, the local_promotion_price= current_price, which is denominated in the local currency and retained to two decimal places. |
| `response.item_list[].image` | object |  |
| `response.item_list[].image.image_url_list` | string[] | List of image url. |
| `response.item_list[].image.image_id_list` | string[] | List of image id. |
| `response.item_list[].image.image_ratio` | string | Image ratio |
| `response.item_list[].weight` | string | The weight of this item, the unit is KG. If set the weight of models under this item, will return the max weight of all models during the switching period to ensure system compatibility, please switch to call v2.product.get_model_list to get the weight of models. |
| `response.item_list[].dimension` | object | The dimension of this item. If set the dimension of models under this item, will return the dimension with largest volume calculated by height*length*width during the switching period to ensure system compatibility, please switch to call v2.product.get_model_list to get the dimension of models. |
| `response.item_list[].dimension.package_length` | int32 | The length of package for this item, the unit is CM. |
| `response.item_list[].dimension.package_width` | int32 | The width of package for this item, the unit is CM. |
| `response.item_list[].dimension.package_height` | int32 | The height of package for this item, the unit is CM. |
| `response.item_list[].logistic_info` | object[] | The logistics list. |
| `response.item_list[].logistic_info[].logistic_id` | int32 | The identity of logistic channel. |
| `response.item_list[].logistic_info[].logistic_name` | string | The name of logistic. |
| `response.item_list[].logistic_info[].enabled` | boolean | Related to shopee.logistics.GetLogistics result.logistics.enabled only affect current item. |
| `response.item_list[].logistic_info[].shipping_fee` | float | Only needed when logistics fee_type = CUSTOM_PRICE. |
| `response.item_list[].logistic_info[].size_id` | int32 | If specify logistic fee_type is SIZE_SELECTION size_id is required. |
| `response.item_list[].logistic_info[].is_free` | boolean | when seller chooses this option, the shipping fee of this channel on item will be set to 0. Default value is False. |
| `response.item_list[].logistic_info[].estimated_shipping_fee` | float | Estimated shipping fee calculated by weight. Don't exist if channel is no-integrated. |
| `response.item_list[].pre_order` | object |  |
| `response.item_list[].pre_order.is_pre_order` | boolean | Pre-order will be set true. |
| `response.item_list[].pre_order.days_to_ship` | int32 | The days to ship. Only work for pre-orde. |
| `response.item_list[].wholesales` | object[] | The wholesales tier list. |
| `response.item_list[].wholesales[].min_count` | int32 | The min count of this tier wholesale. |
| `response.item_list[].wholesales[].max_count` | int32 | The max count of this tier wholesale. |
| `response.item_list[].wholesales[].unit_price` | float | The current price of the wholesale in the listing currency.If item is in promotion, this price is useless. |
| `response.item_list[].wholesales[].inflated_price_of_unit_price` | float | The After-tax Price of the wholesale show to buyer. |
| `response.item_list[].condition` | string | Is it second-hand. |
| `response.item_list[].size_chart` | string | Url of size chart image. |
| `response.item_list[].item_status` | string | Enumerated type that defines the current status of the item. Applicable values: NORMAL, BANNED, UNLIST, SELLER_DELETE, SHOPEE_DELETE, REVIEWING . |
| `response.item_list[].deboost` | boolean | If deboost is true, means that the item's search ranking is lowered. |
| `response.item_list[].has_model` | boolean | Does it contain model. |
| `response.item_list[].has_promotion` | boolean | Indicates whether the item is currently under any ongoing promotion. |
| `response.item_list[].video_info` | object[] | Info of video list. |
| `response.item_list[].video_info[].video_url` | string | Url of video. |
| `response.item_list[].video_info[].thumbnail_url` | string | Thumbnail of video. |
| `response.item_list[].video_info[].duration` | int32 | Duration of video. |
| `response.item_list[].brand` | object |  |
| `response.item_list[].brand.brand_id` | int32 | Id of brand. |
| `response.item_list[].brand.original_brand_name` | string | Original name of brand. |
| `response.item_list[].item_dangerous` | int32 | This field is only applicable for local sellers in Indonesia and Malaysia. Use this field to identify whether a product is a dangerous product. 0 for non-dangerous product and 1 for dangerous product. For more information, please visit the market's respective Seller Education Hub. |
| `response.item_list[].gtin_code` | string | gtin code for br region, will return this code only item has default model Note: gtin_code = "00" means that this item is “Item without GTIN” |
| `response.item_list[].size_chart_id` | int64 | id of new size chart. |
| `response.item_list[].promotion_image` | object |  |
| `response.item_list[].promotion_image.image_id_list` | string[] | Promotion image |
| `response.item_list[].promotion_image.image_url_list` | string[] | Promiton image urls |
| `response.item_list[].promotion_image.image_ratio` | string | Promotion image ratio |
| `response.item_list[].compatibility_info` | object |  |
| `response.item_list[].compatibility_info.vehicle_info_list` | object[] |  |
| `response.item_list[].compatibility_info.vehicle_info_list[].brand_id` | int64 | ID of the brand. |
| `response.item_list[].compatibility_info.vehicle_info_list[].model_id` | int64 | ID of the model. |
| `response.item_list[].compatibility_info.vehicle_info_list[].year_id` | int64 | ID of the year. |
| `response.item_list[].compatibility_info.vehicle_info_list[].version_id` | int64 | ID of the version. |
| `response.item_list[].scheduled_publish_time` | timestamp | Scheduled publish time of this item. |
| `response.item_list[].authorised_brand_id` | int64 | ID of authorised reseller brand. |
| `response.item_list[].ssp_id` | int64 | Shopee's unique identifier for Shopee Standard Product. |
| `response.item_list[].is_fulfillment_by_shopee` | boolean | return true if the item only has a default model and it is FBS model |
| `response.item_list[].tag` | object |  |
| `response.item_list[].tag.kit` | boolean | Indicate if the item is kit item. |
| `response.item_list[].purchase_limit_info` | object | purchase limit info |
| `response.item_list[].purchase_limit_info.min_purchase_limit` | int32 | minimum purchase count for each order |
| `response.item_list[].purchase_limit_info.max_purchase_limit` | object |  |
| `response.item_list[].purchase_limit_info.max_purchase_limit.purchase_limit` | int32 | maximum purchase limit for each order |
| `response.item_list[].medicine_id` | int64 | [Only for ID local sellers] as a unique identifier for each standardized medicine. |
| `response.item_list[].certification_info` | object | For PH product certification input Required for some category and attribute option |
| `response.item_list[].certification_info.certification_list` | object[] | Array of certification records for the product, each containing type, certificate number, permit ID, and proof documents. |
| `response.item_list[].certification_info.certification_list[].permit_id` | int32 | Permit ID, get from v2.product.get_product_certification_rule |
| `response.item_list[].certification_info.certification_list[].certification_no` | string | Certification No. |
| `response.item_list[].certification_info.certification_list[].expiry_date` | int32 | expiry timestamp |
| `response.item_list[].certification_info.certification_list[].certification_proofs` | object[] | An array of proof documents for the certification; each element represents one proof file. |
| `response.item_list[].certification_info.certification_list[].certification_proofs[].image_id` | string | The unique image ID of the certification proof, returned by the image upload API. |
| `response.item_list[].certification_info.certification_list[].certification_proofs[].ratio` | float | image weight/ image height. |
| `response.item_list[].certification_info.certification_list[].certification_proofs[].file_name` | string | The name of the uploaded certification proof file. |
| `response.item_list[].certification_info.certification_list[].certification_proofs[].image_url` | string | The image url of the proof |
| `response.complaint_policy` | object | Complaint policy.Only returned for local PL sellers, and need_complaint_policy in request is true. |
| `response.complaint_policy.warranty_time` | string | Time for a warranty claim.Value should be in one of ONE_YEAR TWO_YEARS OVER_TWO_YEARS. |
| `response.complaint_policy.exclude_entrepreneur_warranty` | boolean | If True means "I exclude warranty complaints for entrepreneur" |
| `response.complaint_policy.complaint_address_id` | int64 | The identity of complaint address. |
| `response.complaint_policy.additional_information` | string | Additional information for complaint policy |
| `response.tax_info` | object | Tax information |
| `response.tax_info.ncm` | string | Mercosur Common Nomenclature, it is a convention between Mercosur member countries to easily recognize goods, services and productive factors negotiated among themselves.(BR region) Note: ncm = "00" means that this item doesn't have a NCM. |
| `response.tax_info.diff_state_cfop` | string | Tax Code of Operations and Installments for orders that seller and buyer are in different states. It identifies a specific operation by category at the time of issuing the invoice. (BR region) |
| `response.tax_info.csosn` | string | Code of Operation Status – Simples Nacional, code for company operations to identify the origin of the goods and the taxation regime of the operations. (BR region) |
| `response.tax_info.origin` | string | Product source, domestic or foreig (BR region) |
| `response.tax_info.cest` | string | Tax Replacement Specifying Code (CEST), to separate within the same NCM products that do or do not have ICMS tax substitution. (BR region) Note: cest = "00" means that this item doesn't have a CEST. |
| `response.tax_info.measure_unit` | string | (BR region) |
| `response.tax_info.invoice_option` | string | Value shuold be one of NO_INVOICES VAT_MARGIN_SCHEME_INVOICES VAT_INVOICES NON_VAT_INVOICES and if value is NON_VAT_INVOICE vat_rate should be null (PL region) |
| `response.tax_info.vat_rate` | string | Value should be one of 0% 5% 8% 23% NO_VAT_RATE (PL region) |
| `response.tax_info.hs_code` | string | HS Code (Only for IN region) |
| `response.tax_info.tax_code` | string | Tax Code (Only for IN region) |
| `response.tax_info.tax_type` | int32 | tax_type only for TW whitelist shop. Shopee will referred Tax type when substitute sellers for issuing e-receipts to buyers. All variations share the same tax type. The meaning of value: 0: no tax type 1: tax-able 2: tax-free |
| `response.tax_info.pis` | string | Only for BR shop. PIS - Programa de Integração Social (Social Integration Program). It is a government tax to collect resources for the payment of unemployment insurance and other employee related rights. PIS % - the tax applied to this product |
| `response.tax_info.cofins` | string | Only for BR shop. COFINS – Contribuição para Financiamento da Seguridade Social (Contribution for Social Security Funding). It is a government tax to collect resources for public health system and social security. COFINS % - the tax applied to this product |
| `response.tax_info.icms_cst` | string | Only for BR shop. ICMS - Imposto sobre Circulação de Mercadorias e Serviços (Circulation of Goods and Services Tax). CST - Código da Situação Tributária (Tax Situation Code) is represented by a combination of 3 numbers with the purpose of demonstrating the origin of a product and determining the form of taxation that will apply to it. Therefore, each digit in the CST Table has a specific meaning: the first digit indicates the origin of the operation, the second digit represents the ICMS taxation on the operation and the third digit provides additional information about the form of taxation. |
| `response.tax_info.pis_cofins_cst` | string | Only for BR shop. The CST PIS/Cofins is a code on the Electronic Invoice (NF-e) that identifies the tax situation of PIS (Programa de Integração Social) and Cofins (Contribuição para o Financiamento da Seguridade Social) in sales of goods. |
| `response.tax_info.federal_state_taxes` | string | Only for BR shop. Enter the total percentage of the combination of federal, state, and municipal taxes, using up to two decimals. |
| `response.tax_info.operation_type` | string | Only for BR shop. 1: Retailer 2: Manufacturer |
| `response.tax_info.ex_tipi` | string | Only for BR shop. The EXTIPI field in the NF-e (Nota Fiscal Eletrônica) is used to indicate if there's an exception to the IPI (Imposto sobre Produtos Industrializados) tax rate for a specific product. |
| `response.tax_info.fci_num` | string | Only for BR shop. The FCI Control Number is a unique identifier assigned to each import FCI (Import Content Form). It's mandatory on the corresponding NF-e (electronic invoice) to ensure compliance with Brazilian import tax regulations. |
| `response.tax_info.recopi_num` | string | Only for BR shop. RECOPI NACIONAL is a Brazilian government system that facilitates the registration and management of tax-exempt operations involving paper destined for printing books, newspapers, and periodicals (known as "papel imune" in Portuguese). |
| `response.tax_info.additional_info` | string | Only for BR shop. Include relevant information to display on Invoice. |
| `response.tax_info.group_item_info` | object | Only for BR shop. Required if the item is a group item. |
| `response.tax_info.group_item_info.group_qtd` | string | Example: The package contains 6 soda cans. Whether you are selling a pack of 6 cans (fardo) or a single can (unit), enter 6. |
| `response.tax_info.group_item_info.group_unit` | string | Example: The package contains 6 soda cans. Whether you are selling a pack of 6 cans (fardo) or a single can (unit), enter UNI for the individual can. |
| `response.tax_info.group_item_info.group_unit_value` | string | Example: The package contains 6 soda cans. Whether you are selling a pack of 6 cans (fardo) or a single can (unity), enter the value of the individual can. |
| `response.tax_info.group_item_info.original_group_price` | string | Example: The item is a package that contains 6 soda cans. Enter the price of the whole package. |
| `response.tax_info.group_item_info.group_gtin_sscc` | string | Example: The item is a package that contains 6 soda cans. Please inform the GTIN SSCC code for the package. |
| `response.tax_info.group_item_info.group_grai_gtin_sscc` | string | Example: The item is box, that contain 6 packages. Each package contains 6 soda cans. Please inform the GRAI GTIN SSCC code for the Box. |
| `response.tax_info.export_cfop` | string | 7101 - for sales of self-produced goods 7102 - resale of third-party goods a tax code used in Brazil to classify and identify the nature of goods or services transactions for tax purposes. This is used for goods export to other counties |
| `response.description_info` | object | New description field. Only whitelist sellers can use it. |
| `response.description_info.extended_description` | object | If description_type is extended , Description information will be returned through this field. |
| `response.description_info.extended_description.field_list` | object[] | Field of extended description |
| `response.description_info.extended_description.field_list[].field_type` | string | Type of extended description field ：values: See Data Definition- description_field_type (text , image). |
| `response.description_info.extended_description.field_list[].text` | string | If field_type is text, text information will be returned through this field. |
| `response.description_info.extended_description.field_list[].image_info` | object | If field_type is image, image url will be returned through this field. |
| `response.description_info.extended_description.field_list[].image_info.image_id` | string | Image id |
| `response.description_info.extended_description.field_list[].image_info.image_url` | string | Image url. |
| `response.description_type` | string | Type of description : values: See Data Definition- description_type (normal , extended). |
| `response.stock_info_v2` | object | new stock object |
| `response.stock_info_v2.summary_info` | object | stock summary info |
| `response.stock_info_v2.summary_info.total_reserved_stock` | int32 | Stock reserved for promotion. Note: For SIP P Item, will return the total reserved stock for P Item and all A Items under the P Item; |
| `response.stock_info_v2.summary_info.total_available_stock` | int32 | total available stock |
| `response.stock_info_v2.seller_stock` | object[] | seller stock |
| `response.stock_info_v2.seller_stock[].location_id` | string | location id |
| `response.stock_info_v2.seller_stock[].stock` | int32 | stock in the current warehouse |
| `response.stock_info_v2.seller_stock[].if_saleable` | boolean | To return if the stock of the location id is saleable |
| `response.stock_info_v2.shopee_stock` | object[] | shopee stock |
| `response.stock_info_v2.shopee_stock[].location_id` | string | location id |
| `response.stock_info_v2.shopee_stock[].stock` | int32 | stock in the current warehouse |
| `response.stock_info_v2.advance_stock` | object | Only for PH/VN/ID/MY local selected shops. |
| `response.stock_info_v2.advance_stock.sellable_advance_stock` | int32 | Refers to Advance Fulfillment stock that Seller has shipped out and is available to be used to fulfill an order. |
| `response.stock_info_v2.advance_stock.in_transit_advance_stock` | int32 | Refers to Advance Fulfillment stock that seller has shipped out and is still in transit and unavailable to be used to fulfill an order. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
