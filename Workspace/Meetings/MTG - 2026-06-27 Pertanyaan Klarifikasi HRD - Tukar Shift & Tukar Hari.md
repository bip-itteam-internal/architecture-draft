---
publish: false
---

# Pertanyaan Klarifikasi HRD — Tukar Shift & Tukar Hari

- **Tanggal disusun**: 2026-06-27
- **Tujuan**: bahan diskusi sebelum redesign fitur tukar shift/hari
- **Terkait**: [[MTG - 2026-06-26 Hasil Meeting HRD]] (keputusan shift-only), [[MTG - 2026-06-26 Diskusi HRD - Koreksi Presensi & Tukar Shift]]

## Konteks (kenapa perlu ditanya)

Implementasi sekarang adalah model **satu orang** — pemohon menggeser jadwalnya sendiri:
- Tidak ada **pihak kedua** (rekan yang ikut tergeser) di data maupun alur.
- Tidak ada cek **coverage/kapasitas** shift. Kalau pemohon pindah slot sepihak, slot lama bisa kosong & slot tujuan dobel tanpa kontrol.

Sebelum ngoding ulang, perlu jelas dulu **maksud bisnisnya**. Pertanyaan di bawah dikelompokkan; jawaban menentukan apakah cukup pembatasan kecil atau perlu model baru (swap antar-rekan + consent + coverage).

---

## Struktur fitur yang disepakati (2026-06-27)

Nama payung fitur: **Tukar Jadwal Kerja**. Berisi **dua sub-fitur** dengan model berbeda:

| Sub-fitur | Definisi | Pihak terlibat | Alur persetujuan |
|---|---|---|---|
| **Tukar Shift** | Tukar **slot jam** dengan rekan (role ber-shift) | Pemohon **+ rekan** | rekan (consent) → atasan → HRD |
| **Tukar Hari** | Geser **hari kerja/libur** sendiri, **tanpa pengganti** | Pemohon saja | TBD (atasan → HRD?) |

- **Tukar Shift** = swap antar-rekan (jawaban Q1–Q6); coverage terjaga otomatis **bila** rekan di slot pool yang sama.
- **Tukar Hari** = unilateral, **tidak menggeser orang lain** (Q2: "gak perlu pengganti"). Alur approval-nya belum ditetapkan.

> **Implikasi dok:** published `HRIS - Shift Exchange` akan **di-rename → `HRIS - Tukar Jadwal Kerja`** dan direstruktur jadi 2 sub-fitur **saat redesign diimplementasikan**. Untuk sekarang dok itu tetap grounded ke kode lama (single-person).

---

## 1. Konsep & ruang lingkup

1. "Tukar shift" yang dimaksud = **swap dengan rekan** (rekan ikut bertukar jadwal), atau cukup **ubah jadwal sendiri** (seperti sekarang)? bisa tukar dengan rekan dengan, dengan 3 step yaitu rekan yang mau tukar, atasan dan hrd
2. "Tukar hari" (kerja di hari libur → ambil libur pengganti) dianggap **fitur yang sama** dengan tukar shift, atau **dipisah**? tukar hari gak perlu pengganti
3. Apakah perlu membedakan jelas antara: (a) ganti **slot jam** di hari sama, vs (b) geser **hari kerja↔libur**?

## 2. Persetujuan rekan (consent)

4. Kalau swap antar-rekan: rekan yang dituju **harus menyetujui dulu** sebelum atasan, atau atasan bisa langsung memutuskan? ya, rekan yang dituju **harus menyetujui dulu** sebelum atasan,
5. Kalau rekan **menolak** → pengajuan otomatis batal? ya
6. Siapa yang memilih rekan — pemohon sendiri, atau ditentukan/disetujui SPV? ya pemohon yg memilih rekan

## 3. Coverage / kapasitas shift

7. Siapa yang menjamin **jumlah orang per slot tetap terpenuhi**? Sistem (paksa swap 1:1) atau **SPV cek manual**?
8. Boleh tidak pengajuan yang membuat **satu slot kosong** (mis. tak ada rekan pengganti, cuma geser sendiri)?
9. Ada **minimum staffing** per slot per role (mis. Security minimal X orang/slot) yang harus dijaga?

## 4. Aturan role & batasan

10. Konfirmasi role ber-shift: **hanya Security, Host Live, Production**? Ada role shift lain (driver, cleaning, dll.)?
11. Swap boleh **lintas-role**, atau **hanya dalam role/tim yang sama**?
12. Batasan jam: boleh **dobel-shift berturut** (mis. pagi lalu malam di hari sama)? Ada **jeda minimum** antar-shift?
13. Slot shift yang berlaku saat ini — konfirmasi masih benar?
    - Security: `07:00–19:00`, `19:00–07:00`
    - Production: `08:00–16:00`, `16:00–00:00`, `00:00–08:00`
    - Host Live: `07:00–15:00`, `12:00–20:00`, `16:00–24:00`, `08:00–16:00`

## 5. Tukar hari / libur pengganti / comp-off

14. "Kerja di hari libur nasional → libur pengganti" termasuk fitur tukar shift, atau **comp-off/lembur** yang terpisah?
15. Libur pengganti **harus di bulan yang sama** (aturan sekarang)? Atau boleh diakumulasi/dibawa ke bulan berikut?
16. Kerja di hari libur → dapat **uang lembur**, cukup **libur pengganti**, atau keduanya?

## 6. Alur persetujuan

17. Approver tetap seperti sekarang?
    - Karyawan biasa: Kepala dept → HR
    - Supervisor: HR → Direktur
    - Staff/SPV HR: jalur khusus
18. Keputusan **SPV HRD step-1 auto-approve** (lihat [[MTG - 2026-06-26 Hasil Meeting HRD]] poin 3) berlaku juga di tukar shift?

## 7. Batas waktu & pembatalan

19. `exchange_date` minimal **H+3* dari hari ini — tetap
20. Boleh **batalkan setelah disetujui**? Sampai kapan (mis. sebelum H-1)? ya gaboleh dibatalkan

## 8. Payroll & dampak lain

21. Tukar shift berdampak ke **tunjangan shift** (mis. tunjangan shift malam ikut pindah ke orang yang menggantikan)?
22. Ada dampak ke **perhitungan keterlambatan/SP** bila slot berubah?

---

## Yang menentukan besar pekerjaan

| Jawaban HRD | Implikasi teknis |
|---|---|
| Cukup "ubah jadwal sendiri" | Selesai — tinggal guard shift-only (sudah). |
| Swap antar-rekan + consent | **Model baru**: field counterparty, tahap persetujuan rekan, `applyApprovedShiftExchange` tukar 2 entri, validasi coverage. |
| Comp-off dipisah | Fitur/sub-flow tersendiri di luar "tukar shift". |
