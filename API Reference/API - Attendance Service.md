## Deskripsi

*Endpoint **attendance-service** (kehadiran multi-metode, jadwal, leave/shift/correction/perjalanan-dinas, guestbook, payroll-supplement). Gateway: `/api/attendance/*`. Grounded ke `services/attendance/*.go`.*

- **Implementasi**: [[Microservices - Attendance Service]] · **Status**: ✅
- **Indeks**: [[API - Index]] · RBAC: `RequireHRISStaff`, `RequireSecurity`, `RequireGuestbookRBAC`, `RequireITStaff`, `RequireHRISStaffOrITSupervisor` (kelola jadwal), `gerbangRoster` (roster); banyak rute open (gated header/token/serial).

## Attendance entries & jadwal
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| POST | `/tap` | Clock-in/out (fingerprint/mobile/website; `?method=`) | open (serial/MAC/token) |
| GET | `/entries` | List entri (paginated). Filter: `?department=` (diterjemahkan via employee `/list?type=employee`), `?status=` (nilai mentah `/data-type/attendance-status`), `?search=`, dan rentang tanggal `?period_start=`/`?period_end=` (**DD-MM-YYYY**, inklusif, atas field `realtime`; format salah dibalas **400**). Rentangnya **bebas** — endpoint tak membatasinya ke periode berjalan. FE `/hris/attendance` mengirimnya dari pemilih **bulan kalender** di dalam panel filter (default bulan berjalan; sejak 2026-08-31 menggantikan preset Minggu/Bulan/Tahun ini) — lihat [[HRIS - Attendance System]] | HRIS |
| GET | `/history` | Riwayat absensi sendiri (bulanan). `?late=true&month=YYYY-MM` membalas **satu angka** (jumlah telat periode 26→25), dipakai [[APP - MyBharata]].<br>⚠️ **Belum merged** (`feat/attendance-telat-berpotongan`): angka itu kini hanya menghitung telat yang **berpotongan jam**, memakai `kriteriaTelatDihitung` yang sama dengan `/internal/late-recap` supaya angka yang dilihat karyawan tak bercabang dari angka yang dipakai HR menerbitkan SP | header |
| GET | `/report` | Laporan periode 26→25 (`?yyyy-mm`); tiap entry juga membawa `leave_subtype` (bedakan Izin urusan kantor vs pribadi di FE) | HRIS |
| PATCH | `/:id/update` | Update entri (+dokumen/status/comment) | HRIS |
| GET | `/payroll-supplement` | Agregasi jam → payout_pct (`?employee_id`); dibayar/dipotong per status dari master treatment.<br>⚠️ **Belum merged** ([#1317](https://github.com/bip-itteam-internal/bip-erp/pull/1317)): bertambah blok **`days`** berisi rincian PER HARI (`date`, `scheduled_hours`, `late_hours`, `leave_hours`, `unpaid_full_day`, `alpha`) yang jadi masukan potongan kehadiran di [[Microservices - Payroll Service]]. Aditif — `payout_pct` dan seluruh field lama tak berubah. Slice kosong dikirim `[]` bukan `null`, karena payroll membedakan "versi lama, field belum ada" dari "periode memang tanpa entri" | open |
| GET | `/payroll-status-treatment` | Perlakuan dibayar/dipotong per status (untuk payout) | `payroll.view` |
| PUT | `/payroll-status-treatment` | Set flag `paid` satu status (`{status, paid}`) | `payroll.manage` |
| GET | `/today` · `/schedule` · `/sync/company-work-schedules` · `/data-type/:dt` | Jadwal harian/bulanan/sync/enum | open |
| GET | `/company-work-schedule` | Definisi shift milik perusahaan aktif (`EffectiveCompanyID`). Amplopnya membawa **`code_managed`** — lihat [[Microservices - Attendance Service]] soal artinya yang **bukan** "jangan menambah" | open |
| POST | `/company-work-schedule` | Buat definisi shift. `schedule_id` **unik GLOBAL** (409 bila dipakai); `display_name` **wajib** dan tertutup (`REGULAR`/`MORNING`/`DAY`/`AFTERNOON`/`NIGHT`/`MIDNIGHT`), 400 bila di luar daftar — tanpa nama yang dikenal, kalender merender jam **tanpa keterangan apa pun** dan tak ada galat di mana pun. `company_id` dan `managed_by: "user"` distempel server, **bukan** dari payload | staf HRIS **atau** supervisor IT |
| DELETE | `/company-work-schedule/:schedule_id` | Hapus definisi shift. Difilter `company_id` pemilik **dan** `managed_by: "user"`, jadi shift **bawaan membalas 404** — menghapusnya tak berpengaruh apa pun karena seed menyemainya ulang tiap boot | staf HRIS **atau** supervisor IT |
| GET | `/company-group-rotation` | Pola shift bergilir milik perusahaan aktif (`EffectiveCompanyID`) | open |
| POST | `/company-group-rotation` | Buat pola rotasi. `group_id` **unik GLOBAL** (409 bila dipakai); `starting_date` **wajib** (400 bila kosong) karena ia yang menentukan langkah mana yang berlaku — sebelumnya tak divalidasi dan tersimpan sebagai tahun 0001 lalu menghasilkan fase acak ([#1357](https://github.com/bip-itteam-internal/bip-erp/pull/1357)) | staf HRIS **atau** supervisor IT |
| DELETE | `/company-group-rotation/:group_id` | Hapus pola rotasi (difilter `company_id` pemilik **dan** `managed_by: "user"`; rotasi bawaan membalas 404) | staf HRIS **atau** supervisor IT |
| GET/PATCH | `/mood` | Mood check-in harian | header |

## Holiday
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| GET | `/holiday` | List hari libur per tahun | open |
| POST/DELETE | `/holiday` · `/holiday/:id` | Tambah/hapus hari libur | HRIS |

## Leave request (cuti/izin/dinas)
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| POST | `/request/create` | Ajukan cuti (multipart + dokumen). **Idempoten**: dedup berbasis konten (`employee_id`+`leave_type`+`leave_subtype`+`from_date`+`to_date` yang masih `Waiting`/`Approved`) → pengajuan identik dianggap sukses tanpa duplikat | header |
| GET | `/request/view` | Lihat pengajuan (`?as=reviewer|reviewed`) | header |
| PATCH | `/request/review` · `/request/cancel` | Approve/reject / batal | header |
| GET/PATCH | `/request/security-lookup` · `/request/security-verify` | Verifikasi security cuti per-jam | Security |

## Shift exchange & correction
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| POST/GET/PATCH | `/schedule-exchange/create` · `/consent` · `/partners` · `/view` · `/review` · `/cancel` | **Tukar Jadwal Kerja** (collection `schedule_exchange_request`). **create**: hanya karyawan shift → non-shift **403**; `type:"shift"`+`partner_employee_id` = swap antar-rekan (simpan `exchange_work_time`+`partner_work_time`), `type:"day"` = geser hari. `exchange_date` **H+3**. **consent**: rekan setuju/tolak swap (langkah 1; tolak→Canceled). **partners** `?date=`: kandidat rekan swap (role sama, terjadwal). **view** `?as=reviewer/reviewed/partner` (`partner` = inbox consent rekan, 2026-06-29), `?filter=ongoing/past`, `?id=`, `?search=`. **review**: atasan→HRD, diblokir sampai consent. **cancel**: hanya saat Waiting | header |
| POST/GET | `/correction` · `/correction/mine` · `/correction` | Koreksi absen (window 7 hari; clock-in: kosong/Late, kecuali telat terverifikasi guestbook; list `?filter=ongoing/past` via status review, `?status=`) | header |
| GET | `/correction/candidates` | Entri kandidat koreksi 7 hari terakhir (hari ini s/d H-7, lintas-bulan, tanpa month); `?type=clockin/clockout/any` — untuk pemilih tanggal FE | header |
| PATCH | `/correction/:id/cancel` · `/correction/:id/review` | Batal / review koreksi | header |

## Roster jadwal bebas per tanggal
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| GET | `/roster` | Sel roster + karyawan ber-roster satu departemen (`?department=` wajib, `?from=`/`?to=` YYYY-MM-DD) | `gerbangRoster` |
| PUT | `/roster` | Simpan banyak sel (`{department, cells[]}`; sel = `employee_id`, `date` **RFC3339 penuh**, `off`, `work_time`, `note`). Maks **500 sel** per permintaan; validasi seluruh sel dulu, baru `BulkWrite` | `gerbangRoster` |
| DELETE | `/roster` | Kosongkan sel (`{department, cells[{employee_id, date}]}`) → tanggal kembali ke jadwal dasar; entri hari berjalan ikut dipulihkan | `gerbangRoster` |

**`gerbangRoster`** (`services/attendance/roster.go`) meloloskan **staf HRIS ke atas** untuk SELURUH departemen, atau siapa pun yang tokennya membawa klaim `supervised_departments` untuk departemen di dalam cakupannya saja. Cakupannya dibaca MENTAH (`SupervisedDepartmentsStrict`, tanpa fallback ke departemen sendiri); dengan fallback, setiap karyawan akan lolos atas rekan sedepartemennya — termasuk host yang menggeser jam shiftnya sendiri sesaat sebelum tap masuk. Modul `it` **tidak** punya akses roster sama sekali, berbeda dari kelola shift/rotasi di atas.

⚠️ Ini **bukan** `common.CanManageDepartment`, yang bentuknya mirip tapi mengunci ambang **supervisor** dan menopang gerbang peninjau Kaizen di [[Microservices - Form Builder Service]]. Roster sengaja punya penjaganya sendiri supaya menurunkan ambang di sini tidak melebarkan Kaizen.

Menolak: tanggal lampau, penulisan lintas perusahaan, departemen di luar cakupan, dan sel hari ini yang karyawannya sudah tap masuk atau sudah berstatus cuti/dinas. `date` bertipe Go `time.Time` sehingga **tanggal telanjang `YYYY-MM-DD` gagal di-parse** — kirim timestamp RFC3339 utuh. Keputusan: [[ADR - 0036 Roster Harian Menimpa Jadwal Dasar]].

## Pergantian jadwal terjadwal (berlaku-mulai)
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| POST | `/work-schedule-assignment` | Jadwalkan pergantian jadwal seorang karyawan (`employee_id`, `schedule_type` `static`/`pattern`, `schedule_id` **atau** `group_id`, `berlaku_mulai`). Menerima `YYYY-MM-DD` maupun RFC3339; keduanya dinormalkan ke tengah malam WIB | `RequireHRISStaffOrITSupervisor` |
| GET | `/work-schedule-assignment/:employee_id` | Dokumen dasar (`base`), seluruh baris (`assignments`, selalu `[]` bukan `null`), dan `active` = yang berlaku hari ini (dihitung backend, bukan frontend) | `RequireHRISStaffOrITSupervisor` |
| DELETE | `/work-schedule-assignment/:id` | Batalkan penugasan yang **belum** berlaku; yang sudah berlaku dibalas **409** | `RequireHRISStaffOrITSupervisor` |

⛔ **Aturan H+1: `berlaku_mulai` paling cepat BESOK**, hari ini dan tanggal lampau dibalas **400**. Ini menutup jendela penyemaian entri presensi yang gagal senyap secara struktural; alasan lengkapnya di [[Microservices - Attendance Service]].

Koleksi `work_schedule_assignment` (di `attendance_db`), index **unik** `(employee_id, berlaku_mulai)` — tanggal yang sudah terpakai dibalas **409**. Dokumen dasar `work_schedule` tidak pernah disentuh. Kedua jalur tulis mengirim pemberitahuan inbox berkategori `schedule` ke karyawannya ([[Microservices - Notification Service]]).

## Business trip (perjalanan dinas)
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| POST | `/business-trip/create` | Ajukan perjalanan dinas (multipart + dokumen opsional); body: `trip_type`, `destination`, `purpose`, `agenda`, `from_date`/`to_date` (RFC3339), `transports` (multi), `accommodation`, `budget_transport_pp`/`budget_accommodation`/`budget_allowance`. Generate nomor `<seq>/HRD/PERJADIN/<bulan-romawi>/<tahun>`; reviewer Atasan Langsung→HRD | header |
| GET | `/business-trip/view` | Lihat pengajuan (`?as=reviewer\|reviewed`, `?id=`, `?search=`, `?trip_type=`) | header |
| PATCH | `/business-trip/review` · `/business-trip/cancel` | Approve/reject (HRD tak boleh self-approve) / batal pending | header |

> Opsi enum via `/data-type/:dt`: `business-trip-type`, `business-trip-transport`, `business-trip-accommodation`. Anggaran = estimasi (tanpa Finance). Detail: [[HRIS - Perjalanan Dinas]].

## Pengganti pada pengajuan (2026-08-22)
Satu endpoint melayani **cuti dan perjalanan dinas**, dibedakan query `type` — dua endpoint terpisah berarti dua tempat yang harus sejalan. Grounded ke `services/attendance/replacement.go`.

| Method | Path | Fungsi | Auth |
|---|---|---|---|
| GET | `/replacement-candidates` | Rekan yang boleh ditunjuk menggantikan pemohon. `?type=leave\|business-trip` + `?id=<hex>` (wajib keduanya; selain itu **400**). Balas `{ data[], reason }` — `data[]` = `EmployeeSlice` (`employee_id`, `full_name`, `department`, `position`) | header; hanya **peninjau pengajuan itu** (filter sama dengan endpoint review) → selain itu **403** |

- **`reason` SELALU dikirim**, termasuk saat daftar terisi (nilainya string kosong). Tiga sebab daftar kosong menuntut tindakan berbeda dan ketiganya terlihat sama bila klien cuma menampilkan daftar kosong: pemohon berjadwal shift, daftar karyawan tak dapat dimuat, atau memang tak ada rekan seposisi.
- **503** bila database belum siap (penjaga `mongodb.GetCollection == nil`; tanpa itu paniknya keluar sebagai 502 tanpa petunjuk).
- `PATCH /request/review` dan `PATCH /business-trip/review` menerima field opsional **`replacement_employee_id`**, dibaca **hanya pada cabang SPV**. Nilai yang tak lolos validasi dibalas **400** dengan alasannya; tidak dikirim = perilaku persis seperti sebelum fitur ini ada. Dokumen pengajuan bertambah field `replacement` (`omitempty`) berisi salinan `employee_id`/`full_name`/`department`/`position` + `assigned_by`/`assigned_at`.
- ⚠️ Kandidat diambil dari [[Microservices - Employee Service]] `/list?type=employee`, yang membaca perusahaan dari **header** (`EffectiveCompanyID`) — **bukan** query `company_id` seperti cabang `type=supervisor`. Karena itu `routes.InternalRequest` dipanggil dengan `*fiber.Ctx`, bukan `nil`; dengan `nil` header tak diteruskan dan kandidatnya diam-diam berasal dari perusahaan default.

Aturan lengkap + yang sengaja belum dibuat: [[HRIS - Employee Request & Approval]].

## HR requests terpadu (lintas jenis)
Ringkasan/detail **lintas jenis** (Izin/Cuti/Sakit/Dinas/Koreksi/Tukar) dari satu endpoint — FE reuse satu kartu + stepper. Grounded ke `hr_admin.go` (`handleMyRequests`/`handleHRRequestsList`/`handleHRRequestDetail`).

| Method | Path | Fungsi | Auth |
|---|---|---|---|
| GET | `/requests/mine` | Ringkasan pengajuan **milik pemanggil** ("Aktivitas Saya"); `?filter=ongoing/past`. Bentuk `HRRequestSummary` (header + `steps` timeline review + tanggal per jenis) | header |
| GET | `/hr/requests` | Daftar ringkas untuk **peninjau / admin HR**. `?as=reviewer` (antrian) / `reviewed` (sudah) = difilter per peran **rekan / atasan(SPV) / HRD** (rekan hanya untuk Tukar); tanpa `as` = mode admin HR (hanya yang sudah sampai HRD). Filter `?type=`, `?status=`, `?department=`, `?search=`, `?from=`/`?to=` (yyyy-MM-dd, atas `metadata.created_at`), `?page=`/`?limit=`. Guard: pemohon tak muncul atas pengajuan sendiri | header; mode admin: `hris.pengajuan.view` (fallback dept HR / posisi Cost Control) |
| GET | `/hr/requests/detail` | Dokumen penuh satu pengajuan by `?type=` & `?id=`; `?as=self` (pemilik) / `reviewer\|reviewed` (peninjau, filter per jenis; item tab "sudah" hanya cocok `as=reviewed`) / tanpa = admin HR. Body = doc per jenis (sama dengan `/*/view`) | header; mode admin: `hris.pengajuan.view` (fallback sama) |

> FE mybharata: "Aktivitas Saya" pakai `/requests/mine`; "Review Submission" + kartu beranda pending pakai `/hr/requests` (+ `/hr/requests/detail` fetch-on-tap). Detail: [[APP - MyBharata]]. Aplikasi **selalu** mengirim `as`, jadi ia tak pernah menyentuh mode admin dan tak terpengaruh gerbang izinnya.

> **Rute `review` keempat jenis** (`PATCH /request/review`, `/business-trip/review`, `/correction/:id/review`, `/schedule-exchange/review`) tetap tanpa middleware, tapi **cabang tahap HRD**-nya sejak 2026-08-09 digerbang `hris.pengajuan.approve` (fallback union `department == "Human Resource"`). Tahap SPV dan consent rekan tak tersentuh: keduanya relasional. Gerbangnya di dalam handler, bukan middleware, karena satu rute melayani kedua tahap sekaligus.

## Guestbook · WiFi · Internal
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| GET/POST | `/guestbook/token` · `/guestbook/token-validate` | Token tamu 15 menit | open |
| GET/POST/PATCH | `/guestbook` | List/buat/edit entri tamu (POST `internal`/telat simpan `employee_id`) | GuestbookRBAC / Security |
| POST/GET | `/fingerprint/export` | Upsert/list ekspor fingerprint | open (serial) |
| GET/POST/DELETE | `/networks` · `/internal/wifi/add` · `/delete` | WiFi kantor (validasi on-site) | open / ITStaff |
| GET | `/internal/summary` | Ringkasan untuk HRIS orchestrator. Membawa DUA blok dengan jendela berbeda: `summary.total_clock_in`/`total_clock_out` = **24 jam bergulir** (tak terpengaruh parameter apa pun), dan `kehadiran` = **satu bulan kalender** yang dipilih `?periode=YYYY-MM`. Periode kosong / tak terurai / masa depan → **bulan berjalan** (bukan 400). Pembanding `kehadiran` berbeda aturan untuk bulan berjalan vs bulan selesai — lihat [[HRIS - Attendance System]] | HRIS |
| GET | `/internal/late-recap` | ✅ merged & hidup di prod (diverifikasi 2026-08-14). Jumlah telat **per karyawan** satu periode, untuk usulan SP1 di [[HRIS - Disciplinary (Surat Peringatan)]]. `?period=YYYY-MM` (wajib, 400 bila tak terurai) · `?min=` (bawaan 1). Periodenya **26 bulan lalu sampai 25 bulan ini**, dihitung `rentangPeriodeTelat` yang sama dengan `/history?late=true` supaya tak lahir dua angka "telat bulan ini". Balasan `{period, from, to, min, data[]{employee_id, late_count}}`, `data` selalu slice non-nil. Menghormati `?company=` bagi admin pusat.<br>⚠️ **Belum merged** (`feat/attendance-telat-berpotongan`): yang dihitung hanya `status = Terlambat` **DAN** `late_hour > 0`, jadi keterlambatan di dalam toleransi tak lagi masuk. Penyaring yang sama berlaku di `/history?late=true` | HRIS |

**`/internal/` bukan berarti privat** pada tabel di atas: gateway tetap meneruskannya dari internet, jadi tiap rute memeriksa identitas pemanggilnya sendiri. `/internal/late-recap` memaparkan siapa saja yang sering terlambat di seluruh perusahaan, karena itu digerbang `RequireHRISStaff`.

## KPI (panggilan mesin)
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| GET | `/kpi/attendance` | Rekap kedisiplinan **per karyawan** satu periode, untuk sumber `kedisiplinan_absensi` di [[Microservices - Employee Service]] | `?key=` = `ATTENDANCE_SERVICE_KEY` |

Parameter **semuanya wajib**: `periode` (`YYYY-MM`), `company_id`, `employee_id` (dipisah koma, maksimum **200** per permintaan), `key`. Yang kurang dibalas 400; `employee_id` melebihi batas juga 400 dan bukan dipotong diam-diam, supaya tak ada angka yang terlihat lengkap untuk sebagian orang saja.

Balasan `{"data": {periode, dari, sampai, data: [...]}}`. `dari`/`sampai` dikirim eksplisit karena batasnya **siklus payroll 26→25**, bukan bulan kalender, dan tebakan paling wajar justru yang salah. Tiap baris membawa `employee_id`, `hari_kerja`, `tepat_waktu`, `terlambat`, `tanpa_keterangan`, `pending`.

- **`hari_kerja` = hari yang MENUNTUT kehadiran**, memakai definisi yang sama persis dengan kartu Kehadiran (`statusTakDihitung`). Cuti, izin, sakit, dinas, dan seluruh hari libur tidak masuk: semuanya sah menurut Peraturan Perusahaan Pasal 15-18, dan menghitungnya sebagai kegagalan membuat angka turun justru ketika orang menempuh prosedur yang benar.
- **`pending` dipisah, tidak masuk `hari_kerja`.** Ia berarti belum diputuskan, bukan belum hadir. Dikirim terpisah justru karena itu: bagi metrik ketuntasan administrasi, sisa `Pending` adalah pekerjaan yang belum selesai. Satu angka jadi gangguan bagi satu metrik dan pokok bagi metrik lain.
- **`employee_id` yang tak punya entri tetap dikirim sebagai baris nol**, bukan dihilangkan.
- Status yang **belum dikenal** masuk `hari_kerja`, sengaja: mengabaikannya membuat kategori baru menghilang dari penyebut tanpa seorang pun sadar sehingga persentasenya naik sendiri.

⚠️ Auth-nya **kunci layanan di query, bukan RBAC modul**, sebab pemanggilnya mesin tanpa JWT. Kunci kosong menutup rute (401), bukan membukanya. Nilainya wajib sama dengan yang dipasang di blok employee-service.

## Dokumen Terkait
- [[Microservices - Attendance Service]] · [[HRIS - Leave Request]] · [[HRIS - Tukar Jadwal Kerja]] · [[HRIS - Attendance Correction]] · [[HRIS - Perjalanan Dinas]] · [[HRIS - Payroll]] · [[HRIS - Disciplinary (Surat Peringatan)]] · [[API - Index]]
