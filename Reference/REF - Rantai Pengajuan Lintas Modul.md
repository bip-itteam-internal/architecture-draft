## Deskripsi

*Peta rantai bisnis yang **secara alur seharusnya satu pengajuan berjalan sampai selesai**, tetapi di kode dipecah jadi beberapa pengajuan terpisah — sehingga ketika pengajuan pertama disetujui, orang membuka layar lain dan **mengetik ulang** data yang sama sebagai pengajuan baru. Disusun 2026-08-26 dari pembacaan kode, bukan dari dokumen.*

- **Status**: ⚠️ **Peta masalah, belum ada keputusan.** Seluruh temuan terverifikasi di kode; **arah perbaikannya sengaja belum diputuskan** (lihat §Belum Diputuskan). Dokumen ini ada supaya keputusannya diambil dari peta utuh, bukan dari satu rantai yang kebetulan sedang disentuh.
- **Diukur ulang 2026-09-22** ke `origin/main`, dan hasilnya **lebih baik daripada peta aslinya** di tiga titik, masing-masing sudah diralat di tempatnya: bukti isolasi manufacture di §1 sudah tidak berlaku, `RealisasiQty` di §1 membuat hulu PO Marketing bergerak sebagian, dan learning sudah membangun rantai baru yang tersambung benar (§2). Klaster pengadaan dan produksi tetap putus di **kedua** pemeriksaan: sebelas nama rujukan dicari (`permintaan_id`, `pesanan_id`, `material_order_id`, `marketing_po_id`, `request_id`, `po_id`, `pr_id`, `penerimaan_id`, `budget_id`, `pengajuan_id`, `training_request_id`) dan **seluruhnya nol hasil**, sementara penyambungnya tetap teks (`no_permintaan` 2×, `nomor_po` 2×, `no_pesanan`, `no_terima`) dan kata "terpenuhi" di procurement muncul 5× **seluruhnya di komentar**. ⚠️ Rantai yang dibangun SESUDAH peta ini justru patuh (`plan_item_id`, `requisition_id`, `manpower_plan_id`, `candidate_id`, `program_id`, `ulasan_comment_id`), jadi yang tersisa adalah utang lama, bukan kebiasaan yang masih berjalan.
- **Diukur ulang 2026-09-29** ke bip-erp `origin/main` `89296af7`, erp-frontend `origin/main` `1b9821715`, dan data PROD (baca saja; seluruh image prod dibangun 2026-09-29 04:38 WIB). Cakupannya diperluas dari rantai "pengajuan" ke **28 mata rantai** di lima klaster proses (Procure-to-Pay, Order-to-Cash, Plan-to-Produce, Hire-to-Pay, Komplain → CAPA). Kriteria tersambung: hilir menyimpan **id** hulu (bukan teks ketik ulang) **dan** status hulu bergerak. Hasil: **18 tersambung, 2 sebagian, 8 putus atau tak ada modulnya** (64%; 68% bila yang sebagian dihitung setengah). Yang **membaik**: jalur Pengajuan Barang ([[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]]) tersambung dari permintaan sampai jurnal (§9). ⚠️ **Tapi di PROD jalur itu baru berisi 2 dokumen**, dan pengadaan harian masih berjalan di Accurate, jadi "tersambung di kode" belum berarti "dipakai". Yang **tetap putus**: PPIC → pengadaan (§1), status hulu PR/PO (§4), `penerimaan_erp` yang hanya `InsertOne` (§5), hire → karyawan (§6), cuti → payroll tanpa cutoff (§7). Yang **baru tercatat**: stok FG masuk sebelum rilis QC dan dua register rilis batch (§10), payroll tak menjurnal (§11), komplain tak melahirkan CAPA tertaut (§12), stok keluar FG manual (§13).
- **Gerbangnya kini ada**: `.agent-kit/rules/review-checklist.md` §F2 menolak entitas hilir yang menyimpan ulang hulu tanpa rujukan id, dengan dua pemeriksaan yang sama dengan §Cara mengaudit ulang di bawah. Keparahannya sengaja dibatasi pada rantai putus **baru**; rantai di dok ini tidak memblokir PR yang tak menyentuhnya, karena arah perbaikannya memang belum diputuskan.
- **Path di repo**: `bip-erp/services/{manufacture,procurement,learning,recruitment,attendance,payroll,employee,warehouse,integration,inventory}` · `bip-erp/shared-library`
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
| ~~**Penguat**~~ | ⛔ **Bukti ini SUDAH TIDAK BERLAKU, diukur ulang 2026-09-22.** Dulu berbunyi: `InternalURL` manufacture kosong, jadi service itu tak pernah memanggil siapa pun. Di `origin/main` manufacture memanggil integration di **empat** tempat (`accurate_push.go:294`, `resi.go:345`, `returns.go:351`, `sync_hpp.go:56`) serta employee dan notification (`po_notify.go:108`, `:173`). ⚠️ Yang patah bukan cuma angkanya melainkan **metodenya**: komentar di `po_notify.go:97` menyatakan `EMPLOYEE_MODULE_URL` sengaja dibaca `os.Getenv` langsung, **tidak** lewat map yang divalidasi. Jadi `InternalURL` kosong tak lagi membuktikan sebuah service terisolasi, di sini maupun di service mana pun. Ukur dengan meng-grep `*_MODULE_URL`, bukan map-nya. |
| **Akibat** | Data yang sama diketik **tiga kali di tiga layar**. `MaterialOrder` bahkan tak punya field status, jadi tak ada cara tahu permintaan bahan mana yang sudah jadi PO. |

Ini bentuk paling murni dari pola tersebut, dan yang paling banyak memakan waktu orang.

**Diukur ulang 2026-09-29: masih putus.** `git grep -i -E 'material_?order|MaterialOrder|procurement_po' origin/main -- services/procurement` **nol hasil**, manufacture tak punya `PROCUREMENT_MODULE_URL`, dan `ProcurementPO` tetap tanpa id MO. Rujukan baris di tabel atas sudah bergeser: struct `ProcurementPO` kini di `shared-library/models/manufacture/models.go:702-721`.

⚠️ **Setengah langkah yang sudah ada, diukur 2026-09-22**: `MarketingPOItem.RealisasiQty` (`shared-library/models/manufacture/models.go`) diisi PPIC saat menindak PO, dan dipakai metrik KPI akurasi demand forecasting SPV Marketing. Jadi untuk PO Marketing hulunya **sudah bergerak sebagian**, berbeda dari kalimat "status hulu berhenti bergerak" di §Pola. Yang tetap hilang rujukan id-nya, sehingga realisasi tak bisa ditelusuri ke permintaan mana. `MaterialOrder` sendiri tidak berubah: nol rujukan, nol field status (diperiksa ulang di `origin/main`).

✅ **Dikuatkan secara independen** oleh [[Manufacture - Material Order (SPK)]] (ditulis 2026-08-26 dari sisi fitur, bukan dari sisi rantai): MO dinyatakan **"tanpa status/approval"**, dan ketiga sub-tab pada layar yang sama — SPK Material Order, PO Marketing, Permintaan Pengadaan — disebut **"entitas terpisah"**. Dua pembacaan yang berangkat dari arah berbeda sampai pada kesimpulan yang sama, dan itu menaikkan keyakinan bahwa keterpisahannya struktural, bukan kebetulan cara baca.

### 2. Pengajuan pelatihan → Pelatihan (putus total)

| | |
|---|---|
| **Entitas** | `learning.TrainingRequest` (`models_request.go:63-90`) → `learning.Training` (`models_training.go:85-114`) → `TrainingParticipant` |
| **Diduplikasi** | `topic`/`title`, `training_type_id`, `estimated_cost`/`cost`, `department_key` |
| **Referensi hilang** | `request_id` — **nol hasil** di seluruh `services/learning` non-test. Diverifikasi langsung. |
| **Akibat** | Pengajuan berstatus **Disetujui adalah ujung jalan**. HR membuat event pelatihan dari nol dan mendaftarkan pesertanya ulang. Di frontend pun tak ada aksi lanjutan dari layar pengajuan. |

Rantai ini berada di **satu service yang sama**, jadi ia membuktikan penyebabnya bukan sekadar batas service.

✅ **Dan service yang sama sudah membuktikan bisa**, diukur 2026-09-22. Rantai **baru** rencana pelatihan tahunan ke kelas tersambung benar lewat `training.plan_item_id` (`services/learning/models_training.go`), dan status pelaksanaannya **diturunkan** dari kelas yang tertaut (`statusButirRencana`, dipakai `kpi_rencana_pelatihan.go:65-66`), bukan disimpan sebagai salinan — bentuk paling kuat untuk lolos gerbang §F2, karena status yang diturunkan tak bisa basi. Peserta juga tertaut lewat `TrainingParticipant.TrainingID`. Sementara itu `request_id` tetap **nol hasil**, jadi rantai di atas masih putus. Dua rantai bertetangga di satu service, satu patuh satu tidak: ini menggeser sebabnya dari "tim belum bisa" ke "yang lama belum disentuh".

### 3. Pengajuan budget → realisasi kas kecil (putus, tersambung hanya lewat agregat)

| | |
|---|---|
| **Entitas** | `procurement.PengajuanBudget` (`pengajuan_budget.go:80-171`) → `procurement.TransaksiKas` (`kas_transaksi.go:41+`) |
| **Diduplikasi** | `unit_kode`, `periode`, `kategori_kode`, `nominal`, `keterangan`, `vendor`, `akun_beban_no`/`nama` |
| **Referensi hilang** | `pengajuan`/`budget` apa pun — **nol hasil** di `kas_transaksi.go`. Diverifikasi langsung. |
| **Jembatan yang ada** | Pengajuan disetujui menambah `TambahanTopUp` pada `PlafonKas` unit+periode yang sama (`pengajuan_budget_approval.go:125`) |
| **Akibat** | Yang bisa dijawab hanya *"plafon unit ini bulan ini bertambah sekian"*. **"Transaksi mana merealisasikan pengajuan mana" tak bisa dijawab sama sekali** — padahal itu pertanyaan audit yang wajar. |

✅ **Keputusan sudah diambil, 26 Agustus 2026** — [[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]]. Rantai ini **tidak disambung**, melainkan **dihapus dari kedua ujungnya**: `PengajuanBudget` diganti `PengajuanPembelian` yang berjalan sampai barang diterima, dan kas kecil dipensiunkan sehingga `TransaksiKas` berhenti menjadi hilirnya. Pertanyaan TBD *"apakah satu transaksi kas boleh merealisasikan banyak pengajuan"* dengan sendirinya gugur.

⚠️ **Yang lahir sebagai gantinya, dan belum diputuskan**: modul pengganti menerbitkan **PO dan penerimaan sendiri**, sementara jalur `permintaan_erp` → `pesanan_erp` → `penerimaan_erp` di §4 tetap hidup. Dua jalur pengadaan berdampingan di satu service yang sama. Ini konsekuensi yang dicatat sadar di ADR-nya, bukan temuan baru.

📏 **Diukur di PROD 2026-09-29 (`procurement_db`, baca saja)**: kedua jalur ERP nyaris tak terpakai. `pengajuan_barang` **2 dokumen total**; `permintaan_erp`, `pesanan_erp`, `penerimaan_erp`, dan `purchase_order` masing-masing **0**. Yang aktif 30 hari terakhir justru koleksi hasil tarik dari Accurate: `pesanan_pembelian` 37 (total 1.109), `penerimaan` 68 (total 1.965), `permintaan_barang` 11 (total 261), `katalog` 56 (`sync_pembelian.go`; penerimaan RI hanya list/detail dari Accurate, `accurate_penerimaan.go:30`, `:63`). Jadi pengadaan harian masih dikerjakan di Accurate, dan pertanyaan "dua jalur dilebur atau tidak" (§TBD) kini punya pertanyaan yang lebih dulu: jalur ERP mana yang akan benar-benar dipakai.

### 4. PR → PO → Penerimaan (setengah jalan, dan inilah yang paling menyesatkan)

| | |
|---|---|
| **Entitas** | `permintaan_erp` → `pesanan_erp` → `penerimaan_erp` |
| **Yang sudah ada** | `RincianPesanan.NoPermintaan` (`pesanan_erp.go:76-77`), `RincianPenerimaan.NoPesanan`/`NoPermintaan` (`penerimaan_erp.go:51-52`), plus modal "Ambil dari Permintaan/Pesanan" di frontend |
| **Kenapa tetap putus** | Referensinya **nomor bertipe string, per-baris, tanpa validasi** — header `PesananERP` tak punya `permintaan_id`, header `PenerimaanERP` tak punya `pesanan_id`. Nilainya hanya di-`TrimSpace`, tak pernah dicek benar-benar ada. |
| **Status hulu mati** | `StatusPermintaanSebagian`, `StatusPermintaanSelesai`, `StatusPesananSebagian`, `StatusPesananTerproses` **hanya ada sebagai definisi** (`permintaan_erp.go:27-28`, `pesanan_erp.go:34-35`) dan satu filter di test. **Nol penulisan di kode produksi.** Diverifikasi langsung. |
| **Akibat** | PR yang sudah sepenuhnya dibelikan **tetap `menunggu_diproses` selamanya**. Konstanta yang tak pernah ditulis terbaca seperti fitur yang ada. |

⚠️ Rantai ini paling berbahaya bagi pembaca dokumentasi: ada tombolnya, ada konstantanya, ada kolomnya — dan tak satu pun bekerja sebagai rantai.

**Diukur ulang 2026-09-29: tidak berubah.** Rujukan antar-dokumen tetap string `NoPermintaan`/`NoPesanan`, keempat konstanta status `Sebagian`/`Selesai`/`Terproses` tetap nol penulisan. Tiga rujukan di sekitar jalur ini juga lemah: `QualityRMCheck.PenerimaanRef` menyimpan id penerimaan tetapi tak divalidasi (`shared-library/models/manufacture/models.go:1162`); `QualityIncoming` hanya teks `Material`/`Supplier` (`:1041-1042`); faktur Accurate biasa hanya menyimpan `NomorPO` string (`services/procurement/faktur.go:103`), nol rujukan penerimaan.

### 5. Penerimaan barang → stok (putus)

`BuatPenerimaanHandler` (`penerimaan_erp_handler.go:24-97`) hanya `InsertOne`. Tak ada panggilan ke warehouse/inventory/manufacture; `Gudang` sekadar string bebas. **Barang yang diterima di ERP tidak menambah stok mana pun.** Diverifikasi ulang 26 Agustus 2026 — masih berlaku.

🟡 **Akan tertutup sebagian** oleh [[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]]: penerimaan yang lahir **dari pengajuan pembelian** akan menambah stok (raw material lewat `POST /transaksi` manufacture) atau melahirkan item aset (barang umum di inventory). Penerimaan yang dibuat lewat jalur `penerimaan_erp` biasa **tetap tidak menambah stok** — jadi §5 tidak gugur, hanya menyempit.

✅ **Diukur ulang 2026-09-29: sisi pengajuan sudah dikodekan** (rinciannya §9): stok bertambah lewat kunci `<nomor>#<urutan>` dan `Ref` = nomor pengajuan. `BuatPenerimaanHandler` sendiri tidak berubah, masih hanya `InsertOne` (`penerimaan_erp_handler.go:88`).

Temuan tambahan dari pembacaan yang sama: `services/inventory` **tidak punya stok berjumlah sama sekali** (nol referensi qty/stok). Barang GA dilacak sebagai **aset per unit** — master item, kategori, repair, handover. "Menambah stok gudang GA" karena itu berarti melahirkan item aset, bukan menaikkan angka.

### 6. Rekrutmen: hire → karyawan → onboarding (rantai ada sampai offer, putus di hire)

| | |
|---|---|
| **Yang tersambung** | `job_posting.requisition_id` · `candidate.posting_id` · `offer.candidate_id` |
| **Referensi hilang** | `Offer` tanpa `requisition_id`; `OnboardingInstance` tanpa `candidate_id` maupun `offer_id` (`models_onboarding.go:90-106`), dan menyimpan ulang `employee_name`/`position`/`department` sebagai snapshot dari frontend |
| **Titik putusnya** | `PUT /candidates/:id/link-employee` hanya **menautkan sesudahnya**. HR wajib membuka HRIS "Tambah Karyawan" sebagai **form baru** lalu memanggil `create-employee` |
| ⚠️ **Catatan penting** | [[HRIS - Recruitment]] menandai alur dua-langkah ini **✅ selesai** — jadi vault saat ini memperlakukannya sebagai **desain, bukan cacat**. Bila peta ini hendak mengubah statusnya, itu keputusan sadar yang perlu dinyatakan, bukan diperbaiki diam-diam. |
| **Diukur ulang 2026-09-29** | Requisition → lowongan → kandidat → offer **tersambung** (`models_posting.go:36`, `models_candidate.go:17`, `models_offer.go:37`). Offer → karyawan **sebagian**: tautannya hanya satu arah (`Candidate.EmployeeID` lewat `PUT /candidates/:id/link-employee`), karyawan tidak menyimpan `candidate_id`, dan requisition berhenti di `Posted` (status hulu tak bergerak saat kandidatnya jadi karyawan). |

### 7. Pengajuan cuti/koreksi → payroll (putus sesudah run ditutup)

payroll-service **tidak pernah membaca** `leave_request`; ia hanya menerima agregat harian dari attendance. Tak ada penjaga cutoff periode gaji pada **kelima** jenis pengajuan, sehingga pengajuan backdate bisa melewati tutup buku tanpa rekonsiliasi. [[HRIS - Employee Request & Approval]] sudah mencatatnya dan menyatakan **"Keputusan saat ini: dibiarkan apa adanya"** — jadi ini gap yang **sudah diputuskan untuk ditunda**, bukan temuan baru.

**Diukur ulang 2026-09-29: tidak berubah.** Absensi dan cuti mengalir ke payroll sebagai agregat (`/payroll-supplement`), tetap tanpa penjaga cutoff periode. Ujung hilir payroll sendiri putus ke akuntansi, lihat §11.

### 8. Perjalanan dinas → pencairan (sengaja putus)

`shared-library/models/attendance/models.go:862` menyatakannya eksplisit: **"TIDAK terhubung ke Finance/payroll/reimbursement (keputusan scope)"**. Uang saku diproses manual di luar sistem. ADR-nya masih 🟡 Diusulkan: [[ADR - 0007 Reimbursement Perjalanan Dinas]]. **Ini bukan cacat**, dicantumkan supaya tak berulang kali "ditemukan" sebagai temuan baru.

### 9. Pengajuan Barang → penerimaan → QC → stok → faktur → pembayaran → jurnal (tersambung di kode, nyaris kosong di PROD)

Dipetakan 2026-09-29. Ini jalur **pengganti** yang lahir dari [[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]], dan satu-satunya rantai pengadaan di peta ini yang lolos kedua kriteria: satu dokumen berjalan dari permintaan sampai jurnal, dan setiap rujukan ke hilir **diisi server**, bukan diketik.

| Mata rantai | Rujukan | Bukti |
|---|---|---|
| Permintaan | satu dokumen `PengajuanBarang` dengan `Items`, jenjang persetujuan, status | `services/procurement/pengajuan_barang.go:201-212` |
| PO | **bukan dokumen terpisah**: hanya penanda Pembelian + teks `NomorPO` | `pengajuan_barang.go:218`, `:236` |
| Penerimaan | `ItemPengajuan.QtyDiterima` di dokumen yang sama | `pengajuan_barang.go:55` |
| QC | `HasilQC`/`KlaimQC` di dokumen yang sama | `pengajuan_barang.go:464`, `:478` |
| Stok | kunci `<nomor>#<urutan>`; manufacture mencatat `Ref` = nomor pengajuan; inventory menyimpan `SumberPengajuan` | `pengajuan_barang_stok_payload.go:78-79`, `services/manufacture/stok_dari_pengajuan.go:129`, `shared-library/models/inventory/models.go:313` |
| Faktur | `FakturID` + `FakturBillNumber` deterministik `PB-<nomor>` | `pengajuan_barang.go:438-439` |
| Pembayaran | `Pembayaran.FakturID` | `services/procurement/pembayaran.go:29` |
| Jurnal | `JurnalNomor`/`JurnalID` | `pengajuan_barang.go:279-280` |

⚠️ **Jangan membaca tabel ini sebagai "pengadaan ERP sudah tersambung".** Di PROD 2026-09-29 `pengajuan_barang` baru **2 dokumen**, sementara pengadaan harian (37 pesanan pembelian dan 68 penerimaan dalam 30 hari) masih dikerjakan di Accurate lalu ditarik ke ERP (§3). Rantainya dibangun benar; pemakaiannya belum ada. ⚠️ Mata rantai PO hanya teks `NomorPO`, jadi bila kelak PO diterbitkan sebagai dokumen sendiri, titik itu yang pertama perlu dinaikkan jadi id.

### 10. Plan-to-Produce (1 dari 6 tersambung, 1 sebagian)

Dipetakan 2026-09-29.

| Mata rantai | Keadaan | Bukti |
|---|---|---|
| Rencana produksi → MO | **Putus** | `production_plan.go` hanya kalkulator (nol `InsertOne`/`UpdateOne`); `MaterialOrder` tanpa id rencana dan tanpa status (`shared-library/models/manufacture/models.go:546-557`) |
| MO → kebutuhan RM | **Tersambung** | `Ingredients` tertanam di MO (`models.go:552`) |
| Kebutuhan RM → pengambilan RM | **Putus** | `SelisihRM` tanpa id MO maupun batch (`models.go:252-280`); RM berkurang saat `ProductionLog` dibuat dengan `Ref` = `NoBatch` ketikan (`services/manufacture/production.go:111`) |
| Pengambilan → batch record | **Putus** | `PenimbanganBahan.QtyMO` ditautkan lewat `no_batch` (`models.go:331`); `batch_record.go:472-485` mengambil nilainya dari body |
| Batch record → rilis QC | **Sebagian** | Rilis LULUS ditulis di dokumen yang sama (`batch_record.go:384`, `:406`), tetapi ada **register kedua** `QualityBatchRelease` di employee-service yang hanya menyimpan `BatchNumber` string (`shared-library/models/employee/models.go:1057`). Dua register rilis batch, tanpa rujukan satu sama lain |
| Rilis QC → stok FG | **Putus** | Stok FG naik saat `ProductionLog` dibuat (`production.go:118-130`), **sebelum dan terlepas dari** rilis QC; `ProductionLog` tak menyimpan id batch record |

⛔ **Yang paling berat di klaster ini bukan rujukannya melainkan urutannya**: produk jadi sudah terhitung sebagai stok sebelum QC merilisnya, jadi stok FG di ERP bisa memuat batch yang belum (atau tidak akan) lulus. Bandingkan dengan [[QA - Batch Record & Traceability]] dan [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]].

📏 PROD 2026-09-29: `manufacture_batch_record` 0, `manufacture_selisih_rm` 0; koleksi `quality_batch_release`, `quality_rm_check`, dan `quality_incoming` **belum ada**. Jadi kedua register rilis belum pernah dipakai; memutuskan satu register sekarang belum menuntut migrasi data.

### 11. Payroll → jurnal dan pembayaran (tidak ada modul)

Dipetakan 2026-09-29. `git grep -c -i -E 'accurate|jurnal|journal' origin/main -- services/payroll` **nol hasil**: payroll-service tidak menjurnal ke Accurate dan tidak menerbitkan pembayaran apa pun. Beban gaji masuk pembukuan di luar sistem. PROD: `payroll_run` 3 dokumen. Konteks dari pengukuran yang sama: payroll, insentif, reimbursement, dan penyusutan adalah empat hal yang **tak punya jalur otomatis** ke Accurate sama sekali, sementara penerimaan barang (RI) dan aset tetap masih diinput manual di Accurate ([[External - Accurate]]). Rantai hulunya (§6 dan §7) karena itu berakhir di run payroll, bukan di buku besar. Terkait: [[HRIS - Payroll]] · [[Microservices - Payroll Service]].

### 12. Komplain → validasi QC → CAPA (putus di CAPA)

Dipetakan 2026-09-29. Order atau ulasan → komplain **tersambung**, divalidasi server (`services/employee/quality_complaint.go:169`); komplain → validasi QC terjadi di satu dokumen. Validasi QC → CAPA **putus**: `QualityCAPA` tak punya rujukan ke komplain, dan `complaint_id`/`komplain_id`/`capa_id` **nol hasil** di `services` dan `shared-library`. Komplain yang divalidasi tidak melahirkan CAPA tertaut, jadi "CAPA mana yang menindaklanjuti komplain ini" tak bisa dijawab. PROD: `quality_complaint` 0. Terkait: [[ADR - 0103 Satu Pintu Komplain Produk, Unit Tujuan Diturunkan dari Kategori]] · [[QA - Deviation & CAPA]].

### 13. Order-to-Cash (tersambung, kecuali stok keluar FG)

Dipetakan 2026-09-29.

| Mata rantai | Keadaan | Bukti |
|---|---|---|
| Order → packing | **Tersambung** | `FulfillmentOrder.OrderID` (`services/warehouse/models.go:61`) |
| Order/packing → stok keluar FG ERP | **Putus** | Stok keluar dicatat manual lewat `POST /transaksi/fg` dengan `Ref` teks (`services/manufacture/transaksi_fg.go:27`, `:133`); resi tak menulis stok (`resi.go:449-450`). Stok **Accurate** tetap berkurang lewat faktur |
| Order → faktur | **Tersambung, agregat** | per (`shop_id`, `channel`, `date_wib`) (`services/integration/internal/domain/entity/accurate_daily_invoice.go:78-86`) |
| Settlement → penerimaan → jurnal | **Tersambung** | `accurate_receipt.go:24`, `:28`, `:50-55`; hulu bergerak ke `INVOICE_PAID` (`accurate_daily_invoice.go:59`) |

⚠️ Akibat mata rantai kedua: stok FG di ERP dan di Accurate dikurangi lewat dua jalan berbeda (manual vs faktur), jadi selisih keduanya bukan kejutan melainkan bawaan desain. PROD 2026-09-29: `accurate_daily_invoices` 3.370, `accurate_daily_returns` 11.894, `accurate_tiktok_receipts` 2.200, `accurate_shopee_receipts` 695, `accurate_lazada_receipts` 135; kv `receipt-cutover-date` = 2026-09-01.

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
3. **PPIC → Pengadaan** — nyeri terbesar (tiga kali ketik). ⚠️ **Ongkosnya turun sejak diukur ulang 2026-09-22**: alasan lama "`InternalURL` manufacture masih kosong, jadi ongkos infrastrukturnya nyata" sudah gugur, manufacture kini memanggil tiga service (lihat §1). Jalur pemanggilannya sudah ada; yang kurang tinggal rujukan id dan status hulu. Urutannya layak ditimbang ulang.
4. **Pengajuan budget → realisasi kas** — menuntut keputusan bisnis lebih dulu: apakah satu transaksi boleh merealisasikan lebih dari satu pengajuan.
5. **Mesin alur bersama di `shared-library`** — hanya masuk akal **sesudah** dua sampai tiga rantai di atas dikerjakan tangan. Mengangkat abstraksi sebelum ada tiga pemakai nyata adalah pola yang sudah berulang kali salah di repo ini; lihat prinsip *tunggu pemakai ketiga* di kit.

## Belum Diputuskan (TBD)

- **Apakah arahnya menyambung rantai satu per satu, atau membangun mesin alur bersama.** Belum diputuskan (2026-08-26).
- **Apakah hire → karyawan dianggap cacat atau desain.** Vault saat ini menyatakannya selesai; mengubahnya butuh keputusan eksplisit.
- ~~**Apakah satu transaksi kas boleh merealisasikan banyak pengajuan budget.**~~ **Gugur** 26 Agustus 2026 — kas kecil dipensiunkan, lihat §3.
- **Apakah dua jalur pengadaan dilebur.** Pengajuan Pembelian menerbitkan PO/penerimaan sendiri sementara jalur PR→PO→RI tetap hidup. Belum diputuskan (2026-08-26). ⚠️ Diukur PROD 2026-09-29: jalur baru 2 dokumen, jalur lama 0, pengadaan harian di Accurate (§3).
- **Nasib `MaterialOrder` yang tak punya status sama sekali.** Ditambahi status, atau dilebur ke entitas permintaan.
- **Register rilis batch mana yang berlaku** (dicatat 2026-09-29, §10): rilis LULUS di batch record manufacture, atau `QualityBatchRelease` di employee-service. Keduanya belum berisi data di PROD.
- **Apakah stok FG baru boleh bertambah sesudah rilis QC** (dicatat 2026-09-29, §10). Sekarang ia bertambah saat `ProductionLog` dibuat.
- **Apakah payroll menjurnal ke Accurate dari sistem** (dicatat 2026-09-29, §11), dan siapa pemiliknya.
- **Apakah CAPA wajib merujuk komplain asalnya** (dicatat 2026-09-29, §12).
- **Stok keluar FG ERP dari packing/resi, atau tetap manual** (dicatat 2026-09-29, §13).

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
- [[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]] (jalur §9) · [[Microservices - Warehouse Service]] · [[Microservices - Integration Service]] · [[Microservices - Payroll Service]]
- [[QA - Batch Record & Traceability]] · [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]] · [[QA - Deviation & CAPA]] · [[REF - Kepemilikan Data]] (master data yang dirujuk rantai-rantai ini)
