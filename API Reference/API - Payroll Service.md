## Deskripsi

*Daftar endpoint **Payroll Service** — grounded ke kode (`services/payroll/routes.go` + `main.go` + `rbac.go`; audit 2026-08-26, **34 route** di berkas produksi termasuk `/health` dan `/me`). Arsitektur, fase, rumus perhitungan, dan keadaan produksinya: [[Microservices - Payroll Service]].*

- **Status**: ⚠️ Grounded ke kode (2026-09-01). Dok ini **baru dibuat** pada sync 2026-08-26 — sebelumnya payroll satu-satunya service besar tanpa berkas `API -`, padahal ia menghitung uang. · ⛔ **Dua rute impor di §Impor Payroll Run BELUM ada di produksi**: kodenya masih di branch `feat/payroll-impor-run` yang belum merged dan belum di-deploy. 34 route di atas tetap angka produksi hari ini; dengan kedua rute itu jadi **36**.
- **Prefix gateway**: `/api/payroll/*` → path internal tanpa prefix (`api-gateway/main.go`, env `PAYROLL_MODULE_URL`). Routing & auth: [[API - Index]].

⛔ **Sebelum menyentuh apa pun yang mengubah angka di sini**, baca lebih dulu `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` — turunan Peraturan Perusahaan yang menentukan jatah, ambang, dan besaran potongan. Berkas itu ada di repo **mobile**, tak tertaut dari alur kerja payroll mana pun, dan tak akan ditemukan kecuali dicari. Ia yang menang bila perilaku sistem bertentangan dengannya.

## Model gerbang (RBAC permission-set)

Payroll adalah modul **pertama sesudah ticket** yang menegakkan izin **per-aksi** ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]). Tiap rute memakai `gate(izin, predikatLama)`, dan argumen kedua bukan hiasan: ia **fallback** bagi akun yang belum punya paket payroll sekaligus perilaku **kill-switch** `PAYROLL_PERMISSION_ENFORCEMENT=off`, sehingga menyalakan fitur ini tak mencabut akses siapa pun.

| Predikat tier | Arti | Diturunkan dari |
|---|---|---|
| `isHR` | HR staff ke atas (`staff`/`supervisor`/`admin`) | `system_roles["hris"]` |
| `isHRSupervisor` | Supervisor HR ke atas | idem |
| `isHRAdmin` | Admin HR — config sensitif | idem |
| `isApprover` | Persetujuan final (Direktur) — **saat ini identik `isHRAdmin`** | idem |

Empat izin permission-set: `payroll.view` · `payroll.manage` · `payroll.work` · `payroll.approve` · `payroll.salary.write`. Identitas kosong → **401**; predikat gagal → **403**.

⚠️ **`payroll.salary.write` sengaja berdiri sendiri**, tidak dilebur ke `payroll.work`: staf HR boleh menyetel gaji tetapi **tidak** boleh membuat run, dan pemisahan itulah alasan izin ini ada. Melebur keduanya diam-diam memberi staf HR kemampuan menerbitkan payroll.

⚠️ **Service ini menaikkan `ReadBufferSize` ke 32 KB** (default fasthttp 4 KB) karena header `BIP-Permissions` dari gateway melebihi 4 KB begitu akun punya banyak permission-set. Gejala bila terlupa di service lain: permintaan gagal di lapisan HTTP sebelum handler mana pun jalan.

## Konfigurasi (baca = `view`, tulis = `manage`)

Seluruh config **singleton**, di-seed idempoten saat boot (`seedPayrollConfig`, `ensureTerBrackets`, `ensureAttendanceDeduction`).

| Method | Path | Catatan |
|---|---|---|
| GET | `/config/company` | Identitas perusahaan untuk slip |
| PUT | `/config/company` | `isHRAdmin` |
| GET | `/config/bpjs` | Iuran BPJS (pekerja + pemberi kerja) |
| PUT | `/config/bpjs` | `isHRAdmin` |
| GET | `/config/tax` | PPh21, termasuk tabel **TER** (`ter_table.go`) |
| PUT | `/config/tax` | `isHRAdmin` |
| GET | `/config/attendance-deduction` | Tarif potongan kehadiran |
| PUT | `/config/attendance-deduction` | `isHRAdmin`. **Gerbangnya sengaja SAMA dengan BPJS dan pajak**: yang diubah di sini aturan yang menentukan berapa rupiah dipotong dari gaji, bukan data harian |

## Master data

| Method | Path | Gerbang | Catatan |
|---|---|---|---|
| GET | `/companies` | `view` / `isHR` | Badan usaha (multi-company; identitas slip) |
| POST | `/companies` | `manage` / `isHRAdmin` | |
| PUT | `/companies/:id` | `manage` / `isHRAdmin` | |
| DELETE | `/companies/:id` | `manage` / `isHRAdmin` | |
| GET | `/salary-components` | `view` / `isHR` | Komponen gaji; di-seed default bila kosong |
| GET | `/salary-components/:id` | `view` / `isHR` | |
| POST | `/salary-components` | `manage` / `isHRAdmin` | |
| PUT | `/salary-components/:id` | `manage` / `isHRAdmin` | |
| DELETE | `/salary-components/:id` | `manage` / `isHRAdmin` | |

## Gaji per karyawan

| Method | Path | Gerbang | Catatan |
|---|---|---|---|
| GET | `/employee-salary` | `view` / `isHR` | Daftar penetapan gaji |
| GET | `/employee-salary/:employeeId` | `view` / `isHR` | Belum ditetapkan → **404 `gaji karyawan belum ditetapkan`**, bukan 200 bernilai nol |
| PUT | `/employee-salary/:employeeId` | **`salary.write`** / `isHR` | Izin terpisah — lihat §Model gerbang. ⚠️ **Upsert PENUH**: field yang tak dikirim jadi nol |
| POST | `/employee-salary/bulk-bpjs-base` | **`salary.write`** / `isHR` | Isi massal DUA dasar upah BPJS dari Excel HR. ⛔ **Tanpa `upsert`** — karyawan tanpa penetapan gaji **dilaporkan gagal**, tidak dibuatkan record bergaji nol. `$set` hanya dua dasar upah + `updated_by/at`. Kegagalan **per baris** (`{diperbarui, tanpa_ubah, gagal[]}`), maks 1000 baris. Didaftarkan **sebelum** saudara ber-`:employeeId` |
| GET | `/employer-cost` | ⚠️ **tanpa `gate()`** | Beban perusahaan per karyawan (bruto + iuran BPJS pemberi kerja), dikonsumsi **modul insentif** sebagai biaya operasional per orang. `?employee_ids=a,b,c&period=YYYY-MM`. Tanpa gerbang izin **secara sengaja**: pemanggilnya service lain yang tak membawa identitas orang. Penjaganya kunci gateway (`ValidateGateway` di `main.go`), dan ia hanya memulangkan satu angka beban per karyawan |

## Payroll Run & THR

| Method | Path | Gerbang | Catatan |
|---|---|---|---|
| POST | `/payroll-runs` | `work` / `isHRSupervisor` | Buat run bulanan. Body **`scope`** = `semua`(default)\|`karyawan`\|`magang` — nilai tak dikenal dibalas **400**, bukan dijatuhkan ke `semua`: salah ketik yang *melebarkan* lingkup berarti orang yang tak dimaksud ikut terbayar |
| POST | `/thr-runs` | `work` / `isHRSupervisor` | Buat run THR (Fase 4). Masa kerja ditarik dari employee-service `/internal/export/all` |
| GET | `/payroll-runs` | `view` / `isHR` | Difilter `?type=thr\|monthly`. Tiap run membawa `jumlah_karyawan`/`total_gross`/`total_net` — **dihitung saat dibaca** dari `payroll_run_line` (`bson:"-"`), tidak disimpan, supaya mustahil basi terhadap slip di dalamnya |
| GET | `/payroll-runs/:id` | `view` / `isHR` | |
| GET | `/payroll-runs/:id/lines/:employeeId` | `view` / `isHR` | Satu baris slip di dalam run |
| POST | `/payroll-runs/:id/recalculate` | `work` / `isHRSupervisor` | **Dispatch per `type`** lewat `modeHitungUlangRun`, sebuah `switch` yang **menolak tipe tak dikenal** alih-alih menjatuhkannya ke perhitungan bulanan. Run `import` dibalas **400**. ⛔ Penjaganya berjalan **sebelum** `DeleteMany`: begitu barisnya terhapus, penolakan di langkah berikutnya tak menyelamatkan apa pun |
| POST | `/payroll-runs/:id/approve` | **`approve`** / `isApprover` | |
| POST | `/payroll-runs/:id/publish` | **`approve`** / `isApprover` | Publish yang membuat slip terlihat karyawan |

## Impor Payroll Run (⚠️ merged, belum di produksi)

Backfill riwayat gaji yang sudah dibayar lewat spreadsheet HRD. Keputusan lengkap berikut
gerbang datanya: [[ADR - 0070 Impor Payroll Run dari Spreadsheet HRD untuk Backfill Riwayat Gaji]].

| Method | Path | Gerbang | Catatan |
|---|---|---|---|
| POST | `/payroll-runs/import` | `work` / `isHRSupervisor` | Buat run `type=import` **beserta seluruh barisnya dalam satu permintaan**. Gerbangnya sama dengan `POST /payroll-runs`: keduanya menerbitkan payroll untuk banyak orang sekaligus. Didaftarkan **sebelum** saudara ber-`:id` |
| DELETE | `/payroll-runs/:id` | `work` / `isHRSupervisor` | Hanya `type=import` **DAN** `status=draft`; run engine dan run non-draft dibalas **400**. Gerbangnya `work`, bukan `approve`: menghapus draft adalah kebalikan dari **membuatnya**, dan yang salah unggah harus bisa membatalkannya sendiri |

- ⛔ **ALL-OR-NOTHING.** Satu baris bermasalah → **400** berisi `gagal[]` (`{baris, employee_id, alasan}`) dan **nol dokumen tersimpan**. Berbeda sengaja dari `bulk-bpjs-base` yang gagal per baris: di sana tiap baris menulis field independen, di sini seluruh baris membentuk satu run yang totalnya harus utuh. `Payroll-MongoDB` standalone **tanpa replica set** sehingga transaksi Mongo tak tersedia.
- **Urutan pemeriksaan disengaja**: validasi murni (bentuk, duplikat `employee_id`, rekonsiliasi) dijalankan **sebelum** penjaga `mongodb.DB == nil`, sehingga permintaan yang bentuknya salah tetap dibalas 400 walau Mongo mati — dan seluruh jalur itu bisa diuji lewat Fiber tanpa database.
- **Rekonsiliasi**: `pendapatan − potongan` wajib sama dengan `net` (kolom TOTAL TERIMA), toleransi **0,01**. Yang tak cocok ditolak **berikut selisihnya dalam rupiah**.
- **Nama komponen** wajib ada di master `salary_component` (termasuk yang non-aktif, karena slip lama memakai nama yang sudah dipensiunkan). Nama bebas ditolak 400. ⚠️ Layar impor **ikut menawarkan yang non-aktif**, berlabel `(non-aktif)`; menyaringnya di layar membuat kelonggaran ini tak bisa dijangkau siapa pun.
- **`lines[].company_name`** (opsional) = kop slip dari kolom KETERANGAN sheet. Urutan menang: **nama dari sheet → `employee_salary.company_id` → default**. Nama yang tak ada di master `payroll_company` **ditolak 400 berikut namanya**, tidak jatuh ke default. Pencocokan melumatkan kapitalisasi dan spasi berlebih saja: `CV` dan `PT` **tidak** disamakan (entitas beda, NPWP beda), dan nama **kembar** di master ditolak sebagai ambigu karena iterasi map Go tak berurutan. Kosong/absen berarti "sheet tak menyebutnya".
- **`employee_id` diverifikasi** ke [[Microservices - Employee Service]] `/internal/export/all`. Gagal mengambilnya **MENGGAGALKAN impor** (502), berbeda dari `computeRunLines` yang memperlakukan kegagalan yang sama sebagai kosmetik.
- **Excel diurai di FRONTEND**, sama seperti `bulk-bpjs-base`: tak ada `excelize`, tak ada multipart, **tak ada dependensi Go baru**.

## Slip self-service (tanpa izin payroll apa pun)

Hak bawaan tiap karyawan atas datanya sendiri, ditegakkan lewat `employee_id` dari **header gateway**, bukan dari query. Ketiganya **hanya** melayani run ber-status `published`.

| Method | Path | Catatan |
|---|---|---|
| GET | `/payroll-runs/my` | Slip milik pemanggil. Field internal HR (`notes`, `created_by`, `approved_by`, `published_by`) **di-redact** |
| GET | `/payroll-runs/my/:id` | idem |
| GET | `/payroll-runs/my/:id/pdf` | Slip PDF, **dibuat saat diminta dan tidak disimpan** — seluruh bahannya sudah tersnapshot di `PayrollRunLine`, jadi menyimpan berkasnya hanya menambah tempat kedua yang bisa basi. `github.com/go-pdf/fpdf` (pure Go, tanpa cgo, image Docker tak berubah bentuk). Gateway men-streaming `application/pdf` apa adanya |

⛔ **Ketiga rute `/my*` WAJIB didaftarkan sebelum `GET /payroll-runs/:id`**, kalau tidak segmen `my` ketangkap sebagai `:id`. Kelas gotcha yang sama sudah menggigit di tempat lain: rute literal yang tertelan saudara ber-`:param` membalas **200 berisi bentuk yang masuk akal**, bukan 404, sehingga tak ada apa pun yang berbunyi salah — lihat catatan rute di [[Microservices - Calendar Service]].

⚠️ **Penjaga "hanya published" hidup di satu fungsi** (`findMyPayslipLine`) yang dipakai bersama versi JSON dan PDF. Penjaga yang hidup di dua tempat cepat atau lambat berubah di satu tempat saja, dan yang bocor adalah slip yang belum disetujui.

## Health & identitas

| Method | Path | Catatan |
|---|---|---|
| GET | `/health` | `{"message":"ok"}`. Di belakang kunci gateway |
| GET | `/me` | Identitas dari header gateway (bukti SSO end-to-end): `employee_id`, `username`, `full_name`, `department`, `position`, `system_roles`, `is_hr`. Tanpa `gate()` |

## Catatan keadaan produksi

⛔ **Nol run pernah `approved` atau `published`**, jadi **nol slip pernah dilihat karyawan** (dua dokumen `payroll_run`, keduanya `draft`, dibuat 2026-07-30 dan 2026-08-05). Fase 2, 4, dan 5 sudah live di produksi tetapi **belum pernah dipakai orang sungguhan** — ter-deploy bukan berarti terbukti bisa dipakai. Angka terkini dan rinciannya di [[Microservices - Payroll Service]].

## Dokumen Terkait

- [[Microservices - Payroll Service]] · [[API - Index]] · [[CORE - API Master Gateway]]
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[CORE - RBAC dan Permission Set]]
- [[Microservices - Attendance Service]] (sumber `/payroll-supplement`) · [[Microservices - Employee Service]] (masa kerja THR) · [[Microservices - Insentive Service]] (konsumen `/employer-cost`)
