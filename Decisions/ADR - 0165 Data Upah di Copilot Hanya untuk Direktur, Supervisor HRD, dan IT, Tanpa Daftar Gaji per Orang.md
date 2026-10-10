# ADR - 0165 Data Upah di Copilot Hanya untuk Direktur, Supervisor HRD, dan IT, Tanpa Daftar Gaji per Orang

> **Status**: 🟡 Diusulkan, 2026-10-10. Persetujuan ditulis manusia di baris ini (`🟢 Diterima, <tanggal>, oleh <login/jabatan>`). Arah dasarnya berasal dari keputusan pemilik produk 2026-10-10 untuk batas penanya; bentuk selebihnya (ambang rekap, batas peringkat, penentuan bulan gaji) dipilih pelaksana dan menunggu persetujuan. Kodenya sudah merged di `main` (bip-erp #2922, #2928, #2929); ukur ulang sebelum mengandalkan kalimat ini.

## Untuk Manajemen

**Apa yang berubah di layar.** Pertanyaan tentang gaji, biaya karyawan, dan komponen gaji di Copilot hanya dijawab untuk tiga golongan: **Direktur**, **supervisor HRD**, dan **staf IT**. Bagi yang lain, kartu dan saran bertema gaji tidak ditawarkan, dan bila pertanyaannya tetap diketik, Copilot menyatakan bahwa penanya tidak berhak.

Aturan yang dijaga sistem:

- Copilot **tidak menampilkan daftar gaji seluruh karyawan**. Peringkat per orang paling banyak 20 baris; untuk daftar lengkap, penanya diarahkan ke halaman Payroll.
- Rekap per departemen (jumlah karyawan, total gross, total net) menggabungkan departemen yang berisi **kurang dari 3 orang** ke satu baris, supaya nominal satu atau dua orang tidak bisa dibaca dari total.
- Departemen dalam rekap itu adalah **departemen saat gaji dihitung** bila tercatat; bila tidak tercatat, yang dipakai departemen karyawan hari ini dan layar menyebutnya.
- **Bulan gaji ditentukan sistem dari tanggal awal dan akhir run**, bukan dari label bulan yang diketik atau disimpan. Gaji yang masih draf diberi tanda draf.

**Siapa yang terdampak.** Direktur, supervisor HRD, dan staf IT yang memakai Copilot untuk gaji. Pengguna Copilot lain tetap memakai Copilot untuk topik non-gaji.

**Apa yang TIDAK dijanjikan.**

- Copilot **bukan pengganti halaman Payroll** untuk daftar lengkap per orang.
- Rekap per departemen untuk run lama yang dihitung sebelum departemen dicatat memakai departemen karyawan hari ini, jadi orang yang pindah departemen terhitung di departemen barunya. Layar menyebutnya.
- Definisi resmi HR untuk **bulan gaji run berjendela tak baku** (mis. run magang yang berjalan dari tanggal 8 sampai 7) belum diputuskan; sistem memakai bulan kalender yang memuat hari terbanyak dari jendela itu.

**Perkiraan besaran kerja.** Sudah dikerjakan dalam satu gelombang backend dan frontend; keputusan ini mencatat aturannya.

## Deskripsi

*Menetapkan siapa yang boleh melihat data upah lewat Copilot, bahwa Copilot tidak menjadi jalan lain menuju daftar gaji per orang, dan bahwa bulan gaji ditentukan sistem dari jendela run.*

- **Path di repo**: `bip-erp/shared-library/common/akses_copilot.go` (`BolehPayrollCopilot`, `SupervisorHRD`), `bip-erp/services/assistant/internal/alat/` (`alat_hrga_payroll.go` keluarga data upah, `payroll_umum.go` bulan gaji, `payroll_departemen.go` rekap), `bip-erp/services/payroll/` (`PayrollRunLine.Department`), `erp-frontend/src/features/copilot/lib/akses-payroll.ts`
- **Tanggal**: 2026-10-10
- **Terkait**: [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]] · [[Microservices - Assistant Service]] · [[Microservices - Payroll Service]] · [[REF - Kepemilikan Data]]

## Context

Dibaca dari `bip-erp` `origin/main` (2026-10-10):

- Gerbang Copilot (`BolehPakaiCopilot`) mengizinkan supervisor departemen mana pun, Direktur, Corporate Secretary, dan IT. Golongan itu lebih lebar daripada golongan yang berwenang atas data upah.
- Alat payroll Copilot memanggil payroll-service dengan identitas penanya, jadi gerbang payroll-service di sumber tetap berlaku. Gerbang itu satu lapis; keputusan ini menambah lapis di sisi Copilot, di atasnya.
- Kunci `period` pada run payroll diturunkan dari tanggal awal jendela dan bukan bulan gaji (lihat [[Microservices - Payroll Service]] § Periode Kehadiran). Alat yang mencocokkan bulan yang disebut penanya dengan kunci itu salah memilih run.
- Run payroll tidak menyimpan departemen karyawan sampai #2929; rekap per departemen memerlukan departemen saat digaji atau pengganti yang disebut jujur.
- `insentif_snapshot` berisi angka insentif per orang dan tidak didaftarkan ke model; ia tetap termasuk data upah bagi gerbang.

## Decision

- **K1. Golongan berhak = Direktur, supervisor HRD, IT.** Satu tempat menulis aturannya: `common.BolehPayrollCopilot`. Direktur dibaca dari jabatan Direktur saja, **bukan** daftar setara-Direktur (Corporate Secretary tidak termasuk). Supervisor HRD menuntut **dua** hal sekaligus: cakupan supervisi memuat departemen Human Resource, dan peran modul HRIS supervisor atau admin. IT memakai predikat yang sama dengan cabang IT gerbang Copilot.
- **K2. Tiga lapis.** (1) Alat keluarga data upah tidak ditawarkan ke model bagi penanya di luar golongan; (2) bila tetap dipanggil, alatnya tidak dijalankan dan dibalas `tidak_berhak`; (3) gerbang payroll-service di sumber tetap berlaku bagi yang lolos. Hak dibawa lewat context dan tanpa nilai berarti tidak berhak.
- **K3. Keluarga data upah satu daftar.** Seluruh alat payroll ditambah `insentif_snapshot`; alat payroll baru otomatis ikut. `insentif_saya` (milik penanya sendiri) bukan anggota.
- **K4. Tidak ada daftar gaji lengkap di Copilot.** Peringkat per orang paling banyak 20 baris. Rekap per departemen dihitung alat dari seluruh baris run, dengan ambang 3 orang (departemen lebih kecil digabung, dan yang terkecil berikutnya ikut dilebur sampai gabungannya mencapai ambang).
- **K5. Departemen rekap dari snapshot per baris run** (`PayrollRunLine.Department`, disalin dari employee saat run dihitung atau diimpor, tanpa backfill). Baris tanpa snapshot memakai departemen karyawan saat ini; asalnya selalu disebut (`saat_gaji_dihitung`, `saat_ini`, `campuran`). Bila departemen saat ini tak terbaca, rekap untuk baris itu tidak dibuat.
- **K6. Bulan gaji ditentukan sistem**: bulan kalender yang memuat hari terbanyak dari jendela run (seri = bulan akhir). Jendela baku 26-25 hasilnya sama dengan aturan payroll-service. Penanya tidak menyebut kunci `period`.
- **K7. Frontend hanya menawarkan.** `GET /api/assistant/akses` membalas `boleh_payroll`; layar memakainya untuk menampilkan kartu, templat, dan saran bertema gaji. Penegakannya di backend.

Pilihan yang ditolak:

- **Mengikuti gerbang Copilot umum.** Terlalu lebar untuk data upah.
- **Mengandalkan gerbang payroll-service saja.** Sah sebagai lapis terakhir, tetapi Copilot menjadi jalan baru menuju data yang sama, dan penanya yang berhak atas satu rute belum tentu berhak atas bentuk ringkasan lintas orang.
- **Daftar gaji lengkap per orang di Copilot.** Halaman Payroll sudah ada dan lebih terkontrol.
- **Mencocokkan bulan gaji dengan kunci `period`.** Kunci itu bukan bulan gaji.

## Consequences

- Penanya yang bukan golongan berhak mendapat penolakan yang jelas, bukan jawaban kosong.
- Rekap departemen untuk run lama berlabel `saat_ini` bisa menyimpang dari departemen saat digaji; label asal menjaga agar pembaca tahu.
- Salinan departemen di baris run adalah **salinan satu arah** dari employee-service ([[REF - Kepemilikan Data]]): tidak pernah ditulis tangan, payroll tidak menulisnya balik. Penjaga "tak dibaca perhitungan mana pun" ada di kode (informasi saja).
- Aturan golongan berhak hidup di satu fungsi; mengubah golongan berarti mengubah satu tempat, ditambah uji yang mengunci isinya.
- Ambang 3 orang melindungi dari pembacaan nominal perorangan lewat total; ia tidak melindungi dari penanya yang memang berhak membuka halaman Payroll.

## Belum diputuskan

- **Definisi resmi HR untuk bulan gaji run berjendela tak baku** (jendela 8 sampai 7 untuk run magang). Perlu keputusan HR; aturan "hari terbanyak" adalah pilihan pelaksana.
- Apakah golongan berhak perlu diperluas (mis. Corporate Secretary) atau dipersempit lebih lanjut.
- Apakah run lama perlu diisi departemen saat digaji (backfill); saat ini sengaja tidak.

## Dokumen Terkait

- [[Microservices - Assistant Service]] § Gelombang 2026-10-10
- [[Microservices - Payroll Service]] § Snapshot departemen per baris run
- [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]]
- [[REF - Kepemilikan Data]]