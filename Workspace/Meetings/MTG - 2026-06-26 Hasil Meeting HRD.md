---
publish: false
---

# Hasil Meeting HRD

- **Tanggal**: 2026-06-26
- **Jenis**: Keputusan kebijakan HR (atribut attendance/leave/correction/shift)
- **Terkait**: [[MTG - 2026-06-26 Diskusi HRD - Koreksi Presensi & Tukar Shift]] (sebagian poin menjawab pertanyaan di sana)

> Tiap keputusan diberi **status di kode** (grounded) agar jelas mana yang sudah jalan vs butuh implementasi.

---

## 1. Izin meninggalkan pekerjaan: urusan kantor vs pribadi

**Keputusan:** "Izin meninggalkan pekerjaan" dibedakan dua jenis:
- **Urusan kantor** → **tidak potong gaji**.
- **Urusan pribadi** → **potong gaji**.

**Status di kode:** 🟡 **BARU.** Subtype leave saat ini belum membedakan kantor/pribadi, dan **belum ada flag potong-gaji** pada subtype. 
**Tindak lanjut:** tambah dua subtype (mis. di `leave-subtype`/`hr-request-subtype`) + atribut **payroll (potong/tidak)**, lalu hubungkan ke perhitungan gaji. Pengaruh: [[HRIS - Leave Request]] + data-type subtype + sisi payroll.

## 2. Beda warna status (report cuti) di FE ERP

**Keputusan:** status cuti pada **report di FE ERP (web)** dibedakan **warnanya**.

**Status di kode:** 🟡 **BARU (web).** Modul report ada di `erp-frontend/src/features/hris/report`. Perlu pewarnaan per-status pada tampilan report cuti.
**Tindak lanjut:** FE web (erp-frontend) — definisikan warna per status cuti di report. Pengaruh: [[APP - Web ERP]] / modul HRIS report.

## 3. Approval SPV HRD step-1 auto-approve

**Keputusan:** ketika reviewer adalah **SPV HRD**, **review step-1-nya auto-approve**.

**Status di kode:** ⚠️ **Sebagian sudah.**
- **Koreksi**: SPV HR yang mengajukan koreksi **sudah self-approve** (Kasus 4) — langsung diterapkan. ✅
- **Leave**: supervisor (termasuk SPV HR?) saat ini **di-reroute ke Direktur**, bukan auto-approve. Perlu konfirmasi apakah keputusan ini juga berlaku untuk **leave** (SPV HRD step-1 auto-approve).
**Tindak lanjut:** samakan perilaku auto-approve SPV HRD lintas request bila dimaksud. Pengaruh: [[HRIS - Attendance Correction]] (sudah), [[HRIS - Leave Request]] (perlu cek/ubah).

## 4. Koreksi presensi hanya 7 hari ke belakang

**Keputusan:** koreksi presensi **hanya untuk 7 hari ke belakang**.

**Status di kode:** ✅ **SUDAH SESUAI.** `correctionWindowDays = 7` + `validateCorrectionWindow` (tolak > 7 hari & tanggal masa depan). Endpoint kandidat `/correction/candidates` juga pakai window 7 hari. **Tak perlu perubahan.** Lihat [[HRIS - Attendance Correction]].

## 5. Tukar shift hanya untuk Security, Host Live, Produksi

**Keputusan:** tukar shift **hanya untuk karyawan ber-shift** — **Security, Host Live, Production**.

**Status di kode:** ✅ **Guard sudah dipasang** (2026-06-27) — `IsShiftBasedSchedule` di awal `POST /shift-exchange/create`, non-shift → **403**. Lebih jauh, fitur ini berkembang jadi redesign **Tukar Jadwal Kerja** (Tukar Shift swap-antar-rekan + Tukar Hari) — lihat [[MTG - 2026-06-27 Pertanyaan Klarifikasi HRD - Tukar Shift & Tukar Hari]].
**Tindak lanjut:** dok [[HRIS - Tukar Jadwal Kerja]] sudah di-rename & ditandai redesign 🟡; sisa pertanyaan HRD (coverage, role, comp-off, payroll) menunggu jawaban.

---

## Ringkasan tindak lanjut

| # | Keputusan | Status | Aksi |
|---|---|---|---|
| 1 | Izin kantor/pribadi (potong gaji) | 🟡 baru | subtype + flag payroll |
| 2 | Warna status report cuti (web) | 🟡 baru | FE erp-frontend |
| 3 | SPV HRD step-1 auto-approve | ⚠️ sebagian | koreksi ✅; cek/leave |
| 4 | Koreksi 7 hari ke belakang | ✅ sudah | — |
| 5 | Tukar shift shift-only | ✅ guard | redesign Tukar Jadwal Kerja menunggu HRD |
