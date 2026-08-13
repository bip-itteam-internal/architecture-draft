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
- **Aturan kunci — posisi template WAJIB = posisi karyawan PADA PERIODE ITU**: submit ditolak `400 "template position … does not match employee position … for period …"`. Sejak 2026-08-10 pembandingnya **bukan lagi** `work_data.position` hari ini, melainkan jabatan yang dipegang pada **akhir periode yang dinilai**, dijawab dari `employee_movement` ([[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]]).
	- Sebabnya: karyawan yang pindah 1 September membuat penilaian Agustus-nya **mustahil diisi benar** dengan patokan lama — template yang benar untuk Agustus ditolak, dan satu-satunya yang diterima justru template jabatan yang belum dipegangnya sepanjang bulan itu. Bukan kasus langka: KPI memang sering baru diisi setelah bulannya lewat.
	- Perpindahan yang berlaku **di tengah** periode dianggap sudah terjadi; penilaian bulanan harus punya satu jawaban, bukan dua. Catatan `scheduled`/`cancelled` diabaikan, dan gagal baca riwayat jatuh ke perilaku lama alih-alih memblokir penilaian.
	- **Sisi FE mengikuti** sejak 2026-08-10 (bip-erp [#1146](https://github.com/bip-itteam-internal/bip-erp/pull/1146) + erp-frontend [#963](https://github.com/bip-itteam-internal/erp-frontend/pull/963)). Modal Score KPI dulu menyaring dropdown ke posisi karyawan **saat ini**, sehingga untuk periode sebelum perpindahan template yang benar justru tersembunyi walau backend menerimanya.
		- Jawabannya diambil dari server lewat **`posisi_periode`** yang menumpang di respons `GET /kpi/score` — rute yang **sudah** dipanggil modal itu dengan pasangan `(employee_id, period)` yang sama persis, jadi nol permintaan tambahan dan nol endpoint baru.
		- Aturannya sengaja **tidak** disalin ke TypeScript. Dua sumber kebenaran pasti menyimpang, dan yang menyimpang di sini membuat penilai melihat dropdown yang isinya ditolak server — pola yang sudah ditandai sebagai langkah mundur waktu aturan kelompok departemen sempat digandakan ke frontend.
		- Field **opsional**: selama backend belum ter-deploy, penyaringan jatuh ke jabatan terkini persis seperti perilaku sebelumnya. Dikunci uji.
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
- **Tampilan FE** (✅ live 2026-08-06, PR erp-frontend [#813](https://github.com/bip-itteam-internal/erp-frontend/pull/813)): halaman KPI mengikuti **pola satu card** yang sudah dipakai seluruh layar daftar HRIS lain — banner, tab departemen, ringkasan, dan tabel dalam satu card. Sebelumnya tiga card bertumpuk dan itu membuat KPI jadi satu-satunya layar HRIS yang tertinggal. Satu komponen (`KpiPageContent`) melayani **11 rute**: `/hris/kpi`, `/hris/kpi/templates`, `/portal/kpi`, serta KPI milik Finance, IT, GA, Quality, Procurement, Kesekretariatan, dan Manufaktur — dibedakan hanya oleh tiga props (`lockedDepartment`, `teamScope`, `view`). Rincian polanya di [[APP - Web ERP]].
	- **Kartu ringkasan tanpa warna ambang.** Total / sudah dinilai / belum dinilai / rata-rata semuanya bernada netral, berbeda dari kartu di Kelola Karyawan atau Resign yang berubah warna menurut target. Alasannya: **ambang KPI belum pernah disepakati siapa pun**, dan mewarnai kartu tanpa ambang berarti menyatakan penilaian yang tak ada dasarnya. Begitu ambang ditetapkan, `StatSummary` sudah punya prop `tone` dan tinggal diisi.
	- **Tab "Kesimpulan"** (✅ live 2026-08-13, erp-frontend commit `d4356c9c`, `feat/workspace-position`): **tab default & pertama** di semua rute ber-tab (KPI Tim + KPI per-modul). Menerjemahkan tiap baris skor jadi tindak lanjut untuk SPV — ≥80 = **Pertahankan**; di bawahnya = keterangan apa yang perlu ditingkatkan (dorong ke 80 / pendampingan / telusuri penurunan tren / lengkapi bukti); belum dinilai = ajakan menilai. Logika di `src/features/hris/kpi/lib/kesimpulan.ts`.
		- **Band de-facto, BUKAN ambang resmi.** Memakai `<60` / `60–79` / `≥80` yang **sudah** dipakai dashboard/analitik (`need training <60`, `top performer ≥80`), bukan menetapkan ambang baru. Ini tak menabrak butir "kartu ringkasan tanpa warna ambang" di atas: kartu tetap netral, keterangan tekstual sengaja tak mengklaim itu target resmi. Begitu ambang resmi ditetapkan, ubah dua konstanta `AMBANG_KURANG`/`AMBANG_BAIK`.
		- **Turun 100% dari data `GET /kpi` yang sama** — tak ada endpoint/kontrak baru (versi ringan; rincian metrik-lemah spesifik sengaja di luar lingkup).
		- **Grafik**: **donut** distribusi 4 band (warna status + legend jumlah/persen) berdampingan dengan **line chart rata-rata KPI per bulan** (6 bulan mundur dari periode aktif; bulan tanpa penilaian = jeda, bukan 0). Line memakai `useKpiTrend` (`useQueries`, satu `GET /kpi` per bulan, queryKey `kpi-trend` terpisah agar filter status tabel tak memotong rata-rata). recharts via `ChartContainer` shared.
		- **Fix hydration**: `KpiPageContent` (pemakai `useSearchParams`) kini dibungkus `<Suspense>` — tanpa batas itu Next App Router membail seluruh route ke render klien dan HTML server ≠ klien. Berlaku ke-11 rute tanpa menyentuh berkas page.
	- ⚠️ **Mode supervisor di halaman ini mustahil menyala** — cacat gerbang yang **pra-ada** dan belum diperbaiki; lihat butir lengkapnya di [[APP - Web ERP]] bagian "Belum Diimplementasikan / Catatan". **TBD**, karena perbaikannya butuh keputusan siapa "HR" versus "supervisor" lebih dulu.
- **Pengisian nilai 100% manual**: `ApplyKPIValues` hanya menerima map `label → 0..100` dari body request; tidak ada jalur auto-fill dari service lain. Analisis kelayakan otomasi per metrik (data production 2026-07-31: 70 template, 311 metrik, 73 metrik sumber datanya sudah siap) ada di [[HRIS - Otomasi Skor KPI]].

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
- [[HRIS - Otomasi Skor KPI]] — analisis kelayakan mengisi skor otomatis dari data ERP (peta 311 metrik ke sumber datanya, modul yang ada tapi datanya kosong, dan rencana bertahap)
- [[HRIS - Work Review]] — penilaian kualitatif (KPI = sisi kuantitatif); pertimbangkan **berbagi satu Review Cycle** ketimbang sistem terpisah
- [[HRIS - Career & Promotion]] — masukan keputusan promosi
- [[HRIS - Analysis]] · [[HRIS - Big Pictures]] · [[HRIS - Interrelationship Matrices]]
