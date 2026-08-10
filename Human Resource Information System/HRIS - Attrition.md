## Deskripsi

*Dashboard ini menampilkan seluruh attrition dari departemen internal yang mencakup karyawan yang masuk dan yang keluar*

- **Status**: ⚠️ Sebagian diimplementasikan — **catatan terminasi sudah live di produksi** (koleksi `employee_resign`, sejak 2026-08-05), dan **kartu turnover bulan berjalan ✅ live** di halaman Resign serta di Dashboard HRGA (verifikasi produksi 2026-08-10). Dashboard penuh (ikhtisar, detail per departemen, demografi) masih 🟡 konsep; contohnya masih spreadsheet.

[Contoh dari sistem ini](https://docs.google.com/spreadsheets/d/113QO_RgfYz7f6NTyfFWxZjN5YQp1GxyJ/edit?gid=340825885#gid=340825885)

## Fitur

- Dashboard
	- Ikhtisar segala hal yang sangat baik untuk pelaporan kepada stakeholder
- Detail
	- Tampilan attrition secara detail yang dilihat per departemen
- Demografi
	- Informasi detail mengenai gender, tipe, dan alasan terminasi (lookup tambahan yang mudah untuk kepergian per departemen)

## Kebutuhan

- [x] Master data karyawan (referensi lookup)
- [x] **Catatan terminasi (pembuatan dan terhubung ke data karyawan)** — koleksi `employee_resign` di [[Microservices - Employee Service]]: kategori, tanggal efektif, **alasan**, dan dokumen pendukung per karyawan. ✅ **live di produksi 2026-08-05** (PR bip-erp [#1009](https://github.com/bip-itteam-internal/bip-erp/pull/1009), erp-frontend [#803](https://github.com/bip-itteam-internal/erp-frontend/pull/803)). Lihat [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]].

Yang berubah dengan adanya catatan resign adalah **prasyarat datanya terpenuhi**: lima kategori terminasi dan alasan bebas per karyawan kini tersimpan, sehingga bagian Demografi ("gender, tipe, dan alasan terminasi") punya sumber. Sebelumnya `system_authentication.is_active` cuma boolean tanpa konteks, jadi pertanyaan "berapa yang keluar karena PHK bulan ini" tak bisa dijawab dari data mana pun.

⚠️ **Datanya masih kosong.** Verifikasi produksi 2026-08-06: `employee_resign` **0 dokumen**, akun aktif **183**. Angka apa pun yang dihitung darinya akan nol sampai HR benar-benar memakai menunya.

### Kartu turnover bulan berjalan — ✅ live di produksi

Cicilan pertama Dashboard: empat kartu di halaman Resign ([[APP - Web ERP]]) yang disuplai `GET /resign/summary`, kini juga tampil sebagai `KartuAmbang` di tab **Ringkasan** dan **HRD Supervisor** Dashboard HRGA.

⚠️ **Di dashboard, turnover 0% tampil HIJAU "aman"** karena `statusAmbang` menilai `0 <= target` sebagai memenuhi. Selama `employee_resign` masih kosong itu mengabarkan retensi sempurna yang sebenarnya berarti "belum ada yang dicatat". Halaman Resign sudah menyelesaikan ini lebih dulu dengan **keterangan permanen di bawah kartu** bahwa hitungannya hanya mencakup yang tercatat lewat menu itu; keterangan yang sama **belum ada di dashboard**. 🔜 Direncanakan. Rumusnya **rata-rata headcount**, `keluar / ((awal + akhir) / 2) × 100`, dengan target **5% bulanan** yang dikirim server (bukan disalin frontend, supaya warna kartu tak pernah berbeda pendapat dengan servernya).

Tiga keterbatasan yang menempel pada angkanya, dan semuanya berasal dari bentuk datanya, bukan dari implementasinya:

- **Tak ada riwayat headcount sama sekali.** `system_authentication.is_active` cuma boolean keadaan sekarang, tanpa tanggal dan tanpa koleksi jejak. Headcount awal bulan karena itu **direkonstruksi**: `aktif sekarang + keluar bulan ini − masuk bulan ini`.
- **Rekonstruksi itu buta terhadap penonaktifan yang tak lewat menu Resign.** Sebelum menu ini ada, satu-satunya jalur adalah IT menonaktifkan akun langsung, dan itu tak meninggalkan catatan. Orangnya terhitung seolah tak pernah keluar.
- **Karena itu hanya bulan BERJALAN yang disajikan.** Bulan lampau menuntut penguraian mundur bulan demi bulan, tiap langkah menambah galat, dan hasilnya terlihat pasti padahal tidak.

⚠️ Saat dashboard penuh dibangun nanti: **tanggal keluar yang dipercaya adalah `effective_date`, bukan `applied_at`.** Keduanya bisa berbeda bila catatan dibuat mundur atau cron sempat tak jalan.

## Dokumen Terkait

- [[HRIS - Retention]] — counterpart (yang bertahan)
- [[HRIS - Personalia]] — sumber data off-boarding/terminasi
- [[Microservices - Employee Service]] · [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]] — koleksi & aturan catatan terminasi
- [[HRIS - Analysis]] · [[HRIS - Big Pictures]] · [[HRIS - Interrelationship Matrices]]
