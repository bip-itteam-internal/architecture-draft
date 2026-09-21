## Untuk Manajemen

Lembar HRD "Actual vs Planning MPP" akan dihitung sistem, tidak lagi diketik tangan tiap bulan. Yang berubah di layar: menu Manpower Planning mendapat kolom Aktual, Selisih, dan Deadline di samping Rencana yang sudah ada, dengan pengelompokan Divisi lalu Departemen lalu Posisi, beserta tombol unduh Excel. Rencana cukup diisi sekali di awal tahun dan direvisi hanya bila berubah; bulan yang tak direvisi otomatis mengikuti angka bulan sebelumnya.

Yang terdampak: HRD dan staf rekrutmen berhenti menghitung jumlah karyawan manual tiap bulan. Direktur ikut melihat layarnya. Kepala departemen lain tidak.

**Yang TIDAK dijanjikan, dan ini bagian terpenting.** Angka bulan yang sudah lewat belum bisa dipercaya sampai satu hal dibereskan lebih dulu: per 21 September 2026 ada 35 akun karyawan non-aktif di produksi, tetapi hanya 11 yang punya catatan keluar bertanggal. Dua puluh empat orang dinonaktifkan tanpa melewati menu Resign, jadi sistem tidak tahu mereka berhenti bulan apa. Akibatnya, bila bulan lampau dihitung hari ini, jumlah karyawan Juni terbaca 188 padahal lembar HRD menulis 158, dan selisihnya justru membuat tim rekrutmen tampak lebih baik daripada kenyataan. Karena angka ini dipakai menilai kerja tim rekrutmen, jejak keluar itu diperbaiki dulu, baru bulan lampau dibuka. Bulan berjalan tetap bisa dipercaya sejak hari pertama.

Besaran kerja: tiga bagian berurutan. Merapikan jejak keluar dan membuat master Divisi lebih dulu, lalu layar Aktual vs Rencana untuk bulan berjalan, lalu riwayat bulan lampau. Bagian pertama menyentuh data produksi dan dikerjakan manusia, bukan otomatis.

## Deskripsi

*Kolom Actual pada lembar MPP dihitung sistem dari data karyawan, bukan diketik HRD. Rencana MPP mendapat sumbu waktu berupa bulan berlaku, bukan satu angka per tahun. Divisi lahir sebagai master data tersendiri supaya bisa dipakai modul mana pun. Riwayat bulan lampau baru dibuka setelah setiap penonaktifan karyawan punya tanggal, sebab angka ini menilai orang.*

- **Status**: 🟡 **Diusulkan**, disetujui user 2026-09-21, kode belum ada.
- **Path di repo**: `bip-erp/services/employee/headcount_periode.go` (baru) · `bip-erp/services/employee/master_divisi.go` (baru) · `bip-erp/shared-library/models/employee/divisi.go` (baru) · `bip-erp/services/recruitment/models_mpp.go` (sumbu bulan) · `bip-erp/services/recruitment/mpp_actual.go` (baru) · `erp-frontend/src/app/(main)/hris/recruitment/manpower-plans/page.tsx` · `erp-frontend/src/features/hris/recruitment/mpp/` (baru: tabel aktual vs rencana)
- **Tanggal**: 2026-09-21

## Context

HRD memelihara lembar "ACTUAL VS PLANNING MPP PERIODE 2026" di luar ERP: bertingkat Divisi lalu Departemen lalu Posisi, per bulan berkolom Actual, Planning, Gap, Keterangan, dan Deadline, dengan subtotal per departemen. Kolom Actual-nya **diketik manual dari data HRIS**, jadi orang menghitung ulang angka yang sudah dimiliki sistem. Keputusan yang diambil dari lembar itu, menurut pemilik prosesnya, adalah **menilai kerja tim rekrutmen**. Itu menaikkan taruhannya: angka yang menggerakkan penilaian orang menuntut gerbang yang berbeda dari angka untuk rapat mingguan.

Gap-nya sudah tercatat sebagai TBD di [[HRIS - Recruitment]] §Rencana Tenaga Kerja (MPP), dan ADR ini yang menutupnya.

**Yang sudah ada, dan ternyata lebih banyak daripada dugaan awal.**

1. **Planning sudah tersimpan**, per (departemen, posisi, tahun) di `services/recruitment/models_mpp.go:25-33`, lengkap dengan layar, CRUD, dan gerbang tulis `recruitment.manpower_plan_manage` ([[ADR - 0092 Rekrutmen Lintas Perusahaan lewat Paket Izin]]).
2. **Actual per (departemen, posisi) sudah dihitung sistem** hari ini: `GET /data-type/headcount?department=&position=` (`services/employee/main.go:228-262`) memotong `system_authentication.is_active` dengan `work_data`, dan sudah dipakai mengisi "Jumlah Sekarang" di form requisition. Jadi kolom Actual bukan fitur baru, ia hanya belum pernah ditampilkan berdampingan dengan Rencana.
3. **Jabatan seseorang pada periode lampau sudah bisa direkonstruksi** lewat `posisiSaatPeriode` (`services/employee/kpi_posisi_periode.go:38-108`), memakai snapshot departemen dan posisi asal di `employee_movement` (`shared-library/models/employee/movement.go:139-184`).
4. **Riwayat headcount per bulan tingkat perusahaan** sudah ada di `services/employee/turnover_riwayat.go`, maksimal enam bulan.
5. **Pengelompokan HRGA sudah ada sebagai data**, bukan perlu dibuat: `master_department.supervision_label` bernilai `HRGA` pada departemen Human Resource, dan itu pula yang dipakai KPI. HRD mengonfirmasi lembar memang menggabungkan Human Resource dan General Affair.

**Yang diukur di produksi 2026-09-21, dan yang membalik rancangan awal.**

| Yang diukur | Angka |
|---|---|
| Karyawan aktif hari ini (akun aktif dipotong `work_data`) | 180 dari 182 akun aktif |
| Rekonstruksi akhir Mei / Juni / Juli / Agustus / September | 177 / 188 / 203 / 202 / 204 |
| Lembar HRD Mei / Juni | 162 / 158 |
| Akun non-aktif | 35 |
| Catatan resign berstatus `applied` | 11 |
| Baris MPP tahun 2026 | 6 baris, seluruhnya lahir dari resign |
| Kandidat berstatus Buffer | 0 |

Dua puluh empat penonaktifan **tidak punya tanggal keluar**. Rekonstruksi mundur (`headcountAwal`, `turnover.go:72-78`) bekerja dari karyawan aktif sekarang ditambah yang keluar dikurangi yang masuk, jadi orang tanpa catatan keluar dihitung seolah masih bekerja sepanjang tahun. Itu sebabnya angka Juni sistem 188 sementara lembar HRD 158. [[HRIS - Attrition]] sudah memperingatkan kebutaan ini; ADR ini mengukurnya.

Kebutaan kedua yang lebih halus: `work_data.department` dan `position` **ditimpa** saat mutasi diterapkan, jadi membagi headcount lampau per posisi tanpa membaca `employee_movement` akan menempelkan jabatan hari ini ke bulan lampau, menggeser dua sel sekaligus.

**Kepemilikan data.** Fakta "siapa karyawan aktif, di departemen dan posisi apa" dimiliki employee-service ([[REF - Kepemilikan Data]]). Recruitment tidak boleh menyalinnya; ia membacanya. Aturan yang sama sudah dipakai sumber KPI `rekrutmen` yang live 2026-09-21.

**Divisi belum ada di mana pun.** Tidak di `master_department`, tidak di frontend. HRD meminta Divisi dibuat sebagai master data supaya bisa dipakai modul mana pun, bukan sebagai daftar tetap di dalam satu layar.

## Decision

1. **Actual dihitung sistem, tidak pernah diketik.** Definisinya: jumlah karyawan aktif pada **hari terakhir bulan** itu, per (perusahaan, departemen, posisi). Sumbernya employee-service. Recruitment membacanya lewat rute berkunci layanan, pola yang sama dengan bahan KPI rekrutmen ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]).

2. **Bulan lampau memakai jabatan saat itu, bukan jabatan hari ini.** Perhitungan wajib melewati `employee_movement` (lihat `posisiSaatPeriode`), bukan `work_data` apa adanya.

3. **Riwayat bulan lampau TIDAK dibuka sebelum jejak keluar bertanggal.** Selama masih ada akun non-aktif tanpa catatan resign, layar hanya menyajikan **bulan berjalan**, dan bulan lampau ditandai "belum dapat dihitung" beserta alasannya, bukan diisi angka yang keliru. Ambangnya eksplisit: nol akun non-aktif tanpa tanggal keluar untuk perusahaan yang dilihat.

4. **Penonaktifan karyawan wajib lewat menu Resign.** Penonaktifan langsung oleh IT tanpa catatan keluar diperlakukan sebagai kesalahan data, bukan jalur yang sah. Dua puluh empat kejadian yang sudah terjadi ditambal sebagai data, dengan tanggal dari HRD.

5. **Rencana MPP mendapat bulan berlaku**, bukan dua belas baris per posisi. Satu baris rencana berlaku sejak bulan tertentu sampai digantikan baris berikutnya, sehingga HRD mengisi sekali setahun dan merevisi hanya saat berubah. Bulan yang tak direvisi mewarisi angka bulan sebelumnya.

6. **Divisi jadi master data tersendiri** (`master_divisi`), dengan departemen menunjuk divisinya. Bukan daftar tetap di dalam kode, bukan kolom teks bebas.

7. **Nama departemen mengikuti sistem, bukan lembar.** HRGA tetap ditampilkan sebagai pengelompokan lewat `supervision_label` yang sudah ada, bukan sebagai departemen baru.

8. **Gerbangnya HRD dan Direktur.** Layar Aktual vs Rencana dibatasi pemegang izin penyusun MPP ditambah Direktur. Ini lebih sempit daripada tabel MPP sekarang yang terbaca semua pemegang `recruitment.view`.

9. **Selisih (Gap) tidak menjadi metrik KPI di ADR ini.** Sumber KPI `rekrutmen` yang sudah live tetap apa adanya. Memasang metrik baru dari Gap adalah keputusan tersendiri, dan tidak sah sebelum keputusan 3 dan 4 terpenuhi.

## Consequences

**Yang membaik.** HRD berhenti menghitung headcount manual tiap bulan. Angka yang dipakai menilai tim rekrutmen lahir dari satu sumber yang sama dengan layar, bukan dari ketikan yang tak bisa ditelusuri. Divisi jadi tersedia untuk modul lain, misalnya laporan dan dashboard.

**Ongkos dan risiko yang diterima sadar.**

- **Angka bulan lampau tertunda.** Layar sengaja menolak menampilkannya sampai jejak keluar bersih. Itu terasa seperti fitur setengah, dan memang disengaja: angka yang salah lebih mahal daripada kolom yang kosong beralasan.
- **Penambalan 24 catatan keluar menyentuh data produksi**, dikerjakan manusia dengan tanggal dari HRD, bukan ditebak sistem. Tanpa tanggal yang benar, penambalan hanya memindahkan kesalahan.
- **Selisih terhadap lembar HRD belum tentu hilang.** Setelah jejak keluar bersih, angka hari ini tetap 182 sementara lembar Juni menulis 158. Bila selisih masih ada, penyebab berikutnya harus dicari ke definisi karyawan yang dipakai HRD, bukan ditutup dengan penyesuaian angka.
- **MPP harus benar-benar diisi.** Hari ini 6 baris untuk 2026, sementara lembar memuat sekitar 174. Kolom Rencana akan kosong untuk hampir semua posisi sampai HRD mengisinya, dan itu pekerjaan data, bukan pekerjaan kode.
- **Beban baca bertambah** di employee-service: agregasi per (departemen, posisi) untuk satu bulan, dipanggil tiap layar dibuka. Batas waktu dan cache mengikuti pola bahan KPI rekrutmen.

**Konsekuensi deploy.** Rute baru berkunci layanan berarti env baru di dua blok compose dan `docker compose up -d --force-recreate` untuk keduanya, bukan `restart`; urutannya employee-service lebih dulu, lalu recruitment-service, lalu frontend. Master Divisi menambah koleksi baru beserta seed awal. Tidak ada kategori inbox baru.

## Dokumen Terkait

- [[HRIS - Recruitment]] §Rencana Tenaga Kerja (MPP) — cara kerja MPP dan Posisi Kosong
- [[HRIS - Organization Structure]] — master departemen, jenjang jabatan, dan kini Divisi
- [[HRIS - Attrition]] — kebutaan rekonstruksi terhadap penonaktifan di luar menu Resign
- [[REF - Kepemilikan Data]] — pemilik fakta karyawan aktif, departemen, dan posisi
- [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] · [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] · [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]] · [[ADR - 0092 Rekrutmen Lintas Perusahaan lewat Paket Izin]]
- [[ANALISA - Actual vs Planning MPP]] — pecahan tugasnya
