# WH - Laporan Produk Terkirim per Gudang

## Deskripsi

*Laporan harian **produk terkirim, dibatalkan, dan diretur** per produk master untuk dua gudang, **Sadewa** dan **Tinggarjaya**, supaya tim stok bisa menelusuri dari produk mana stok yang kurang. Tersedia dalam dua bentuk dari satu sumber data: **berkas Excel** (ditarik manual) dan **pesan teks WhatsApp otomatis** ke grup stok tiap pagi. Dokumen ini adalah satu-satunya tempat aturan hitungnya ditulis lengkap; dok service lain hanya menunjuk ke sini.*

- **Stack**: Go + Fiber (warehouse-service merakit, integration-service menghitung) + MongoDB + Redis (kunci jadwal) + NotifAPI lewat notification-service untuk WhatsApp.
- **Path di repo**: `bip-erp/services/warehouse/laporan_terkirim.go` (Excel, tarikan data, pengelompokan gudang) · `laporan_terkirim_wa.go` (teks, penjadwal, pengirim, rute manual) · `services/integration/internal/domain/entity/laporan_terkirim.go` (aturan hitung) · `.../usecase/laporan_terkirim.go` · `.../infrastructure/repository/laporan_terkirim_repo.go` · `.../interface/http/laporan_terkirim_handler.go`.
- **Status**: ⚠️ Implemented (ada catatan) — Excel ✅ live prod sejak 2026-10-12 (bip-erp [#2998](https://github.com/bip-itteam-internal/bip-erp/pull/2998)); pengiriman WhatsApp terjadwal ✅ live prod sejak 2026-10-13 (bip-erp [#3053](https://github.com/bip-itteam-internal/bip-erp/pull/3053); pesan pertama terkirim 12:28 WIB lewat catch-up, **jadwal 08:00 yang tulen belum terverifikasi per 2026-10-13**); format tabel monospace sejak [#3082](https://github.com/bip-itteam-internal/bip-erp/pull/3082) (2026-10-13). Detail catatan di *Belum Diimplementasikan / Catatan*.
- **API**: [[API - Warehouse Service]] (§Laporan Produk Terkirim per Gudang) · [[API - Integration Service]] (`/transactions/laporan/produk-terkirim`).

## Persona / Pengguna

| Persona | Peran & Divisi | Akses | Device |
|---|---|---|---|
| Admin gudang / leader / SPV gudang Tinggar | Operasional gudang | Tarik Excel dan kirim ulang WA lewat API (`admin_gudang`, `leader`, `spv`) | PC (Postman/skrip) |
| IT supervisor | Tech Development | Sama, plus uji ke grup IT | PC |
| Anggota grup WhatsApp stok | Tim gudang Tinggarjaya dan Sadewa, finance, seluruh IT | **Membaca** pesan harian; tidak ada akses API | WhatsApp Web dan ponsel |

- **Tujuan**: tahu per produk berapa yang keluar, dibatalkan setelah dikirim, dan diretur balik, tiap hari, tanpa menyusun rekap tangan.
- **Pain point**: stok Accurate berkurang pada hari kirim, sedangkan cancel/retur datang di hari lain; tanpa pemisahan kolom, selisih sulit ditelusuri.
- **Aksi utama**: membaca pesan pagi; menarik Excel bila perlu detail atau tanggal lampau.
- `admin_gudang_sadewa` (mitra Sadewa yang punya akses menu Sadewa) **ditolak** di API ini, walau mereka anggota grup WhatsApp dan sah membaca pesannya: gerbang API mengikuti aturan antrian gudang (lihat [[WH - Warehouse Sadewa]]), grup mengikuti keputusan pemilik proses.

## Aturan Hitung (satu sumber: integration-service)

Tanggal = **hari WIB** (`Asia/Jakarta`), setengah-terbuka `[00:00, 24:00)`. Satuan **pcs master** (bundle dipecah).

| Kolom | Rumus | Catatan |
|---|---|---|
| **Qty Terkirim** | Order ber-`shipped_at` pada hari itu, **bruto**: apa pun status order sekarang (`SHIPPED`, `COMPLETED`, juga yang kemudian `CANCELLED`/`RETURNED`). Order sampel (`is_sample`) ikut. | Barangnya memang sudah keluar dan stok Accurate sudah berkurang pada hari itu (`shipped_at` = hari faktur). Memfilter `status = SHIPPED` saja salah: order lanjut jadi `COMPLETED`, dan membuang yang kemudian batal membuat Cancel/Retur terhitung ganda. |
| **Qty Cancel** | Order yang **sudah** ber-`shipped_at`, dicatat pada hari `cancelled_at` (hari kejadian). | Cancel **sebelum** dikirim tidak dihitung: stok belum berkurang. Hari Cancel bisa beda dari hari kirimnya. |
| **Qty Retur** | Order berstatus `RETURNED` dengan `return.solution = 0` (retur barang kembali), dicatat pada hari `return.requested_at`, sebesar `return.items[].returned_quantity` (retur sebagian sah). | **Refund-only** (`solution = 1`) dikeluarkan karena tidak menambah stok gudang; berlaku untuk TikTok (`REFUND`) dan Shopee sama. `returned_at` **tidak dipakai**: kosong pada 420 dari 593 order `RETURNED` (diukur 2026-10-12). |
| **Total** | Terkirim − Cancel − Retur | Di Excel berupa rumus `=D-E-F`, bukan nilai mati. |

⛔ **Hitung ganda yang disengaja dan yang tidak.** Satu order muncul di Terkirim pada hari X dan di Cancel/Retur pada hari Y: itu **pengimbang**, bukan hitung ganda. Yang dilarang adalah menjumlahkan kolomnya sembarangan di luar rumus Total, dan memakai `status` sebagai penyaring Terkirim.

### Gudang

- **Sadewa** = toko yang terdaftar di `warehouse_db.sadewa_shops` (23 toko TikTok per 2026-10-12). **Tinggarjaya** = semua toko lain, termasuk Shopee dan Lazada. Tak ada master gudang; ini aturan implisit yang sama dengan scope menu Sadewa ([[WH - Warehouse Sadewa]], [[ADR - 0136 Pemilik Master Barang dan Master Gudang]] belum memutuskan master gudang).
- ⚠️ Pembagian memakai isi `sadewa_shops` **saat laporan ditarik**, juga untuk tanggal lampau: toko yang dipindah antar-gudang mengubah laporan lama bila diulang. Pencatatan "sudah terkirim" per tanggal menjaga pesan WhatsApp tidak berubah, tapi Excel tanggal lampau bisa berubah.
- Integration menghitung **per toko x produk** dan tidak tahu daftar Sadewa (database-per-service, [[ADR - 0002 Database-per-Service]]); warehouse-service yang mengelompokkan toko ke gudang.

### Produk, bundle, dan nama

- Bundle dipecah lewat `product_sku_mappings` (`master_sku`, `qty_per_unit`). Mapping tersimpan **satu baris per listing TikTok**, jadi satu bundle muncul puluhan kali: baris ber-`master_sku` sama = alias (dihitung **sekali**, bukan dijumlah), beda `master_sku` = komponen bundle. Aturannya satu fungsi `SusunKomponenSKU` (`incentive_profit.go`) yang **dipakai bersama** HPP insentif (`HitungHPPInsentif`/`HitungHPPSampel`) dan laporan ini (dipindah apa adanya dari `susunPetaHPP`, perilaku HPP tidak berubah). SKU kosong dicocokkan lewat **nama** ke baris penyelamat (`PenyelamatTanpaSKU`); yang tak cocok masuk footer, tidak dikarang.
- Nama produk dari `product_costs.product_name` (berlaku terbaru), cadangan `items.name` (BASE). Satu SKU punya 10 sampai 18 nama listing berbeda antar-toko, jadi nama **tidak boleh** diambil dari order.
- **Tak terpetakan** (SKU salah ketik seperti `PJB - 006`, atau kosong tanpa kecocokan nama): tidak ikut dihitung, jumlah pcs-nya ditulis di footer per gudang (satuan listing, sebelum bundle dipecah). Item yang terpetakan sebagian dihitung tak terpetakan seluruhnya. Cakupan terukur: 21.961 dari 21.968 pcs (99,97%) pada 5–10 Okt 2026.

### Hari dilewati

- **Excel**: bila Terkirim, Cancel, dan Retur semuanya nol → 404 JSON bersebab, bukan berkas kosong.
- **WhatsApp**: dilewati hanya bila **kedua gudang** nol di ketiganya; selain itu **dua pesan selalu terkirim** (gudang yang nol mendapat pesan kecil "Tidak ada produk…").
- Hari Minggu jarang nol: kurir tidak mengambil barang sehingga Terkirim kecil (4 pcs pada 4 Okt, 16 order pada 11 Okt), tapi Cancel tetap terjadi (287 pcs pada 11 Okt). Karena itu aturannya "semua nol", bukan "Terkirim nol".

## Bentuk Keluaran

### Excel

`GET /api/warehouse/wms/laporan/produk-terkirim?tanggal=YYYY-MM-DD` (bawaan: kemarin WIB). Berkas `produk-terkirim-<tanggal>.xlsx`, dua sheet **Sadewa** dan **Tinggarjaya**, kolom Tanggal, Kode, Nama Produk, Qty Terkirim, Qty Cancel, Qty Retur, Total; baris total (`SUM`); catatan di bawah (pcs tak terpetakan, aturan Cancel/Retur, hari Minggu). Gaya mengikuti contoh finance "Produk Terkirim per Hari". ⚠️ Berkas biner: klien yang menampilkannya sebagai teks (mis. tombol unduh Hoppscotch) **merusaknya** (Excel menawarkan "recover"); simpan langsung sebagai byte (PowerShell `Invoke-WebRequest -OutFile`).

### WhatsApp (teks, dua pesan per hari)

Satu pesan per gudang, Sadewa lalu Tinggarjaya, memuat **semua produk**. Bentuk "angka-dulu" (keputusan pemilik 2026-10-13): judul dan tanggal, **Total dan Bersih di atas**, legenda `CNCL = cancel, RTR = retur`, lalu blok monospace WhatsApp dengan baris judul `KIRIM CNCL RTR  PRODUK`; tiap baris produk = tiga angka rata kanan berpemisah ribuan titik, dua spasi, lalu `KODE Nama` **utuh**. Lebar kolom dihitung dari data pesan. Catatan di bawah blok.

- WhatsApp **tidak punya tabel** (hanya `*tebal*`, `_miring_`, blok tiga backtick); angka di kiri dipilih supaya yang terlipat saat baris kepanjangan hanya ujung nama. Diuji manusia 2026-10-13: **WhatsApp Web rapi; di ponsel nama produk terlipat (diterima)**.
- Backtick di nama/kode diganti apostrof dan newline jadi spasi supaya blok tak rusak.
- Pesan dipecah di batas **baris** bila melebihi **3.500 karakter** (batas NotifAPI belum terverifikasi, 3.500 konservatif; Tinggarjaya 32 produk ± 2.800 karakter, biasanya satu pesan). Tiap potongan membuka dan menutup blok sendiri dan mengulang baris judul kolom; potongan lanjutan berjudul `*Gudang X (lanjutan i/n)*`.

## Penjadwal WhatsApp (`laporan_terkirim_wa.go`)

- **Goroutine di warehouse-service** (pola `startReconciler`/`startOpenOrderSweep`): tunda awal 30 detik lalu cek tiap **5 menit**, dibungkus `recover`. Tanpa `REDIS_URL` jadwal tidak menyala (log), rute manual tetap hidup.
- **Jam kirim = lantai** (bawaan **08:00 WIB**, env `LAPORAN_TERKIRIM_JAM_KIRIM`, nilai rusak jatuh ke 08:00): pemeriksa berjalan terus, jadi bila container mati pada 08:00 pesan terkirim begitu hidup lagi (**catch-up**). Tanggal yang dilaporkan = **kemarin menurut kalender WIB**, bukan UTC. Catch-up hanya untuk "kemarin": tanggal yang gagal seharian dan ditinggalkan saat tengah malam harus dikirim manual.
- **Idempoten per (tanggal, gudang, alias)**: koleksi `warehouse_laporan_terkirim_wa` (`warehouse_db`), indeks unik `tanggal_gudang_alias_unique`; dokumen `status` (`terkirim`|`dilewati`), `bagian`, `diproses_at`, `jumlah_proses`. Dicatat **sesudah** semua potongan gudang itu sukses (yang gagal dicoba lagi pada pemeriksaan berikutnya); alias ikut kunci supaya uji ke grup IT tak menghabiskan jatah grup stok. Dua instance: kunci Redis `lock:warehouse-laporan-terkirim-wa` (redsync, `WithTries(1)`, kedaluwarsa 5 menit; batas satu pemeriksaan 4 menit).
- **Alias grup terjadwal**: env `LAPORAN_TERKIRIM_WA_ALIAS` (bawaan `stock`). Alias `stock` dipetakan di `shared-library/notification/whatsapp/whatsapp.go` ke env **`WHATSAPP_GROUP_STOCK_ID`**. warehouse-service ikut mengompilasi pemetaan itu dan memeriksa alias tak terisi **sendiri** (gagal tertutup, tidak mengirim), karena `/wa/send-group` tidak menolak alias kosong — lihat [[Microservices - Notification Service]].
- **Kegagalan tidak senyap**: satu pesan teks ke grup alias `it-alert` per pemeriksaan (galat kirim, alias tak terisi, sumber data gagal, galat Mongo/Redis), throttle **1 jam di memori**: galat konfigurasi menetap bisa ± 16 peringatan per hari dan throttle ter-reset saat restart.
- Hari sepi dicatat `dilewati` **permanen** untuk (tanggal, gudang, alias) tanpa jejak peringatan: bila ingesti macet dan integration mengembalikan nol baris, laporan hari itu tak pernah terkirim; jalan keluar kirim ulang manual dengan `paksa:true`.

## Rute Manual Kirim WhatsApp

`POST /api/warehouse/wms/laporan/produk-terkirim/wa`, body opsional `{"tanggal":"YYYY-MM-DD","paksa":bool,"alias":"stock"|"it"}`. Memakai kode pengirim yang sama dengan jadwal. Alias dibatasi daftar-izin (`stock`, `it`, alias terjadwal); `sales` dan `it-alert` ditolak 400 supaya angka gudang tak dikirim ke grup yang bukan haknya. Respons dan gerbang di [[API - Warehouse Service]].

## Env dan Koleksi

| Nama | Di mana | Fungsi |
|---|---|---|
| `INTEGRATION_SERVICE_KEY` | warehouse **dan** integration (nilai sama) | Kunci layanan untuk `?key=` ke `/transactions/laporan/produk-terkirim`. Dipakai ulang dari jalur KPI employee→integration; kosong = laporan membalas 502 yang menyebut variabelnya. |
| `WHATSAPP_GROUP_STOCK_ID` | `.env` server (dibaca notification **dan** warehouse) | Id grup WhatsApp stok (bentuk `...@g.us`). **Tidak boleh ditulis di repo atau dok** (vault publik). |
| `LAPORAN_TERKIRIM_JAM_KIRIM` | opsional | Jam kirim, bawaan `08:00` WIB. |
| `LAPORAN_TERKIRIM_WA_ALIAS` | opsional | Alias grup terjadwal, bawaan `stock`. |
| `NOTIFICATION_MODULE_URL`, `NOTIFICATION_SERVICE_KEY`, `INTERNAL_GATEWAY_KEY`, `REDIS_URL` | warehouse | Sudah ada (kabar komplain); dipakai ulang. |

Koleksi baru: `warehouse_laporan_terkirim_wa` (di atas). Tak ada penyimpanan data laporan: seluruhnya dihitung saat diminta dari `transaction_orders`.

## Belum Diimplementasikan / Catatan

- ⚠️ **Jadwal 08:00 yang tulen belum terbukti** per 2026-10-13: satu-satunya pengiriman sejauh ini lewat catch-up. Verifikasi: log `laporan terkirim WA <tanggal>` di warehouse dan dua baris `group message sent to "stock"` di notification sekitar 08:05, ditambah dua catatan baru di `warehouse_laporan_terkirim_wa`.
- ⛔ **Start pertama sesudah jam kirim mengirim SEKETIKA ke alias bawaan.** Pada deploy pertama (2026-10-13 12:27 WIB) laporan 12 Okt terkirim ke grup stok 12:28, sebelum sempat diuji ke grup IT. Untuk menguji lebih dulu: set `LAPORAN_TERKIRIM_WA_ALIAS=it` **sebelum** container warehouse dibuat ulang, atau deploy sebelum jam kirim. Restart berikutnya tidak mengirim apa pun selama laporan kemarin sudah tercatat (terbukti restart 14:49 dan 22:16 hari yang sama).
- ⛔ **Deploy DUA container, keduanya `--force-recreate`**: notification-service dan warehouse-service (env grup dibaca saat container dibuat). Bila hanya notification yang dibuat ulang, warehouse memperingatkan "alias belum terisi" dan tidak mengirim (gagal berisik, bukan senyap). Urutannya notification dulu.
- Store Mongo (`catatanWAMongo`) dan indeks unik dites dengan fake saja; terbukti hidup di produksi lewat dua catatan 2026-10-12.
- Bila potongan ke-2 satu gudang gagal setelah potongan ke-1 masuk, percobaan ulang mengirim potongan ke-1 lagi (duplikat, tak ada yang hilang); tidak terjadi pada data sekarang (satu pesan per gudang).
- Retur Shopee berstatus logistik hilang/belum tiba (`solution=0`) belum dibedakan dari barang yang benar-benar kembali; dicatat di footer Excel.
- Perbandingan dengan `fulfillment_orders` WMS (`HANDED_OVER`) dan faktur Accurate harian **belum** dibuat. Angka acuan 2026-10-10 (bruto): Sadewa 729 pcs (9 produk), Tinggarjaya 2.858 pcs (32 produk); selisih +1 dari ukur bebas karena satu item ber-SKU kosong yang dipetakan lewat nama.
- Pengiriman **berkas Excel** lewat WhatsApp tidak ada: kode WhatsApp mengirim teks saja dan dukungan dokumen NotifAPI belum terverifikasi (email dengan lampiran sudah didukung `shared-library/notification/email`).
- Tombol atau halaman FE untuk menarik Excel belum ada (ditarik lewat API/skrip).

## Dependensi & Integrasi

- [[Microservices - Integration Service]] — menghitung per toko x produk (`GET /transactions/laporan/produk-terkirim`, kunci layanan).
- [[Microservices - Notification Service]] — meneruskan `POST /wa/send-group` ke NotifAPI; alias `stock`.
- [[Microservices - Warehouse Service]] — pemilik penjadwal, pengelompokan gudang (`sadewa_shops`), koleksi catatan, dan rute.
- [[IT - Background Jobs & Schedulers]] — baris jadwal in-process.
- Nomor pengirim NotifAPI satu untuk semua alias (sama dengan notifikasi CI/CD); nomor itu harus menjadi anggota grup tujuan.

## Dokumen Terkait

- [[WH - Fulfillment Flow & WMS Tinggarjaya]] · [[WH - Warehouse Sadewa]] · [[REF - Kepemilikan Data]]
- [[API - Warehouse Service]] · [[API - Integration Service]] · [[RUN - Deploy Microservices bip-erp]]
- [[ADR - 0136 Pemilik Master Barang dan Master Gudang]] — master gudang belum diputuskan; laporan ini memakai `sadewa_shops` sebagai satu-satunya definisi.
