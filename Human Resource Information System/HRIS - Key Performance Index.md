## Deskripsi

*Penilaian kinerja berbasis **skor KPI**. **Penting dipisahkan**: engine **skor→insentif tim marketing SUDAH ADA** di kode ([[Microservices - Insentive Service]]); sedangkan **appraisal/KPI bulanan menyeluruh per-karyawan semua departemen** (dijelaskan di "Fitur" bawah) masih **konsep**.*

[Contoh dari sistem ini](https://drive.google.com/drive/folders/15fGQNX5usiMXIk2GY8DAqahHFF5ahPpA)

- **Status**: ⚠️ Sebagian — engine KPI→insentif (marketing) ✅ di [[Microservices - Insentive Service]]; appraisal bulanan menyeluruh 🟡 konsep.

## Sudah Diimplementasikan — KPI engine insentif (marketing)

> Grounded ke [[Microservices - Insentive Service]] (✅ production). Cakupan: **9 role marketing** (Supervisor, ADV Leader TikTok, ADV Marketplace, ADV Meta, Host Live, Affiliate, CRM, CS, ICC) — **bukan** seluruh karyawan/departemen.

- `master-kpi` (CRUD; bobot total 100) · `POST /calculate` (scoring bertingkat per-role) · hasil + workflow approve/override · cron harian menarik metrik iklan (TikTok GMV-Max / Shopee GMS) dari [[Microservices - Integration Service]].
- Skor → **insentif** ([[Finance - Incentive]] / [[Sales - Incentive]]). Koleksi: `master_kpis`, `kpi_score`, `incentive_results` ([[DB - Overview and Notes]]).

## Konsep — appraisal bulanan menyeluruh (belum di kode)

Rancangan KPI/appraisal per-karyawan **semua departemen** (form bulanan diisi supervisor → diteruskan ke HR), **beda** dari engine insentif marketing di atas. Detailnya:

## Fitur

Dokumen ini seharusnya diisi oleh supervisor untuk setiap karyawan, namun hal tersebut tidak menutup kemungkinan bagi karyawan itu sendiri untuk mengisi dokumen lalu meminta review dari supervisor mereka masing-masing

Dokumen perlu diisi dan dikumpulkan pada hari pertama setiap bulan (kasus khusus jika hari pertama jatuh pada hari minggu/hari libur maka akan menjadi hari berikutnya)

Kami menginginkan cara yang mudah untuk mengisi catatan dan kalkulasi otomatis untuk setiap skor, di-review oleh supervisor lalu diteruskan langsung ke HR, di mana HR dapat melihat laporan seperti berikut:

- Dashboard
	- Ikhtisar segala hal yang sangat baik untuk pelaporan kepada stakeholder
	- Tampilan catatan per-departemen
	- Tampilan catatan per-orang
- Siklus form scoring key performance index
	- Ini adalah skor per-orang
	- Setiap departemen memiliki template scoring yang berbeda, namun sekali lagi, kita memerlukan standarisasi dokumen

## Detail yang Tertunda

- [ ] Informasi lebih lanjut tentang hal-hal yang mungkin mengubah payroll karyawan, contoh: overtime, insentif, asuransi

## Kebutuhan

- [ ] Master data karyawan (referensi lookup)
- [ ] Pembuatan form key performance index berdasarkan departemen (terhubung ke data karyawan)

## Dokumen Terkait

- **Implementasi**: [[Microservices - Insentive Service]] (engine KPI→insentif marketing) · [[Finance - Incentive]] · [[Sales - Incentive]]
- [[HRIS - Work Review]] — penilaian kualitatif (KPI = sisi kuantitatif); pertimbangkan **berbagi satu Review Cycle** ([[ERPGo - Performance Review Cycles]]) ketimbang sistem terpisah
- [[HRIS - Career & Promotion]] — masukan keputusan promosi
- [[HRIS - Analysis]] · [[HRIS - Big Pictures]] · [[HRIS - Interrelationship Matrices]]
