## Deskripsi

*Kontrak **webhook Accurate Online**: tipe event yang benar-benar ada, dua endpoint API untuk memperpanjang & memeriksa riwayat kiriman, dan — bagian yang paling mahal — **alat ukur mana yang sahih** saat webhook tampak tidak mengirim. Dipisah dari [[External - Accurate]] karena permukaannya berbeda: yang di sana kontrak DATA (faktur, retur, stok, akun), yang di sini kontrak PENDAFTARAN & PENGIRIMAN, dengan model per-aplikasi yang punya kelas kegagalannya sendiri.*

- **Status**: ⚠️ Implemented (ada catatan) — konsumsi webhook stok `ITEM_QUANTITY`/`STOCK_MUTATION` live (lihat [[Microservices - Integration Service]] §Accurate); pembaru masa aktif otomatis ada (`accurate-webhook-renew`); **kiriman untuk database prod 1443290 belum terbukti tiba** (lihat §Belum Terjawab)
- **Sumber kebenaran tipe event**: `bip-erp/docs/accurate-api/accurate-api-resmi.json` (dokumentasi resmi, blok versi `1.0.0#5678`; berkas diambil 2026-07-28). Cara membuktikan: `python3 docs/accurate-api/lihat.py /api` lalu cari aksi `webhook-history` / `webhook-renew`.
- **Endpoint pendaftaran**: `account.accurate.id/api/*` (bukan host data `zeus.accurate.id`)

## 24 Tipe Event Resmi

Field `type` pada `webhook-history` mencantumkan seluruh tipe yang dikenal Accurate — **24, tidak lebih** (diverifikasi 2026-09-10 dari dokumentasi resmi di repo, bukan dari portal):

| Rumpun | Tipe |
|---|---|
| Item & stok | `ITEM` · `ITEM_QUANTITY` · `ITEM_ADJUSTMENT` · `ITEM_TRANSFER` · `STOCK_MUTATION` · `WAREHOUSE` |
| Penjualan | `SALES_QUOTATION` · `SALES_ORDER` · `DELIVERY_ORDER` · `SALES_INVOICE` · `SALES_INVOICE_OWING` · `SALES_RETURN` · `SALES_RECEIPT` |
| Pembelian | `PURCHASE_REQUISITION` · `PURCHASE_ORDER` · `RECEIVE_ITEM` · `PURCHASE_INVOICE` · `PURCHASE_RETURN` · `PURCHASE_PAYMENT` |
| Manufaktur | `JOB_ORDER` · `MATERIAL_ADJUSTMENT` · `ROLL_OVER` |
| Lain | `CUSTOMER` · `GLACCOUNT` |

⛔ **TIDAK ADA `JOURNAL_VOUCHER` — jurnal umum tak punya event webhook sendiri.** Ini penting bagi siapa pun yang berharap menangkap **jurnal manual finance** secara realtime: tak ada saluran push untuk itu, dan satu-satunya jalan tetap **menarik** (polling) seperti yang dilakukan job `accurate-serap-jurnal-kas` (lihat [[IT - Background Jobs & Schedulers]]).

Yang **ada** dan sering disalahpahami sebagai penggantinya: **`GLACCOUNT`**. Jurnal yang menyentuh akun kas memang menggerakkan akun itu, jadi eventnya bisa menyala — tetapi yang diberitahukan adalah **akunnya**, bukan jurnalnya. Isi, nomor, keterangan, dan baris jurnalnya tetap harus ditarik terpisah. Merancang fitur yang menganggap `GLACCOUNT` = notifikasi jurnal akan menghasilkan data yang kurang tanpa satu pun galat.

## Dua Endpoint API Webhook

Keduanya di host **`account.accurate.id`**, bukan host data. Autentikasi sama dengan endpoint `account.accurate.id/api/*` lainnya (lihat [[RUN - Accurate API Access Token (OAuth)]]):

```
Authorization: Bearer <token>
X-Api-Timestamp: <unix detik>
X-Api-Signature: <hex HMAC-SHA256(timestamp, ACCURATE_SECRET_KEY)>
```

### `webhook-renew.do` — memperpanjang masa aktif

- **Masa aktif webhook Accurate MAKSIMAL 7 hari**, lalu berhenti mengirim **TANPA galat**. Kegagalannya senyap: tak ada penolakan, webhook cuma diam, dan layar rekonsiliasi tetap tampak normal dengan data yang membeku — terbaca sebagai "tidak ada transaksi", bukan "saluran datanya mati".
- **Menerima GET maupun POST**, dan **tanpa body** (diukur 2026-09-10). Ini menutup pertanyaan yang sebelumnya terbuka di kode (`accurate_client_webhook.go` menulis "bentuk request BELUM TERVERIFIKASI" karena dokumentasi resmi hanya menyebut nama endpoint tanpa parameter).
- Balasan sukses: `{"s":true,"d":"17/09/2026"}` — **`d` adalah tanggal aktif baru** (`dd/MM/yyyy`), bukan pesan. Bentuk ini juga terverifikasi 2026-09-10.
- Di ERP dijalankan otomatis oleh job **`accurate-webhook-renew`** (harian 05:55 WIB, satu call per run) — harian, bukan tiap 7 hari, supaya satu run gagal masih menyisakan enam kesempatan pulih. `s=false` diperlakukan sebagai **galat** (bukan "tak ada data"), karena renew gagal yang dilaporkan sukses berarti webhook mati minggu depan tanpa jejak.

### `webhook-history.do` — riwayat kiriman

```
GET /api/webhook-history.do?from=&to=[&databaseId=][&type=]
```

- Cakupan: kiriman **1 bulan terakhir**.
- `from` & `to` **wajib**, format **`dd/MM/yyyy HH:mm:ss`**, dan **rentangnya maksimal 24 jam** (dinyatakan dokumentasi resmi pada field `to`). Rentang lebih lebar harus dipecah per hari.
- `databaseId` & `type` opsional.

## ⛔ `webhook-history` melaporkan PER-APLIKASI, bukan per-database

**Ini menyesatkan berjam-jam pada 2026-09-10.** Endpoint ini hanya melaporkan kiriman milik **aplikasi yang menerbitkan token pemanggil**. Dokumentasi resminya sendiri menyatakan API ini "hanya dapat diakses oleh token dari pengguna yang merupakan developer dari aplikasi" — dan konsekuensi yang tak tertulis di sana adalah lingkup jawabannya juga terikat aplikasi itu.

Yang terjadi: token ERP diterbitkan aplikasi **"Bharata"**, sementara webhook diatur di aplikasi **lain**. Hasilnya endpoint membalas **`rowCount:0`** — **padahal Debug Log console penuh kiriman**.

⚠️ **Nol dari endpoint ini BUKAN bukti tak ada kiriman.** Ini kelas kegagalan yang sudah berulang di repo ini: 200 berisi nol baris, bentuk respons sah, angka masuk akal, dan pembacanya menyimpulkan "webhooknya tidak jalan" lalu mulai memperbaiki hal yang tidak rusak.

**Alat ukur yang sahih:**

1. **Debug Log di Area Developer** portal Accurate — melaporkan seluruh kiriman aplikasi yang bersangkutan.
2. **Koleksi `webhook_logs` sendiri** (integration_db) — payload raw selalu disimpan sebelum diproses, jadi ini bukti tibanya kiriman di sisi kita, terlepas dari apa yang dilaporkan Accurate.

`webhook-history` tetap berguna, tapi **hanya** bila tokennya diterbitkan aplikasi yang sama dengan yang memasang webhook. Sebelum memakainya sebagai bukti, buktikan dulu aplikasinya cocok (lihat §Cara mengetahui aplikasi penerbit token).

## ⛔ ADA DUA aplikasi Accurate bernama mirip

Keduanya milik Bharata dan **mudah tertukar** — namanya mirip, keduanya menyentuh database prod (diukur 2026-09-10):

| Nama aplikasi | App Key | Database | Catatan |
|---|---|---|---|
| **Bharata** | `60a3a843-22f5-4b8a-9cd4-7175aedf4fee` | prod **1443290** | **token ERP dipakai dari sini** (`ak` di payload token) |
| **PT. Bharata Internasional Pharmaceutical** | `4abce909-5970-4f00-9c39-4fecdd40d6f9` | Trial IT **2886480** + prod (dipasang 2026-09-10) | **webhook diatur di sini** |

Karena token ERP dan setelan webhook tinggal di **aplikasi berbeda**, tiap pemeriksaan yang menganggap keduanya satu akan salah — dan itu persis akar kekeliruan `rowCount:0` di atas.

### Cara mengetahui aplikasi penerbit sebuah token

Token `aat.…` terdiri dari tiga bagian dipisah titik. **Decode base64 bagian ketiga**, lalu baca:

| Field | Arti |
|---|---|
| `ak` | App Key |
| `an` | nama aplikasi |
| `ap` | app id |
| `d` | database id |

Ini pemeriksaan yang murah dan **wajib dilakukan sebelum menyimpulkan apa pun** dari `webhook-history` atau dari "webhook tidak mengirim".

## ⛔ `databaseId` di payload webhook ≠ `id` dari `db-list.do` sebagai penyaring

Payload webhook memuat `databaseId: 2886480`, dan database itu memang ber-`id: 2886480` di `db-list.do`. **Tetapi jangan menyaring webhook dengan membandingkan `databaseId` payload ke `ACCURATE_DB_ID`** — env itu sengaja kosong di prod (lihat [[External - Accurate]] §Mode token), jadi penyaring semacam itu akan membuang semua kiriman atau meloloskan semuanya, tergantung arah perbandingannya.

**Cara memeriksa database ID yang pasti** — tanya aliasnya:

```
GET /api/db-detail.do?id=<ID>     → mengembalikan `alias`
```

Terverifikasi 2026-09-10:

| `id` | `alias` |
|---|---|
| 2886480 | **Trial IT** |
| 1443290 | **PT Bharata Internasional Pharmaceutical** (prod) |

⚠️ **Jebakan yang sempat menyesatkan: nomor dokumen bisa SAMA di dua database berbeda.** `INV/2026/09/10/001-KY+GB` ada di **keduanya**, tapi `id` internal dan nominalnya berbeda:

| Database | `id` internal | Nominal |
|---|---|---|
| Trial IT (2886480) | 88554 | 222.000 |
| Prod (1443290) | 88020 | 454.000 |

**Mencocokkan nomor dokumen saja bukan bukti dokumen yang sama.** Penomoran Accurate berjalan per-database, jadi dua database yang dipakai berbarengan akan menerbitkan nomor yang bertabrakan sebagai kebetulan yang tampak meyakinkan. Yang membedakan: `id` internal, nominal, dan alias database dari `db-detail.do`.

## Ongkos & Frekuensi (terukur prod 2026-09-10)

Angka-angka ini menentukan apakah sebuah fitur ditarik (polling) atau ditunggu (webhook), dan seberapa sering:

- **`glaccount/get-bs-account-amount.do?asOfDate=`** — **1,48 detik**, 56 KB, mengembalikan **347 akun neraca sekaligus dalam satu call**. ⚠️ Membacanya **per-akun** mengalikan biaya tanpa menambah informasi apa pun; ambil sekali, saring di sisi kita.
- **Volume jurnal ≈ 6.462/bulan** (terbukti Juli 2026) ≈ **208/hari** → menarik detail satu hari ≈ **211 call**.
- **Limiter Accurate 6 req/detik dibagi SELURUH service** — bukan per-job, bukan per-endpoint. Job yang menumpuk di jam yang sama saling merebut jatah laju, termasuk merebutnya dari jalur yang menghadap pengguna.

### Aktivitas kas toko: gelombang tiap ~3 jam

Receipt terkirim per jam WIB (prod, jendela 2 hari, diukur 2026-09-10):

| Jam WIB | 08:00 | 11:00 | 14:00 | 17:00 | 20:00 |
|---|---|---|---|---|---|
| Receipt | 10 | 7 | 11 | 7 | 4 |

⚠️ **Ini membatalkan asumsi lama "penyerapan sehari sekali cukup".** Kas toko bergerak sepanjang jam kerja, dan accounting membuka layar **di tengah hari**, bukan cuma pagi — jadi penyerapan yang hanya jalan dini hari menyajikan data yang sudah tertinggal beberapa gelombang saat orang benar-benar membacanya.

## Belum Terjawab (hipotesis TERBUKA — jangan dibaca sebagai fakta)

🟡 **Webhook aplikasi `4abce909…` belum terbukti mengirim untuk database prod 1443290**, meski aplikasi sudah dipasang di sana (2026-09-10), status **ACTIVE**, Target URL terbukti membalas **HTTP 200**, dan pendaftaran sudah di-renew. **Empat kali** uji membuat pelanggan via API di prod: **nol kiriman**. Sementara **Trial IT mengirim normal**.

⛔ **Hipotesis yang SUDAH DICORET — jangan diulang** (masing-masing sudah dibuktikan salah, dan mengulangnya membakar waktu yang sama untuk kedua kalinya):

| Dugaan | Kenapa dicoret |
|---|---|
| "Webhook hanya terpicu dari UI, bukan dari API" | Kiriman Trial IT justru **dari API** |
| "Setelan webhook per-database" | Setelannya **tunggal per-aplikasi** |
| "Token aplikasi berbeda tak memicu" | ERP memakai token app **Bharata**, webhook app **lain** tetap terpicu di Trial IT |

**Yang belum terjawab**: apakah pemasangan aplikasi ke database baru butuh **langkah aktivasi tambahan**, atau apakah status langganan **"Gratis coba integrasi"** (prod) vs **"Tagihan Aktif"** (Trial IT) memengaruhinya. **Perlu jawaban support Accurate** — bukan percobaan tambahan dari sisi kita, karena ketiga dugaan yang bisa diuji sendiri sudah habis.

## Dependensi & Integrasi

- [[Microservices - Integration Service]] — konsumen: `POST /webhooks/services/accurate` (tipe `ITEM_QUANTITY`/`STOCK_MUTATION`), payload raw ke `webhook_logs`, job `accurate-webhook-renew`
- [[External - Accurate]] — kontrak API data, host, signing, mode token (`ACCURATE_DB_ID` sengaja kosong di prod)
- [[IT - Background Jobs & Schedulers]] — `accurate-webhook-renew` (05:55) & `accurate-serap-jurnal-kas` (jalur TARIK untuk jurnal manual, karena tak ada event `JOURNAL_VOUCHER`)
- [[RUN - Accurate API Access Token (OAuth)]] — cara mendapat token & signing header

## Dokumen Terkait

- [[External - Accurate]] · [[ADR - 0001 Akuntansi via Accurate]] · [[ADR - 0014 Accurate Token DB-backed via OAuth]]
- [[Microservices - Integration Service]] · [[API - Integration Service]]
- [[IT - Background Jobs & Schedulers]] · [[RUN - Accurate API Access Token (OAuth)]]
- [[APP - Web ERP]] — menu `integration-accurate` (monitoring auto-sync)
