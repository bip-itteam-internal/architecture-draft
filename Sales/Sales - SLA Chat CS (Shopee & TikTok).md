---
status: ⚠️ Implemented (ada catatan) — Shopee live, TikTok menunggu approval scope
diukur: 2026-09-08
---

# Sales - SLA Chat CS (Shopee & TikTok)

Metrik SLA respons chat toko untuk KPI Customer Service. Seluruh angka di
dokumen ini berasal dari **panggilan API nyata ke produksi**, bukan dari
dokumentasi — karena dokumentasi kedua platform terbukti tidak cocok dengan
perilaku sebenarnya.

## Ringkas: apa yang tersedia

| | Shopee | TikTok |
|---|---|---|
| Bisa dipanggil hari ini | ✅ 9/9 toko HTTP 200 | ❌ 401 code 105005 |
| Response rate | ✅ | ✅ (setelah scope turun) |
| **Kecepatan balas (menit)** | ❌ **tidak dikirim** | ✅ |
| Atribusi per-agen | ❌ | ❌ |
| Drill-down per sesi | ❌ | ✅ `sessions/search` |

## Shopee — terbuka, tapi lebih sempit dari dokumentasinya

`GET /api/v2/account_health/get_shop_performance` — **tanpa parameter tanggal**.

⛔ **Metric 21 (Response Time), 29 (Average Response Time), dan 23
(No. of Non-Responded Chats) TIDAK DIKIRIM** untuk toko Indonesia, meski
dokumentasi Shopee mendaftarkan ketiganya. Dari 15 metrik yang datang, CS
hanya tiga:

| metric_id | nama | rentang terukur |
|---|---|---|
| 11 | `response_rate` | 86,73 – 100,00 % |
| 22 | `shop_rating` | 4,74 – 4,77 |
| 95 | `csat_rate` | 0 – 100 % |

**Konsekuensi: KPI "kecepatan balas dalam menit" TIDAK BISA dibangun dari
Shopee.** Jangan menjanjikannya.

⛔ **Target BERBEDA antar toko** — Kyura Beauty Official Store `>= 60`,
delapan toko lain `>= 70`. Baca dari respons per toko; konstanta akan salah
untuk toko itu, dan salahnya senyap.

⛔ **Ini SNAPSHOT 30 hari BERJALAN, bukan angka harian.** Endpointnya tak
menerima parameter tanggal; dipanggil hari ini memberi rata-rata 30 hari
terakhir, besok jendelanya bergeser, dan data kemarin **tak bisa diminta
ulang**. Karena itu MENJUMLAHKAN atau MERATA-RATAKAN `response_rate` lintas
tanggal itu SALAH — tiap baris sudah rata-rata yang saling tumpang tindih.

### ⛔ Jebakan kredensial yang memakan waktu paling lama

`SHOPEE_ERP_SYSTEM_PARTNER_ID` / `_KEY`, **BUKAN** `SHOPEE_PARTNER_ID`.

Tiap `account_type` punya pasangan partner sendiri, dan token terbitan app
ERP_SYSTEM hanya sah bila ditandatangani partner ERP_SYSTEM. Salah pasang
menghasilkan **403 `invalid_acceess_token`** — pesan yang terbaca seperti
token kedaluwarsa padahal tokennya sempurna (masih berlaku, dekripsi sukses,
JWT valid). Terbukti 2026-09-08: seluruh 9 toko gagal 403 sampai partner_id
ditukar, lalu seluruhnya 200.

`shopee_credentials` berisi 27 dokumen = 3 tipe × 9 toko. Hanya `ERP_SYSTEM`
yang punya izin `account_health`.

### Chat Shopee tertutup seluruhnya

Modul `sellerchat` menyatakan **"No APP type can call this API"** — bukan soal
izin kita, tak ada tipe app yang boleh. Diverifikasi lewat kontrol pembanding:
`get_shop_performance` di halaman sejenis mencantumkan "Seller In House System"
dan "Customized APP" dan tidak punya baris itu.

Juga **tidak ada push code chat** di `v2.push.set_app_push_config`, jadi
webhook pun tak tersedia.

## TikTok — tergerbang scope, dan scope itu untuk CRM

`GET /customer_service/202407/performance` membalas **401 code 105005**.

Diverifikasi dengan **kontrol positif**: `/authorization/202309/shops` memakai
token dan signing yang sama membalas **200 code=0**. Jadi penolakannya murni
soal scope `seller.customer_service` — bukan token, bukan signing, bukan path.
Versi `202407` sudah terbukti benar (endpoint salah membalas 404, bukan
penolakan izin).

⚠️ **Customer Service API TikTok adalah API PEMINDAHAN KANAL untuk CRM, bukan
API pembacaan data.** Dokumen resminya: *"messages from your TikTok Shop buyers
will be forwarded to third party customer support system... agents to reply
directly on their Customer support platform."*

Itu menjelaskan syarat approval yang tampak aneh: pemohon wajib **sudah punya
antarmuka chat yang berfungsi** (screenshot + rekaman layar), plus data
order/fulfillment/after-sales di layar yang sama. Mereka memeriksa apakah
pemohon benar-benar sebuah CRM.

Syarat skala: 1.000 seller ter-otorisasi ATAU 1 juta panggilan/hari — **dengan
pengecualian** untuk app kategori "TikTok Shop Seller" (merchant bertim dev
sendiri). Jalur itu terbuka bagi kita, tapi syarat antarmuka chat tetap
berlaku lebih dulu.

Target SLA resmi TikTok (jendela 30 hari): 24-hour response rate ≥80 %,
resolution rate ≥65 %, CSAT ≥75 %.

⚠️ Kalaupun BIP membangun CRM, cakupannya **hanya TikTok** — chat Shopee tetap
tertutup, jadi CS masih harus membuka Seller Center untuk Shopee. Setengah
kanal; layak ditimbang sebelum memutuskan investasinya.

## ⛔ KPI ini menilai TOKO, bukan ORANG

Tidak ada satu pun platform yang memberi atribusi per-agen:

- **Shopee** — tak ada sama sekali, hanya agregat per toko
- **TikTok** — dok resmi: *"If a seller has multiple customer service agents,
  their conversations are passed as the main account to the buyer"*

Konsekuensinya mengikat desain: dua CS yang berbagi satu toko menerima angka
**identik**, meski yang satu membalas dalam 5 menit dan yang lain 5 jam.

KPI ini mengukur **"toko yang saya pegang terlayani sebaik apa"**, bukan "saya
membalas secepat apa". Wajib dikomunikasikan begitu ke manajemen.

Karena itu baris yang dikembalikan membawa `cs_lain` (jumlah CS lain di toko
yang sama), dan layar menampilkannya — supaya penilai tahu skornya bersama.

## Yang dibangun di ERP

| Bagian | Lokasi |
|---|---|
| Job sinkron harian | `sync-cs-sla` di marketing-analytics |
| Koleksi mart | `mart_cs_sla_daily` (kunci unik `channel+shop_id+date`) |
| Endpoint mesin | `GET /kpi/sla-chat-cs` (kunci layanan) |
| Endpoint browser | `GET /icc/sla-chat` (JWT) |
| Sumber KPI | `sla_chat_cs` di employee-service |
| Pemetaan CS→toko | `cs_shop_mappings`, `/icc/cs-mappings` |
| Layar | tab "Performa Chat" (panel ICC) + tab "Penugasan CS" (ICC Management) |

⚠️ **`date` = tanggal PENGAMBILAN (WIB)**, bukan tanggal data. Salah zona
membuat tanggal meleset satu hari, dan karena snapshot Shopee tak bisa diminta
ulang, salahnya **permanen**.

⚠️ **Metrik yang tak dikirim disimpan `null`, bukan `0`.** `0%` response rate
adalah vonis terburuk untuk toko yang sebenarnya tidak diukur.

⚠️ **CS berbeda orang dari ICC pemegang toko.** Pemetaannya terpisah
(`cs_shop_mappings`, banyak-ke-banyak) — `icc_account_mappings` adalah
kepemilikan toko, bukan tanggung jawab chat. ICC yang merangkap CS cukup
terdaftar di keduanya. CS terdaftar lewat `system_roles.insentive = "crm"` dan
berada di departemen yang sama dengan ICC (Kyura, Beauty Hacks).

## Dokumen Terkait

- [[Microservices - Marketing Analytics Service]] — tempat job dan endpoint hidup
- [[HRIS - Otomasi Skor KPI]] — mekanisme sumber KPI
- [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] — kenapa rute KPI digerbang
  kunci layanan, bukan bersandar pada JWT gateway
