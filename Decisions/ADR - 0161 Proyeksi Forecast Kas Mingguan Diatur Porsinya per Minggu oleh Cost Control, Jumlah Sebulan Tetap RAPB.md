# ADR - 0161 Proyeksi Forecast Kas Mingguan Diatur Porsinya per Minggu oleh Cost Control, Jumlah Sebulan Tetap RAPB

> **Status**: 🟢 Diterima, 2026-10-09, oleh Azzerith (aturan persetujuan ADR di [[ADR - 0151 Issue Siap Dikerjakan Agent Bila Keputusannya Bisa Ditunjuk, Ditandai Manusia]]). Asal keputusan: permintaan atasan Finance yang disampaikan Azzerith, bentuknya dipilih di sesi analisa 2026-10-09. 🟡 **Kodenya belum ada.**

## Untuk Manajemen

**Apa yang berubah di layar.** Di tab **Forecast Mingguan** halaman Anggaran & Cost Control, angka Proyeksi tiap minggu bisa diatur sendiri oleh Cost Control, tidak lagi selalu dibagi rata menurut jumlah hari. Minggu yang memang berat pengeluarannya bisa dibesarkan dan minggu lain dikecilkan. Di bawah tabel muncul **riwayat perubahan**: siapa yang mengubah, kapan, dan angka mana berubah dari berapa menjadi berapa.

Aturan yang dijaga sistem:

- Jumlah proyeksi sebulan **harus tetap sama** dengan anggaran bulan itu. Yang diatur hanya pembagiannya antar-minggu.
- Minggu yang **sudah mulai atau sudah lewat terkunci** dan tidak bisa diubah lagi.
- Tiap minggu yang belum mulai boleh diubah **paling banyak 2 kali**.
- Bulan yang tidak diatur tetap memakai pembagian menurut jumlah hari seperti sekarang.

**Siapa yang terdampak.** Cost Control (yang mengatur), Supervisor Finance dan pembaca halaman Anggaran & Cost Control (yang melihat proyeksi dan riwayatnya).

**Apa yang TIDAK dijanjikan.**

- **Skor KPI akhir bulan tidak berubah karena fitur ini.** KPI "akurasi forecast kas" dihitung dari total sebulan, dan total sebulan tidak berubah saat porsinya digeser antar-minggu. Yang membaik adalah ketepatan angka **per minggu** di tabel, bukan nilai KPI.
- Tidak ada pengaturan per akun: semua akun mengikuti porsi minggu yang sama.
- Total anggaran tidak bisa diubah dari tab ini; itu tetap lewat tab Anggaran Bulanan.
- Tidak ada persetujuan atasan atas tiap perubahan; pengamannya kunci minggu, batas 2 kali, dan riwayat.
- Bila tinggal satu minggu yang belum mulai, minggu itu tidak bisa diubah lagi, karena tidak ada minggu lain untuk digeser.

**Perkiraan besaran kerja.** Sedang: satu pekerjaan backend dan satu pekerjaan layar, backend naik lebih dulu.

## Deskripsi

*Proyeksi mingguan pada Forecast Kas Mingguan selama ini diturunkan sepenuhnya dari anggaran RAPB yang dibagi menurut jumlah hari, tanpa satu sel pun yang diketik orang. Pengeluaran kas nyatanya tidak merata tiap minggu, sehingga pembagian itu hampir pasti meleset per minggunya. Keputusan ini mengizinkan Cost Control mengatur porsi tiap minggu dengan jumlah sebulan tetap sama dengan RAPB, menetapkan kunci dan batas ubahnya, dan mewajibkan riwayat perubahan. Ia membalik sebagian keputusan sebelumnya ("tidak diketik siapa pun") tanpa mengubah rumus maupun cakupan KPI Cost Control #4.*

- **Path di repo** (yang **akan** disentuh): `bip-erp/services/integration/internal/usecase/laporan_mingguan.go` + `minggu_periode.go` · `bip-erp/services/integration/internal/domain/entity/anggaran_mingguan.go` · entity + repo porsi mingguan dan riwayatnya di `bip-erp/services/integration/internal/` (baru) · `bip-erp/services/integration/internal/interface/http/anggaran_mingguan_handler.go` + pendaftaran rute di `main.go` + `finance_baca_gate.go` · `bip-erp/services/assistant/internal/alat/akt_anggaran_mingguan.go` (teks) · `erp-frontend/src/features/finance/anggaran/components/tab-forecast-mingguan.tsx` + form atur proyeksi (baru) + tabel riwayat (baru)
- **Tanggal**: 2026-10-09
- **Terkait**: [[Finance - Serapan Anggaran dan Cost Control]] (cara kerja di layar) · [[Finance - Rancangan Finance Service]] (asal aturan pro-rata dan rumus akurasi) · [[ADR - 0159 Serapan Anggaran Dibaca dari Pengajuan sebagai Bagian dari Terpakai, Rute Tulis Anggaran Digerbang Izin Sendiri]] (K7 dan K9) · [[HRIS - Matriks KPI per Departemen]]

## Context

- **Yang berlaku sekarang** (kode `bip-erp` di `main`, dibaca 2026-10-09): proyeksi akun × minggu = anggaran bulanan akun itu dibagi menurut jumlah hari tiap minggu; minggu = potongan 7 hari dari tanggal 1. Tidak ada jalur isian. Ini ditulis sebagai keputusan di [[Finance - Rancangan Finance Service]] ("Proyeksinya diturunkan dari RAPB, tidak diketik siapa pun") dan dikukuhkan [[ADR - 0159 Serapan Anggaran Dibaca dari Pengajuan sebagai Bagian dari Terpakai, Rute Tulis Anggaran Digerbang Izin Sendiri]] K7 ("otomatis, tanpa isian"). ADR 0159 sendiri masih 🟡 Diusulkan, jadi keputusan ini berdiri di atas keputusan yang kodenya sudah merged tetapi belum berstatus Diterima.
- **Kebutuhannya**: pengeluaran kas tidak merata tiap minggu. Rencana kas disusun staf Cost Control dengan angka dari Accurate. Yang diminta manajemen adalah "proyeksi bisa diedit manual"; kebutuhannya adalah porsi tiap minggu mengikuti jadwal bayar yang sebenarnya.
- **Akurasi dan KPI dihitung dari TOTAL sebulan**, bukan rata-rata akurasi mingguan ([[Finance - Rancangan Finance Service]]; endpoint ringkas KPI mengirim total bulan). Bahan KPI Cost Control #4 dan metrik SPV Finance yang memakai sumber yang sama ([[HRIS - Matriks KPI per Departemen]]). Akibatnya menggeser porsi antar-minggu dengan total tetap **tidak menggerakkan angka KPI akhir bulan**.
- **Pemegang KPI adalah orang yang akan mengatur proyeksinya sendiri** (posisi Cost Control, [[Finance - FAT Persona]]). Itu alasan kunci, batas ubah, dan riwayat dijadikan bagian keputusan, bukan pelengkap.
- **Layar punya dua tabel** dari satu respons: ringkasan per minggu dan rincian akun × minggu. Angka yang diketik orang adalah total per minggu, jadi harus ada aturan menurunkannya ke rincian per akun supaya dua tabel tidak saling menyangkal.
- **Yang sudah ada dan dipakai ulang**: izin tulis `finance.anggaran.kelola` beserta paket `finance_anggaran` (ADR 0159 K9); pola jejak perubahan sebelum → sesudah yang menggagalkan aksi bila jejaknya gagal tercatat (finance-service); pembagian minggu yang sudah ada. **Yang belum ada di repo**: batas jumlah perubahan dan kunci berdasarkan tanggal mulai (dicari dengan `git grep` atas `services` dan `shared-library`, nihil).
- **Tidak diukur**: isi data produksi. Keberadaan anggaran Oktober 2026 diketahui dari layar produksi yang ditunjukkan pemohon; angka rupiahnya sengaja tidak disalin ke vault.

## Decision

| # | Keputusan |
|---|---|
| K1 | Proyeksi mingguan **boleh diatur orang**. Ini membalik "tidak diketik siapa pun" di [[Finance - Rancangan Finance Service]] dan bagian "tanpa isian" pada ADR 0159 K7. Rumus akurasi, cakupan 6 akun kas-keluar, dan cara KPI #4 dihitung **tidak berubah**. |
| K2 | Yang diketik adalah **total rupiah per minggu** (seluruh akun kas-keluar digabung), bukan per akun. |
| K3 | **Jumlah seluruh minggu harus sama dengan anggaran RAPB kas-keluar bulan itu.** Simpan ditolak bila tidak sama. |
| K4 | Yang **disimpan adalah porsi tiap minggu** terhadap total bulan, satu set per periode (tahun, bulan), bukan nominalnya. Proyeksi akun × minggu = anggaran akun × porsi minggu itu, sehingga tabel rincian per akun selalu cocok dengan tabel ringkasan, dan RAPB tetap satu-satunya sumber angka anggaran. Sisa pembulatan tetap ditimpakan ke minggu terakhir. |
| K5 | Periode **tanpa** isian memakai pembagian menurut jumlah hari seperti sekarang (bawaan). |
| K6 | **Kunci**: sebuah minggu terkunci sejak hari pertamanya menurut WIB. Minggu yang sedang berjalan dan yang sudah lewat tidak bisa diubah. Karena itu pergeseran hanya terjadi antar-minggu yang belum mulai, dan jumlah minggu-minggu itu harus tetap. |
| K7 | **Batas ubah**: tiap minggu paling banyak **2 kali** diubah per periode. Sekali simpan menambah hitungan pada **tiap minggu yang angkanya berubah**. Minggu yang sudah 2 kali ditolak. |
| K8 | **Riwayat perubahan** wajib, hanya-tambah: siapa, kapan, dan per minggu angka sebelum → sesudah. Ditampilkan di bawah tabel Forecast Mingguan. Simpan **gagal** bila riwayatnya gagal tercatat. Hitungan K7 diturunkan dari riwayat ini, bukan disimpan sebagai angka kedua. |
| K9 | **Izin**: mengatur proyeksi memakai `finance.anggaran.kelola` yang sudah ada; membaca proyeksi dan riwayat memakai izin baca halaman (`finance.accounting.view`). Tidak ada izin baru. |
| K10 | Kunci, batas ubah, dan kesamaan jumlah **diputuskan backend**. Layar hanya menampilkan keadaan (terkunci, sisa kesempatan ubah) yang dikirim backend dan tidak menghitungnya sendiri. |
| K11 | **Unggah ulang RAPB di tengah bulan**: porsi yang tersimpan diterapkan ke anggaran baru untuk **semua** minggu, termasuk yang sudah terkunci. Nominal minggu terkunci boleh ikut bergeser; jumlah sebulan selalu sama dengan RAPB. Tidak ada potret nominal per minggu. *(Diputuskan Azzerith 2026-10-09.)* |
| K12 | **Bulan mendatang boleh diatur** sebelum bulannya mulai, selama anggaran bulan itu sudah diunggah. Bulan yang sudah lewat seluruhnya tidak bisa diatur (semua minggunya terkunci). *(Diputuskan Azzerith 2026-10-09.)* |
| K13 | **Tidak ada tombol kembalikan ke bawaan.** Kembali ke pembagian menurut jumlah hari dilakukan dengan mengetik ulang angkanya, dan itu terhitung sebagai perubahan biasa (K7). *(Diputuskan Azzerith 2026-10-09.)* |

Di luar cakupan: pengaturan per akun per minggu; mengubah rumus KPI menjadi rata-rata akurasi mingguan; persetujuan atasan per perubahan; mengubah total anggaran dari tab ini; pemicu manual penarikan realisasi.

## Consequences

**Yang membaik**

- Akurasi per minggu di tabel menjadi bermakna, karena proyeksinya mengikuti jadwal bayar.
- Dua tabel di layar tetap satu sumber (K4); unggah ulang RAPB tidak membuat isian jadi tidak sah.
- Setiap perubahan proyeksi bisa ditelusuri ke orang dan waktunya.

**Yang memburuk atau tetap terbuka**

- **Angka KPI akhir bulan tidak berubah** oleh fitur ini. Bila yang diharapkan manajemen adalah skor KPI membaik, itu keputusan lain (rumus KPI), dan harus dikatakan terang saat fitur diserahkan.
- Semua akun mengikuti porsi minggu yang sama, padahal jadwal bayar tiap akun bisa berbeda. Rincian per akun karena itu tetap perkiraan.
- **Turunan K6 + K7**: bila tinggal satu minggu yang belum mulai, atau pasangan gesernya sudah habis kesempatannya, minggu itu tidak bisa diubah lagi.
- Karena yang disimpan porsi, **unggah ulang RAPB sesudah bulan berjalan ikut mengubah nominal proyeksi minggu yang sudah terkunci**. Ini diterima sadar (K11).
- Teks alat asisten AI yang menyatakan "proyeksi = anggaran dibagi menurut jumlah hari" menjadi salah untuk periode yang diatur, dan harus diperbarui bersama backend.
- Kalimat di layar "tidak ada yang diisi di tab ini" harus diganti.

**Urutan deploy**

- Backend (integration-service, lalu assistant-service untuk teksnya) sebelum frontend. Layar lama tetap berjalan terhadap backend baru karena bentuk respons baca hanya bertambah.
- Satu koleksi baru di integration-service; tanpa env baru.
- Pemegang peran Cost Control harus sudah memegang paket `finance_anggaran` di produksi (prasyarat yang sama dengan ADR 0159).

**Kaitan dengan bip-erp#2865** (minggu yang belum selesai tidak dihitung): keduanya menyentuh penyusun laporan mingguan yang sama. Bila #2865 diterapkan, akurasi bulan berjalan dihitung dari minggu yang sudah selesai saja, dan di situ porsi mingguan **memang** memengaruhi angka tengah bulan; angka akhir bulan tetap tidak terpengaruh. Kerjakan berurutan, jangan paralel.

## Belum diputuskan

- **Nama pengubah di riwayat**: gateway hanya meneruskan id karyawan; nama disalin saat simpan atau diambil saat tampil. Diserahkan ke pelaksana backend, dicatat di PR.

## Dokumen Terkait

- [[Finance - Serapan Anggaran dan Cost Control]]
- [[Finance - Rancangan Finance Service]]
- [[Finance - FAT Persona]]
- [[HRIS - Matriks KPI per Departemen]]
- [[API - Integration Service]]
- [[CORE - RBAC dan Permission Set]]
- [[ADR - 0159 Serapan Anggaran Dibaca dari Pengajuan sebagai Bagian dari Terpakai, Rute Tulis Anggaran Digerbang Izin Sendiri]]
- [[ADR - 0151 Issue Siap Dikerjakan Agent Bila Keputusannya Bisa Ditunjuk, Ditandai Manusia]]
