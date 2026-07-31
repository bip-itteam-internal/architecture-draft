## Deskripsi

*Penilaian kinerja berbasis **skor KPI**. **Penting dipisahkan**: engine **skor→insentif tim marketing SUDAH ADA** di kode ([[Microservices - Insentive Service]]); sedangkan **appraisal/KPI bulanan menyeluruh per-karyawan semua departemen** (dijelaskan di "Fitur" bawah) masih **konsep**.*

[Contoh dari sistem ini](https://drive.google.com/drive/folders/15fGQNX5usiMXIk2GY8DAqahHFF5ahPpA)

- **Status**: ⚠️ Sebagian — engine KPI→insentif (marketing) ✅ di [[Microservices - Insentive Service]]; appraisal per-karyawan lintas-departemen ✅ **sebagian** di [[Microservices - Employee Service]] (`/kpi/*`: template per posisi + scoring); siklus bulanan wajib & workflow review supervisor→HR 🟡 konsep.

## Sudah Diimplementasikan — KPI engine insentif (marketing)

> Grounded ke [[Microservices - Insentive Service]] (✅ production). Cakupan: **9 role marketing** (Supervisor, ADV Leader TikTok, ADV Marketplace, ADV Meta, Host Live, Affiliate, CRM, CS, ICC) — **bukan** seluruh karyawan/departemen.

- `master-kpi` (CRUD; bobot total 100) · `POST /calculate` (scoring bertingkat per-role) · hasil + workflow approve/override · cron harian menarik metrik iklan (TikTok GMV-Max / Shopee GMS) dari [[Microservices - Integration Service]].
- Skor → **insentif** ([[Finance - Incentive]] / [[Sales - Incentive]]). Koleksi: `master_kpis`, `kpi_score`, `incentive_results` ([[DB - Overview and Notes]]).

## Sudah Diimplementasikan — appraisal per-karyawan (employee-service)

> Grounded ke [[Microservices - Employee Service]] (`/kpi/*`) + FE [[APP - Web ERP]] (`src/features/hris/kpi/`). Sebagian dari konsep appraisal menyeluruh di bawah kini **sudah berjalan** untuk penilaian per-karyawan lintas departemen (bukan hanya marketing).

- **Template per posisi**: `GET/POST/DELETE /kpi/templates` (filter `?department=&position=`). Tiap template = `{name, department, position, metrics[]}`; metrik `{label, weight, description}` (nilai 0–100, bobot total tiap template).
- **Scoring per-karyawan+periode** (`YYYY-MM`): submit `template_id` + `values{label→0..100}`. Template di-**snapshot** ke `kpi_score` (skor lampau beku — edit master template tidak retroaktif); final = Σ(weight×value).
- **Aturan kunci — posisi template WAJIB = posisi karyawan**: submit ditolak `400 "template position … does not match employee position …"` bila `template.position != workData.position`. FE (modal Score KPI) menyaring dropdown template ke posisi karyawan agar tak salah pilih (bila belum ada template untuk posisi tsb → diarahkan membuat dulu).
- **RBAC per departemen** (`RequireKPIDepartmentRBAC`). `department` boleh berisi **beberapa departemen dipisah koma** — dalam hal itu **SEMUA** harus terjangkau role pemanggil; satu saja tak berhak berarti ditolak, agar tampilan gabungan tak membocorkan departemen yang bukan haknya. Role `hris` tetap lolos untuk departemen mana pun.
- **Cakupan TIM untuk Leader** (`GET /kpi?scope=team`, branch `feat/atasan-langsung-kpi-leader` + `feat/kpi-leader-portal`, **belum merge**): menyaring ke **bawahan langsung** pemanggil (`work_data.supervisor_id`), bukan ke departemen. Menu KPI di Portal Saya yang dulu khusus supervisor kini juga terbuka bagi mereka.
	- **Gerbangnya keberadaan bawahan, BUKAN role, nama jabatan, maupun jenjang.** Leader ber-role `staff` sehingga selalu ditolak `RequireKPIDepartmentRBAC`; sementara pola judul `Supervisor|^Leader$` tak cocok untuk "Leader Production", "AR Leader", atau "QA Leader" yang benar-benar ada di data, dan jenjang jabatan belum tercatat di mana pun. Konsekuensi yang disengaja: begitu bawahan seseorang dipindahkan, menunya ikut hilang.
	- Cabang gerbangnya **dipisah**, bukan menambal `RequireKPIDepartmentRBAC` — gerbang itu meloloskan seluruh staf `hris` untuk departemen mana pun, dan pelebaran itu tak boleh terbawa ke jalur baru. Tanpa bawahan **aktif**, `scope=team` ditolak 403 supaya tak jadi pintu belakang.
	- **Supervisor menang** bila seseorang kebetulan keduanya: ia tetap melihat seluruh departemennya, termasuk orang yang sudah punya Leader.
	- Penyaringan keaktifan memakai `system_authentication.is_active`, sama seperti pipeline, supaya gerbang dan isi halaman sepakat.
- **Tampilan gabungan lintas departemen**: departemen yang **satu tim** ditampilkan sebagai satu kelompok berlabel pendek (saat ini **HRGA** = Human Resource + General Affair), departemen lain tetap terpisah. Sumbernya **master data** `master_department.supervised_by` + `supervision_label` — bukan konfigurasi frontend, bukan hardcode (lihat [[HRIS - Organization Structure]]).
	- **Berlaku untuk SIAPA PUN yang berhak melihat kedua departemen**, bukan hanya supervisornya. Penggabungan adalah sifat organisasi, bukan sifat penontonnya: staf HR (`hris:staff`) melihat HRGA menyatu sama seperti SPV-nya. Staf GA tak terpengaruh karena tanpa role `hris` mereka tak sampai ke menu HRIS.
	- **Data karyawan tidak diubah**: `work_data.department` tiap orang tetap di departemen masing-masing. Yang disatukan hanya tampilannya, sehingga pemisahan kembali **tanpa migrasi data** dan tanpa deploy — cukup ubah master data.
	- Penggabungan dihitung di **level orang**, bukan menjumlahkan ringkasan antar-departemen, supaya rata-rata tertimbang menurut jumlah anggota (HR 6 orang vs GA 15 orang memberi hasil berbeda jauh bila salah cara).
	- Hanya **mengelompokkan ulang** baris yang sudah lolos filter `department` + RBAC, tidak pernah menarik baris baru. Sebuah kelompok batal bila kurang dari dua anggotanya ikut difilter, dan labelnya kembali ke nama departemen asli.
	- Query `merge=<daftar>` + `merge_label=<nama>` tetap diterima untuk penggabungan **ad-hoc**, dan menimpa pengelompokan master data bila dikirim.
	- Beberapa kelompok bisa hidup berdampingan (mis. HR+GA dan Finance+Procurement) tanpa perubahan kode.
- **Bentuk respons**: satu departemen (atau beberapa yang seluruhnya digabung) → `{department, summary, members}`; selain itu → `{summary, departments[]}`.
- **Dashboard/analitik**: agregasi per departemen (rata-rata, coverage) + daftar *need training* (<60) & *top performer* (≥80).
- **Belum**: penegakan siklus bulanan & workflow review supervisor→HR (lihat konsep di bawah) = **TBD**.

## Konsep — appraisal bulanan menyeluruh (sebagian sudah — lihat bagian di atas)

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
- [[HRIS - Work Review]] — penilaian kualitatif (KPI = sisi kuantitatif); pertimbangkan **berbagi satu Review Cycle** ketimbang sistem terpisah
- [[HRIS - Career & Promotion]] — masukan keputusan promosi
- [[HRIS - Analysis]] · [[HRIS - Big Pictures]] · [[HRIS - Interrelationship Matrices]]
