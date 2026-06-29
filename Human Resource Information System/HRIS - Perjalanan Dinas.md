## Deskripsi

*Pengajuan **perjalanan dinas** (business trip request): karyawan mengajukan izin perjalanan dinas digital beserta detail perjalanan, logistik, dan **estimasi anggaran**, melalui rantai persetujuan **Atasan Langsung → HRD**. Ini menggantikan formulir kertas HRD "FORMULIR PENGAJUAN PERJALANAN DINAS". Entitas **terpisah** dari [[HRIS - Leave Request]] — concern-nya perjalanan + biaya, bukan sekadar absensi — namun **reuse** infrastruktur review bersama dari [[HRIS - Employee Request & Approval]]. Begitu disetujui HRD, status kehadiran pada rentang tanggal otomatis menjadi **Dinas**.*

- **Status**: ⚠️ Implemented (backend penuh; **FE belum** — MyBharata/Web ERP menyusul; ada catatan di bawah)
- **Stack/Path**: Go + Fiber + MongoDB — `services/attendance/business_trip.go`, model di `shared-library/models/attendance/models.go`
- **Diproses oleh**: [[Microservices - Attendance Service]] · **Kontrak**: [[API - Attendance Service]]

## Latar Belakang

* Formulir perjalanan dinas HRD selama ini berbasis kertas (informasi pemohon, detail perjalanan, agenda, anggaran, tanda tangan Atasan Langsung & HRD).
* Dibutuhkan pengajuan digital dengan jejak yang bisa dilacak + persetujuan berjenjang, konsisten dengan pola pengajuan HRIS lain.

## Beda dari "Dinas" pada Leave Request

| | [[HRIS - Leave Request]] subtype **Dinas** | **Perjalanan Dinas** (dok ini) |
|---|---|---|
| Tujuan | Menandai *ketidakhadiran* untuk keperluan kehadiran/payroll | Mengajukan *perjalanan + anggaran* untuk disetujui sebelum berangkat |
| Collection | `leave_request` | `business_trip_request` |
| Data | jenis/subtipe, tanggal, alasan | + lokasi, moda transportasi, akomodasi, agenda, **anggaran** |
| Dampak | status kehadiran → `Dinas` | status kehadiran → `Dinas` (sama) |

> Keduanya bisa men-set status kehadiran `Dinas`. Saat ini subtype Dinas di leave **tetap ada** — potensi tumpang tindih (karyawan bisa mengajukan dua-duanya); rasionalisasi diserahkan ke iterasi berikutnya (TBD).

## Model Data

Collection: `business_trip_request` (database attendance). Counter nomor dokumen: `business_trip_counter`.

```
BusinessTripRequest {
  _id            ObjectID
  employee_id / full_name / position / department   // Informasi pemohon
  document_number    string     // <seq>/HRD/PERJADIN/<bulan-romawi>/<tahun>

  trip_type      string         // BusinessTripTypes
  destination    string         // Lokasi/Alamat tujuan
  purpose        string         // Tujuan perjalanan
  agenda         string         // Agenda/kegiatan
  from_date / to_date  time     // Tanggal berangkat / kembali
  transports     []string       // BusinessTripTransports (multi-select)
  accommodation  string         // BusinessTripAccommodations
  budget { transport_pp, accommodation, allowance : int64 }  // estimasi rupiah
  document       MinIOFile      // dokumen pendukung opsional

  status         ReviewStatus   // diturunkan dari spv_status + hr_status
  spv_status     ReviewData     // Atasan Langsung
  hr_status      ReviewData     // HRD
  metadata       Metadata
}
```

Reuse `ReviewData` / `ReviewStatus` / `ResolveLeaveRequestStatus` dari domain attendance (sama seperti leave; bson key `spv_status`/`hr_status` disamakan agar `buildReviewFilter` dipakai ulang).

### Enum (registry `/data-type/:dt`)

| data-type | Nilai |
|---|---|
| `business-trip-type` | Kunjungan kerja · Rapat/Meeting · Seminar/Workshop/Pelatihan · Lainnya |
| `business-trip-transport` | Pesawat · Kereta Api · Bus · Kendaraan Pribadi Roda Dua · Kendaraan Pribadi Roda Empat · Mobil Dinas |
| `business-trip-accommodation` | Hotel · Tidak membutuhkan |

## Anggaran (estimasi, tanpa Finance)

`budget` (transportasi PP, akomodasi, uang saku — rupiah `int64`) adalah **estimasi yang diisi pemohon**, ditampilkan ke reviewer saat persetujuan. **TIDAK** terhubung ke Finance/payroll/reimbursement — sesuai formulir kertas yang tak memuat tanda tangan Finance. Bila kelak butuh pencairan/reimbursement, itu pekerjaan integrasi Finance terpisah (bdk. [[GA - Procurement System]] yang masih konsep).

## Penentuan Reviewer & Alur

Rantai **2 tingkat**: **Atasan Langsung (SPV) → HRD**, reuse `getSupervisorData(department)` dari [[Microservices - Employee Service]].

```
Karyawan buat pengajuan (nomor dokumen di-generate)
   └── Notif Atasan Langsung
        └── Atasan setuju? ──tidak──> Ditolak (notif pemohon)
              └── ya → Notif HRD
                    └── HRD setuju? ──tidak──> Ditolak
                          └── ya → Disetujui → status kehadiran rentang tanggal = Dinas
```

- Bila pemohon adalah supervisor-nya sendiri → review SPV dialihkan ke **Direktur** (sama seperti leave).
- **HRD tidak boleh menyetujui pengajuannya sendiri** (guard `employee_id != reviewer`; lebih ketat dari leave, mengikuti pola [[HRIS - Attendance Correction]]).

## Nomor Dokumen

Format **`<seq>/HRD/PERJADIN/<bulan-romawi>/<tahun>`** (mis. `001/HRD/PERJADIN/II/2026`). Sequence di-`$inc` atomik per-tahun via collection `business_trip_counter` (`_id` = tahun), di-generate sesaat sebelum insert.

## Pasca-Persetujuan (Dampak ke Attendance)

`applyApprovedBusinessTripToAttendance` men-set status entri kehadiran `[from_date..to_date]` (≤ hari ini) menjadi **Dinas**. Entri **masa depan** ditangani cron pra-generate (`preAllocEntries`) yang juga membaca `business_trip_request` yang disetujui (full-day; tanpa logika jam). Auto-ignore 24 jam & reminder reviewer T+18 jam mengikuti pola [[HRIS - Leave Request]].

## Endpoint API

Di bawah **Attendance Service** (`/api/attendance/...`), diproxy lewat [[CORE - API Master Gateway]]. Detail kontrak: [[API - Attendance Service]].

| Metode | Route | Keterangan |
|--------|-------|------------|
| POST | `/business-trip/create` | Buat pengajuan (multipart + upload dokumen opsional) |
| GET | `/business-trip/view?as=reviewer\|reviewed` | Lihat pengajuan (sebagai pengaju / reviewer) |
| PATCH | `/business-trip/review` | Atasan/HRD approve atau reject |
| PATCH | `/business-trip/cancel` | Batalkan pengajuan pending milik sendiri |

## Belum Diimplementasikan / Catatan

- **Frontend belum ada** — pengajuan ([[APP - MyBharata]]) & reviewer HRD ([[APP - Web ERP]]) menyusul.
- **Nomor dokumen bisa gap** — sequence terpakai walau pengajuan ditolak/dibatalkan.
- **Tidak ada guard backdate** — `from_date` lampau diperbolehkan; menyetujui pengajuan backdate akan menimpa status absensi historis menjadi Dinas (TBD: tambahkan guard karena dinas seharusnya forward-looking).
- **View belum punya filter `ongoing/past`** (seperti leave) — FE bisa diminta nanti.
- **Anggaran tanpa Finance** — estimasi saja (lihat di atas).
- Rasionalisasi vs subtype Dinas pada leave — TBD.

## Dependensi & Integrasi

- [[HRIS - Employee Request & Approval]] (framework induk) · [[HRIS - Leave Request]] (pembeda konsep)
- [[Microservices - Attendance Service]] · [[Microservices - Employee Service]] (supervisor) · [[Microservices - Notification Service]] (FCM + inbox) · [[Microservices - File Service]] (upload dokumen)
- [[HRIS - Big Pictures]] · [[HRIS - Attendance System]]
