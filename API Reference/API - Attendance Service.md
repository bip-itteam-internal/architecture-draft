## Deskripsi

*Endpoint **attendance-service** (kehadiran multi-metode, jadwal, leave/shift/correction/perjalanan-dinas, guestbook, payroll-supplement). Gateway: `/api/attendance/*`. Grounded ke `services/attendance/*.go`.*

- **Implementasi**: [[Microservices - Attendance Service]] · **Status**: ✅
- **Indeks**: [[API - Index]] · RBAC: `RequireHRISStaff`, `RequireSecurity`, `RequireGuestbookRBAC`, `RequireITStaff`; banyak rute open (gated header/token/serial).

## Attendance entries & jadwal
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| POST | `/tap` | Clock-in/out (fingerprint/mobile/website; `?method=`) | open (serial/MAC/token) |
| GET | `/entries` | List entri (paginated, filter dept/status/periode) | HRIS |
| GET | `/history` | Riwayat absensi sendiri (bulanan) | header |
| GET | `/report` | Laporan periode 26→25 (`?yyyy-mm`); tiap entry juga membawa `leave_subtype` (bedakan Izin urusan kantor vs pribadi di FE) | HRIS |
| PATCH | `/:id/update` | Update entri (+dokumen/status/comment) | HRIS |
| GET | `/payroll-supplement` | Agregasi jam → payout_pct (`?employee_id`); dibayar/dipotong per status dari master treatment | open |
| GET | `/payroll-status-treatment` | Perlakuan dibayar/dipotong per status (untuk payout) | `payroll.view` |
| PUT | `/payroll-status-treatment` | Set flag `paid` satu status (`{status, paid}`) | `payroll.manage` |
| GET | `/today` · `/schedule` · `/sync/company-work-schedules` · `/data-type/:dt` | Jadwal harian/bulanan/sync/enum | open |
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
| GET | `/roster` | Sel roster + karyawan ber-roster satu departemen (`?department=` wajib, `?from=`/`?to=` YYYY-MM-DD) | `CanManageDepartment` |
| PUT | `/roster` | Simpan banyak sel (`{department, cells[]}`; sel = `employee_id`, `date` **RFC3339 penuh**, `off`, `work_time`, `note`). Maks **500 sel** per permintaan; validasi seluruh sel dulu, baru `BulkWrite` | `CanManageDepartment` |
| DELETE | `/roster` | Kosongkan sel (`{department, cells[{employee_id, date}]}`) → tanggal kembali ke jadwal dasar; entri hari berjalan ikut dipulihkan | `CanManageDepartment` |

Menolak: tanggal lampau, penulisan lintas perusahaan, departemen di luar cakupan supervisi, dan sel hari ini yang karyawannya sudah tap masuk atau sudah berstatus cuti/dinas. `date` bertipe Go `time.Time` sehingga **tanggal telanjang `YYYY-MM-DD` gagal di-parse** — kirim timestamp RFC3339 utuh. Keputusan: [[ADR - 0036 Roster Harian Menimpa Jadwal Dasar]].

## Business trip (perjalanan dinas)
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| POST | `/business-trip/create` | Ajukan perjalanan dinas (multipart + dokumen opsional); body: `trip_type`, `destination`, `purpose`, `agenda`, `from_date`/`to_date` (RFC3339), `transports` (multi), `accommodation`, `budget_transport_pp`/`budget_accommodation`/`budget_allowance`. Generate nomor `<seq>/HRD/PERJADIN/<bulan-romawi>/<tahun>`; reviewer Atasan Langsung→HRD | header |
| GET | `/business-trip/view` | Lihat pengajuan (`?as=reviewer\|reviewed`, `?id=`, `?search=`, `?trip_type=`) | header |
| PATCH | `/business-trip/review` · `/business-trip/cancel` | Approve/reject (HRD tak boleh self-approve) / batal pending | header |

> Opsi enum via `/data-type/:dt`: `business-trip-type`, `business-trip-transport`, `business-trip-accommodation`. Anggaran = estimasi (tanpa Finance). Detail: [[HRIS - Perjalanan Dinas]].

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
| GET | `/internal/summary` | Ringkasan 24 jam (utk HRIS orchestrator) | HRIS |
| GET | `/internal/late-recap` | ⚠️ **belum merge & belum deploy** (branch `feat/employee-surat-peringatan`). Jumlah telat **per karyawan** satu periode, untuk usulan SP1 di [[HRIS - Disciplinary (Surat Peringatan)]]. `?period=YYYY-MM` (wajib, 400 bila tak terurai) · `?min=` (bawaan 1). Periodenya **26 bulan lalu sampai 25 bulan ini**, dihitung `rentangPeriodeTelat` yang sama dengan `/history?late=true` supaya tak lahir dua angka "telat bulan ini". Balasan `{period, from, to, min, data[]{employee_id, late_count}}`, `data` selalu slice non-nil. Menghormati `?company=` bagi admin pusat | HRIS |

**`/internal/` bukan berarti privat** pada tabel di atas: gateway tetap meneruskannya dari internet, jadi tiap rute memeriksa identitas pemanggilnya sendiri. `/internal/late-recap` memaparkan siapa saja yang sering terlambat di seluruh perusahaan, karena itu digerbang `RequireHRISStaff`.

## Dokumen Terkait
- [[Microservices - Attendance Service]] · [[HRIS - Leave Request]] · [[HRIS - Tukar Jadwal Kerja]] · [[HRIS - Attendance Correction]] · [[HRIS - Perjalanan Dinas]] · [[HRIS - Payroll]] · [[HRIS - Disciplinary (Surat Peringatan)]] · [[API - Index]]
