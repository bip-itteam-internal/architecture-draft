> **Status**: 🟡 **Diusulkan**, 2026-10-19. Menunggu keputusan **Leader Warehouse + Supervisor Quality** (keputusan K-4 di [[ANALISA - Fondasi Manufaktur]]). **Belum ada kode baru**; yang ditulis di sini usulan beserta pertanyaan yang harus dijawab Pemutus.

## Untuk Manajemen

**Apa yang perlu diputuskan.** Bagaimana sistem mencatat bahan baku dan bahan kemas yang baru datang sampai boleh dipakai produksi: status apa saja yang ada, siapa yang menetapkannya, dan kapan bahan boleh keluar dari gudang.

**Usulan singkat.**
1. Bahan yang datang **masuk karantina dulu**. Hanya jumlah yang dinyatakan **Lulus** QC yang menjadi stok siap pakai; sisanya tetap tertahan sampai diputuskan.
2. **Satu catatan hasil QC** per penerimaan, dipakai bersama oleh Gudang, QC, dan Procurement. Hari ini ada empat tempat terpisah.
3. **Bahan karantina tidak bisa dikeluarkan ke produksi.** Hari ini sistem tidak menahan apa pun.
4. Bahan **Ditolak** tidak pernah masuk stok dan dikembalikan ke pemasok lewat Procurement. Ini sama dengan praktik sekarang.

**Siapa yang terdampak.** Staf dan Leader Warehouse (penerimaan, label, pengeluaran ke produksi), QC (pemeriksaan bahan masuk), Supervisor Quality (konfirmasi penolakan), Procurement (retur ke pemasok), PPIC (stok yang terbaca siap pakai).

**Kenapa perlu ditulis sekarang.** Diukur di kode `origin/main` 2026-10-19 dan data prod: alur pengajuan bahan mencatat 68 penerimaan dalam 30 hari, sementara register QC bahan masuk di modul Quality berisi **0** catatan. Tanpa keputusan ini, butir M-13 (satu gerbang QC bahan masuk) dan M-24 (retur ke pemasok) tidak bisa dikerjakan, dan stok bahan yang terbaca di ERP bisa memuat bahan yang belum diperiksa.

**Apa yang tidak dijanjikan.** Format label fisik dan cetak kartu stok (keputusan K-5). Pengujian di tengah produksi (IPC) dan rilis barang jadi (keputusan K-3). Waktu adopsi: aturan ini baru bermakna bila penerimaan bahan memang dicatat di ERP (butir Fase 1).

**Perkiraan besaran kerja.** Sedang (estimasi): satu catatan QC tertaut penerimaan dan lot, gerbang pengeluaran di manufacture-service, dan penyesuaian layar QC serta Gudang RM.

## Pertanyaan untuk Pemutus

Jawab di issue K-4 atau langsung di dok ini. Rekomendasi disertakan; Pemutus boleh memilih lain.

| # | Pertanyaan | Pilihan | Rekomendasi |
|---|---|---|---|
| 1 | SOP QC hanya mengenal label **LULUS** dan **DITOLAK**; kuesioner menyebut juga **Reject**. Apakah Reject sama dengan Ditolak? | (a) sama, cukup Lulus/Ditolak seperti SOP; (b) berbeda (sebutkan bedanya) | **(a)** bila tak ada beda nyata. Kode pengajuan barang sudah memperlakukan `qty_reject` sebagai barang ditolak yang diklaim ke pemasok |
| 2 | ~~Boleh satu kiriman dipecah?~~ | - | **Sudah terjawab, tidak ditanyakan lagi**: kode QC penerimaan mencatat sebagian lulus, sebagian ditolak, sebagian karantina per baris; SOP bahan kemas meminta yang memenuhi dan tidak memenuhi spesifikasi dipisahkan |
| 3 | Apakah penolakan perlu dikonfirmasi SPV Quality, atau cukup keputusan QC? | cukup QC / QC lalu dikonfirmasi SPV Quality | **Sebagian sudah di SOP**: SOP QC menetapkan QC yang menyetujui atau menolak. Konfirmasi SPV Quality hanya muncul dari kuesioner, jadi itu yang ditanyakan |
| 4 | ~~Bahan karantina boleh dipakai saat mendesak?~~ | - | **Sudah terjawab, tidak ditanyakan lagi**: SOP PPIC hanya mengizinkan bahan berstatus release dari QC dipindah ke penyimpanan. Sistem mengikuti: tidak pernah |
| 5 | Pencatatan barang masuk manual (tanpa pengajuan, mis. sampel atau kiriman lama) | wajib lewat karantina juga / boleh langsung masuk stok | **Wajib lewat karantina.** Tidak ada aturan tertulis; hari ini jalur manual langsung menambah stok siap pakai |
| 6 | Hasil QC ditempel per **lot** (no. lot pemasok + ED) atau per kedatangan saja? | per lot / per kedatangan | **Per lot**. Kode mencatat per kedatangan dan per baris (dengan beberapa batch per baris); SOP tidak menetapkan |

*Dicocokkan ke vault (SOP QC, SOP PPIC, kajian), kode, dan data prod 2026-10-19 sebelum dikirim, supaya Pemutus tak ditanya hal yang sudah tertulis.*

### Jawaban Quality Supervisor (2026-10-19, lewat WA)

| # | Jawaban | Arti untuk keputusan |
|---|---|---|
| 1 | "Reject + Ditolak", lalu dikonfirmasi "betul, = maksudnya" | **Satu status**: Reject = Ditolak. Sistem memakai dua hasil QC, **Lulus** dan **Ditolak**, seperti SOP QC (terkonfirmasi 2026-10-19) |
| 3 | "Penolakan cukup diputuskan QC" | Tidak ada konfirmasi SPV Quality; QC menetapkan Lulus atau Ditolak |
| 6 | "Hasil QC dicatat per batch" | Hasil QC ditempel per batch/lot pemasok (Decision 2-3), bukan per kedatangan |

Pertanyaan 5 (barang masuk di luar pengajuan wajib karantina) menunggu jawaban Leader Warehouse RM.

## Deskripsi

*Satu gerbang karantina untuk bahan masuk pabrik: penerimaan membentuk lot berstatus karantina, QC menetapkan hasil per lot, dan hanya qty Lulus yang menambah stok siap pakai; pengeluaran ke produksi menolak bahan yang belum Lulus.*

- **Status**: lihat blockquote di baris pertama dokumen ini
- **Keputusan papan**: K-4; membuka M-13 dan M-24 di [[ANALISA - Fondasi Manufaktur]]
- **Issue terkait**: bip-itteam-internal/bip-erp#2190 (satukan pemeriksaan barang masuk), #2250 (incoming inspection), #2249 (pengecekan raw material)
- **Tanggal**: 2026-10-19

## Context

Diukur di kode `bip-erp` `origin/main` (a13cd40a, 2026-10-19). Rujukan baris bisa bergeser sesudah tanggal itu.

**Empat tempat menyimpan "status" bahan masuk, dengan kosakata berbeda:**

| Tempat | Nilai | Catatan |
|---|---|---|
| Lot bahan (manufacture, `StatusLotBahan`) | `MENUNGGU`, `DISETUJUI`, `DITOLAK` | persetujuan **PPIC** atas tanggal masuk, bukan hasil QC (`shared-library/models/manufacture/models.go`) |
| Quality Incoming (`quality_incoming`) | `Menunggu`, `Lulus`, `Tolak` (hanya di komentar) | server tidak memvalidasi nilainya; menyimpan nama bahan dan pemasok sebagai teks bebas tanpa rujukan penerimaan atau lot |
| Quality RM Check (`quality_rm_check`) | `Belum`, `OK`, `Bermasalah` | rujukan penerimaan diterima apa adanya dari layar, tidak divalidasi, tidak menggerakkan apa pun |
| Pengajuan barang (procurement) | angka `qty_lulus`, `qty_reject`, `qty_karantina` per baris + penanda `karantina_aktif` | **satu-satunya yang menggerakkan alur**: dokumen tertahan selama masih ada karantina; hanya qty lulus yang dikirim ke stok manufaktur |

**Akibatnya hari ini:**
- Penerimaan lewat pengajuan barang menambah stok manufaktur tanpa membentuk lot, jadi hasil QC tidak terbawa ke lot dan ED-nya hilang dari penelusuran.
- **Tidak ada gerbang pemakaian.** Pengeluaran bahan hanya memeriksa jumlah stok cukup; pemeriksaan FIFO/FEFO hanya menilai kepatuhan untuk KPI, tidak memblokir; daftar lot tersedia sengaja ikut membaca lot `MENUNGGU`.
- **Pencatatan barang masuk manual** di manufacture langsung menambah stok siap pakai tanpa QC.
- Layar QC bahan masuk (`/quality/incoming`, `/quality/pengecekan-rm`) sudah dibangun, tetapi koleksinya di prod **belum pernah terbentuk** (0 dokumen). Layar penerimaan QC di modul Pengajuan Barang adalah yang benar-benar menahan stok.

**Praktik di lapangan (kuesioner, [[Manufacture - Kajian Fondasi Sistem]] Temuan 3):** label kuning karantina, lalu Lulus / Reject / Ditolak (label merah, konfirmasi SPV Quality); bahan Ditolak tak pernah masuk stok dan langsung diretur Procurement; bahan kemas tak ber-ED.

## Decision

*Usulan; berlaku sesudah status di baris pertama menjadi Diterima.*

1. **Satu catatan hasil QC bahan masuk**, tertaut ke penerimaan (id divalidasi server) dan ke lot. Layar QC di modul Quality dan layar penerimaan QC di Pengajuan Barang membaca dan menulis catatan yang sama, bukan register terpisah (arah #2190).
2. **Penerimaan membentuk lot berstatus Karantina** dengan no. lot pemasok dan ED (bahan kemas boleh tanpa ED).
3. **Hasil per lot** memakai istilah yang dijawab Pemutus di pertanyaan 1. Kiriman boleh dipecah (pertanyaan 2).
4. **Hanya qty Lulus yang menambah stok siap pakai.** Qty karantina terbaca terpisah sebagai stok tertahan, supaya PPIC melihat bahan yang sudah datang tapi belum bisa dipakai.
5. **Gerbang pengeluaran di server**: pengeluaran ke produksi menolak lot yang belum Lulus, dengan pesan yang menyebut lot dan statusnya.
6. **Pencatatan barang masuk manual** ikut membentuk lot Karantina (pertanyaan 5).
7. **Ditolak** tidak pernah masuk stok dan menjadi dasar retur ke pemasok di Procurement (M-24).
8. Status persetujuan PPIC atas lot yang sudah ada (`MENUNGGU/DISETUJUI/DITOLAK`) **tidak dicampur** dengan status QC. Perlu tidaknya persetujuan PPIC itu dipertahankan diputuskan terpisah saat M-13 dirancang.

## Consequences

**Yang didapat.** Stok siap pakai yang terbaca PPIC benar-benar sudah lulus QC; satu bahan bisa ditelusuri dari kiriman pemasok ke lot dan ke batch produksi; QC tidak mengetik ulang data penerimaan.

**Yang harus diterima.**
- Gudang tidak bisa mengeluarkan bahan sebelum QC selesai mencatat hasil di sistem. Bila QC terlambat mencatat, produksi tertahan. Itu disengaja, tetapi butuh kesepakatan batas waktu pencatatan QC.
- Dua layar QC yang sudah dibangun (`/quality/incoming`, `/quality/pengecekan-rm`) akan disatukan atau dipensiunkan.
- Data lama: stok yang sudah ada saat aturan berlaku dianggap Lulus (saldo pembuka), tidak diperiksa ulang.

## Alternatif yang ditolak

- **Tetap di procurement saja (angka per baris, tanpa lot).** Menahan stok sudah bekerja, tetapi hasil QC tidak menempel ke lot, sehingga FEFO dan penelusuran batch tetap buta.
- **Memakai status lot PPIC yang ada sebagai status QC.** Artinya berbeda (tanggal masuk vs mutu); mencampurnya membuat persetujuan PPIC terbaca sebagai kelulusan QC.
- **Gerbang hanya di layar (tombol dinonaktifkan).** Jalur lain (API, impor, layar lain) tetap bisa mengeluarkan bahan karantina; gerbangnya harus di server.
