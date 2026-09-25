# Finance - Proses Insentif

## Deskripsi

*Proses P12, insentif berbasis profit, dari [[Finance - Proses Bisnis dan Kebutuhan Sistem]]. Dok ini memuat tujuan, cara dikerjakan hari ini, yang sudah ada di ERP, alur target di sistem, celah yang harus ditutup, kontrol yang wajib dijaga, dan ukuran untuk membuktikan efisiensinya. Aturan hitung lengkap dan riwayat SK ada di [[Finance - Incentive]]; dok ini tidak menyalinnya.*

- **Status**: ⚠️ **Implemented (ada catatan)**. Mesin insentif profit, Dashboard Insentif, dan Master Target sudah di kode dan live; yang menahan pemakaian adalah master data yang belum terisi dan keputusan yang masih terbuka ([[Finance - Incentive]] § Yang masih menahan).
- **Sumber**: [[Finance - Incentive]], [[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]], [[ADR - 0081 Insentif Saya Pindah ke MyBharata di Dalam Slip Gaji]], dan survei alur kerja Finance 14 sampai 16 September 2026. Keadaan prod bertanggal di tiap butir; ukur ulang sebelum dipakai memutuskan.
- **Kelompok celah**: **A** sudah ada, tinggal dipakai · **B** sudah ada, perlu diperbaiki · **C** belum ada, perlu dibangun (definisi di dok induk).

## Tujuan

Insentif dihitung dari profit yang benar dan target yang ditetapkan satu kali oleh yang berwenang, diperiksa dan disetujui sebelum dibayar, dan bisa dijelaskan kepada penerimanya.

## Hari ini (*survei 2026-09*)

Insentif karyawan dicantumkan sebagai pekerjaan oleh Junior Accountant dan Cost Control, dan pencapaian target profit serta penilaian realisasi iklan rutin diminta departemen lain dari Cost Control. Menurut [[Finance - FAT Persona]], target insentif level supervisor dipegang Supervisor FAT. Langkah kerjanya tidak dirinci di isian survei (TBD, dikonfirmasi lewat wawancara).

## Sudah ada di ERP

- **Rumus**: profit = uang cair (net settlement) dikurangi HPP, beban iklan, dan biaya operasional; insentif = tarif bertingkat (0 sampai 5 persen menurut pencapaian target) dikali profit; dinilai tiga level ICC, Leader, dan Supervisor; gerbang retur 7 persen berbasis jumlah order selama pencapaian paling tinggi 100 persen ([[Finance - Incentive]] § Skema Berlaku).
- **Biaya operasional**: beban karyawan dari payroll (bruto ditambah iuran BPJS pemberi kerja, bukan gaji bersih) dan beban non-gaji dari proyek Accurate per karyawan ([[ADR - 0033 Beban Operasional Insentif dari Proyek Accurate]]).
- **Target satu pintu**: target per orang diketik Supervisor divisinya, target level supervisor oleh Finance atau Direktur, dan angka yang sama dibaca KPI; mengubah target di periode berjalan wajib beralasan, dan target diri sendiri ditolak ([[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]]).
- **Periode**: order masuk bulan M bila dikirim di bulan M dan uangnya cair paling lambat tanggal 25 bulan M+1; yang cair sesudahnya hangus untuk insentif, sedangkan KPI memakai jendela bergeser ([[Finance - Incentive]] § Aturan periode).
- **Layar dan akses**: Dashboard Insentif dan Master Target dibuka pemegang paket "Menu: Insentif Profit"; rincian beban karyawan hanya untuk Finance; menulis target digerbang terpisah dan lebih ketat. Hasil insentif berstatus DRAFT tampil di kotak persetujuan dashboard Finance (`bip-erp/services/integration/internal/interface/http/persetujuan_handler.go:16-19`).
- **Penerima**: insentif sendiri tampil di slip gaji MyBharata ([[ADR - 0081 Insentif Saya Pindah ke MyBharata di Dalam Slip Gaji]]).
- **Prod 2026-09-17** (jumlah dokumen per koleksi `insentive_db`, baca-saja): 62 target profit, terbaru dibuat 2026-09-11; 6 hasil insentif tersimpan (`incentive_results`), terbaru dibuat 2026-07-10; `incentive_opex` 0. Target terus diisi, tetapi tidak ada hasil baru yang tersimpan sejak Juli.

## Alur target

Master data lengkap (atribusi toko ke ICC, beban non-gaji per proyek karyawan, HPP) → target ditetapkan satu pintu → profit dan insentif dihitung otomatis per periode → periode final (akhir tanggal 25 bulan berikutnya) → Finance **membekukan** periode menjadi snapshot per orang lalu **menyetujuinya** → snapshot yang disetujui masuk slip gaji sebagai komponen **Insentif** (terpisah dari Bonus) pada run pertama sesudah persetujuan, dan ditandai terbayar saat run di-publish → Finance mencocokkan disetujui dengan terbayar → penerima melihat rinciannya di MyBharata. Keputusannya: 🟡 [[ADR - 0125 Insentif Profit Dibayar lewat Slip Gaji dari Snapshot yang Disetujui Finance]] (belum di kode).

## Celah

- **A** Atribusi toko ke ICC dilengkapi. Per 2026-08-02 baru 10 dari 28 toko punya pemetaan, sehingga sebagian besar profit Juli tidak berpemilik.
- **A** Beban non-gaji dibukukan ke proyek karyawan di Accurate. Per 2026-08-02 baru 6 dari 62 proyek karyawan terisi.
- **A** Target Leader diisi. Pembagian rata turun praktis tidak berjalan karena `incentive_org` kosong; per 2026-09-11 target September belum memuat Leader.
- **B** Alur persetujuan dan pembekuan periode. [[Finance - Incentive]] mencatat alur approval/freeze belum ada per 2026-08-02, sementara hasil DRAFT kini sudah tampil di kotak persetujuan; periksa ulang apa yang sudah terkunci sesudah disetujui. Koleksi hasil tersimpan tidak bertambah sejak 2026-07-10 (diukur 2026-09-17); apakah dashboard menghitung saat dibuka tanpa menyimpan, atau penyimpanannya berhenti, belum diperiksa (**TBD**).
- **TBD** HPP yang dipakai perhitungan menunggu Finance melengkapinya; kaitannya dengan costing di [[Finance - Proses Costing HPP Produk]].
- **TBD** Keputusan terbuka untuk Finance: PPN di dalam profit, target sebelum atau sesudah opex, dan jadwal bayar menurut SK (tanggal 1 atau 5) terhadap cutoff pencairan tanggal 25.
- **TBD** Hierarki tim insentif sebagai turunan HRIS atau pemilik untuk konteksnya sendiri ([[REF - Kepemilikan Data]] § Duplikasi).
- **C** Jalur pembayaran insentif **diputuskan 2026-09-25**: lewat slip gaji, komponen `Insentif`, dari snapshot yang disetujui Finance ([[ADR - 0125 Insentif Profit Dibayar lewat Slip Gaji dari Snapshot yang Disetujui Finance]]). Hari ini (prod 2026-09-25) HR mengetik angka insentif ke kolom Bonus di sheet gaji HRD yang lalu diimpor; satu-satunya run payroll di prod memuat satu baris Bonus dari 174 slip. Status per 2026-09-25: snapshot + persetujuan (T1) dan komponen Insentif (T3) live DEV; pencocokan impor + klaim + tanda terbayar (T4) di kode, belum merged. Semula yang belum ada: snapshot dan persetujuan skema profit (dashboard dihitung saat dibuka, cache 15 menit; `disetujui` pada target tak pernah `true`), komponen Insentif, dan pemeriksaan impor terhadap snapshot.
- **TBD** Perlakuan PPh 21 dan dasar BPJS untuk komponen Insentif, tahap persetujuan pertama oleh Supervisor, dan tanggal tutup payroll (dikonfirmasi Finance dan HR; lihat ADR 0125 §3, §7, §8).

## Kontrol wajib

Penetap target bukan penerima insentif atas target itu; perubahan target di periode berjalan beralasan dan tercatat; beban karyawan per orang hanya terlihat oleh Finance; hasil insentif disetujui sebelum dibayar. Sejak [[ADR - 0125 Insentif Profit Dibayar lewat Slip Gaji dari Snapshot yang Disetujui Finance]] ditambah: penyetuju akhir adalah Finance dan bukan penerima snapshot itu; penetap target (Supervisor marketing) bukan pemberi persetujuan bayar; insentif profit hanya dibayar lewat komponen Insentif, tidak lewat Bonus; satu snapshot terbayar paling banyak satu kali.

> ⛔ **Komponen Insentif tidak pernah diisi di master gaji.** Nilai master ikut ke `/employer-cost`, sehingga insentif akan menjadi beban gaji yang mengurangi profit insentif itu sendiri (melingkar, kelas yang sama dengan akun Accurate 6102 di [[ADR - 0033 Beban Operasional Insentif dari Proyek Accurate]]). Insentif hanya masuk sebagai baris per periode di run.

## Ukuran efisiensi

Porsi profit yang punya pemilik (toko teratribusi); jumlah baris bertarget nol; lama dari akhir periode sampai insentif disetujui.

Sumber data baseline: Dashboard Insentif dan Master Target per periode.

## Proses terkait

- P2: [[Finance - Proses Pembayaran Keluar]]
- P7: [[Finance - Proses Gaji dan Iuran BPJS]]
- P11: [[Finance - Proses Costing HPP Produk]]

## Dokumen Terkait

- [[Finance - Proses Bisnis dan Kebutuhan Sistem]] · [[Finance - Kalender dan Rantai Tenggat]] · [[Finance - Sambungan dan Permintaan Data Lintas Departemen]] · [[Finance - FAT Persona]]
- [[Finance - Incentive]] · [[Microservices - Insentive Service]] · [[ADR - 0125 Insentif Profit Dibayar lewat Slip Gaji dari Snapshot yang Disetujui Finance]] · [[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]] · [[ADR - 0081 Insentif Saya Pindah ke MyBharata di Dalam Slip Gaji]] · [[ADR - 0033 Beban Operasional Insentif dari Proyek Accurate]] · [[REF - Kepemilikan Data]]
