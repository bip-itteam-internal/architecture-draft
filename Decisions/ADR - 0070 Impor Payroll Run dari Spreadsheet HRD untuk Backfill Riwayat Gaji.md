# ADR - 0070 Impor Payroll Run dari Spreadsheet HRD untuk Backfill Riwayat Gaji

## Untuk Manajemen

- **Yang berubah di layar**: HR bisa mengunggah spreadsheet gaji yang **sudah dibayar** lewat tombol **Impor dari Spreadsheet** di halaman Payroll Run. Angkanya masuk apa adanya sebagai run baru berjenis **Impor**, lalu melewati Setujui dan Terbitkan seperti run biasa, sehingga karyawan bisa membuka slipnya sendiri berikut PDF-nya.
- **Siapa terdampak**: HR Supervisor (mengimpor), Direktur (menyetujui), seluruh karyawan yang gajinya diimpor.
- **Tidak dijanjikan**: sistem **tidak menghitung ulang apa pun** dan **tidak memeriksa kebenaran** angka yang diunggah. Yang diperiksa hanya bahwa baris-barisnya berjumlah sama dengan kolom TOTAL TERIMA. Bila spreadsheet-nya sendiri salah, slip yang terbit ikut salah.
- **Besaran kerja**: sedang. Tak ada perubahan pada mesin penggajian; yang baru satu rute impor, satu rute hapus, dan layar pemetaan kolom.

## Deskripsi

*Payroll sudah live sejak Fase 1-5 tetapi **belum pernah dipakai menggaji seorang pun** (dua `payroll_run` di produksi, keduanya `draft`, nol slip terbit). Sementara itu HRD sudah membayar gaji berbulan-bulan lewat spreadsheet. ADR ini memutuskan riwayat itu dimasukkan ke sistem sebagai **jenis run ketiga** yang angkanya DISALIN, bukan dihitung, supaya karyawan punya slip yang bisa dibuka tanpa menunggu mesin penggajian dipercaya.*

- **Status**: **Accepted** (2026-09-01). Irisan pertama dan kedua **MERGED dan sudah ada di `main` kedua repo** (bip-erp [#1604](https://github.com/bip-itteam-internal/bip-erp/pull/1604) + [#1611](https://github.com/bip-itteam-internal/bip-erp/pull/1611), erp-frontend [#1371](https://github.com/bip-itteam-internal/erp-frontend/pull/1371) + [#1375](https://github.com/bip-itteam-internal/erp-frontend/pull/1375); diverifikasi ke `origin/main` 2026-09-03). Irisan ketiga (Decision 14, karyawan non-aktif) **OPEN**: bip-erp [#1691](https://github.com/bip-itteam-internal/bip-erp/pull/1691), erp-frontend [#1434](https://github.com/bip-itteam-internal/erp-frontend/pull/1434). ✅ **Gerbang data sudah TERJAWAB** dari sheet produksi (§Gerbang Data: Terjawab). ⛔ Tetapi **BELUM deploy dan NOL verifikasi lewat gateway**, jadi impor produksi tetap belum boleh dijalankan.
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
8. **Karyawan tanpa `employee_salary` tetap diimpor** (backfill justru mencakup orang yang struktur gajinya belum pernah dimasukkan). Bila sheet **tidak** menyebut badan usahanya, kop slipnya jatuh ke badan usaha **default** dan baris itu **ditandai** `warn_codes: import_company_default`. Sejak Decision 12, penanda itu **tidak** menyala bila sheet menyebutnya.
9. **`scope` sengaja dibiarkan KOSONG.** Lingkup run impor ditentukan isi berkas, bukan penyaring tipe kepegawaian; mengisinya `semua` akan berbohong karena sheet bisa memuat sebagian orang saja.
10. **Gerbang izin `payroll.work` / `isHRSupervisor`** untuk impor **dan** hapus — sama dengan membuat run. Menghapus draft impor adalah kebalikan dari **membuatnya**, bukan dari menerbitkannya ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]).

Ditambahkan 2026-09-01 setelah sheet produksi diterima (bip-erp [#1611](https://github.com/bip-itteam-internal/bip-erp/pull/1611), erp-frontend [#1375](https://github.com/bip-itteam-internal/erp-frontend/pull/1375)):

11. **Komponen `Potongan Absensi` lahir NON-AKTIF, dan itu penjaganya bukan penanda status.**

    Sheet menulis seluruh potongan kehadiran sebagai **satu** kolom ABSENSI, sementara engine memecahnya jadi **empat** baris berpengali berbeda (Pasal 20, lihat [[HRIS - Payroll]]). Rinciannya tidak ada lagi untuk bulan yang sudah dibayar, dan mengarangnya berarti menerbitkan slip yang menyebut sebab yang tak pernah diverifikasi siapa pun.

    ⛔ `is_active` menentukan sebuah komponen muncul atau tidak di layar **Penetapan Gaji**. Bila komponen ini aktif, seseorang bisa melekatkannya ke struktur gaji karyawan, dan sejak saat itu **setiap run engine memotong `Potongan Absensi` manual DITAMBAH empat baris kehadiran yang dihitung otomatis**. Potongan yang sama diambil **dua kali** dari gaji orang, tanpa satu pun galat, dengan gejala cuma slip yang sedikit lebih kecil dari seharusnya.

    Non-aktif tetap **diterima impor**, karena `namaKomponenMaster` memang sengaja membaca seluruh master termasuk yang non-aktif. Satu flag memberi **dua sifat sekaligus** — dipakai impor, mustahil masuk engine — tanpa menambah field baru ke master.

    Konsekuensinya: begitu engine mengambil alih penggajian, komponen ini **tidak perlu** dipensiunkan. Ia memang sudah tak bisa dipakai run engine sejak awal, dan namanya tetap ada supaya slip riwayat yang menyebutnya tetap bisa dijelaskan (sealasan dengan `pensiunkanKomponen`).

    ⚠️ Penjaga ini menuntut **`employee-salary-form` menyaring `is_active`**, dan sebelumnya tidak. Tanpa perbaikan itu seluruh keputusan ini tidak menjaga apa pun.

12. **Kop slip diambil dari kolom KETERANGAN sheet, mengalahkan `employee_salary`.**

    Urutan menang: **nama dari sheet → `employee_salary.company_id` → badan usaha default.**

    Alasannya `employee_salary` cuma menyimpan keadaan **hari ini**, sementara yang di-backfill slip belasan bulan lalu, dan orang yang sama bisa digaji atas nama CV berbeda dari bulan ke bulan. Menyimpulkan kop dari penetapan gaji berarti mencetak kop hari ini di atas slip lama.

    Nama yang disebut tapi **tak ada di master DITOLAK**, tidak jatuh ke default: kop slip menentukan badan hukum mana yang tercetak, dan menebaknya menghasilkan slip yang terlihat sah atas nama entitas yang tak pernah membayarnya.

    Dua hal sengaja **tidak** dilumatkan saat mencocokkan nama: **bentuk badan hukum** (`CV Sinar` dan `PT Sinar` dua entitas dengan NPWP berbeda) dan **nama kembar di master** (iterasi map Go tak berurutan, jadi "ambil yang pertama" memilih entitas berbeda tiap proses restart; kembar ditolak sebagai ambigu).

13. **Komponen NON-AKTIF ditawarkan di layar impor, dan hanya di sana.** Server sudah menerimanya sejak awal, tetapi layar impor menyaringnya sehingga kelonggaran itu tak bisa dijangkau siapa pun — padahal backfill slip lama justru sering menyebut nama yang sudah dipensiunkan (`BPJS Ketenagakerjaan` gabungan dipensiunkan sejak dipecah per program, tapi slip Januari memang memakainya). Kini ditawarkan, ditaruh di belakang dan berlabel `(non-aktif)`: yang menahan orang adalah **labelnya**, bukan ketiadaannya.

Ditambahkan 2026-09-03 (bip-erp [#1691](https://github.com/bip-itteam-internal/bip-erp/pull/1691),
erp-frontend [#1434](https://github.com/bip-itteam-internal/erp-frontend/pull/1434); **keduanya
masih OPEN**):

14. **Karyawan NON-AKTIF ikut dimuat di layar impor, dan hanya di sana.**

    Decision 13 diterapkan ke sumbu **kedua**, dan bentuk masalahnya persis sama: server
    penerima impor **tidak pernah** menyaring `is_active` — `fetchEmployeeIdentities` membaca
    `/internal/export/all` yang tak punya saringan itu — sementara layar membandingkan ke
    `/list?type=employee` yang menyaringnya. Karyawan yang sudah resign karena itu ditolak
    dengan **"Employee ID tidak dikenal"**, kalimat yang menunjuk ke ID sehingga yang
    diperiksa orang adalah spreadsheet-nya, dan spreadsheet-nya benar. Ditemukan saat impor
    produksi menolak 4 dari 174 baris.

    Backfill riwayat gaji adalah fitur yang **dijamin** memuat orang seperti itu: semakin lama
    periode yang dimasukkan, semakin banyak yang sudah keluar. Sejalan dengan Decision 8 yang
    sudah memutuskan karyawan tanpa `employee_salary` tetap diimpor.

    Penyelesaiannya mengikuti Decision 13: bendera **opt-in** `include_inactive=true` di
    `/list?type=employee`, dipakai satu layar, dan barisnya **ditandai** bukan disembunyikan.
    Yang menahan orang tetap labelnya. Rincian benderanya: [[API - Employee Service]].

    ⛔ **Gerbangnya DUA SUMBU**: `RequireHRISStaffCheck` **atau** izin `payroll.work`. Bukan
    kelonggaran melainkan koreksi — layar pemakainya dijangkau lewat izin, bukan lewat
    `system_roles`, dan akun ber-permission-set bisa memegang paket payroll tanpa peran `hris`
    sama sekali. Satu sumbu saja membuat orang itu dibalas 403 lalu melihat daftar kosong,
    sehingga **seluruh** barisnya ditolak: lebih buruk daripada bug yang sedang diperbaiki.
    Karena kegagalan itu tetap mungkin lewat sebab lain, layar impor kini **berbunyi eksplisit
    bila daftar karyawannya gagal dimuat** alih-alih membiarkan barisnya bicara sendiri.

    ⚠️ **Dua batas yang diterima sadar.** Pertama, bendera ini tak menyentuh `$unwind`, jadi
    karyawan yang tak punya dokumen `system_authentication` sama sekali tetap terbuang dengan
    gejala yang identik; apakah kelas itu berpenghuni **belum diukur di produksi**, dan
    melonggarkannya lebih dulu berarti menambah kelas baris yang belum pernah diuji demi orang
    yang belum terbukti ada. Kedua, bendera ini tak berlaku untuk akun pihak luar
    (`barisAkunLuar` menyaring `is_active` sendiri dan barisnya tak membawa field itu),
    sehingga kedua bendera yang menyala bersamaan menghasilkan daftar yang aturannya tidak
    seragam.

    **Konsekuensi yang perlu disadari**: slip bisa terbit untuk orang yang akunnya sudah mati,
    dan ia **tidak bisa membukanya sendiri** lewat MyBharata. Menyelesaikannya menuntut
    keputusan tentang akses akun yang sudah dinonaktifkan, wilayah
    [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]], dan sengaja tidak diputuskan di
    sini.

## Gerbang Data: Terjawab (2026-09-01)

✅ Sheet gaji HRD **produksi** (21 baris, angka asli) diterima 2026-09-01. Aritmetikanya diuji pada **empat baris** dan **cocok sampai rupiah**, sehingga gerbang ini tertutup.

| Kolom | Kesimpulan |
|---|---|
| **TOTAL TK** | ✅ **SUBTOTAL JHT + JP.** Jangan pernah dipetakan sebagai potongan. WIRAWAN 204.400+102.000=306.400 · ZULHAKIM 55.400+27.700=83.100 · ENDRI 124.400+62.200=186.600 · RIDHO 55.400+27.700=83.100. BPJS **Kesehatan tidak ikut** (RIDHO: Kes 81.600, TOTAL TK tetap 83.100). Artinya sama persis dengan `kolomRinci.totalTk` milik ERP, jadi dugaan sebelumnya benar |
| **Tunjangan PPh 21** | ⚠️ **IKUT ditambahkan ke TOTAL TERIMA.** Ini **MEMBALIK** catatan versi pertama ADR ini yang menyatakan ia "terbukti DIKELUARKAN" |
| **ABSENSI** | Potongan sungguhan, satu angka gabungan. Dipetakan ke komponen baru `Potongan Absensi` (lihat Decision 11) |
| **KASBON** | Potongan sungguhan |
| **KETERANGAN** | ✅ Berisi **badan usaha penggaji** (10 dari 21 baris terisi), bukan catatan bebas. Lihat Decision 12 |
| **JABATAN** | Muncul **dua kali** di satu header: nama jabatan dan tunjangan. Tetap tak ditebak |
| **PPh 21** | Muncul **dua kali**: tunjangan dan potongan. Tetap tak ditebak |
| **NIK** | Berisi `employee_id` (`BIP-9999-99-99`), **bukan** nomor KTP |

Bukti aritmetika untuk baris pertama:

```
WIRAWAN WIDI ATMOKO
  (18.064.250 + 9.038.550 + 3.025.700 + 200.000 + 5.109.500)   ← T. PPh 21 IKUT
− (5.109.500 + 102.000 + 204.400 + 102.000)                    ← TOTAL TK TIDAK
= 29.920.100                                                    ← persis TOTAL TERIMA
```

ENDRI (ABSENSI 82.637), ZULHAKIM (KASBON 1.000.000), dan FUAD (keduanya) juga rekonsiliasi tepat.

⛔ **Pelajaran yang wajib dibawa ke impor berikutnya: DATA DUMMY BISA MEMALSUKAN BUKTI.** Contoh pertama dari HRD menyamakan seluruh nominal (semua tunjangan 10.000.000, semua potongan 200.000), sehingga dua baris dengan Tunjangan PPh 21 berbeda kebetulan bertotal sama. Itu terbaca sebagai bukti kuat bahwa kolomnya dikeluarkan, dan ditulis ke ADR ini sebagai "terbukti". Yang sebenarnya terbaca adalah **artefak penyamaran data**. Kesimpulan aritmetika hanya boleh ditarik dari angka yang benar-benar berbeda satu sama lain.

Inilah justru alasan rancangan ini **tidak menebak kolom sama sekali** dan menyerahkannya ke rekonsiliasi: gerbang datanya sempat dijawab keliru, dan kodenya tetap tidak salah karena ia memang tak pernah bersandar pada jawaban itu.

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
