## Deskripsi

*Framework bersama untuk **pengajuan karyawan (employee request)** — pola umum: **karyawan mengajukan → review/approval berjenjang → diterapkan otomatis ke attendance**. Ini "induk" dari beberapa subsistem HRIS yang berbagi infrastruktur review yang sama (semua di attendance service). Di aplikasi mobile, turunannya dikelompokkan di menu **Submission**.*

- **Status**: ✅ Implemented (infrastruktur bersama dipakai Leave/Shift/Correction; Overtime belum mengikuti pola ini)

## Turunan (jenis request)

| Jenis | Dokumen | Endpoint | Reviewer |
|---|---|---|---|
| Cuti / Izin | [[HRIS - Leave Request]] | `/request/*` | SPV → HR |
| Tukar shift / hari | [[HRIS - Tukar Jadwal Kerja]] | `/schedule-exchange/*` | multi-level (review_1 + review_2) |
| Koreksi clock-in/out | [[HRIS - Attendance Correction]] | `/correction/*` | role-based (4 kasus) |
| Lembur (SPKL) | [[HRIS - Overtime]] | *(belum)* | *(rencana mengikuti pola ini)* |

## Komponen Bersama (di kode)

Semua di [[Microservices - Attendance Service]]:
- **Model**: `ReviewData`, `ReviewStatus` (`Menunggu / Disetujui / Ditolak / Diabaikan / Dibatalkan`)
- **Resolusi status**: `Resolve*Status(...)` — menggabungkan beberapa review jadi status final
- **Penentuan reviewer**: `getSupervisorData(department)` + `build*ReviewFilter(...)`
- **Pola endpoint**: `create` / `view` (`?as=reviewer|reviewed`) / `review` / `cancel`
- **Notifikasi**: FCM + inbox ke reviewer & pemohon (via [[Microservices - Notification Service]])
- **Apply-to-attendance**: setelah disetujui, otomatis menyesuaikan entri attendance

## Pola Alur (umum)

```
Karyawan buat request
   → notif reviewer
   → review berjenjang (approve / reject)
        ├─ disetujui → terapkan ke attendance + notif pemohon
        └─ ditolak → notif pemohon
   (pemohon dapat membatalkan selama masih pending)
```

## Batas Tanggal per Jenis Request

Tiap turunan punya aturan tanggal sendiri (grounded ke kode attendance service). **Tidak ada** satu pun yang menjaga konsistensi terhadap **periode gaji (26–25)**:

| Jenis | Batas tanggal | Tutup-buku / payroll-lock |
|---|---|---|
| Cuti / Izin | `to_date > from_date`; subtype "Pulang cepat"/"Datang terlambat" = **hari ini**; cuti tahunan cek kuota. Tak ada batas mundur → **bisa di-backdate** | ❌ tidak ada |
| Tukar shift | `exchange_date` min **2 hari** ke depan + `work_date` & `exchange_date` **bulan kalender sama** | ❌ tidak ada |
| Koreksi clock-in/out | window **7 hari** (`correctionWindowDays`) + tak boleh tanggal masa depan | ❌ tidak ada |
| Lembur (SPKL) | *(belum diimplementasikan)* | — |

**Catatan konsistensi gaji (gap diketahui):** karena Leave bisa backdate & Correction berlaku mundur 7 hari, pengajuan **bisa melewati cutoff** periode gaji → bila periode sudah tutup-buku & dibayar, perubahan attendance tak otomatis ter-rekonsiliasi dengan gaji (mismatch). **Keputusan saat ini: dibiarkan apa adanya** (mengikuti perilaku Leave yang memang tanpa penjaga cutoff). Bila diperlukan, aturan cutoff = **keputusan level payroll terpisah** (sumber tanggal cutoff / flag `locked`), berlaku lintas-request — belum dibangun.

## Manfaat & Catatan

- **Reuse infrastruktur** → konsisten + cepat menambah jenis request baru
- **Saran**: [[HRIS - Overtime]] sebaiknya mengikuti pola ini (model `overtime_request` + `create/view/review/cancel` + apply ke `overtime_hour`)

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]] · [[HRIS - Attendance System]]
- [[Microservices - Attendance Service]] · [[Microservices - Notification Service]] · [[Microservices - Employee Service]]
- [[APP - MyBharata]] (menu Submission)
