## Deskripsi

*Peta rantai bisnis yang **secara alur seharusnya satu pengajuan berjalan sampai selesai**, tetapi di kode dipecah jadi beberapa pengajuan terpisah — sehingga ketika pengajuan pertama disetujui, orang membuka layar lain dan **mengetik ulang** data yang sama sebagai pengajuan baru. Disusun 2026-08-26 dari pembacaan kode, bukan dari dokumen.*

- **Status**: ⚠️ **Peta masalah, belum ada keputusan.** Seluruh temuan terverifikasi di kode; **arah perbaikannya sengaja belum diputuskan** (lihat §Belum Diputuskan). Dokumen ini ada supaya keputusannya diambil dari peta utuh, bukan dari satu rantai yang kebetulan sedang disentuh.
- **Path di repo**: `bip-erp/services/{manufacture,procurement,learning,recruitment,attendance,payroll,employee}` · `bip-erp/shared-library`
- **Beda dari [[REF - Alur Persetujuan]]**: dokumen itu menjawab **"persetujuan apa saja yang ada dan siapa yang berwenang"**, disusun per-mekanisme-gerbang. Dokumen ini menjawab **"rantai bisnis mana yang terpecah, dan di titik mana ia putus"**, disusun per-alur-bisnis. Sumbunya berbeda; keduanya dipakai bersama.

## Pola yang dicari, dan cara mengenalinya

Bukan setiap alur bertahap itu cacat. Yang jadi temuan adalah bentuk spesifik ini:

> Entitas hilir **menyimpan ulang** data entitas hulu (nama barang, jumlah, pemohon, nominal) **tanpa menyimpan referensi id** ke hulunya.

Dua akibat yang selalu menyertainya, dan keduanya senyap:

1. **Pertanyaan penelusuran jadi mustahil dijawab.** "Pengajuan ini sudah direalisasikan berapa?" tak punya jawaban, karena tak ada yang menghubungkan realisasi ke pengajuannya. Yang bisa dijawab hanya agregat.
2. **Status hulu berhenti bergerak.** Pengajuan yang sudah 100% dipenuhi tetap berbunyi `menunggu_diproses` selamanya, dan tak ada satu pun galat yang menandainya.

⚠️ **Prefill BUKAN sambungan.** Beberapa layar sudah punya tombol "Ambil dari …" yang menyalin isi dokumen hulu ke form hilir. Itu menolong pengetik, tetapi yang tersimpan tetap salinan lepas: begitu tombolnya ditekan, tak ada apa pun yang tahu keduanya berkerabat. Membaca adanya tombol itu sebagai "rantainya sudah tersambung" adalah kesimpulan yang sudah terbukti keliru di sini — lihat §PR → PO → Penerimaan.

## Inventaris

Kolom **Bukti** menyebut apa yang diduplikasi dan field referensi apa yang dicari lalu **tidak ditemukan**. Ketiadaan field selalu dibuktikan dengan pencarian, tak pernah diasumsikan.

### 1. PPIC → Pengadaan (putus total)

Rantai bisnisnya: PPIC menghitung kebutuhan bahan → permintaan pengadaan → Procurement menerbitkan PR/PO.

| | |
|---|---|
| **Entitas** | `manufacture.MaterialOrder` → `manufacture.ProcurementPO` → `procurement.PermintaanERP` |
| **Diduplikasi** | `supplier_name`, `sku_bahan`, `nama_bahan`, `qty_order`, `unit`, `price_per_unit`, `tanggal_kirim_target`, `procurement_pic` — seluruhnya teks/angka bebas (`shared-library/models/manufacture/models.go:619-638`) |
| **Referensi hilang** | `permintaan_id` · `pesanan_id` · `material_order_id` · `marketing_po_id` — **nol hasil** di seluruh `services/manufacture` |
| **Penguat** | `services/manufacture/main.go:16` → `var InternalURL = map[string]string{}` — **kosong**. Manufacture-service tak pernah memanggil service lain sama sekali. Diverifikasi langsung. |
| **Akibat** | Data yang sama diketik **tiga kali di tiga layar**. `MaterialOrder` bahkan tak punya field status, jadi tak ada cara tahu permintaan bahan mana yang sudah jadi PO. |

Ini bentuk paling murni dari pola tersebut, dan yang paling banyak memakan waktu orang.

✅ **Dikuatkan secara independen** oleh [[Manufacture - Material Order (SPK)]] (ditulis 2026-08-26 dari sisi fitur, bukan dari sisi rantai): MO dinyatakan **"tanpa status/approval"**, dan ketiga sub-tab pada layar yang sama — SPK Material Order, PO Marketing, Permintaan Pengadaan — disebut **"entitas terpisah"**. Dua pembacaan yang berangkat dari arah berbeda sampai pada kesimpulan yang sama, dan itu menaikkan keyakinan bahwa keterpisahannya struktural, bukan kebetulan cara baca.

### 2. Pengajuan pelatihan → Pelatihan (putus total)

| | |
|---|---|
| **Entitas** | `learning.TrainingRequest` (`models_request.go:63-90`) → `learning.Training` (`models_training.go:85-114`) → `TrainingParticipant` |
| **Diduplikasi** | `topic`/`title`, `training_type_id`, `estimated_cost`/`cost`, `department_key` |
| **Referensi hilang** | `request_id` — **nol hasil** di seluruh `services/learning` non-test. Diverifikasi langsung. |
| **Akibat** | Pengajuan berstatus **Disetujui adalah ujung jalan**. HR membuat event pelatihan dari nol dan mendaftarkan pesertanya ulang. Di frontend pun tak ada aksi lanjutan dari layar pengajuan. |

Rantai ini berada di **satu service yang sama**, jadi ia membuktikan penyebabnya bukan sekadar batas service.

### 3. Pengajuan budget → realisasi kas kecil (putus, tersambung hanya lewat agregat)

| | |
|---|---|
| **Entitas** | `procurement.PengajuanBudget` (`pengajuan_budget.go:80-171`) → `procurement.TransaksiKas` (`kas_transaksi.go:41+`) |
| **Diduplikasi** | `unit_kode`, `periode`, `kategori_kode`, `nominal`, `keterangan`, `vendor`, `akun_beban_no`/`nama` |
| **Referensi hilang** | `pengajuan`/`budget` apa pun — **nol hasil** di `kas_transaksi.go`. Diverifikasi langsung. |
| **Jembatan yang ada** | Pengajuan disetujui menambah `TambahanTopUp` pada `PlafonKas` unit+periode yang sama (`pengajuan_budget_approval.go:125`) |
| **Akibat** | Yang bisa dijawab hanya *"plafon unit ini bulan ini bertambah sekian"*. **"Transaksi mana merealisasikan pengajuan mana" tak bisa dijawab sama sekali** — padahal itu pertanyaan audit yang wajar. |

### 4. PR → PO → Penerimaan (setengah jalan, dan inilah yang paling menyesatkan)

| | |
|---|---|
| **Entitas** | `permintaan_erp` → `pesanan_erp` → `penerimaan_erp` |
| **Yang sudah ada** | `RincianPesanan.NoPermintaan` (`pesanan_erp.go:76-77`), `RincianPenerimaan.NoPesanan`/`NoPermintaan` (`penerimaan_erp.go:51-52`), plus modal "Ambil dari Permintaan/Pesanan" di frontend |
| **Kenapa tetap putus** | Referensinya **nomor bertipe string, per-baris, tanpa validasi** — header `PesananERP` tak punya `permintaan_id`, header `PenerimaanERP` tak punya `pesanan_id`. Nilainya hanya di-`TrimSpace`, tak pernah dicek benar-benar ada. |
| **Status hulu mati** | `StatusPermintaanSebagian`, `StatusPermintaanSelesai`, `StatusPesananSebagian`, `StatusPesananTerproses` **hanya ada sebagai definisi** (`permintaan_erp.go:27-28`, `pesanan_erp.go:34-35`) dan satu filter di test. **Nol penulisan di kode produksi.** Diverifikasi langsung. |
| **Akibat** | PR yang sudah sepenuhnya dibelikan **tetap `menunggu_diproses` selamanya**. Konstanta yang tak pernah ditulis terbaca seperti fitur yang ada. |

⚠️ Rantai ini paling berbahaya bagi pembaca dokumentasi: ada tombolnya, ada konstantanya, ada kolomnya — dan tak satu pun bekerja sebagai rantai.

### 5. Penerimaan barang → stok (putus)

`BuatPenerimaanHandler` (`penerimaan_erp_handler.go:24-97`) hanya `InsertOne`. Tak ada panggilan ke warehouse/inventory/manufacture; `Gudang` sekadar string bebas. **Barang yang diterima di ERP tidak menambah stok mana pun.**

### 6. Rekrutmen: hire → karyawan → onboarding (rantai ada sampai offer, putus di hire)

| | |
|---|---|
| **Yang tersambung** | `job_posting.requisition_id` · `candidate.posting_id` · `offer.candidate_id` |
| **Referensi hilang** | `Offer` tanpa `requisition_id`; `OnboardingInstance` tanpa `candidate_id` maupun `offer_id` (`models_onboarding.go:90-106`), dan menyimpan ulang `employee_name`/`position`/`department` sebagai snapshot dari frontend |
| **Titik putusnya** | `PUT /candidates/:id/link-employee` hanya **menautkan sesudahnya**. HR wajib membuka HRIS "Tambah Karyawan" sebagai **form baru** lalu memanggil `create-employee` |
| ⚠️ **Catatan penting** | [[HRIS - Recruitment]] menandai alur dua-langkah ini **✅ selesai** — jadi vault saat ini memperlakukannya sebagai **desain, bukan cacat**. Bila peta ini hendak mengubah statusnya, itu keputusan sadar yang perlu dinyatakan, bukan diperbaiki diam-diam. |

### 7. Pengajuan cuti/koreksi → payroll (putus sesudah run ditutup)

payroll-service **tidak pernah membaca** `leave_request`; ia hanya menerima agregat harian dari attendance. Tak ada penjaga cutoff periode gaji pada **kelima** jenis pengajuan, sehingga pengajuan backdate bisa melewati tutup buku tanpa rekonsiliasi. [[HRIS - Employee Request & Approval]] sudah mencatatnya dan menyatakan **"Keputusan saat ini: dibiarkan apa adanya"** — jadi ini gap yang **sudah diputuskan untuk ditunda**, bukan temuan baru.

### 8. Perjalanan dinas → pencairan (sengaja putus)

`shared-library/models/attendance/models.go:862` menyatakannya eksplisit: **"TIDAK terhubung ke Finance/payroll/reimbursement (keputusan scope)"**. Uang saku diproses manual di luar sistem. ADR-nya masih 🟡 Diusulkan: [[ADR - 0007 Reimbursement Perjalanan Dinas]]. **Ini bukan cacat**, dicantumkan supaya tak berulang kali "ditemukan" sebagai temuan baru.

## Kenapa ini terjadi

Bukan kelalaian satu-dua orang. Penyebabnya struktural: **tidak ada satu pun komponen approval berjenjang bersama.** Yang ada empat mesin terpisah yang tak saling pakai:

| Mekanisme | Lokasi | Bentuk | Dipakai |
|---|---|---|---|
| `ReviewData` + `ReviewStatuses` | `shared-library/models/attendance/models.go:974-997` | **dua slot tetap** `spv_status`/`hr_status` | attendance-service saja |
| `ReviewSlot` + `RequestStatuses` | `services/learning/models_request.go:34-60` | dua slot tetap, **ditulis ulang** | learning-service saja |
| `JenjangWajib` + `TahapSaatIni` + riwayat | `services/procurement/pengajuan_budget.go:71-77` | **satu-satunya rantai n-tahap sungguhan** | terkubur di `package main` procurement |
| `reqTransitions` | `services/recruitment/models_requisition.go:35-52` | state machine per-entitas | recruitment saja |

Alasannya bahkan **tertulis di kode**, di `services/learning/models_request.go:28-31`:

> *"Kosakatanya sengaja sama dengan ReviewStatus milik pengajuan HR lain … **Modul ini tinggal di service berbeda sehingga tipenya tak bisa dipakai bersama**, tapi kata yang berbeda untuk keadaan yang sama cuma menambah hal yang harus diingat orang."*

Dua konsekuensi yang sudah terlihat:

- **Dua slot tetap tak muat menampung rantai berbeda panjang.** [[HRIS - Employee Request & Approval]] mencatat dua alur menaruh peninjau HR di slot `spv_status`, sehingga tahapnya dikenali dari **isi data**, bukan dari nama field.
- **Tiga konvensi berbeda untuk hal yang sama.** "Riwayat pengajuan yang sudah diputus" ditulis `?as=reviewed`, filter kosong, dan `?tampilan=riwayat` di tiga modul ([[APP - Web ERP]]).

`shared-library` (117 berkas Go) **tidak punya** paket `approval`, `workflow`, maupun `request`. Satu-satunya artefak lintas-service di sana adalah daftar jabatan `SetaraDirektur` — konstanta, bukan mesin.

## Usulan urutan, bila kelak dikerjakan

Belum diputuskan. Diurutkan menurut **rasio nyeri terhadap ongkos**, bukan menurut kemudahan:

1. **PR → PO → Penerimaan** — paling murah karena referensinya sudah setengah ada. Menaikkan `NoPermintaan` jadi id di header + menulis status pemenuhan hulu sudah menutup sebagian besar nyerinya, tanpa mesin baru.
2. **Pengajuan pelatihan → Pelatihan** — satu service, satu field (`request_id`), satu tombol lanjutan. Kasus terkecil yang membuktikan polanya bisa ditutup.
3. **PPIC → Pengadaan** — nyeri terbesar (tiga kali ketik), tetapi lintas service dan `InternalURL` manufacture masih kosong, jadi ongkos infrastrukturnya nyata.
4. **Pengajuan budget → realisasi kas** — menuntut keputusan bisnis lebih dulu: apakah satu transaksi boleh merealisasikan lebih dari satu pengajuan.
5. **Mesin alur bersama di `shared-library`** — hanya masuk akal **sesudah** dua sampai tiga rantai di atas dikerjakan tangan. Mengangkat abstraksi sebelum ada tiga pemakai nyata adalah pola yang sudah berulang kali salah di repo ini; lihat prinsip *tunggu pemakai ketiga* di kit.

## Belum Diputuskan (TBD)

- **Apakah arahnya menyambung rantai satu per satu, atau membangun mesin alur bersama.** Belum diputuskan (2026-08-26).
- **Apakah hire → karyawan dianggap cacat atau desain.** Vault saat ini menyatakannya selesai; mengubahnya butuh keputusan eksplisit.
- **Apakah satu transaksi kas boleh merealisasikan banyak pengajuan budget.** Menentukan bentuk relasinya (satu-ke-banyak atau banyak-ke-banyak).
- **Nasib `MaterialOrder` yang tak punya status sama sekali.** Ditambahi status, atau dilebur ke entitas permintaan.

## Cara mengaudit ulang peta ini

Untuk tiap dugaan rantai terputus, buktikan **dua** hal — satu saja tidak cukup:

1. Entitas hilir menyimpan ulang field milik hulu (baca structnya).
2. Tidak ada field referensi. **Grep nama field yang mungkin** (`<hulu>_id`, `no_<hulu>`, `<hulu>_nomor`) di seluruh service hilir, dan laporkan cacah hasilnya. Nol hasil adalah bukti; tidak menemukannya saat membaca sekilas **bukan**.

Tambahan yang sering terlewat: konstanta status yang **didefinisikan tetapi tak pernah ditulis**. Grep nama konstantanya dan periksa apakah ada penugasan di luar definisi dan test — empat konstanta di §4 lolos bertahun-tahun justru karena terlihat ada.

## Dokumen Terkait

- [[REF - Alur Persetujuan]] — siapa yang berwenang memutuskan (sumbu berbeda, dipakai bersama)
- [[HRIS - Employee Request & Approval]] · [[Microservices - Procurement Service]] · [[Microservices - Manufacture Service]] · [[Microservices - Learning Service]] · [[Microservices - Recruitment Service]]
- [[Manufacture - Material Order (SPK)]] — sisi fitur dari rantai §1, menguatkan temuannya secara independen
- [[HRIS - Recruitment]] · [[ADR - 0007 Reimbursement Perjalanan Dinas]] · [[APP - Web ERP]]
