---
publish: false
---

# Tukar Jadwal Kerja — Persona & Flow (🟡 desain redesign)

> Bahan untuk memahami alur. **Belum diimplementasikan** — menggambarkan model swap-antar-rekan yang disepakati (lihat [[HRIS - Tukar Jadwal Kerja]] & [[MTG - 2026-06-27 Pertanyaan Klarifikasi HRD - Tukar Shift & Tukar Hari]]).

## Aktor (siapa saja yang terlibat)

| Persona | Peran | Muncul di |
|---|---|---|
| **Andi** | Pemohon Tukar Shift (Satpam, Security) | Tukar Shift |
| **Citra** | Rekan tujuan (Satpam, Security) | Tukar Shift |
| **Budi** | Pemohon Tukar Hari (Operator Produksi) | Tukar Hari |
| **Pak Dedi** | Atasan / Koordinator (kepala tim Security) | keduanya |
| **Bu Sari** | HRD (approver final) | keduanya |

---

## Persona detail

### 1. Andi — Pemohon Tukar Shift
- **Jabatan**: Satpam, `SECURITY-GROUP-1`. Jumat 5 Juli dijadwalkan **shift malam (19:00–07:00)**.
- **Tujuan**: ada acara keluarga malam tgl 5 → ingin pindah ke **shift pagi (07:00–19:00)** di tanggal yang sama, dengan menukar bersama rekan yang shift pagi.
- **Pain lama**: cukup izin lisan ke koordinator, tak ada jejak; sering bentrok karena tak tercatat.
- **Yang ia lakukan**: buka app → pilih tanggal (5 Juli) → pilih **rekan** (Citra) → kirim. Lalu menunggu Citra setuju, atasan, dan HRD.

### 2. Citra — Rekan tujuan (counterparty)
- **Jabatan**: Satpam, `SECURITY-GROUP-2`. Jumat 5 Juli dijadwalkan **shift pagi**.
- **Tujuan**: menerima permintaan tukar dari Andi → memutuskan **setuju / tolak**.
- **Yang ia lakukan**: terima notif "Andi minta tukar shift 5 Juli (pagi↔malam)" → lihat detail → **Setuju** (lanjut ke atasan) atau **Tolak** (pengajuan batal otomatis).
- **Catatan**: tanpa persetujuan Citra, pengajuan **tidak akan** sampai ke atasan.

### 3. Budi — Pemohon Tukar Hari
- **Jabatan**: Operator Produksi, `PRODUCTION-GROUP-1`. Dijadwalkan **kerja Sabtu 5 Juli**, **libur Senin 7 Juli**.
- **Tujuan**: ada urusan tgl 5 → ingin **libur tgl 5** dan **kerja tgl 7** sebagai gantinya. **Tanpa menukar dengan siapa pun** (unilateral).
- **Yang ia lakukan**: pilih `work_date` (7 Juli, yang tadinya libur) + `exchange_date` (5 Juli, yang tadinya kerja) → kirim. **Tidak** memilih rekan.
- **Beda dari Andi**: tidak ada langkah "consent rekan" — langsung ke atasan.

### 4. Pak Dedi — Atasan / Koordinator
- **Peran**: kepala tim/koordinator yang menilai dampak operasional (apakah tukar bikin shift kekurangan orang).
- **Yang ia lakukan**: terima pengajuan (Tukar Shift: **setelah** rekan setuju; Tukar Hari: langsung) → cek coverage → **Approve / Reject** (+ catatan).

### 5. Bu Sari — HRD
- **Peran**: persetujuan final + jejak administratif.
- **Yang ia lakukan**: terima setelah atasan approve → **Approve** → sistem menerapkan perubahan jadwal.

---

## Diagram Alur (Excalidraw)

![[Tukar Jadwal Kerja - Flow.excalidraw]]

> **Kiri** = Flow A (Tukar Shift, 3 langkah dengan rekan). **Kanan** = Flow B (Tukar Hari, unilateral). Warna: 🟨 pemohon · 🟪 keputusan (rekan/atasan/HRD) · 🟥 ditolak/batal · 🟩 diterapkan. Detail tekstual di bawah.

---

## Flow A — Tukar Shift (swap antar-rekan, 3 langkah)

```
Andi (pemohon)
  │ pilih tanggal 5 Juli + pilih rekan: Citra
  ▼
[1] Citra (rekan)  ──tolak──▶ BATAL (notif ke Andi)
  │ setuju
  ▼
[2] Pak Dedi (atasan)  ──tolak──▶ DITOLAK (notif ke Andi)
  │ approve
  ▼
[3] Bu Sari (HRD)  ──tolak──▶ DITOLAK (notif ke Andi)
  │ approve
  ▼
TERAPKAN: jadwal 5 Juli ditukar
  • Andi  : malam → pagi
  • Citra : pagi  → malam
  (jumlah orang per slot TETAP → coverage aman)
  │
  ▼
Notif "disetujui" ke Andi & Citra
```

**Notifikasi di tiap langkah**: Andi & Citra dapat update status; reviewer berikutnya dapat notif "perlu direview".

## Flow B — Tukar Hari (unilateral, tanpa rekan)

```
Budi (pemohon)
  │ work_date = 7 Juli (tadinya libur), exchange_date = 5 Juli (tadinya kerja)
  ▼
[1] Pak Dedi (atasan)  ──tolak──▶ DITOLAK
  │ approve
  ▼
[2] Bu Sari (HRD)  ──tolak──▶ DITOLAK     ← alur approval Tukar Hari masih TBD
  │ approve
  ▼
TERAPKAN: jadwal Budi
  • 5 Juli : kerja → LIBUR
  • 7 Juli : libur → kerja
  (TIDAK ada pengganti → slot 5 Juli berkurang 1 orang ⚠️)
```

---

## Titik keputusan yang masih TBD (kelihatan jelas di flow)

| Di langkah | Pertanyaan TBD | Persona terdampak |
|---|---|---|
| Pemilihan rekan (Andi) | Rekan **harus se-lokasi**? (Tinggarjaya vs pusat) | Andi, Citra |
| Penerapan Tukar Hari (Budi) | Boleh bikin slot **kekurangan orang**? minimum staffing? | Budi, Pak Dedi |
| Persetujuan (Pak Dedi) | Apakah sistem yang cek coverage, atau Pak Dedi manual? | Pak Dedi |
| Penerapan (siapa pun) | Boleh **dobel-shift berturut**? (kode belum cek) | semua |
| Approval Tukar Hari | Approver-nya atasan→HRD, atau beda? | Budi |

> Aturan yang **sudah pasti**: pemohon harus karyawan ber-shift; `exchange_date` minimal **H+3**; **tidak boleh dibatalkan** setelah disetujui. Lintas-role **mustahil** (slot per-role). Warehouse saat ini **dikecualikan**.

---

## Skenario Jalan Gagal (failure paths)

### Tukar Shift (Andi & Citra)
1. **Rekan menolak** — Citra menolak permintaan → status **Batal**, notif ke Andi. Andi boleh **ajukan ulang ke rekan lain**.
2. **Atasan menolak (coverage)** — Pak Dedi menilai shift malam jadi kurang orang → **Ditolak** + catatan. Notif ke Andi & Citra.
3. **HRD menolak** — Bu Sari menolak (mis. terlalu sering tukar / alasan tak valid) → **Ditolak**.
4. **Rekan beda role** — Andi (Security) memilih rekan Produksi → **ditolak sistem** (slot per-role; lintas-role mustahil). *(sudah pasti dari kode)*
5. **Rekan beda lokasi** — Andi (pusat) memilih rekan Tinggarjaya → **TBD** (kode belum cek pool per-lokasi; perlu keputusan).

### Tukar Hari (Budi)
6. **Slot jadi bolong** — Budi libur tgl 5 tanpa pengganti → shift kurang orang. Saat ini **bergantung penilaian atasan**; bisa **ditolak otomatis** hanya bila minimum staffing ditetapkan *(TBD)*.
7. **Dobel-shift berturut** — Budi kerja tgl 7 padahal mepet shift sebelumnya tanpa jeda → **kode belum mengecek** *(TBD)*.

### Validasi sistem (otomatis, sebelum sampai ke reviewer)
8. **Terlalu mepet (< H+3)** — `exchange_date` kurang dari 3 hari dari hari ini → **ditolak otomatis** ("minimal H+3").
9. **Non-shift / Warehouse** — karyawan non-shift atau Warehouse mengajukan → **403** (guard `IsShiftBasedSchedule`).
10. **Batalkan setelah disetujui** — pemohon mencoba cancel saat status sudah **Disetujui** → **tidak diizinkan** (cancel hanya saat **Menunggu**).

> Ringkas: penolakan bisa datang dari **3 sumber** — (a) **rekan** (consent, Tukar Shift saja), (b) **reviewer** (atasan/HRD, manual), (c) **sistem** (validasi otomatis: H+3, shift-only, status-cancel). Sumber (b) untuk coverage/dobel-shift masih manual karena guard otomatisnya **belum ada** (TBD).
