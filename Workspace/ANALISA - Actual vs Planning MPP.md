# ANALISA - Actual vs Planning MPP

Pecahan kerja dari [[ADR - 0113 Actual vs Planning MPP Dihitung Sistem per Bulan, Berpijak pada Jejak Keluar Bertanggal]] (disetujui user 2026-09-21). Tiap butir cukup jelas untuk dilempar ke `/start-task`. Urutannya mengikat: T1 dan T2 mendahului sisanya, dan T5 tidak sah sebelum T1 tuntas.

## T1. Jejak keluar bertanggal (DATA, dikerjakan manusia)

**Kenapa pertama.** Selama masih ada akun non-aktif tanpa catatan keluar, seluruh angka bulan lampau salah, dan angkanya menilai orang.

- Ukur ulang: akun `is_active:false` dibanding catatan resign berstatus `applied` (per 2026-09-21: 35 lawan 11).
- HRD menyediakan tanggal keluar untuk 24 orang yang tak punya catatan. Tanggal dari HRD, bukan tebakan sistem.
- Tambal sebagai catatan resign lewat menu, atau skrip bergerbang dengan backup dan dry run bila terlalu banyak. **Tulis produksi dijalankan manusia.**
- Selesai bila: nol akun non-aktif tanpa tanggal keluar untuk perusahaan BIP, dan rekonstruksi akhir Juni mendekati angka lembar HRD. Bila masih meleset, hentikan dan cari sebab berikutnya di definisi karyawan versi HRD, jangan menyesuaikan angka.

## T2. Master Divisi — 🔜 berkode, belum merge & belum deploy

Branch: bip-erp `feat/employee-master-divisi` · erp-frontend `feat/hris-master-divisi` (2026-09-21). Rencana & gerbang verifikasinya: `.task-plans/2026-09-21-master-divisi.md`.

- Koleksi `master_divisi` di employee-service beserta CRUD dan layar master data, mengikuti pola master departemen yang sudah ada. ✅ Ada.
- Departemen menunjuk divisinya lewat `master_department.divisi_key`. ✅ Ada.
- Isi awal: Commercial, Operational, Supporting, Management. ✅ Di-seed, **tanpa pemetaan** — keputusan user 2026-09-21: memetakan departemen ke divisi pekerjaan HRD, bukan tebakan sistem. Departemen tanpa divisi tampil bertanda "Belum berdivisi" beserta hitungannya, jadi sisa pekerjaan menagih dirinya sendiri.
- ⚠️ **Koreksi angka**: bukan "12 departemen BIP". Diukur PROD 2026-09-21 ada **13 dokumen** `master_department` — 12 BIP + 1 ELT (`pct` Percetakan, 13 karyawan aktif) — dan departemen `printing` milik BIP punya **nol** karyawan aktif. Karena itu divisi ter-scope **per perusahaan**, bukan satu daftar global.
- Dipakai lintas modul: dibaca lewat `GET /data-type/divisi`, jalur yang sudah dipakai modul lain (`useDataTypes`), bukan endpoint baca baru. ✅ Ada.
- **Selesai bila**: tiap departemen aktif punya divisi (pekerjaan HRD, belum), dan daftar divisi bisa dibaca modul lain lewat master data (✅ sudah, menunggu deploy).

Dua keputusan yang diambil saat mengerjakannya dan layak diingat:

- **Nama `divisi` dipertahankan** walau kata itu sudah dipakai untuk arti lain di kode (`common.ReachDivision` dan `space.division`, keduanya berisi NAMA DEPARTEMEN), karena itulah istilah HRD. Perbedaannya ditulis di kode dan di [[REF - Kepemilikan Data]] supaya tak jadi arti ketiga yang menyesatkan.
- **Seed hanya mengisi perusahaan yang belum punya satu pun divisi.** Bentuk pertamanya (upsert per-key) menghidupkan kembali divisi yang sengaja dihapus HRD tiap service naik — tombol Hapus yang dibatalkan sendiri oleh deploy berikutnya, tanpa galat.

## T3. Perhitungan Actual per periode di employee-service — 🔜 berkode, belum merge & belum deploy

Branch: bip-erp `feat/employee-headcount-periode` (2026-09-21). Rencana & gerbang verifikasinya: `.task-plans/2026-09-21-headcount-periode.md`.

- Fungsi dan rute agregat: jumlah karyawan aktif pada akhir bulan, per (perusahaan, departemen, posisi). ✅ Ada (`GET /kpi/headcount-periode`).
- Bulan berjalan memakai status akun; bulan lampau memakai `employee_movement` lewat pola `posisiSaatPeriode`, bukan `work_data` apa adanya. ✅ Ada.
- Menolak menjawab bulan lampau selama T1 belum tuntas, dengan alasan yang terbaca, bukan angka. ✅ Ada — 200 ber-`dapat_dihitung:false`, **tanpa** `baris` dan `total` sama sekali.
- Rute berkunci layanan (pola bahan KPI rekrutmen), bukan bersandar pada prefix. ✅ Ada (`EMPLOYEE_SERVICE_KEY`).
- Test wajib: karyawan yang mutasi di tengah tahun tidak menggeser dua sel sekaligus; karyawan non-aktif tanpa tanggal keluar membuat bulan lampau ditolak, bukan dihitung. ✅ Keduanya ada.
- **Selesai bila**: dipanggil sekali lewat jaringan docker dan membalas bentuk kontraknya, lalu T5 memakainya. Bulan lampau **masih akan menolak** sampai T1 dan T6 (data) tuntas, dan itu memang yang diinginkan.

Empat keputusan yang diambil saat mengerjakannya dan layak diingat:

- **Metode selisih tidak bisa dipakai sama sekali, dan itu ditemukan saat `/plan`, bukan saat kode.** `/resign/summary/riwayat` merekonstruksi dengan mengurangi yang keluar dan menambah yang masuk; metode itu sudah ditolak untuk cakupan di bawah perusahaan, dikunci uji, karena mutasi antar departemen terhitung sebagai pengunduran diri. T3 karena itu merekonstruksi **per orang**. ⚠️ Konsekuensinya angka T3 tak akan sama persis dengan endpoint itu, dan pengalihannya ke mesin T3 jadi **PR terpisah** supaya perubahan angka yang sudah dilihat HR tak menyelinap bersama fitur baru.
- **Gerbang bulan lampau dibuat LINTAS TENANT**, bukan per perusahaan. Cakupan gerbang wajib sama dengan cakupan yang dihitung; gerbang yang cuma melihat `work_data.company_id` hari ini akan berkata "bersih" untuk orang yang pada bulan itu milik perusahaan lain. Ongkosnya: kebersihan data satu tenant menyandera tenant lain.
- **Rehire hampir lolos.** Penanda "sudah keluar" semula mengeluarkan siapa pun yang punya catatan resign berlaku sebelum akhir periode, sehingga orang yang direkrut ulang lenyap dari setiap bulan lampau sesudah kepergian pertamanya — padahal bulan berjalan tetap menghitungnya, dan gerbang backlog tak melihatnya karena akunnya aktif. Aturan penjaganya ternyata **sudah ada** di `kpi_sumber_rekrutmen.go`; satu fakta yang hidup di satu tempat dan hilang di tempat kedua.
- **`company_id` yang salah ketik semula dijawab nol yang meyakinkan.** Kueri gerbang mencocokkan persis, jadi perusahaan tak dikenal menghasilkan backlog kosong, gerbang lolos diam-diam, dan responsnya `dapat_dihitung:true` dengan `total:0` — gerbangnya tidak menyala justru karena perusahaannya salah. Kini divalidasi ke master perusahaan dan dibalas 400.

## T4. Rencana MPP bersumbu bulan

- Baris rencana mendapat bulan berlaku; berlaku sampai digantikan baris berikutnya. HRD mengisi sekali setahun, merevisi saat berubah.
- Tambah Keterangan dan Deadline per baris.
- Migrasi baris 2026 yang sudah ada (6 baris) ke bentuk baru tanpa mengubah artinya.
- Jaga agar cakupan buffer yang sudah live tidak berubah angkanya: penyebutnya tetap rencana yang berlaku.

## T5. Layar Aktual vs Rencana

- Kolom Aktual, Rencana, Selisih, Keterangan, Deadline; kelompok Divisi lalu Departemen lalu Posisi dengan subtotal, plus baris JUMLAH ALL TEAM.
- HRGA tampil sebagai pengelompokan lewat `supervision_label` yang sudah ada, bukan departemen baru.
- Gerbang: pemegang izin penyusun MPP ditambah Direktur. Lebih sempit daripada tabel MPP sekarang.
- Ekspor Excel (halaman MPP sekarang belum punya).
- Bulan lampau tampil sebagai keadaan "belum dapat dihitung" beserta alasannya selama T1 belum tuntas.

## T6. Isi MPP 2026 yang sebenarnya (DATA, HRD)

- Hari ini 6 baris untuk 2026, lembar HRD memuat sekitar 174.
- Tanpa ini, kolom Rencana kosong untuk hampir semua posisi dan cakupan buffer tetap 0%.

## Di luar lingkup

- **Metrik KPI baru dari Selisih.** Sumber KPI `rekrutmen` yang live 2026-09-21 tetap apa adanya; memasang metrik baru adalah keputusan tersendiri dan tidak sah sebelum T1 tuntas.
- **Memperbaiki pipeline rekrutmen** (kandidat lewat lowongan, status Buffer terisi). Itu sebab angka KPI rekrutmen 0%, dan ditangani terpisah dari lembar ini.
