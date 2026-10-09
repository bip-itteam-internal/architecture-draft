## Deskripsi

*Kontrak **webhook Accurate Online**: tipe event yang benar-benar ada, dua endpoint API untuk memperpanjang & memeriksa riwayat kiriman, dan — bagian yang paling mahal — **alat ukur mana yang sahih** saat webhook tampak tidak mengirim. Dipisah dari [[External - Accurate]] karena permukaannya berbeda: yang di sana kontrak DATA (faktur, retur, stok, akun), yang di sini kontrak PENDAFTARAN & PENGIRIMAN, dengan model per-aplikasi yang punya kelas kegagalannya sendiri.*

- **Status**: ⚠️ Implemented (ada catatan) — konsumsi webhook stok `ITEM_QUANTITY`/`STOCK_MUTATION` live (lihat [[Microservices - Integration Service]] §Accurate); pembaru masa aktif otomatis (`accurate-webhook-renew`) **baru berfungsi sejak 2026-10-06** (alamat host diperbaiki, bip-erp PR #2654; sebelumnya nol sukses) tetapi **terbukti memperpanjang aplikasi yang SALAH** (uji 2026-10-07/08): webhook dijaga Renew manual di portal, bukan job. Perbaikan (kredensial renew terpisah + penjaga app key, PR #2858) live tetapi tak aktif sampai env diisi, dan belum jelas apakah aplikasi pemilik webhook bisa menerbitkan token `aat.…` (§ Riwayat renew otomatis dan pemulihan); kiriman untuk database prod 1443290 **terbukti tiba** (diukur 2026-10-06, § Belum Terjawab)
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

### Riwayat renew otomatis dan pemulihan (diukur 2026-10-06)

- **Job otomatis tidak pernah berhasil sampai 2026-10-06.** `RenewWebhook` memanggil host DATA (`baseURL`, mis. `zeus.accurate.id`) alih-alih host level-akun di atas, dan dibalas HTTP 404 `{"s":false,"d":["URL API tidak tepat"]}` tiap hari; `workers.worker_history` mencatat nol sukses dari 2026-09-18 sampai 2026-10-06 (riwayat sebelum 2026-09-18 belum dibaca). Alamat diperbaiki di bip-erp PR [#2654](https://github.com/bip-itteam-internal/bip-erp/pull/2654) (live prod 2026-10-06 15:21); balasan sukses kini diperiksa (`d` harus tanggal `dd/MM/yyyy` sah dan lebih dari hari ini WIB) dan tanggal berlaku di-log (`berlaku_sampai`).
- **Kronologi webhook prod** (diukur dari `webhook_logs`, `platform=ACCURATE`): renew manual 2026-09-10 membalas `d=17/09/2026`; kiriman terakhir 2026-09-17 21:10:59 WIB (`SALES_RECEIPT`); **nol event selama 19 hari**, padahal ERP menulis ke Accurate tiap hari; Renew manual lewat portal 2026-10-06 ±09:28 WIB; event pertama sesudahnya 09:28:39 WIB. Kedua database berhenti bersamaan (`databaseId` 1443290 prod dan 2886480 Trial IT).
- ⛔ **Status "ACTIVE" di portal TIDAK berarti masih mengirim.** Pada 2026-10-06 portal menampilkan Webhook Status ACTIVE sementara **Sisa Aktif 0 Hari**; yang menentukan adalah Sisa Aktif. Alat ukur yang sahih untuk "webhook hidup?" tetap `webhook_logs` (`created_at` event terbaru), bukan status.
- **Memulihkan manual:** Area Developer → Aplikasi → (aplikasi pemilik webhook) → Webhook → tombol **Renew**; Sisa Aktif kembali 7 hari. Halaman yang sama memuat Debug Log, Hapus, dan Pengaturan (tipe event).
- **Celah yang ada sebelum perbaikan:** tak ada pengawas "webhook senyap". Kegagalan renew hanya muncul sebagai notifikasi `Worker Failed` yang tenggelam di antara notifikasi sukses, dan 19 hari kiriman hilang tanpa ada yang berbunyi. Pengawas atas `webhook_logs` belum ada (butuh keputusan ambang jam).
- ✅ **Uji pembeda kandidat per-aplikasi (TERJAWAB 2026-10-08: job memperpanjang aplikasi yang SALAH; lihat dua butir sesudah ini):** token ERP diterbitkan aplikasi "Bharata", webhook diatur di aplikasi lain (lihat § ADA DUA aplikasi), dan belum diketahui apakah `webhook-renew.do` juga per-aplikasi seperti `webhook-history`. Trigger manual 2026-10-06 15:36 sukses (`berlaku_sampai=13/10/2026`), tetapi hari ini + 7 sama dengan hasil Renew manual, jadi belum membedakan. Sesudah renew terjadwal 2026-10-07 05:55: Sisa Aktif aplikasi pemilik webhook **7 hari** (`berlaku_sampai=14/10/2026`) berarti job memperpanjang webhook yang benar; **6 hari** berarti job memperpanjang milik aplikasi lain.
- ⛔ **Hasil (diukur 2026-10-07 dan 2026-10-08): job memperpanjang aplikasi LAIN, bukan pemilik webhook.** Job renew sukses dua pagi berturut-turut (`d` = 14/10 lalu 15/10, hari ini + 7), tetapi portal aplikasi `4abce909…` menunjukkan Sisa Aktif **7 Hari lalu 6 Hari**: bila job memperpanjang aplikasi ini, angkanya akan tetap 7. Penyebabnya token ERP diterbitkan aplikasi `Bharata` (`60a3a843…`), sedangkan klien renew memakai token slot utama itu. **Balasan `{"s":true,"d":"<tanggal>"}` TIDAK membuktikan webhook yang benar yang diperpanjang**, dan pemeriksaan tanggal `d` (PR #2654) tak bisa membedakannya. Yang menjaga webhook tetap hidup sejak itu adalah **Renew manual di portal** (paling lambat tiap 7 hari), bukan job.
- ⛔ **Uji Postman 2026-10-09: Signature Secret harus milik aplikasi PENERBIT TOKEN.** `webhook-renew.do` dipanggil dengan token dari halaman **API Token** database prod 1443290 dan Signature Secret aplikasi `4abce909…`; Accurate membalas `{"s":false,"d":["Header X-Api-Signature invalid: Require Application 'Bharata' signature"]}`. Dua hal yang terbukti: (1) halaman API Token database itu memuat delapan token, **semuanya bernama aplikasi `Bharata`**, tak satu pun milik `4abce909…`; (2) signature divalidasi terhadap Signature Secret aplikasi penerbit token, jadi token dan secret dari dua aplikasi berbeda tidak pernah cocok. Panggilan ditolak sebelum menyentuh webhook, jadi Sisa Aktif tak berubah. **Belum terjawab:** apakah aplikasi `4abce909…` bisa menerbitkan token `aat.…` sama sekali (dialog "Buat API Token" belum dilihat), atau tokennya harus lewat alur OAuth yang kedaluwarsa dan perlu refresh. Akun yang memegang aplikasi `Bharata` tak diketahui siapa pun di tim, jadi aplikasi itu tak bisa diperiksa atau dipindahi webhook-nya.
- ✅ **Prod ERP tidak memakai OAuth** (diukur 2026-10-09, baca-saja): `ACCURATE_CLIENT_ID` dan `ACCURATE_REDIRECT_URI` kosong di container integration-service, dan tak ada kredensial OAuth tersimpan. ERP hanya memakai token `aat.…` statis dari `.env` (milik aplikasi `Bharata`). Artinya rancangan "kredensial renew statis" hanya masuk akal bila aplikasi `4abce909…` bisa menerbitkan token `aat.…`.
- ✅ **Pengaman yang sudah live (bip-erp PR [#2858](https://github.com/bip-itteam-internal/bip-erp/pull/2858), deploy prod 2026-10-09 10:57, tak aktif sampai env diisi)**: tiga env OPSIONAL di integration-service. Perilakunya (kode `accurate_webhook_credential.go`, `main.go`):

  | Env | Efek |
  |---|---|
  | `ACCURATE_WEBHOOK_RENEW_TOKEN` + `ACCURATE_WEBHOOK_RENEW_SECRET_KEY` terisi **bersama** | klien renew memakai token + Signature Secret itu (statis, tanpa sesi data) |
  | keduanya kosong (keadaan prod sekarang) | perilaku lama (token slot utama) + satu `WARN` saat boot bahwa aplikasi pemilik webhook tidak diverifikasi |
  | hanya salah satu terisi | keduanya diabaikan, fallback ke slot utama, `WARN` |
  | `ACCURATE_WEBHOOK_APP_KEY` terisi | sebelum memanggil Accurate, field `ak` pada payload token dibandingkan dengan nilai ini; beda berarti renew **ditolak tanpa request** dan job tercatat gagal. Mengisinya tanpa kredensial terpisah membuat job gagal tiap hari (disengaja: kegagalan terang menggantikan keberhasilan palsu) |

  ⚠️ Penjaga membaca payload dari token berbentuk **tepat tiga segmen** `aat.<a>.<b>` (segmen ketiga, base64 std atau URL-safe, dengan atau tanpa padding). **Belum dicocokkan dengan token asli**: sebagian token yang terlihat memuat payload JSON di segmen ketiga, tetapi apakah ada segmen keempat belum diketahui, dan token bersegmen lain ditolak penjaga. Hitung titik pada satu token asli sebelum mengisi `ACCURATE_WEBHOOK_APP_KEY`.

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

✅ **Terjawab 2026-10-06: webhook aplikasi `4abce909…` MENGIRIM untuk database prod 1443290.** `webhook_logs` memuat 60.003 entri `databaseId=1443290` dari 2026-09-10 14:33 sampai 2026-09-17 21:11 WIB (dan 1.535 entri Trial IT 2886480 sampai 20:01), lalu event prod kembali sejak Renew manual 2026-10-06 09:28 WIB. Dugaan lama "belum terbukti mengirim" gugur.

⛔ **Hipotesis yang SUDAH DICORET — jangan diulang** (masing-masing sudah dibuktikan salah, dan mengulangnya membakar waktu yang sama untuk kedua kalinya):

| Dugaan | Kenapa dicoret |
|---|---|
| "Webhook hanya terpicu dari UI, bukan dari API" | Kiriman Trial IT justru **dari API** |
| "Setelan webhook per-database" | Setelannya **tunggal per-aplikasi** |
| "Token aplikasi berbeda tak memicu" | ERP memakai token app **Bharata**, webhook app **lain** tetap terpicu di Trial IT |

**Yang belum terjawab**: (1) ✅ `webhook-renew.do` **per-aplikasi**: terjawab 2026-10-08 (job memperpanjang aplikasi yang salah), tersisa apakah aplikasi `4abce909…` bisa menerbitkan token `aat.…` sendiri (§ Riwayat renew otomatis dan pemulihan); (2) penyebab empat uji membuat pelanggan via API di prod (2026-09-10) menghasilkan nol kiriman: tidak ditelusuri (TBD), jangan dibaca sebagai bukti webhook prod mati. Dugaan lama soal langkah aktivasi tambahan dan status langganan ("Gratis coba integrasi" prod vs "Tagihan Aktif" Trial IT) **tidak lagi perlu dijawab support untuk soal ini**: prod terbukti mengirim.

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
