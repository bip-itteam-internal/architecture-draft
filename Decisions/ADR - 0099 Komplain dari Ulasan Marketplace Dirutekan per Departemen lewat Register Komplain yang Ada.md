> **Status**: ⚠️ Diterima, sebagian besar diimplementasikan. **Keputusan 1, 2, 3, 4, 5, dan 6 sudah ada di kode** per 2026-09-16 dan **merged ke `main` hari itu juga**, terverifikasi di DEV; belum di PROD. **Keputusan 8 separuh berjalan**: notifikasi register GUDANG ada di branch bip-erp `feat/warehouse-komplain-notifikasi` + erp-frontend `feat/inbox-kategori-komplain-gudang` per 2026-09-17, belum merge; notifikasi ulasan bintang rendah ke pemegang toko belum dikerjakan. Sisanya (jalur QC dari ulasan, tujuan tanpa register) masih usulan.
>
> ⛔ **Satu asumsi ADR ini terbukti KELIRU dan sudah dikoreksi di kode.** Persona "Account Specialist" di sini diasumsikan terjangkau lewat peran marketing. Diukur di PROD 2026-09-16: keempat puluh orangnya berperan `insentive: icc`, **nol** punya peran `kyura`/`beauty_hacks`, dan hanya **dua** punya peran `integration`. Peran tidak mewakili kepemilikan toko, jadi hak baca dan hak mengajukan diturunkan dari `icc_account_mappings`, bukan dari daftar peran. Jangan merancang gerbang berikutnya di atas asumsi lama itu.

## Untuk Manajemen

Pemegang toko akan diberi tahu saat ada ulasan pembeli berbintang rendah, dan dari baris ulasan itu ia bisa langsung meneruskannya ke unit yang benar-benar bisa memperbaikinya. Untuk keluhan salah kirim dan kemasan, tujuannya gudang; untuk dugaan produk tidak asli, QC. Unit penerima menuliskan tindakan yang diambil lalu menutupnya, dan pemegang toko dikabari hasilnya.

Yang mengubah bentuk pekerjaan ini: **jalur komplain ke gudang ternyata sudah dibangun dan sudah terpasang sebagai penilaian kerja gudang, tetapi belum pernah dipakai sekali pun karena tidak ada layarnya.** Nol catatan di produksi. Jadi sebagian besar yang dibutuhkan bukan membangun, melainkan membukakan pintunya.

Yang terdampak: tiga Account Specialist yang memegang sembilan toko Shopee, tim gudang packing, staf QC, serta supervisor Kyura dan Beauty Hacks. Tugas CS tidak berubah.

Yang **tidak** dijanjikan, dan sebaiknya tidak diharapkan:

- Tidak melayani TikTok. TikTok tidak menyediakan teks ulasan per pembeli sama sekali.
- Tidak membalas pembeli. Seluruh alur ini internal; pembeli tetap dibalas CS.
- Tidak mengklasifikasi ulasan secara otomatis. Kategorinya dipilih orang.
- Belum melayani keluhan yang tujuannya ekspedisi, vendor, atau tim brand, karena ketiganya belum punya tempat mencatat.
- Tidak memasang tenggat penyelesaian, dan tidak menjawab kewajiban regulatif BPOM atas keluhan efek samping.

Perkiraan besaran kerja: **lebih kecil daripada dugaan awal**. Yang terbesar adalah satu layar untuk jalur gudang yang selama ini tak punya layar.

## Deskripsi

*Komplain yang lahir dari ulasan marketplace dirutekan ke unit yang tepat dengan memakai register komplain yang SUDAH ADA di masing-masing tujuan, bukan dengan membangun register ketiga dan bukan dengan menambahkan tujuan ke salah satunya. Pekerjaan utamanya membukakan pintu: layar untuk register gudang yang selama ini tak punya layar, dan tautan dari baris ulasan.*

- **Path di repo**:
  - `bip-erp/services/warehouse/komplain.go` (register gudang, sudah ada; rute bacanya ✅ dibuka ke marketing 2026-09-16)
  - `bip-erp/services/warehouse/komplain_akses.go` (✅ **baru**, 2026-09-16: gerbang baca komposit gudang-atau-marketing + resolver cakupan toko lewat `GET /icc/mappings/me`)
  - `bip-erp/services/employee/quality_complaint.go` (register QC, sudah ada; menerima salinan ulasan)
  - `bip-erp/shared-library/models/employee/models.go` (`QualityComplaint`, blok salinan ulasan)
  - `erp-frontend/src/app/(main)/integration/reviews/` (tombol ajukan dari baris ulasan, **baru**)
  - `erp-frontend/src/app/(main)/warehouse/komplain/` + `src/features/warehouse/komplain/` (✅ layar komplain gudang, **baru** 2026-09-16; rutenya `/warehouse`, bukan `/wms` seperti dugaan awal ADR ini)
- **Tanggal**: 2026-09-16 (direvisi hari yang sama, lihat Context)

## Context

Kebutuhan datang sebagai solusi: "klasifikasikan ulasan per toko supaya pemegang toko bisa mengajukan komplain ke pihak terkait, tidak harus ke QC saja". Pengukuran ke produksi mengubah bentuk jawabannya dua kali.

**Datanya ada, dan hanya untuk Shopee.** `integration_db.marketplace_reviews` memuat 17.970 ulasan, seluruhnya SHOPEE dan nol TikTok, membentang 2025-03-05 sampai 2026-09-16. Teks, foto, `order_sn`, dan balasan CS tersimpan. TikTok tidak menyediakan daftar ulasan individual sama sekali. Lihat [[Microservices - Integration Service]].

**Volumenya kecil, dan ini yang membatalkan klasifikasi otomatis.** Bintang tiga ke bawah **dan** berteks hanya sekitar 65 sepanjang 18 bulan, yaitu 3 sampai 4 per bulan untuk sembilan toko. Sebaran bintang: 81, 51, 343, 1.230, 16.265. Pada volume itu satu pilihan yang ditekan manusia lebih murah sekaligus tidak bisa salah diam-diam.

**Temanya milik unit yang berbeda.** Dari 40 ulasan bintang tiga ke bawah terbaru: pesanan tidak sesuai 7, kemasan dan segel 6, dugaan tidak asli 5, klaim iklan tidak sesuai 3, pengiriman lama 2, mendekati kedaluwarsa 1, ditambah beberapa dugaan efek tidak diinginkan. Sisanya, 14 sampai 16 baris, adalah "produknya tidak mempan buat saya", yang bukan sesuatu yang dapat ditindak siapa pun.

**Kepemilikannya lengkap.** Kesembilan toko berulasan punya pemilik aktif, dipegang tiga orang berposisi Account Specialist. Pemetaan CS justru timpang: empat dari sembilan toko, semuanya satu orang. Keduanya sengaja terpisah, lihat [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]].

**Tidak ada yang diberi tahu.** Sync ulasan tidak mengirim notifikasi kepada siapa pun; satu-satunya notifikasi di sana adalah Telegram ketika job-nya gagal.

⚠️ **KOREKSI 2026-09-16, ditemukan saat `/plan` menjalankan gerbang "cari sebelum membangun".** Versi pertama ADR ini menyatakan hanya ada satu register komplain dan bahwa ia terkunci ke QC. **Itu keliru.** Ada DUA register:

| Register | Untuk | Keadaan |
|---|---|---|
| `quality_complaint` (employee_db) | marketing ke QC | dua layar, dipakai |
| `warehouse_komplain_gudang` (warehouse_db) | marketing ke gudang packing | **tak punya layar, nol dokumen di produksi** |

Register gudang itu sudah lengkap: kategori tertutup (`salah_produk`, `salah_jumlah`, `salah_alamat`, `rusak_kemasan`, `kurang_lengkap`), status `baru`/`diproses`/`selesai`/`ditolak`, kolom `tindak_lanjut` dan `selesai_at`, bukti foto, atribusi packer yang disalin dari pesanan saat komplain dibuat, indeks unik `(order_id, kategori)` supaya satu pesanan yang dilaporkan tiga orang tidak menurunkan skor gudang tiga kali, dan gerbang tulis `RequireMarketingStaff` yang sama dengan jalur QC. Ia bahkan sudah jadi KPI baris 1 gudang packing lewat `kpi_sumber_warehouse_packing.go`.

Yang hilang darinya cuma satu: **layar**. Nol dokumen di produksi adalah gejalanya, bukan bukti bahwa gudang tak pernah salah kirim.

Penelusuran menyeluruh atas seluruh service (nama koleksi dan tipe struct yang memuat komplain, complaint, keluhan, aduan) memastikan hanya dua register itu yang ada. Sisanya turunan: `mart_komplain_bulanan` agregat KPI dari ulasan, dua sumber KPI di employee yang membacanya, dan field `keluhan` di task-management yang merupakan deskripsi tiket IT.

**Syarat teknis jalur gudang sudah terpenuhi.** `POST /wms/komplain` menuntut `order_id` ada di `fulfillment_orders`. Di produksi koleksi itu memuat 130.193 pesanan, dan **seluruh 41.400 pesanan Shopee-nya milik kesembilan toko yang punya ulasan**. Ulasan sendiri seluruhnya membawa `order_sn`.

**Tidak ada ADR yang mengatur komplain lintas departemen.** Presedennya [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]], yang memberi kriteria kapan sebuah alur pantas punya koleksi sendiri sekaligus memperingatkan bahaya dua definisi "tiket" dalam satu service.

⚠️ Dasar regulatif untuk keluhan efek samping **tidak ada di vault**. Dok CPOB dan [[QA - Deviation & CAPA]] masih stub, enum sumber CAPA tidak memuat keluhan pelanggan, dan rulebook vault melarang mengarang konten regulatif.

## Decision

1. **Pakai register yang SUDAH ADA di tiap tujuan. Jangan bangun register ketiga, dan jangan tambahkan field tujuan ke salah satunya.** Keluhan pekerjaan gudang masuk ke register gudang; keluhan mutu masuk ke register QC. Keduanya sudah punya alur, gerbang, dan konsumen KPI-nya sendiri, dan menyatukannya berarti membuang dua hal yang sudah bekerja demi satu bentuk yang lebih rapi di atas kertas.

2. **Tidak ada master kategori baru.** Versi pertama ADR ini menetapkannya; itu dibatalkan. Register gudang sudah memiliki daftar kategori tertutup beserta alasan tertulisnya, yaitu bahwa teks bebas membuat metriknya mustahil dijumlahkan. Master ketiga hanya akan jadi sumber kedua yang menyimpang. Pengaju memilih **tujuan** lebih dulu, lalu memilih kategori dari daftar milik tujuan itu sendiri.

3. **Pekerjaan terbesarnya adalah LAYAR untuk register gudang**, bukan model data. Termasuk membuka rute BACA `/wms/komplain` ke marketing, yang hari ini sengaja dibatasi peran gudang dan dicatat di kodenya sebagai perubahan tersendiri.

4. **Isi ulasan DISALIN ke dalam komplain, bukan ditautkan lewat id saja.** Ulasan tinggal di `integration_db`, register di database lain, dan aturan database-per-service melarang lintas database. Salinan bertanggal juga yang benar secara makna: ia bukti, dan ulasan yang kelak disunting atau disembunyikan tidak boleh mengubah dasar komplain yang sudah diajukan. Register gudang sudah memakai prinsip yang sama untuk atribusi packer.

5. **Kategori dipilih manusia.** Tidak ada klasifikasi otomatis, tidak ada LLM, karena volumenya 3 sampai 4 per bulan.

6. **Tujuan yang belum punya register tidak dibuatkan register baru sekarang.** Keluhan yang mengarah ke ekspedisi, vendor, atau tim brand dicatat sebagai belum terlayani dan ditampilkan apa adanya, bukan dipaksa masuk ke salah satu register yang ada. Memaksakannya akan mencemari KPI unit yang bukan penyebabnya.

7. **Kategori "produk tidak efektif" tidak menghasilkan komplain sama sekali.** Ia mayoritas, dan tak ada unit yang dapat menindaknya. Memaksanya jadi tiket menghasilkan tumpukan yang tak bisa ditutup siapa pun.

8. **Notifikasi**: ulasan berbintang rendah memberi tahu pemegang tokonya, diturunkan dari `department_shops`. Register QC sudah punya pola dua kategori inbox (`komplain-qc-diajukan` ke penerima, `komplain-qc-divalidasi` ke pengaju); register gudang belum punya notifikasi sama sekali dan perlu mengikuti pola yang sama. Fan-out lewat jalur terpusat sesuai [[ADR - 0050 Notifikasi Inbox Mendorong Push ke Browser dan Ponsel Sekaligus]].
   - 🔜 *Implementasi register gudang (2026-09-17, branch):* `komplain-gudang-diajukan` ke pemegang peran warehouse `admin_gudang`/`leader`/`spv`, dan `komplain-gudang-ditutup` ke pengaju. Dua penyempitan dari pola QC, keduanya disengaja: pengaju dikabari **hanya saat komplainnya ditutup** (selesai atau ditolak), bukan tiap perubahan status, karena status `diproses` bukan hasil yang perlu ditindaklanjuti pengaju; dan pengawas WMS tak ikut menerima, sebab yang menindak komplain adalah pemegang peran gudang yang sama dengan penjaga rute tindak lanjutnya. Rinciannya di [[Microservices - Warehouse Service]].

9. **Tanpa tenggat dan tanpa SLA untuk sekarang.** SLA yang sudah ada di sistem berasal dari marketplace dan punya penegak di luar; alur internal ini tidak punya. Yang dicatat cukup kapan tiket masuk dan kapan ditutup, sehingga tenggatnya kelak dapat diturunkan dari data sendiri.

10. **Hanya Shopee**, dinyatakan terang di layar.

11. **Kategori dugaan efek tidak diinginkan DITAHAN** sampai QA/RA menyatakan apakah keluhan semacam itu wajib masuk jalur CAPA atau pelaporan BPOM.

12. **Dua utang register QC ditutup hanya bila jalur QC benar-benar disentuh**: `company_id` yang belum ada, dan race `ReplaceOne` berfilter `_id` saja. Keduanya sudah tercatat di [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]].

## Consequences

**Yang membaik.** Jalur gudang yang sudah dibangun dan sudah terpasang di KPI akhirnya bisa dipakai. Keluhan pembeli sampai ke unit yang dapat memperbaikinya, dan untuk pertama kalinya ada jejak bahwa kesalahan yang sama berulang. Permukaan barunya jauh lebih kecil daripada rancangan awal: nol register baru, nol master baru.

**Yang memburuk, dan diterima sadar.** Ada dua register dengan bentuk yang berbeda, jadi rekap lintas tujuan harus menggabungkan sendiri. Itu harga dari tidak membongkar dua modul yang sudah bekerja, dan konsekuensi yang sama sudah diterima [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]] untuk alasan yang sama.

**Yang tetap terbuka.** Tujuan ekspedisi, vendor, dan brand belum punya tempat. Lima toko Beauty Hacks tidak punya CS sama sekali. Kewajiban regulatif atas keluhan efek samping menunggu QA/RA.

**Konsekuensi deploy.** Kategori inbox baru untuk jalur gudang menuntut service pengirim dan notification-service naik bersama, notification-service lebih dulu. ~~Tidak ada env baru.~~ *Koreksi 2026-09-17:* warehouse-service butuh tiga env baru untuk notifikasinya (`EMPLOYEE_MODULE_URL`, `NOTIFICATION_MODULE_URL`, `NOTIFICATION_SERVICE_KEY`), jadi container-nya wajib dibuat ulang, bukan di-restart. Perubahan kontrak respons berarti backend naik sebelum frontend.

**Dokumen terkait**: [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]] · [[Microservices - Integration Service]] · [[Microservices - Notification Service]] · [[Microservices - Employee Service]] · [[Microservices - Warehouse Service]] · [[APP - Web ERP]] · [[Sales - ICC Account Manager Mapping]] · [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]] · [[ADR - 0050 Notifikasi Inbox Mendorong Push ke Browser dan Ponsel Sekaligus]] · [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]] · [[ADR - 0060 Cakupan Keterlihatan Tiket Engagement]]
