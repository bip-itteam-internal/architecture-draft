## Deskripsi

*Payroll Service mengelola **penggajian**: setup komponen gaji, konfigurasi BPJS & pajak, penetapan gaji per karyawan, dan **payroll run** (kalkulasi → approve → terbitkan slip). Ini sisi **implementasi** dari konsep [[HRIS - Payroll]] & [[HRIS - Compensation & Benefits]]. **Fase 1 (Setup & Config)** + **Fase 2 (Engine Run + lifecycle publish + slip self-service)** + **Fase 2b (PPh21 TER)** sudah di kode; slip PDF = fase berikut. Scope tegas: **sampai siapkan data + terbitkan slip, TANPA pembayaran/transfer**.*

- **Stack**: Go + Fiber v2 + MongoDB (`payroll_db`) — selaras pola service bip-erp lain
- **Path**: `services/payroll` (Fase 1 merged #262; Fase 2 PR #265; Fase 2b PPh21 TER PR #270; Payroll Run extend/publish/self-service PR #272; FE Payroll Run PR #171; potongan kehadiran eksplisit [#1317](https://github.com/bip-itteam-internal/bip-erp/pull/1317) + [#1318](https://github.com/bip-itteam-internal/bip-erp/pull/1318) + erp-frontend [#1109](https://github.com/bip-itteam-internal/erp-frontend/pull/1109), merged 2026-08-20)
- **Status**: ⚠️ **Implemented (Fase 1 Setup + Fase 2 Run+publish+self-service + Fase 2b PPh21 TER + Fase 4 THR + Fase 5 PDF slip)** dan **live di produksi** (image BE dibangun 2026-08-25 21:30, FE 21:34). Di belakang [[CORE - API Master Gateway]] (`InternalURL["payroll"]`), auth **SSO** ([[CORE - SSO Flow]]), role `system_roles["hris"]`. Port `6980`, mongo `payroll-mongo-db` (host `32792`). · ⛔ **Belum pernah dipakai menggaji seorang pun**: 2 `payroll_run` di prod, **keduanya `draft`**, tak satu pun pernah `approved` apalagi `published`, jadi nol slip pernah sampai ke karyawan (diukur 2026-08-26). Lihat §Kondisi Pemakaian di Produksi. · 🔴 **Multi-perusahaan: belum ter-scope** — `company_id` di service ini = badan usaha **penggaji** (kop slip), BUKAN tenant; `listEmployeeSalaries`/run generation/THR meng-enumerasi SEMUA karyawan (`bson.M{}`) → campur lintas-perusahaan. Fase lanjut: [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]].

> ⛔ **Sumber aturan bisnisnya TIDAK ADA DI VAULT INI.** Jatah, ambang, dan besaran potongan diturunkan dari Peraturan Perusahaan 2026-2028 ke **`mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md`** — berkas di repo **mobile**, dan `CLAUDE.md` repo itu menyatakan **dokumen itu yang menang** bila perilaku sistem bertentangan dengannya. Yang relevan bagi service ini: mangkir 1,5x sehari dan 2x per hari bila ≥2 hari (Pasal 20), izin jam kerja memotong Tunjangan Kehadiran **dan** uang makan, sakit tanpa surat dokter diperlakukan sebagai izin, dan SP II memotong 25% gaji pokok selama 6 bulan (belum ada di kode).
>
> **Buka berkas itu lebih dulu sebelum menyentuh apa pun yang menghitung uang, sanksi, jatah, atau ambang disiplin.** Penunjuk ini ditambahkan 2026-08-26 karena ketiadaannya sudah menggigit: fitur potongan kehadiran dirancang, direncanakan, dan diimplementasikan penuh dengan mangkir dipotong **1x** — setengah dari yang diatur — dan lolos `/plan` maupun `/implement` tanpa satu pun gerbang menyadarinya. Berkasnya tak akan ditemukan kecuali dicari, karena yang menggarap payroll bekerja di `bip-erp` dan `erp-frontend`. Penyimpangan yang disengaja wajib jadi **ADR**, bukan komentar di kode.

## Endpoint / Fitur (Sudah Diimplementasikan — Fase 1)

### Config global (single-company)
- `GET/PUT /config/company` — identitas perusahaan (nama, kota, penanda tangan HRD) untuk kop slip
- `GET/PUT /config/bpjs` — rate & cap 5 program: Kesehatan, JHT, JP, JKK, JKM
- `GET/PUT /config/tax` — PPh21 metode **TER** + nominal PTKP per status + tabel TER
- `GET/PUT /config/attendance-deduction` — tarif potongan kehadiran (6 angka; lihat §Potongan Kehadiran)
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
	- ⚠️ **Jadi 18 komponen** (9 + 9) di [#1318](https://github.com/bip-itteam-internal/bip-erp/pull/1318): baris potongan "Tunjangan Kehadiran" dipecah jadi empat (Telat/Izin/Mangkir/Uang Makan). **Seed tak berlaku untuk dev & prod** yang koleksinya sudah terisi — backfill per-nama yang mengurusnya, lihat §Potongan Kehadiran.
	- ⚠️ **Prod nyatanya berisi 19, bukan 18** (diukur 2026-08-26): backfill per-nama **menambah** empat baris baru tapi **tidak menonaktifkan** baris `deduction/computed` lama bernama "Tunjangan Kehadiran", sehingga ia masih `is_active` berdampingan dengan penggantinya. Engine tak lagi mengisinya (`attendanceShortfall` dan `PayoutFraction` sudah dihapus), jadi dampaknya bukan salah hitung melainkan **daftar yang membingungkan saat HR membacanya**: satu nama muncul sebagai earning DAN sebagai deduction yatim. Menonaktifkannya perlu keputusan sadar, karena run lama menyimpan nama itu di snapshot slipnya.

### Gaji per Karyawan
- `GET /employee-salary` (list) · `GET/PUT /employee-salary/:employeeId` (upsert; path = sumber kebenaran)
- Field: `basic_salary`, **`upah_bpjs`** (dasar BPJS terpisah dari gaji pokok — temuan dari slip), `ptkp_status` (TK/0…K/3), `component_values[]`, `bpjs_enrollment`, `effective_date`
- Referensi `employee_id` ke [[Microservices - Employee Service]] — NPWP/no.BPJS/rekening **di-join di FE**, tidak disalin.
- ⚠️ **`upah_bpjs` = DASAR upah, bukan nominal potongan.** Engine memakainya sebagai pengali (`computeBpjsEmployee`), jadi mengisinya dengan nominal iuran membuat potongan mengecil sebesar rate itu sendiri (isi 4% dari dasar, potongan jadi 4% dari 4%, alias 25 kali lebih kecil). **Tidak ada validasi yang menahannya**: schema FE hanya `min(0)` dan `validateEmployeeSalary` hanya menolak negatif, jadi angka yang keliru lolos diam-diam sampai slip terbit.
	- **Terjadi di production** (diperiksa 2026-08-05): 10 record `employee_salary` terisi, `upah_bpjs` hanya pernah bernilai **107.200** atau **128.800** dan sama sekali tidak mengikuti gaji pokok (yang bervariasi 1.444.250 sampai 3.000.000). Dibaca sebagai iuran keduanya konsisten: `107.200 = 4% × 2.680.000` dan `128.800 = 4% × 3.220.000` (4% = total rate karyawan Kesehatan 1% + JHT 2% + JP 1%). **Dasar upah yang dimaksud belum dikonfirmasi HR**, jadi koreksi datanya TBD. `effective_date` juga banyak terisi `2027-08-25` (satu record `2026-08-25`, menguatkan dugaan salah ketik tahun).
	- FE sudah diberi penjaga (estimasi nominal + banner peringatan), lihat [[APP - Web ERP]]. Penjaga itu **tak berlaku surut**: record yang sudah terlanjur salah tetap perlu koreksi manual.
	- ⛔ **Diukur ulang 2026-08-26 pada 120 record: keadaannya memburuk pada skala, bukan membaik.** **Nol dari 120** punya `upah_bpjs` yang masuk akal sebagai dasar upah (`>= basic_salary/2`). Rinciannya: **71 kosong/0** (naik dari 41 — seluruh 30 record baru sejak pengukuran sebelumnya masuk ke kelompok ini) dan **49 di bawah separuh gaji pokok**, jumlah yang **tidak berubah**, jadi tak satu pun record lama diperbaiki. Nilai terbanyak persis yang dulu ditemukan: 107.200 (×39), 128.800 (×6), lalu 109.300 (×2) dan 248.600 (×2) — pola "diisi nominal iuran, bukan dasar upah". `effective_date` menguatkan dugaan salah ketik tahun: **46 record bertahun 2027**, hanya 3 di 2026, 71 kosong. Konsekuensinya keras: bila run pertama diterbitkan hari ini, **baris BPJS setiap karyawan salah**, entah nol atau sekitar 25 kali terlalu kecil. Penjaga FE terbukti belum menghentikannya, dan **tak berlaku surut**.
	- ⚠️ **Angkanya bergerak antar-pengukuran**: 86 → 90 dalam hitungan menit pada satu sesi, lalu 120 beberapa hari kemudian. HR sedang aktif mengisi. Ukur ulang sebelum menyimpulkan apa pun dari jumlah yang tertulis di sini; yang **tidak** bergerak adalah rasionya — nol yang wajar, tiga kali diukur.

## Endpoint / Fitur (Sudah Diimplementasikan — Fase 2: Payroll Run)

- **Kalkulasi** (`buildPayslip`): Gaji Pokok = `basic_salary` (bukan komponen → hindari double-count; komponen manual bernama "Gaji Pokok" di-skip sbg guard) + komponen manual + Tunjangan Kehadiran penuh + lembur − BPJS (dari `upah_bpjs` + config) − potongan kehadiran − **PPh21 (TER)**. Hanya komponen `manual` diambil dari `component_values`; yang `computed` dihitung engine.
	- ⚠️ **Potongan kehadiran diganti total** ([#1318](https://github.com/bip-itteam-internal/bip-erp/pull/1318), merged 2026-08-20). Satu baris `base × (1 − payout_pct)` menjadi **empat baris eksplisit bertarif tetap** — rinciannya di §Potongan Kehadiran di bawah. `attendanceShortfall` dan `PayoutFraction` **dihapus**; `payout_pct` tetap disimpan dan ditampilkan tapi tak lagi menentukan satu rupiah pun, dikunci test yang membandingkan dua slip berpayout berbeda.
- **PPh21 (Fase 2b)** — metode **TER bulanan (PMK 168/2023)**: `PPh21 = tarif_efektif(kategori PTKP, bruto) × bruto`. Kategori dari `ptkp_status` (**A**: TK/0,TK/1,K/0 · **B**: TK/2,TK/3,K/1,K/2 · **C**: K/3; tak dikenal → A). Tabel TER A/B/C di config (`tax.ter_brackets`), di-seed default + backfill idempoten. Bruto = total pendapatan engine.
- **Batch run**: `POST /payroll-runs` (metadata `title`, `pay_period_start/end`, `pay_date`, `notes` — **penggajian BULANAN**, tak ada mingguan; `period` label diturunkan dari `pay_period_start` bila kosong; hitung semua karyawan, simpan snapshot per orang; supplement gagal per-orang ditandai, tak gagalkan run) · `GET /payroll-runs` · `GET /payroll-runs/:id` (+ lines) · `POST /:id/recalculate` (draft) · `POST /:id/approve` (approver) · `POST /:id/publish` (approver; approved → published) · `GET /:id/lines/:employeeId`. Status **draft → approved → published**.
- **Slip self-service** (tanpa gate HR — identitas dari header gateway): `GET /payroll-runs/my` (+ `/my/:id`) — karyawan lihat slip **sendiri**, HANYA dari run **published**; field internal HR (`notes`, `created_by`/`approved_by`/`published_by`) di-**redact**. Rute `/my` didaftarkan **sebelum** `/:id` agar tak ketangkap sebagai param.
- **Service-to-service**: panggil [[Microservices - Attendance Service]] `GET /payroll-supplement` (`payout_pct` **persentase 0–100** → prorata Tunjangan Kehadiran + lembur) via `InternalRequest`.

### Potongan Kehadiran (✅ merged 2026-08-20 — [#1318](https://github.com/bip-itteam-internal/bip-erp/pull/1318) bersama [#1317](https://github.com/bip-itteam-internal/bip-erp/pull/1317); FE erp-frontend [#1109](https://github.com/bip-itteam-internal/erp-frontend/pull/1109))

Menggantikan prorata `payout_pct`. Alasannya bukan ketepatan melainkan **keterbacaan**: HRD
menghitung tangan di Excel, dan satu baris gabungan mustahil dicocokkan baris per baris.

- **Empat baris slip**: `Potongan Telat` · `Potongan Izin` · `Potongan Mangkir` · `Potongan Uang Makan`. Nama lama "Tunjangan Kehadiran" berhenti dipakai di sisi potongan — ia muncul dua kali di slip yang sama, dan karyawan yang bertanya "kenapa tunjangan saya dipotong" sedang menanyakan hal yang wajar.
- **Tarif** dari `payroll_config.attendance_deduction` (6 angka, `GET/PUT /config/attendance-deduction`, gerbang sama dengan BPJS & pajak): `hour_divisor` 173 · `day_divisor` 26 · `meal_deduction` 10.000 · `meal_threshold_hours` 4 · `alpha_multiplier_one_day` 1,5 · `alpha_multiplier_multi_day` 2,0.
- **Mangkir mengikuti Peraturan Perusahaan Pasal 20**: 1,5x tarif harian bila sehari, **2x per hari** bila dua hari atau lebih. Penafsiran yang dipilih: begitu mencapai dua hari, SELURUH harinya berpengali 2x (3 hari = 6x, bukan 1,5+2+2). Karena itu mangkir dipisah dari izin, baik di `days` (penanda `alpha`) maupun di baris slip — digabung, "1 hari × tarif" tak akan sama dengan rupiah yang tertulis.
- **Batas pada JUMLAH telat+izin+mangkir ≤ Tunjangan Kehadiran** (bukan `min()` per baris, yang akan membiarkan gabungannya berkali-kali lipat). Uang makan dibatasi Tunjangan Makan sendiri. Saat batas aktif ketiganya diperkecil proporsional, dan sisa pembulatan ditaruh di baris bernilai mentah terbesar supaya baris bernilai nol tak memunculkan potongan hantu. **Dengan pengali 2x, batas jauh lebih sering aktif: 13 hari mangkir sudah menghabiskan seluruh tunjangan.**
- **Angka dasar disnapshot ke `Payslip.attendance_basis`** (`jam_telat`, `hari_izin_ekuivalen`, `hari_mangkir`, `hari_makan_hangus`) — sealasan dengan `CompanySnapshot`: slip yang sudah terbit tak boleh berubah karena kebijakan diubah sesudahnya. Disimpan sebagai **angka**, bukan kalimat jadi, supaya layar bisa menerjemahkannya (ADR 0010); PDF yang memformatnya ke Bahasa Indonesia karena ia dokumen cetak tanpa konteks bahasa.
- ⛔ **Pembagi/pengali nol = kelas bug paling mahal di fitur ini.** `base/0` pada float bukan panic melainkan `+Inf`, lalu batas per tunjangan memangkasnya jadi **tepat sebesar tunjangannya** — karyawan yang telat semenit kehilangan seluruh Tunjangan Kehadiran, slip terbit tanpa galat, dan angkanya terlihat wajar karena bulat. Tiga lapis penjaga: validasi `PUT` menolak, backfill boot mengisi, fungsi hitung memulangkan **0** bila keduanya bocor. Sumber keempat yang tak terduga: `scheduled_hours` **0** dari `work_time` rusak — datang dari data produksi, bukan salah ketik HR, dan dijaga terpisah.
- ⚠️ **Backfill config bekerja PER FIELD, bukan per blok.** Memeriksa satu field saja akan melewatkan config yang SUDAH pernah di-backfill sebelum field lain ada (persis yang terjadi pada pengali mangkir: pembaginya terisi, jadi pemeriksaan menyatakan "tak perlu" sementara pengalinya 0 dan mangkir tak dipotong sama sekali). Karena itu **nol pada pengali mangkir DITOLAK validasi** meski nol pada potongan uang makan sah — nol yang mustahil datang dari HR adalah satu-satunya penanda "belum ditulis" yang bisa dipercaya.
- **Komponen master di-backfill per-nama** (`ensureAttendanceDeductionComponents`), karena `seedSalaryComponents` berhenti begitu koleksi tak kosong dan dev/prod sudah berisi 15 dokumen sejak lama.
- **`days` absen dari respons supplement → baris ditandai `error`**, bukan diam-diam berpotongan nol. Itu berarti payroll naik lebih dulu dari attendance; slipnya akan terbit terlalu murah hati dan tak seorang pun tahu.
- 🔜 **Belum diverifikasi lewat gateway maupun sebagai orang di layar.** Golden test bagian potongannya memakai rincian harian **rekayasa** dan menunggu lembar Excel HRD; yang tetap terbukti dari slip sungguhan hanya gaji pokok, GROSS, dan kedua baris BPJS.
- ⚠️ **Keempat baris potongan KINI sudah terhitung di prod** (diukur langsung ke `Payroll-MongoDB` **2026-08-26**, menggantikan catatan lama "belum menghasilkan satu rupiah pun"). Angka terkini: **2 `payroll_run`, keduanya masih `draft`** (periode `2026-06` dan `2026-07`, dibuat Seno Dwi Prakoso / HRD Supervisor), **120 `payroll_run_line`**, dan **120 dari 120** punya `payslip.attendance_basis` — naik dari 43 baris dengan nol basis. Berarti `recalculate` sudah dijalankan sesudah fitur merge. `employee_salary` juga naik jadi **120** (dari 86). **Yang masih nol tetap nol: tak satu run pun `approved` apalagi `published`**, jadi belum ada rupiah yang sampai ke karyawan. Itu satu-satunya hal yang menahan penyimpangan di bawah agar belum jadi salah bayar.
- ⛔ **Config prod menyimpang dari Pasal 20 pada pengali mangkir sehari, dan sudah terhitung ke 8 slip draft.** Terverifikasi ke produksi 2026-08-26:

	| | `alpha_multiplier_one_day` | `alpha_multiplier_multi_day` |
	|---|---|---|
	| Default kode (`models_config.go`) | **1,5** | 2,0 |
	| Peraturan Perusahaan Pasal 20 | **1,5** | 2 per hari |
	| **Prod** | **2** ⛔ | 2,0 ✅ |

	Disetel **Gilang Permatasari (Human Resource / Personalia) pada 2026-08-21 09:54 WIB** lewat `PUT /config/attendance-deduction` (`updated_by` + `updated_at` di `payroll_config`). Backfill mustahil menuliskannya karena backfill mengisi dengan nilai bawaan, jadi ini suntingan sengaja.

	**Dampak terukur pada dua run draft**: 22 baris ber-`hari_mangkir > 0`. Dari situ **8 baris ber-mangkir tepat 1 hari** total dipotong **Rp 565.065**, sedangkan pada 1,5x seharusnya **Rp 423.799** — **kelebihan potong Rp 141.266** atas 8 orang. 14 baris sisanya (mangkir 2 sampai 13 hari) **tidak terpengaruh**: pengali ≥2 hari memang 2x per hari di kedua versi, jadi angkanya sudah benar. Batas proporsional tak aktif pada kedelapan baris itu (mangkir 1 hari = 2/26 tunjangan, jauh di bawah plafon), sehingga selisihnya lurus 25%.

	Yang membuatnya mudah terlewat: angka ini **menentukan rupiah, tak terlihat di kode mana pun**, dan satu-satunya cara mengetahuinya adalah membaca config di produksi. **Konfirmasikan ke HRD sebelum run pertama di-`approve`** — sesudah `published`, slip men-snapshot angkanya dan koreksi menuntut pembatalan run, bukan sekadar mengubah config.

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

- `salary_component` · `employee_salary` · `payroll_config` (singleton; + **`attendance_deduction`**) · **`company`** (master badan usaha penggaji; identitas/kop slip, `is_default`) · `payroll_run` (+ **`type`** = `monthly`(default, run lama tanpa field)|`thr`; metadata `title`/`period`/`pay_period_start`/`pay_period_end`/`pay_date` + lifecycle `draft→approved→published` + `approved_by/at`, `published_by/at`) · `payroll_run_line` (snapshot payslip per karyawan; `Payslip` + **`attendance_basis`** + **`CompanySnapshot`** kop badan usaha + THR: **`thr_months_of_service`/`thr_proportion`** + `error` bila supplement/masa kerja gagal)

### Kondisi Pemakaian di Produksi (diukur 2026-08-26)

Dokumen ini sebelumnya hanya menceritakan apa yang sudah **di-merge**, dan itu berulang kali
terbaca sebagai "payroll sudah siap". Ia tidak. Angka di bawah yang menentukan kesiapan,
bukan git log.

| Koleksi | Isi prod | Bacaan |
|---|---|---|
| `payroll_run` | **2, keduanya `draft`** (dibuat 2026-07-30 & 2026-08-05) | ⛔ nol run pernah `approved`/`published`, jadi **nol slip pernah dilihat karyawan**. Fase 2, 4, dan 5 belum pernah dipakai orang sungguhan |
| `payroll_run_line` | **120 baris, 120 ber-`attendance_basis`** (naik dari 43 baris / 0 basis) | `recalculate` sudah dijalankan sesudah fitur merge; keempat baris potongan kini terhitung. **22 baris ber-mangkir**, 8 di antaranya tepat 1 hari — lihat penyimpangan pengali di §Potongan Kehadiran |
| `employee_salary` | **120** (dari **207** karyawan aktif, ~58%) | naik dari 90; cakupan masih di bawah tiga perempat. Angkanya memang bergerak antar-pengukuran karena HR mengisinya bertahap |
| `employee_salary.company_id` | terisi di **93 dari 120** (2026-08-26; sebelumnya 60 dari 86) | 27 sisanya jatuh ke badan usaha default |
| `payroll_company` | **41** | cocok dengan skala HRD (1 PT + 40 CV) |
| `salary_component` | **19** (bukan 18) | baris lama "Tunjangan Kehadiran" (deduction) masih aktif, lihat §Master Komponen Gaji |

**Urutan yang menahan run pertama**, dari yang paling mahal bila terlewat: `upah_bpjs`
(nol dari 120 record benar, lihat §Gaji per Karyawan) → pengali mangkir yang menyimpang dari
Pasal 20 → sign-off tabel TER → cakupan gaji yang belum separuh. Tiga yang pertama membuat
angka di slip **salah**, bukan sekadar kosong, dan slip yang sudah `published` men-snapshot
kesalahannya.

## Belum Diimplementasikan / Catatan

- **PPh21 TER** ✅ **sudah di kode (Fase 2b)** — TER bulanan PMK 168/2023. ⚠️ Angka tabel TER **perlu sign-off HRD/Finance**; editable via `PUT /config/tax` (`ter_brackets`) tanpa redeploy. **Rekonsiliasi PPh21 tahunan (Desember, progresif Ps.17)** belum termasuk → Fase 4.
- **Formula lembur** default `jam × (gaji_pokok/173)` (DJTK 1.5×/2× = TBD konfirmasi HRD).
- **Insentif** = komponen manual di slip. Integrasi dengan [[Finance - Incentive]] sejauh ini **satu arah**: modul insentif **menarik** beban karyawan dari sini (`/employer-cost`) untuk dipakai sebagai biaya operasional. Arah sebaliknya — nominal insentif masuk otomatis ke slip — **belum**, dan menunggu keputusan apakah insentif dibayar lewat slip atau transfer terpisah (kalau terpisah, payroll tak perlu disentuh sama sekali). Bila lewat slip, `Taxable` & `BpjsBase` komponennya perlu ditetapkan finance/HRD.
- **THR** ✅ **sudah di kode (Fase 4)** — lihat §Fase 4 di atas. **Sisa Fase 4**: Rekonsiliasi PPh21 Desember (progresif Ps.17) — true-up tahunan yang mengoreksi impresisi TER THR.
- ~~**Slip gaji** (PDF/cetak) = Fase 3~~ → **PDF slip SUDAH ADA = Fase 5** (lihat §Fase 5 di atas). **Dashboard + export Accurate** = **Fase 6** ([[ADR - 0001 Akuntansi via Accurate]]). Penomorannya sempat bertabrakan di dokumen ini: dua hal berbeda sama-sama disebut "Fase 5".
> **Modul `payroll` ditegakkan di DUA service sejak 2026-08-09** ([#1126](https://github.com/bip-itteam-internal/bip-erp/pull/1126)). Master **Perlakuan Kehadiran** (`/payroll-status-treatment`) tinggal di [[Microservices - Attendance Service]] tapi kini digerbang `payroll.view`/`payroll.manage`, menggantikan gerbang departemen `isHRDept`. Karena itu aturan keputusan izinnya naik ke `common.IzinPayrollEfektifDari` dan service INI **mendelegasikan** ke sana (`rbac.go`) alih-alih menyimpan salinan kedua yang bisa menyimpang. Konsekuensi deploy: perubahan izin payroll menuntut **payroll-service dan attendance-service naik bersama**.

- **FE** ([[APP - Web ERP]], grup menu **Payroll**, **sudah di `main`**): **Pengaturan Gaji** (config: Komponen, BPJS, Pajak/PTKP, Perlakuan Kehadiran, Perusahaan) · **Gaji Karyawan** (Daftar Gaji register + edit) · **Payroll Run** (buat → detail KPI+tabel karyawan → approve → publish → modal slip) · **Slip Gaji Saya** (self-service). **FE THR** (menyusul BE #406): tombol "Buat Run THR" + badge **Jenis** (Bulanan/THR) di daftar, detail run THR (kolom masa kerja/proporsi), slip THR self-service (label + payout disembunyikan). ✅ **Sudah ter-deploy ke prod** (image 2026-08-25 21:34): rute `/hris/payroll`, `/hris/payroll/my-payslips`, dan `/pengaturan/payroll` ter-build, dan string "Potongan Kehadiran", "Perlakuan Kehadiran", "Badan Usaha", "Slip Gaji Saya" ada di bundel dengan kontrol negatif nol. E2E sebagai orang tetap belum dijalankan, karena belum ada run yang `published` untuk dilihat.
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
