## Deskripsi

*Endpoint **attendance-service** (kehadiran multi-metode, jadwal, leave/shift/correction, guestbook, payroll-supplement). Gateway: `/api/attendance/*`. Grounded ke `services/attendance/*.go`.*

- **Implementasi**: [[Microservices - Attendance Service]] · **Status**: ✅
- **Indeks**: [[API - Index]] · RBAC: `RequireHRISStaff`, `RequireSecurity`, `RequireGuestbookRBAC`, `RequireITStaff`; banyak rute open (gated header/token/serial).

## Attendance entries & jadwal
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| POST | `/tap` | Clock-in/out (fingerprint/mobile/website; `?method=`) | open (serial/MAC/token) |
| GET | `/entries` | List entri (paginated, filter dept/status/periode) | HRIS |
| GET | `/history` | Riwayat absensi sendiri (bulanan) | header |
| GET | `/report` | Laporan periode 26→25 (`?yyyy-mm`) | HRIS |
| PATCH | `/:id/update` | Update entri (+dokumen/status/comment) | HRIS |
| GET | `/payroll-supplement` | Agregasi jam → payout_pct (`?employee_id`) | open |
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
| POST | `/request/create` | Ajukan cuti (multipart + dokumen) | header |
| GET | `/request/view` | Lihat pengajuan (`?as=reviewer|reviewed`) | header |
| PATCH | `/request/review` · `/request/cancel` | Approve/reject / batal | header |
| GET/PATCH | `/request/security-lookup` · `/request/security-verify` | Verifikasi security cuti per-jam | Security |

## Shift exchange & correction
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| POST/GET/PATCH | `/schedule-exchange/create` · `/consent` · `/partners` · `/view` · `/review` · `/cancel` | **Tukar Jadwal Kerja** (collection `schedule_exchange_request`). **create**: hanya karyawan shift → non-shift **403**; `type:"shift"`+`partner_employee_id` = swap antar-rekan (simpan `exchange_work_time`+`partner_work_time`), `type:"day"` = geser hari. `exchange_date` **H+3**. **consent**: rekan setuju/tolak swap (langkah 1; tolak→Canceled). **partners** `?date=`: kandidat rekan swap (role sama, terjadwal). **review**: atasan→HRD, diblokir sampai consent. **cancel**: hanya saat Waiting | header |
| POST/GET | `/correction` · `/correction/mine` · `/correction` | Koreksi absen (window 7 hari; clock-in: kosong/Late, kecuali telat terverifikasi guestbook; list `?filter=ongoing/past` via status review, `?status=`) | header |
| GET | `/correction/candidates` | Entri kandidat koreksi 7 hari terakhir (hari ini s/d H-7, lintas-bulan, tanpa month); `?type=clockin/clockout/any` — untuk pemilih tanggal FE | header |
| PATCH | `/correction/:id/cancel` · `/correction/:id/review` | Batal / review koreksi | header |

## Guestbook · WiFi · Internal
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| GET/POST | `/guestbook/token` · `/guestbook/token-validate` | Token tamu 15 menit | open |
| GET/POST/PATCH | `/guestbook` | List/buat/edit entri tamu (POST `internal`/telat simpan `employee_id`) | GuestbookRBAC / Security |
| POST/GET | `/fingerprint/export` | Upsert/list ekspor fingerprint | open (serial) |
| GET/POST/DELETE | `/networks` · `/internal/wifi/add` · `/delete` | WiFi kantor (validasi on-site) | open / ITStaff |
| GET | `/internal/summary` | Ringkasan 24 jam (utk HRIS orchestrator) | HRIS |

## Dokumen Terkait
- [[Microservices - Attendance Service]] · [[HRIS - Leave Request]] · [[HRIS - Tukar Jadwal Kerja]] · [[HRIS - Attendance Correction]] · [[HRIS - Payroll]] · [[API - Index]]
