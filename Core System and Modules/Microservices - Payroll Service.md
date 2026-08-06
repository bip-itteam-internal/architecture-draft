## Deskripsi

*Payroll Service mengelola **penggajian**: setup komponen gaji, konfigurasi BPJS & pajak, penetapan gaji per karyawan, dan **payroll run** (kalkulasi → approve → terbitkan slip). Ini sisi **implementasi** dari konsep [[HRIS - Payroll]] & [[HRIS - Compensation & Benefits]]. **Fase 1 (Setup & Config)** + **Fase 2 (Engine Run + lifecycle publish + slip self-service)** + **Fase 2b (PPh21 TER)** sudah di kode; slip PDF = fase berikut. Scope tegas: **sampai siapkan data + terbitkan slip, TANPA pembayaran/transfer**.*

- **Stack**: Go + Fiber v2 + MongoDB (`payroll_db`) — selaras pola service bip-erp lain
- **Path**: `services/payroll` (Fase 1 merged #262; Fase 2 PR #265; Fase 2b PPh21 TER PR #270; Payroll Run extend/publish/self-service PR #272; FE Payroll Run PR #171)
- **Status**: ⚠️ **Implemented (Fase 1 Setup + Fase 2 Run+publish+self-service + Fase 2b PPh21 TER + Fase 4 THR)**. Di belakang [[CORE - API Master Gateway]] (`InternalURL["payroll"]`), auth **SSO** ([[CORE - SSO Flow]]), role `system_roles["hris"]`. Port `6980`, mongo `payroll-mongo-db` (host `32792`). · 🔴 **Multi-perusahaan: belum ter-scope** — `company_id` di service ini = badan usaha **penggaji** (kop slip), BUKAN tenant; `listEmployeeSalaries`/run generation/THR meng-enumerasi SEMUA karyawan (`bson.M{}`) → campur lintas-perusahaan. Fase lanjut: [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]].

## Endpoint / Fitur (Sudah Diimplementasikan — Fase 1)

### Config global (single-company)
- `GET/PUT /config/company` — identitas perusahaan (nama, kota, penanda tangan HRD) untuk kop slip
- `GET/PUT /config/bpjs` — rate & cap 5 program: Kesehatan, JHT, JP, JKK, JKM
- `GET/PUT /config/tax` — PPh21 metode **TER** + nominal PTKP per status + tabel TER
- GET = role HR; PUT = HR admin. Dokumen **singleton**, di-seed default saat boot (idempoten).

### Master Badan Usaha (multi-company — identitas/kop slip)
- CRUD `/companies` — `listCompanies` (GET, HR) · `createCompany` (POST, HR admin) · `updateCompany` (PUT `/:id`) · `deleteCompany` (DELETE `/:id`, badan usaha **default tak bisa dihapus**).
- Field `Company`: `name`, `npwp`, `city`, `hrd_signer`, `bank_name`, `bank_account`, `is_default` (hanya satu default; dijaga saat create/update). Di-seed satu entitas default dari identitas config lama (CV Pure Glow Lux).
- **Konsep**: karyawan bekerja di bawah 1 PT induk tetapi bisa **digaji atas nama badan usaha berbeda**; yang beda antar-entitas **HANYA identitas slip (kop)** — **BPJS/PPh21/PTKP/TER tetap nasional** (config singleton). Saat run, identitas badan usaha disematkan ke tiap slip via `CompanySnapshot` (kop stabil walau master berubah/terhapus).
- **Skala nyata (data HRD, 2026-08-05): 41 badan usaha**, yaitu **PT Bharata Internasional** (default, ~67 karyawan digaji atas namanya) + **40 CV**. Nama-nama CV tersusun dari kumpulan kata yang sama diaduk ulang (`CV Fresh Radiant X` vs `CV Radiant Fresh X`, `CV Skin Elegance Up` vs `CV Skin Elegance Lux`, `CV Elegant Glow Lux` vs `CV Glow Lux Elegance`), sehingga **pemilih di FE wajib bercari, bukan `select` polos** — lihat [[APP - Web ERP]]. Master di-seed lewat skrip sekali jalan, **bukan** `seed.go`: ini data milik klien, bukan nilai bawaan sistem.
- ⚠️ **`company_id` menumpang di `employee_salary`, bukan di data karyawan.** Konsekuensinya penetapan badan usaha **tidak bisa mendahului penetapan gaji**: karyawan tanpa record `employee_salary` tak punya tempat menyimpannya. Membuat record kosong sebagai wadah **berbahaya** — `recalcRun` mengambil seluruh koleksi (`Find(ctx, bson.M{})`), jadi record setengah jadi ikut terhitung bergaji nol. Backfill `company_id` karenanya harus dijalankan **setelah** HR selesai mengisi struktur gaji, dan skripnya dibuat idempoten agar bisa diulang tiap batch.

### Master Komponen Gaji
- CRUD `/salary-components` — komponen `type` (earning/deduction), `input_type` (manual/computed), `taxable`, `bpjs_base`, `sort_order`, `is_active`
- **Di-seed 15 komponen** default **persis slip nyata** (9 pendapatan + 6 pengurangan). Yang `computed` (Lembur, BPJS, PPh21, **potongan** Tunjangan Kehadiran) dihitung engine; **earning Tunjangan Kehadiran = manual** (base per karyawan). GET = HR; tulis = HR admin.

### Gaji per Karyawan
- `GET /employee-salary` (list) · `GET/PUT /employee-salary/:employeeId` (upsert; path = sumber kebenaran)
- Field: `basic_salary`, **`upah_bpjs`** (dasar BPJS terpisah dari gaji pokok — temuan dari slip), `ptkp_status` (TK/0…K/3), `component_values[]`, `bpjs_enrollment`, `effective_date`
- Referensi `employee_id` ke [[Microservices - Employee Service]] — NPWP/no.BPJS/rekening **di-join di FE**, tidak disalin.
- ⚠️ **`upah_bpjs` = DASAR upah, bukan nominal potongan.** Engine memakainya sebagai pengali (`computeBpjsEmployee`), jadi mengisinya dengan nominal iuran membuat potongan mengecil sebesar rate itu sendiri (isi 4% dari dasar, potongan jadi 4% dari 4%, alias 25 kali lebih kecil). **Tidak ada validasi yang menahannya**: schema FE hanya `min(0)` dan `validateEmployeeSalary` hanya menolak negatif, jadi angka yang keliru lolos diam-diam sampai slip terbit.
	- **Terjadi di production** (diperiksa 2026-08-05): 10 record `employee_salary` terisi, `upah_bpjs` hanya pernah bernilai **107.200** atau **128.800** dan sama sekali tidak mengikuti gaji pokok (yang bervariasi 1.444.250 sampai 3.000.000). Dibaca sebagai iuran keduanya konsisten: `107.200 = 4% × 2.680.000` dan `128.800 = 4% × 3.220.000` (4% = total rate karyawan Kesehatan 1% + JHT 2% + JP 1%). **Dasar upah yang dimaksud belum dikonfirmasi HR**, jadi koreksi datanya TBD. `effective_date` juga banyak terisi `2027-08-25` (satu record `2026-08-25`, menguatkan dugaan salah ketik tahun).
	- FE sudah diberi penjaga (estimasi nominal + banner peringatan), lihat [[APP - Web ERP]]. Penjaga itu **tak berlaku surut**: record yang sudah terlanjur salah tetap perlu koreksi manual.

## Endpoint / Fitur (Sudah Diimplementasikan — Fase 2: Payroll Run)

- **Kalkulasi** (`buildPayslip`): Gaji Pokok = `basic_salary` (bukan komponen → hindari double-count; komponen manual bernama "Gaji Pokok" di-skip sbg guard) + komponen manual + Tunjangan Kehadiran penuh + lembur − BPJS (dari `upah_bpjs` + config) − potongan Tunjangan Kehadiran (`base × (1 − payout)`) − **PPh21 (TER)**. Hanya komponen `manual` diambil dari `component_values`; yang `computed` dihitung engine.
- **PPh21 (Fase 2b)** — metode **TER bulanan (PMK 168/2023)**: `PPh21 = tarif_efektif(kategori PTKP, bruto) × bruto`. Kategori dari `ptkp_status` (**A**: TK/0,TK/1,K/0 · **B**: TK/2,TK/3,K/1,K/2 · **C**: K/3; tak dikenal → A). Tabel TER A/B/C di config (`tax.ter_brackets`), di-seed default + backfill idempoten. Bruto = total pendapatan engine.
- **Batch run**: `POST /payroll-runs` (metadata `title`, `pay_period_start/end`, `pay_date`, `notes` — **penggajian BULANAN**, tak ada mingguan; `period` label diturunkan dari `pay_period_start` bila kosong; hitung semua karyawan, simpan snapshot per orang; supplement gagal per-orang ditandai, tak gagalkan run) · `GET /payroll-runs` · `GET /payroll-runs/:id` (+ lines) · `POST /:id/recalculate` (draft) · `POST /:id/approve` (approver) · `POST /:id/publish` (approver; approved → published) · `GET /:id/lines/:employeeId`. Status **draft → approved → published**.
- **Slip self-service** (tanpa gate HR — identitas dari header gateway): `GET /payroll-runs/my` (+ `/my/:id`) — karyawan lihat slip **sendiri**, HANYA dari run **published**; field internal HR (`notes`, `created_by`/`approved_by`/`published_by`) di-**redact**. Rute `/my` didaftarkan **sebelum** `/:id` agar tak ketangkap sebagai param.
- **Service-to-service**: panggil [[Microservices - Attendance Service]] `GET /payroll-supplement` (`payout_pct` **persentase 0–100** → prorata Tunjangan Kehadiran + lembur) via `InternalRequest`.

### Beban pemberi kerja (konsumsi antar-service — modul insentif)

- **`GET /employer-cost?employee_ids=a,b,c&period=YYYY-MM`** — beban **PERUSAHAAN** per karyawan: `bruto` (total pendapatan slip) + `iuran_bpjs_perusahaan` = `total`. Batch (dipisah koma) karena satu dashboard insentif memuat puluhan orang.
- **BUKAN gaji bersih yang diterima karyawan.** Potongan PPh21 & BPJS karyawan tetap uang yang keluar perusahaan (disetor ke kantor pajak/BPJS), jadi memakai gaji bersih akan mengecilkan biaya dan membuat profit insentif tampak lebih besar. Keputusan client 2026-08-02; dikunci test `b.Total <= slip.Net` → merah.
- **`computeBpjsCompany`** (kembaran `computeBpjsEmployee`) — memakai `CompanyRate` + batas upah yang sama. Rate-nya **sudah ada di config sejak awal tapi tak pernah dihitung**, karena iuran pemberi kerja bukan potongan karyawan sehingga tak muncul di slip. Slip nyata: bruto 4.328.500 + iuran 329.728 = **4.658.228** (vs gaji bersih 4.094.423 — selisih 13,8%).
- ⚠️ **Kini mengembalikan DESIMAL**, bukan bilangan bulat (lihat aturan pembulatan di bawah). Konsumen `/employer-cost` (modul insentif) perlu memformatnya; `Total` bisa berbunyi 4.658.228,04.

### Pembulatan BPJS — dua aturan berbeda, disengaja

Grounded ke **Formulir 2a PU BPJS Ketenagakerjaan** milik BHARATA INTERNASIONAL PHARMACEUTICAL (NPP 23222228, periode 08/2026).

| Sisi | Pembulatan | Alasan |
|---|---|---|
| **Iuran karyawan** (`computeBpjsEmployee`) | **KE BAWAH ke kelipatan 100**, per program | Praktik payroll Bharata: yang dipotong dari gaji selalu kelipatan 100. Ini angka yang masuk slip |
| **Iuran perusahaan** (`computeBpjsCompany`) | **Ke sen** (2 desimal) | Ini yang benar-benar disetor, dan BPJS menagih sampai sen |

- Untuk upah 2.773.184: potongan karyawan Kesehatan **27.700** (eksak 27.731,84), JHT **55.400**, JP **27.700**. Iuran perusahaan JHT **102.607,81**, persis seperti kolom Formulir 2a.
- ⚠️ **Selisihnya ditanggung perusahaan.** Karyawan dipotong 110.800 sementara yang disetor 110.927,36, jadi ~127 rupiah per orang per bulan jadi beban perusahaan. Konsekuensi yang disengaja, **dikunci test** (`TestPotonganSlipLebihKecilDariSetoran`) agar arahnya tak pernah terbalik.
- `computeBpjsEmployeeEksak` menyediakan nilai karyawan **tanpa** pembulatan ke bawah, untuk rekonsiliasi dengan tagihan.
- **`roundSen` wajib**, bukan kosmetik: tanpa itu float mentah bocor ke JSON sebagai `214565.88799999998`. Dua desimal juga kebetulan pembulatan yang sama dengan yang dipakai BPJS.
- 🔜 **Belum diputuskan**: pembulatan karyawan dilakukan **per program** (yang dipakai sekarang) atau atas gabungan per lembaga. Untuk upah 2.773.184 hasilnya sama; pada upah lain bisa beda 100 rupiah. Butuh satu slip manual berupah bukan kelipatan 10.000 untuk memastikan.
- 🔜 **JKP belum dikenal** config BPJS (hanya 5 program). Formulir 2a punya kolom Iuran JKP (pemberi kerja + pemerintah), nol di periode ini.
- Angkanya dirakit lewat `buildPayslip` yang **sama persis** dengan payroll run sungguhan, bukan dijumlah ulang — menyalin rumus bruto akan melahirkan rumus tandingan yang menyimpang diam-diam.
- ⚠️ **Sengaja TANPA `gate()`** — tak seperti `/employee-salary`. Pemanggilnya service lain yang tak membawa identitas orang, dan `gate()` membalas **401** begitu header employee id kosong. Pola menyalin `/payroll-supplement` milik [[Microservices - Attendance Service]]: dijaga kunci gateway (`app.Use(ValidateGateway)`) dan **hanya memulangkan satu angka beban per karyawan** — tanpa rincian komponen, tanpa gaji pokok, tanpa slip. Karyawan tanpa penetapan gaji dibalas `ditemukan:false`, bukan dihilangkan dari hasil dan bukan 404: pemanggil harus bisa membedakan "belum ditetapkan" dari "nol".
- Grounded: **golden test reproduksi slip nyata** (gross 4.328.500 & BPJS 32.200/96.600 cocok persis; net 4.094.423 ~slip, selisih ~4 rp krn payout dibulatkan 1 desimal) + smoke E2E lolos.

## Endpoint / Fitur (Sudah Diimplementasikan — Fase 4: THR)

- **`POST /thr-runs`** (`isHRSupervisor`) — buat run THR (`PayrollRun.type="thr"`) untuk SEMUA karyawan sekaligus. **THR = `basic_salary × proporsi(masa kerja)`** (Permenaker 6/2016: ≥12 bln=1; 1–11=bln/12; <1=tak dapat). Basis = **gaji pokok saja**; **satu run untuk semua** (tanpa data agama). Fungsi murni `thrProportion`/`buildThrPayslip` (ter-test).
- **PPh21 THR = TER atas bruto THR (standalone)** — reuse `computePph21TER`; impresisi bulanan **di-true-up saat Rekonsiliasi Desember** (belum ada).
- **Masa kerja** diambil dari [[Microservices - Employee Service]] `GET /internal/export/all` (`join_date`) via `InternalRequest` (header HR pemanggil diteruskan → lolos `RequireHRISStaff`; butuh env **`EMPLOYEE_MODULE_URL`**). Karyawan tanpa `join_date` → line ber-`error` (THR 0, tak salah bayar).
- **Lifecycle & slip self-service REUSE** rute `/payroll-runs/*` (type-agnostic): `GET /payroll-runs/:id`, `/:id/approve`, `/:id/publish`, `/:id/recalculate` (dispatch per `type`), `GET /payroll-runs/my` (slip THR karyawan; dibedakan via `run.type`). Daftar bisa difilter `GET /payroll-runs?type=thr|monthly`.
- **Persona & alur**: [[HRIS - Payroll Persona]].

## Endpoint / Fitur (Sudah Diimplementasikan — Fase 5: PDF Slip)

- **`GET /payroll-runs/my/:id/pdf`** — slip gaji sebagai PDF, **dibuat saat diminta** (tidak disimpan): seluruh bahannya sudah tersnapshot di `PayrollRunLine`, jadi menyimpan berkasnya hanya menambah tempat kedua yang bisa basi. Pustaka `github.com/go-pdf/fpdf` (pure Go, tanpa cgo, jadi image Docker tak berubah bentuk).
- **Otorisasi sama persis dengan versi JSON**: tanpa `gate()`, identitas dari header gateway, **hanya run `published`**. Pencarian keduanya berbagi satu fungsi `findMyPayslipLine` — penjaga "hanya published" yang hidup di dua tempat cepat atau lambat berubah di satu tempat saja, dan yang bocor adalah slip yang belum disetujui.
- **Angka tidak dihitung ulang**, hanya diambil dari snapshot, supaya PDF mustahil berbeda dari yang dilihat karyawan di layar. Dipisah dua lapis: `buildPayslipDocument` (murni, di sinilah isi diuji) dan `renderPayslipPDF` (tata letak).
- ⚠️ **`PayrollRunLine` bertambah `employee_name` + `position`**, disematkan saat run sealasan dengan `CompanySnapshot`. Ini **syarat teknis, bukan sekadar kerapian**: slip diunduh karyawan biasa, sedangkan [[Microservices - Employee Service]] `/internal/export/all` dijaga `RequireHRISStaff` sehingga namanya mustahil diambil saat PDF diminta. Run **lama** tanpa field ini jatuh ke `employee_id`; perlu `recalculate` agar namanya muncul. Gagal mengambil identitas **tidak** menggagalkan run (beda dari `join_date` di THR yang tetap menggagalkan, karena THR-nya jadi salah bayar).
- **Gateway tak perlu diubah**: `Reroute` di shared-library sudah mengenali `application/pdf` dan men-streaming-nya tanpa buffering, dan cache Redis hanya menyimpan `application/json` sehingga PDF tak ter-cache basi.
- Nama berkas membuang karakter yang merusak `Content-Disposition` (termasuk CR/LF), karena judul run adalah masukan bebas dari HR.

## Model Data (`payroll_db`)

- `salary_component` · `employee_salary` · `payroll_config` (singleton) · **`company`** (master badan usaha penggaji; identitas/kop slip, `is_default`) · `payroll_run` (+ **`type`** = `monthly`(default, run lama tanpa field)|`thr`; metadata `title`/`period`/`pay_period_start`/`pay_period_end`/`pay_date` + lifecycle `draft→approved→published` + `approved_by/at`, `published_by/at`) · `payroll_run_line` (snapshot payslip per karyawan + **`CompanySnapshot`** kop badan usaha + THR: **`thr_months_of_service`/`thr_proportion`** + `error` bila supplement/masa kerja gagal)

## Belum Diimplementasikan / Catatan

- **PPh21 TER** ✅ **sudah di kode (Fase 2b)** — TER bulanan PMK 168/2023. ⚠️ Angka tabel TER **perlu sign-off HRD/Finance**; editable via `PUT /config/tax` (`ter_brackets`) tanpa redeploy. **Rekonsiliasi PPh21 tahunan (Desember, progresif Ps.17)** belum termasuk → Fase 4.
- **Formula lembur** default `jam × (gaji_pokok/173)` (DJTK 1.5×/2× = TBD konfirmasi HRD).
- **Insentif** = komponen manual di slip. Integrasi dengan [[Finance - Incentive]] sejauh ini **satu arah**: modul insentif **menarik** beban karyawan dari sini (`/employer-cost`) untuk dipakai sebagai biaya operasional. Arah sebaliknya — nominal insentif masuk otomatis ke slip — **belum**, dan menunggu keputusan apakah insentif dibayar lewat slip atau transfer terpisah (kalau terpisah, payroll tak perlu disentuh sama sekali). Bila lewat slip, `Taxable` & `BpjsBase` komponennya perlu ditetapkan finance/HRD.
- **THR** ✅ **sudah di kode (Fase 4)** — lihat §Fase 4 di atas. **Sisa Fase 4**: Rekonsiliasi PPh21 Desember (progresif Ps.17) — true-up tahunan yang mengoreksi impresisi TER THR.
- ~~**Slip gaji** (PDF/cetak) = Fase 3~~ → **PDF slip SUDAH ADA** (lihat Fase 5 di bawah). **Dashboard + export Accurate** = Fase 5 ([[ADR - 0001 Akuntansi via Accurate]]).
- **FE** ([[APP - Web ERP]], grup menu **Payroll**, **sudah di `main`**): **Pengaturan Gaji** (config: Komponen, BPJS, Pajak/PTKP, Perlakuan Kehadiran, Perusahaan) · **Gaji Karyawan** (Daftar Gaji register + edit) · **Payroll Run** (buat → detail KPI+tabel karyawan → approve → publish → modal slip) · **Slip Gaji Saya** (self-service). **FE THR** (menyusul BE #406): tombol "Buat Run THR" + badge **Jenis** (Bulanan/THR) di daftar, detail run THR (kolom masa kerja/proporsi), slip THR self-service (label + payout disembunyikan). Butuh service ter-deploy di gateway untuk E2E.
- **Slip self-service** kini via [[APP - Web ERP]]; integrasi [[APP - MyBharata]] (Flutter) untuk karyawan menyusul.
- **Multi-company (identitas/kop slip) SUDAH ada** — master badan usaha `/companies` (lihat §Fase 1) memungkinkan menggaji atas nama entitas berbeda (CV Pure Glow Lux, PT Bharata Internasional). **Yang masih single/nasional**: config BPJS/PPh21/PTKP/TER (`payroll_config` singleton) — per-entitas config pajak/BPJS **belum** (ditunda; realita: rate nasional sama antar-entitas).
- Validasi referensial (`component_id` / eksistensi `employee_id`) dilakukan di FE; assign gaji memakai role `isHR`.

## Dependensi & Integrasi

- [[Microservices - Employee Service]] — master karyawan (NPWP/BPJS/bank) via `employee_id`; juga penyedia `payroll-approx`
- [[Microservices - Attendance Service]] — `payroll-supplement` (agregasi kehadiran periode 26→25) = input kalkulasi (Fase 2, **sudah dipakai**)
- [[CORE - API Master Gateway]] · [[CORE - SSO Flow]] — routing + auth
- [[DB - Overview and Notes]] — pola database-per-service ([[ADR - 0002 Database-per-Service]])

## Dokumen Terkait

- [[HRIS - Payroll]] · [[HRIS - Compensation & Benefits]] — konsep/bisnis (pasangan dok ini)
- [[Microservices - Employee Service]] · [[Microservices - Attendance Service]]
- [[Microservices - Insentive Service]] — konsumen `/employer-cost` (beban karyawan sebagai biaya operasional insentif)
- [[Finance - Incentive]] · [[ADR - 0033 Beban Operasional Insentif dari Proyek Accurate]]
