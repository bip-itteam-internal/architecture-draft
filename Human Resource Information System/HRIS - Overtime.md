## Catatan

*Lembur (overtime) — jam kerja tambahan di luar jadwal yang menjadi bonus pada payroll. Saat ini lembur baru dicatat sebagai data pada attendance, belum punya workflow pengajuan/approval terdedikasi seperti [[HRIS - Leave Request]] (pola: [[HRIS - Employee Request & Approval]]).*

- **Status**: ⚠️ Sebagian terimplementasi (pencatatan), workflow pengajuan **belum**

## Kondisi Saat Ini (di kode)

- **Field `overtime_hour`** pada entri attendance ([[Microservices - Attendance Service]]) — diinput/disunting HRIS via update entri (`PATCH /:id/update`)
- **Tipe dokumen "Surat Lembur"** (shared-library) untuk lampiran/kategori dokumen
- Masuk **payroll** sebagai bonus: `payroll-supplement` mengagregasi `totalOvertimeHours` ("overtime is a bonus on top", terpisah dari jam kerja terbayar)

## Belum Ada (Gap / Roadmap)

- **Workflow pengajuan lembur (SPKL)** yang berdiri sendiri — pengajuan oleh karyawan → **approval supervisor/HR** → otomatis set `overtime_hour` — seperti pola [[HRIS - Leave Request]] / [[HRIS - Shift Exchange]]
- Validasi (batas jam, hari libur vs hari kerja, tarif), bukti/lampiran wajib
- Integrasi langsung ke perhitungan insentif/upah lembur

## Rencana (bila dibangun)

- Model `overtime_request` (employee, tanggal, jam, alasan, dokumen, status, review SPV→HR) — mirip `leave_request`
- Endpoint `create / view / review / cancel`
- Saat disetujui → set `overtime_hour` pada entri attendance terkait → ikut payroll

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]]
- [[HRIS - Attendance System]] · [[Microservices - Attendance Service]] · [[HRIS - Payroll]]
- [[HRIS - Leave Request]] (pola pengajuan→approval) · [[APP - Mobile Application]]
