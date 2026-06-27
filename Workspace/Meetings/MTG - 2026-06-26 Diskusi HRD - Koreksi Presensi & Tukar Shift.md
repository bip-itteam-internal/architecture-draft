---
publish: false
---

# Diskusi HRD — Koreksi Presensi & Tukar Shift

- **Tanggal**: 2026-06-26
- **Peserta**: _(HRD: ___ · IT/Dev: ___)_
- **Tujuan**: Mengunci **kebijakan** (policy) untuk fitur **Koreksi Presensi** & **Tukar Shift** yang sudah/akan berjalan, agar implementasi sesuai aturan HR — bukan asumsi developer.
- **Cara pakai dokumen ini**: tiap poin berisi **"Sekarang di sistem"** (fakta kode) + **"Keputusan HRD"** (diisi saat rapat). Yang ditandai ⚠️ = paling berdampak.

> Catatan: nilai "Sekarang di sistem" diambil dari kode attendance service (branch `feat/recruitment-service`). Lihat [[HRIS - Attendance Correction]] & [[HRIS - Tukar Jadwal Kerja]].

---

## Ringkasan keputusan (isi saat rapat)

| # | Topik | Sekarang di sistem | Keputusan HRD |
|---|---|---|---|
| A | Step approval SPV | SPV → naik ke **Direktur** | |
| A2 | SPV HR setujui sendiri (koreksi) | **Boleh (self-approve)** | |
| B | Siapa boleh **tukar hari** | **Semua karyawan** | |
| B2 | Siapa boleh **ganti jam shift** | **Shift-based saja** | |
| C | Tukar shift min H-2 + bulan sama | **Ya** | |
| D | Batas mundur koreksi | **7 hari** | |
| E ⚠️ | Koreksi/tukar shift lewat cutoff gaji | **Tak ada guard** | |
| F | Koreksi telat (anti-fraud) | Terkunci bila terverifikasi guestbook | |
| G | Efek koreksi telat | Status → "Tepat Waktu", late 0 | |

---

## A. Alur persetujuan (approval chain)

**Pertanyaan**: Untuk pemohon **SPV** (non-HR maupun HR), persetujuan cukup sampai **HR** saja, atau harus sampai **Direktur**?

**Sekarang di sistem** (berlaku untuk koreksi & tukar shift, polanya sama):

| Pemohon | Reviewer 1 | Reviewer 2 |
|---|---|---|
| Karyawan biasa | Kepala departemen (SPV) | **HR** *(berhenti di HR)* |
| **SPV non-HR** | HR | **Direktur** |
| Staff HR | Kepala departemen HR | — *(1 level)* |
| **SPV HR** | **Direktur** | — *(1 level)* |

**Sub-pertanyaan (A2)**: Pada **koreksi**, **SPV HR bisa menyetujui pengajuannya sendiri** (self-approve). Boleh secara governance, atau wajib ada reviewer lain?

- **Keputusan HRD (A)**: _______________________________________________
- **Keputusan HRD (A2)**: ______________________________________________

---

## B. Siapa yang boleh mengajukan Tukar Shift?

Fitur ini sebenarnya **2 mode** — mohon diputuskan **per mode**:

**B1 — Tukar hari** (kerja di hari libur → ambil libur pengganti)
- **Sekarang di sistem**: **SEMUA karyawan** boleh (termasuk non-shift, mis. staf kantor kerja di hari libur nasional).
- **Keputusan HRD**: _______________________________________________

**B2 — Ganti jam shift** (`exchange_work_time`, mis. shift pagi → malam)
- **Sekarang di sistem**: **hanya karyawan ber-shift** — Security / Host Live / Production.
- **Keputusan HRD**: _______________________________________________

---

## C. Aturan / syarat Tukar Shift

| Syarat | Sekarang di sistem | Keputusan HRD |
|---|---|---|
| Minimal pengajuan **H-2** (≥ 2 hari ke depan) | **Ya** | |
| `work_date` & `exchange_date` di **bulan kalender sama** | **Ya** | |
| **Alasan** wajib | **Ya** | |
| **Bukti/lampiran** wajib | **Tidak** | |
| **Batas frekuensi** per bulan/karyawan | **Tak ada** | |

---

## D. Batas waktu Koreksi Presensi

**Pertanyaan**: Koreksi presensi boleh mundur berapa lama?

- **Sekarang di sistem**: **7 hari (1 minggu)** ke belakang dari tanggal absen. *(Bukan 2 minggu / 1 bulan.)*
- **Opsi**: tetap 7 hari · 2 minggu · 1 bulan · lainnya: ____
- **Keputusan HRD**: _______________________________________________

---

## E. ⚠️ Cutoff gaji (periode 26→25) — PALING BERDAMPAK

**Pertanyaan**: Koreksi presensi & tukar shift bisa mengubah absen **tanggal lampau**. Bagaimana bila perubahan jatuh **setelah tutup-buku / gaji sudah dibayar**?

- **Sekarang di sistem**: **TIDAK ada penjaga cutoff** — pengajuan bisa melewati periode gaji yang sudah final → potensi **mismatch** absen vs gaji (mengikuti perilaku Cuti yang juga tanpa guard).
- **Perlu diputuskan**:
  1. Boleh ubah absen **setelah cutoff** periode gaji?
  2. Jika ya, bagaimana **rekonsiliasi** ke gaji (carry ke periode berikutnya / koreksi manual / tolak otomatis)?
  3. Siapa sumber tanggal cutoff & status "terkunci"?
- **Keputusan HRD**: _______________________________________________

---

## F. Koreksi keterlambatan & anti-kecurangan

**Pertanyaan**: Karyawan yang **telat** mengajukan koreksi clock-in agar jadi tepat waktu — kapan boleh, kapan diblok?

- **Sekarang di sistem**:
  - Telat yang **sudah tercatat security di guestbook** (sudah di kantor tapi telat absen) → **terkunci**, tak bisa dikoreksi jadi tepat waktu (anti-fraud).
  - Telat yang **belum tercatat guestbook** → **boleh ajukan** koreksi, lewat persetujuan SPV/HR.
- **Keputusan HRD**: _______________________________________________

---

## G. Efek koreksi telat yang disetujui

**Pertanyaan**: Saat koreksi telat **disetujui**, keterlambatan dianggap apa?

- **Sekarang di sistem**: status entri jadi **"Tepat Waktu"** + `late_hour` = 0 (keterlambatan **dimaafkan penuh**). Jam clock-in **asli tetap tersimpan** (mis. 08:30), hanya status yang berubah.
- **Pilihan**: dimaafkan penuh (seperti sekarang) **atau** jam telat tetap tercatat/terhitung meski koreksi disetujui?
- **Keputusan HRD**: _______________________________________________

---

## H. Lain-lain

| Topik | Sekarang di sistem | Keputusan HRD |
|---|---|---|
| Notifikasi hasil persetujuan | **FCM (mobile) saja** | perlu email/inbox? |
| Pembatalan pengajuan oleh pemohon | Boleh selama masih "Menunggu" | |

---

## Tindak lanjut (diisi setelah rapat)

- [ ] _Keputusan → tiket implementasi (jika ada perubahan kode)_
- [ ] _Update dok arsitektur [[HRIS - Attendance Correction]] / [[HRIS - Tukar Jadwal Kerja]] sesuai keputusan_
- [ ] _PIC & deadline: ____
