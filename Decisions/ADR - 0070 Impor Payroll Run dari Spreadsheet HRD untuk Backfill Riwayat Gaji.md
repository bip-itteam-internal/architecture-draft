# ADR - 0070 Impor Payroll Run dari Spreadsheet HRD untuk Backfill Riwayat Gaji

## Untuk Manajemen

- **Yang berubah di layar**: HR bisa mengunggah spreadsheet gaji yang **sudah dibayar** lewat tombol **Impor dari Spreadsheet** di halaman Payroll Run. Angkanya masuk apa adanya sebagai run baru berjenis **Impor**, lalu melewati Setujui dan Terbitkan seperti run biasa, sehingga karyawan bisa membuka slipnya sendiri berikut PDF-nya.
- **Siapa terdampak**: HR Supervisor (mengimpor), Direktur (menyetujui), seluruh karyawan yang gajinya diimpor.
- **Tidak dijanjikan**: sistem **tidak menghitung ulang apa pun** dan **tidak memeriksa kebenaran** angka yang diunggah. Yang diperiksa hanya bahwa baris-barisnya berjumlah sama dengan kolom TOTAL TERIMA. Bila spreadsheet-nya sendiri salah, slip yang terbit ikut salah.
- **Besaran kerja**: sedang. Tak ada perubahan pada mesin penggajian; yang baru satu rute impor, satu rute hapus, dan layar pemetaan kolom.

## Deskripsi

*Payroll sudah live sejak Fase 1-5 tetapi **belum pernah dipakai menggaji seorang pun** (dua `payroll_run` di produksi, keduanya `draft`, nol slip terbit). Sementara itu HRD sudah membayar gaji berbulan-bulan lewat spreadsheet. ADR ini memutuskan riwayat itu dimasukkan ke sistem sebagai **jenis run ketiga** yang angkanya DISALIN, bukan dihitung, supaya karyawan punya slip yang bisa dibuka tanpa menunggu mesin penggajian dipercaya.*

- **Status**: **Accepted** (2026-09-01). ⛔ Kode selesai di branch `feat/payroll-impor-run` (bip-erp + erp-frontend) tetapi **BELUM merged, BELUM deploy, dan BELUM diverifikasi lewat gateway sama sekali**. Satu **gerbang DATA** masih terbuka sebelum impor produksi boleh dijalankan (§Gerbang Data yang Masih Terbuka).
- **Path di repo**: BE `bip-erp/services/payroll` (`impor_run.go`, `impor_run_handlers.go`, `RunTypeImport` di `models_payroll_run.go`, penjaga di `run_handlers.go`); FE `erp-frontend/src/features/hris/payroll` (`lib/impor-payroll-run.ts`, `components/impor-payroll-run-modal.tsx`, `hooks/use-impor-payroll-run.ts`).
- **Tanggal**: 2026-09-01

## Context

- **Yang menahan payroll bukan lagi kode.** Seluruh fase sudah ter-deploy, tetapi nol slip pernah sampai ke karyawan. Rinciannya di [[Microservices - Payroll Service]] §Kondisi Pemakaian di Produksi.
- **Riwayat gaji yang sudah dibayar tidak ada di sistem sama sekali.** Karyawan tak punya slip yang bisa dibuka untuk bulan mana pun, dan tak ada arsip selain berkas Excel milik HRD.
- **Menghitung ulang riwayat lewat mesin penggajian akan menghasilkan angka yang BERBEDA dari yang sudah dibayar**, karena config BPJS, tabel TER, dan tarif potongan kehadiran hari ini belum tentu sama dengan yang berlaku saat gaji itu dibayarkan. Slip yang berbeda dari uang yang masuk rekening lebih buruk daripada tidak ada slip.
- Sudah ada preseden impor Excel yang matang di modul yang sama: `POST /employee-salary/bulk-bpjs-base` (Excel diurai di frontend, server tak pernah menebak orang).

## Decision

1. **Jenis run KETIGA: `PayrollRun.type = "import"`**, berdampingan dengan `monthly` dan `thr`. Barisnya `PayrollRunLine` yang sama persis, sehingga lifecycle (`draft → approved → published`), slip self-service, dan PDF **dipakai ulang tanpa perubahan apa pun**.
2. **Angka DISALIN apa adanya, tidak dihitung.** Konsekuensinya diterima sadar: baris impor **mem-bypass seluruh penjaga uang** — config BPJS, tabel TER PPh21, tarif potongan kehadiran, dan kedua dasar upah BPJS. Tak satu pun rumus di `payroll_calc.go` menyentuhnya.
3. **Penggantinya satu-satunya: REKONSILIASI.** Jumlah baris pendapatan dikurangi jumlah baris potongan **wajib sama** dengan kolom TOTAL TERIMA, toleransi 0,01 (satu sen; menjaga derau float, bukan memaafkan uang yang tak cocok). Yang tak cocok **ditolak berikut selisihnya dalam rupiah**, sehingga kolom penyebabnya menunjuk dirinya sendiri.
4. **Run impor TIDAK bisa dihitung ulang.** `POST /payroll-runs/:id/recalculate` membalas 400. Koreksinya: **hapus lalu impor ulang** selagi `draft`, lewat `DELETE /payroll-runs/:id` yang hanya menerima `type=import` DAN `status=draft`.
5. **ALL-OR-NOTHING**, berbeda sengaja dari `bulk-bpjs-base` yang gagal per baris. Di sana tiap baris menulis field yang independen; di sini seluruh baris membentuk **satu run** yang totalnya harus utuh. `Payroll-MongoDB` jalan **standalone tanpa replica set** sehingga transaksi Mongo tak tersedia, jadi validasi penuh di depan adalah penggantinya.
6. **Nama baris slip WAJIB berasal dari master `salary_component`**; nama bebas ditolak 400. Nama bebas melahirkan baris hantu: tercetak di slip karyawan tetapi tak ada di Pengaturan > Komponen Gaji, sehingga tak seorang pun bisa mengubah atau menjelaskannya.
7. **Kolom yang artinya ambigu TIDAK ditebak.** Layar pemetaan membiarkannya "abaikan" dan HR memetakannya sendiri. Bila ia lupa, kolomnya tak ikut dijumlahkan, rekonsiliasi gagal, dan barisnya ditolak — kegagalan yang berisik, dan itu yang dikehendaki.
8. **Karyawan tanpa `employee_salary` tetap diimpor** (backfill justru mencakup orang yang struktur gajinya belum pernah dimasukkan). Kop slipnya jatuh ke badan usaha **default** dan baris itu **ditandai** `warn_codes: import_company_default`.
9. **`scope` sengaja dibiarkan KOSONG.** Lingkup run impor ditentukan isi berkas, bukan penyaring tipe kepegawaian; mengisinya `semua` akan berbohong karena sheet bisa memuat sebagian orang saja.
10. **Gerbang izin `payroll.work` / `isHRSupervisor`** untuk impor **dan** hapus — sama dengan membuat run. Menghapus draft impor adalah kebalikan dari **membuatnya**, bukan dari menerbitkannya ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]).

## Gerbang Data yang Masih Terbuka

⛔ **Impor PRODUKSI tidak boleh dijalankan sebelum bagian ini terjawab.** Slip yang sudah `published` men-snapshot kesalahannya, dan koreksinya menuntut pembatalan run.

Sheet gaji HRD memuat kolom yang **artinya belum dikonfirmasi**, dan aturan pemakaiannya tidak tertulis di mana pun:

| Kolom | Yang belum pasti |
|---|---|
| **TOTAL TK** | Diduga **subtotal** JHT + JP. ERP sendiri sudah mendefinisikannya begitu: `kolomRinci.totalTk` (`erp-frontend/src/features/hris/payroll/payslip.ts`) menjumlah JHT+JP+JKK+JKM dan dirender berdampingan dengan JHT dan JP **tanpa pernah ditambahkan ke total mana pun**. Bila sheet memakai arti yang sama, TOTAL TERIMA yang memotong TOTAL TK **di samping** JHT dan JP memotong **dua kali** |
| **Tunjangan PPh 21** | Terbukti **DIKELUARKAN** dari TOTAL TERIMA: dua baris dengan nilai tunjangan berbeda (5.107.872 dan 142.889) punya TOTAL TERIMA yang sama persis |
| **JABATAN** | Muncul **dua kali** di satu header: nama jabatan dan tunjangan |
| **PPh 21** | Muncul **dua kali**: tunjangan dan potongan |
| **ABSENSI** | Satu kolom, sementara master memecah potongan kehadiran jadi **empat** baris |
| **NIK** | Berisi `employee_id` (`BIP-9999-99-99`), **bukan** nomor KTP |

⚠️ **Data contoh dari HRD sudah di-dummy-kan** (semua tunjangan 10.000.000, semua potongan 200.000), sehingga TOTAL TK vs JHT+JP **mustahil dibedakan dari sana**. Satu baris data asli sudah cukup menjawabnya.

## Consequences

- **Positif**: riwayat gaji jadi bisa dibuka karyawan tanpa menunggu mesin penggajian dipercaya; lifecycle, slip self-service, dan PDF dipakai ulang utuh; rekonsiliasi mengubah kolom yang salah petak dari **angka salah yang masuk akal** menjadi **penolakan yang menyebut selisihnya**.
- ⛔ **Angka impor tidak dijamin benar oleh apa pun selain spreadsheet-nya.** Yang dijamin cuma bahwa baris-barisnya konsisten dengan totalnya sendiri. Ini penyimpangan paling besar dari seluruh rancangan payroll, dan itu sebabnya ADR ini ada.
- ⚠️ **Satu periode bisa punya run engine DAN run impor sekaligus**, dan bila keduanya `published` karyawan melihat dua slip untuk bulan yang sama. Dedup **sengaja tidak dibangun**: belum ada pemakai kedua yang menentukan aturan "run mana yang menang", dan menebaknya sekarang mengunci bentuk yang belum tentu benar. Yang membedakan di layar: judul run dan badge jenis.
- ⚠️ **`GET /employer-cost` tidak membaca run impor.** Ia menghitung ulang lewat `buildPayslip` dari `employee_salary` yang berlaku sekarang, jadi [[Microservices - Insentive Service]] tetap memakai angka engine. Untuk backfill riwayat itu memang yang benar: biaya insentif bulan lalu tak boleh berubah karena riwayat dimasukkan hari ini.
- **Ongkos**: dua rute baru, satu berkas logika murni + satu handler di BE, satu layar pemetaan kolom di FE. **Nol dependensi Go baru** (Excel diurai di frontend, mengikuti preseden `bulk-bpjs-base`), nol env baru, nol kategori inbox baru.
- **Ditunda**: dedup slip satu periode; impor THR dari spreadsheet (bentuk kolomnya berbeda); pemilih karyawan manual untuk baris tanpa `employee_id` (HR membetulkan sheet lalu unggah ulang, karena membangun picker berarti membangun jalur tebak-orang yang sudah sengaja ditolak di impor dasar upah).
- **Gotcha ke `team-memory.md`**: kolom spreadsheet yang namanya terdengar seperti komponen padahal subtotal — kelas yang sama dengan `iklan_sia_sia`, dan aturannya sama-sama tak tertulis di mana pun kecuali di kepala orang yang membuat sheet-nya.

## Dokumen Terkait

- [[Microservices - Payroll Service]] · [[API - Payroll Service]] · [[HRIS - Payroll]] · [[HRIS - Payroll Persona]]
- [[APP - Web ERP]] (layar impor) · [[Microservices - Employee Service]] (verifikasi `employee_id`)
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]] · [[ADR - 0002 Database-per-Service]]
