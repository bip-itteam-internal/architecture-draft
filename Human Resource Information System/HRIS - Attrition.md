## Deskripsi

*Dashboard ini menampilkan seluruh attrition dari departemen internal yang mencakup karyawan yang masuk dan yang keluar*

- **Status**: 🟡 Konsep / Draft — belum diimplementasi (contoh masih spreadsheet).

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
- [x] **Catatan terminasi (pembuatan dan terhubung ke data karyawan)** — koleksi `employee_resign` di [[Microservices - Employee Service]]: kategori, tanggal efektif, **alasan**, dan dokumen pendukung per karyawan. ⚠️ ada di kode tapi **belum merge & belum deploy**, jadi datanya baru mulai terkumpul setelah fitur dipakai. Lihat [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]].

Dashboard-nya sendiri belum dibangun. Yang berubah dengan adanya catatan resign adalah **prasyarat datanya terpenuhi**: lima kategori terminasi dan alasan bebas per karyawan kini tersimpan, sehingga bagian Demografi ("gender, tipe, dan alasan terminasi") punya sumber. Sebelumnya `system_authentication.is_active` cuma boolean tanpa konteks, jadi pertanyaan "berapa yang keluar karena PHK bulan ini" tak bisa dijawab dari data mana pun.

⚠️ Satu hal yang perlu diperhitungkan saat dashboard dibangun: **tanggal keluar yang dipercaya adalah `effective_date`, bukan `applied_at`.** Keduanya bisa berbeda bila catatan dibuat mundur atau cron sempat tak jalan.

## Dokumen Terkait

- [[HRIS - Retention]] — counterpart (yang bertahan)
- [[HRIS - Personalia]] — sumber data off-boarding/terminasi
- [[Microservices - Employee Service]] · [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]] — koleksi & aturan catatan terminasi
- [[HRIS - Analysis]] · [[HRIS - Big Pictures]] · [[HRIS - Interrelationship Matrices]]
