## Deskripsi

*Posisi yang seluruh metrik KPI-nya bersumber otomatis dibekukan jadi `kpi_score` oleh sistem pada tanggal 10 bulan berikutnya, tanpa menunggu supervisor menekan Simpan. Bulan berjalan ikut dihitung dan ditampilkan hidup sampai tanggal itu. Mengubah siapa yang bertanggung jawab atas sebuah skor, karena itu ditulis sebagai ADR.*

- **Status**: ⚠️ **Diputuskan 2026-08-20, kode selesai, BELUM merge dan BELUM deploy.** Branch `feat/kpi-skor-otomatis` (bip-erp) dan `feat/kpi-bulan-berjalan` (erp-frontend).
- **Ruang lingkup**: `kpi_score` dan `kpi_template` di [[Microservices - Employee Service]]. Tidak menyentuh `POST /kpi` (jalur manusia).

## Context

Otomasi KPI selama ini **hanya menghitung usulan**. Nilainya dihitung ulang tiap kali layar dibuka dan tidak pernah ditulis ke mana pun. Satu-satunya penulis `kpi_score` adalah `POST /kpi`, yaitu tombol Simpan di modal Score KPI. Satu-satunya cron KPI adalah `cronReminderKPI`, yang tiap tanggal 1 pukul 08.45 WIB menyiarkan "Yuk, segera isi KPI bulan lalu" — sistemnya sendiri mengakui siklus M+1 dan tidak menyimpan apa pun.

Diukur langsung ke `employee_db` produksi **2026-08-20**:

| Yang diukur | Angka |
|---|---|
| Dokumen `kpi_score` | 569, periode terakhir **2026-07** (163 dok, rata-rata 76,21) |
| Periode `2026-08` | **nol dokumen** (regex longgar `^2026-0?8` juga nol) |
| Metrik ber-`auto` | **24** dari 362 metrik di 83 template |
| Karyawan aktif | 183 |
| Di posisi ber-otomasi | 38 |
| Di posisi otomasi **PENUH** (bobot 1,00) | **30** — ICC Beauty Hacks 19, ICC Kyura 11 |

Akibatnya tiga puluh orang tercatat "belum dinilai" selamanya walau skornya sudah sepenuhnya ditentukan data, dan kelalaian itu menular ke KPI SPV HRD yang berbunyi "seluruh karyawan berskor minimal 70". Bagi ICC, manusia yang menekan "Pakai usulan" lalu Simpan tidak menambahkan apa pun; ia upacara yang gagalnya senyap.

> Catatan: [[HRIS - Otomasi Skor KPI]] masih menulis **3** metrik otomatis (keadaan 2026-08-07). Angka sebenarnya 24. Dokumen itu perlu disegarkan.

## Decision

**1. Sistem membekukan skor untuk posisi yang bobot otomasinya PENUH.** Cron harian 02:00 WIB, aktif sejak tanggal `TanggalBekuKPI = 10` bulan M+1, memfinalisasi periode M. Gerbangnya empat, dan seluruhnya harus lolos:

- karyawan belum punya `kpi_score` periode itu;
- templatenya tidak ambigu (satu posisi bisa punya beberapa template);
- **seluruh** metrik templatenya ber-`auto` — satu metrik manual membatalkan seluruhnya;
- **seluruh** metriknya benar-benar menghasilkan angka pada periode itu.

Yang tidak lolos **dilewati utuh** dan dicoba lagi esok hari, tidak dibekukan sebagian.

**2. Bulan berjalan ikut dihitung, hidup, sampai dibekukan.** `GET /kpi?sertakan_otomasi=1` mengikutkan skor yang sudah bisa dihitung penuh tetapi belum dibekukan. Bawaannya mati, dan ditolak untuk periode yang sudah tutup.

**3. Supervisor tetap boleh menimpa** lewat `POST /kpi` biasa. Jejaknya sudah ada tanpa field baru: `dinilai_oleh` berisi `OTOMASI` untuk yang dibekukan sistem, dan [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] sudah menstempel `auto_value` ke snapshot sehingga "penilai menimpa angka mesin" terjawab dari `value != auto_value`.

**Tanggal 10 dipilih dari data, bukan selera.** Pengisian manual memang lambat: periode Juni masih **bertambah 5 dokumen pada 19 Agustus**, tujuh minggu sesudah bulannya berakhir. Membekukan tanggal 1 mengunci bulan itu saat hampir tak seorang pun sempat mengisi.

## Consequences

**Yang berubah, dan diterima sadar:**

- **Tiga puluh orang tidak lagi dinilai manusia.** Mereka hilang dari antrean penilaian setelah beku, dan supervisor yang ingin menimpa harus tahu sendiri bahwa ia boleh.
- **`kpi_score` punya penulis kedua.** Sebelumnya hanya `POST /kpi`. Setiap pembacaan yang mengasumsikan "ada dokumen berarti ada manusia yang menilainya" berhenti benar.
- **Ada efek berantai yang menguntungkan.** Metrik `Performance Monitoring Team` milik BeautyHacks dan Kyura Supervisor memakai `skor_tim` bercakupan departemen. Begitu 30 ICC tersimpan, metrik itu langsung bisa dihitung — padahal justru itu yang selama ini macet menunggu anggotanya dinilai. Jebakan urutan yang tercatat di [[HRIS - Otomasi Skor KPI]] sebagai "tak bisa diperbaiki" jadi jauh lebih jarang menggigit.
- **Titik terbaru di bagan tren lahir sebagai rata-rata ICC** lalu bergeser jadi rata-rata perusahaan sepanjang bulan berikutnya. Penyebut "x dari y" karena itu jadi jauh lebih penting daripada sebelumnya.

**Yang tidak berubah:**

- 145 orang tanpa otomasi tetap dinilai manusia, tanpa perubahan apa pun.
- Posisi yang otomasinya **sebagian** (9 template, termasuk BeautyHacks dan Kyura Supervisor pada 0,90) sengaja **tidak** difinalisasi. Membekukan skor berkomponen bolong lebih buruk daripada tidak membekukan.
- Rata-rata bulanan memang **tidak pernah** disimpan; ia dihitung ulang tiap `GET /kpi`. Jadi sejarah rata-rata sudah bergerak sejak dulu, terbukti dari Juni yang bergeser 76,34 → 75,64 dalam 24 jam. Yang beku hanyalah skor per orang.

**Yang sengaja tidak dilakukan:**

- **Cakupan otomasi se-perusahaan.** KPI SPV HRD berbunyi "seluruh karyawan", sementara `KPIAutoScopes` hanya mengenal `department`, `team`, `individu`, `tim_icc`. Metrik itu tetap diisi manusia.
- **Kewajiban mengisi alasan saat menimpa.** `value != auto_value` sudah cukup jadi jejak.

**Risiko yang dijaga kode, bukan oleh kebiasaan:**

- Jabatan yang dipakai adalah jabatan **pada periode itu** (`posisiKPIUntukPenilaian`), bukan jabatan hari ini. Cron dijadwalkan 02:00 justru supaya berjalan **sesudah** `cronTerapkanMutasi` pukul 00:15.
- Penulisan memakai `$setOnInsert`, bukan baca-lalu-tulis, sehingga supervisor yang menekan Simpan di sela-sela tidak tertimpa. Ini sekaligus yang membuat finalisasi idempoten.
- Perusahaan tiap orang diambil dari dirinya sendiri (`resolveCompanyID`), bukan dari pemanggil, sesuai [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]].

## Dokumen Terkait

- [[HRIS - Otomasi Skor KPI]]
- [[HRIS - Key Performance Index]]
- [[Microservices - Employee Service]]
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]
- [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]
