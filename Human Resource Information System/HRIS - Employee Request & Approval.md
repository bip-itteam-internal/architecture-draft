## Deskripsi

*Framework bersama untuk **pengajuan karyawan (employee request)** — pola umum: **karyawan mengajukan → review/approval berjenjang → diterapkan otomatis ke attendance**. Ini "induk" dari beberapa subsistem HRIS yang berbagi infrastruktur review yang sama (semua di attendance service). Di aplikasi mobile, turunannya dikelompokkan di menu **Submission**.*

- **Status**: ✅ Implemented (infrastruktur bersama dipakai Leave/Shift/Correction; Overtime belum mengikuti pola ini)

## Turunan (jenis request)

| Jenis | Dokumen | Endpoint | Reviewer |
|---|---|---|---|
| Cuti / Izin | [[HRIS - Leave Request]] | `/request/*` | SPV → HR |
| Tukar shift / hari | [[HRIS - Shift Exchange]] | `/shift-exchange/*` | multi-level (review_1 + review_2) |
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

## Manfaat & Catatan

- **Reuse infrastruktur** → konsisten + cepat menambah jenis request baru
- **Saran**: [[HRIS - Overtime]] sebaiknya mengikuti pola ini (model `overtime_request` + `create/view/review/cancel` + apply ke `overtime_hour`)

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]] · [[HRIS - Attendance System]]
- [[Microservices - Attendance Service]] · [[Microservices - Notification Service]] · [[Microservices - Employee Service]]
- [[APP - MyBharata]] (menu Submission)
