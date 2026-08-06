## Deskripsi

*Dashboard ini akan membantu Human Resource mengelola karyawan dari awal hingga akhir karier mereka di perusahaan ini*

- **Status**: 🟡 Konsep / Draft — belum diimplementasi (contoh masih spreadsheet).

[Contoh dari sistem ini](https://docs.google.com/spreadsheets/d/14dDRxTWME4N4-TY42BPZFFaXYQOTTZxV/edit?gid=1164498077#gid=1164498077)

## Fitur

-  Task tracker (pada semua subsistem)
	- Ikhtisar dari semua hal yang mencakup analisis saat ini, sedang berjalan, dan yang sudah selesai
	- Task ini mungkin berakhir lebih cepat dari yang diperkirakan
- Dashboard
	- Ikhtisar dari semua hal yang sangat baik untuk pelaporan kepada stakeholder
- Detail
	- Tampilan attrition secara detail yang dilihat per departemen
- Demografi
	- Informasi detail mengenai gender, tipe, dan alasan terminasi (tambahan pencarian mudah untuk kepergian per departemen)

## Subsistem

- Talent acquisition
- Interview
	- Ini bersifat per orang
	- Ini merupakan turunan dari talent acquisition yang berarti bisa memiliki beberapa entri sekaligus
	- Hubungkan informasi ini ke talent acquisition
- On-boarding
	- Ini bersifat per orang
	- Mungkin menutup talent acquisition yang sedang berjalan jika diperlukan
- Retention
	- Berjalan pada waktu tetap, kemungkinan per bulan
- Remote management (Saat ini dinonaktifkan)
- Work review
	- Berjalan pada waktu tetap, kemungkinan per bulan
- Conflict management
	- Terhubung ke karyawan, satu konflik bisa terhubung ke lebih dari satu karyawan
- Off-boarding
	- Pengembalian aset perusahaan (cek daftar aset yang tercatat pada master data karyawan)
	- Clearance administrasi (cek ke departemen Finance)
	- ~~Penonaktifan akun (cek ke departemen IT)~~ → **dikerjakan HR sendiri** lewat catatan resign, tidak lagi diteruskan sebagai permintaan ke IT ([[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]]; ✅ live di produksi 2026-08-05). Menu IT tetap ada sebagai jalur kedua

## Kebutuhan

- [ ] Pembuatan task tracker berdasarkan subsistem
	- Alur dari semua segmen merupakan dokumen statis
- [ ] Master data karyawan (referensi pencarian)
- [ ] Daftar aset karyawan saat ini
- [ ] Clearance administrasi karyawan
- [x] Status akun karyawan — `system_authentication.is_active`, kini bisa diubah HR sendiri lewat catatan resign berikut sebab & tanggalnya (✅ live 2026-08-05)

## Dokumen Terkait

- [[HRIS - Big Pictures]] — peta domain HRIS
- Subsistem turunan: [[HRIS - Recruitment]] · [[HRIS - Retention]] · [[HRIS - Work Review]] · [[HRIS - Conflict Management]] · [[HRIS - Career & Promotion]]
- [[HRIS - Attrition]] · [[HRIS - Personalia]] (off-boarding) · [[HRIS - Interrelationship Matrices]]
- [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]] — penonaktifan akun pindah ke HR
