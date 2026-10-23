> **Status**: 🟢 Diterima, 2026-10-23, oleh irfanarfianto (Pemutus): "buatkan agar menjadi seperti perusahaan umumnya dan bisa membuat perusahaan lebih baik lagi". Rincian butir 1 sampai 9 diputuskan orkestrator atas mandat itu dan ditulis di sini supaya bisa ditinjau. Melanjutkan [[ADR - 0122 Satgas Per-PIC Input Bebas Gantikan Form Builder, SLA Temuan dan Skor dari Approval]] dan **mengubah** §5 (rumus skor) serta §4 (approve tanpa jalan balik). Belum diimplementasikan.

## Untuk Manajemen

Satgas 5R & K3 dibuat setara cara kerja inspeksi di perusahaan pada umumnya:

- **Tiap temuan punya kategori (5R atau K3), tingkat keparahan (ringan, sedang, berat), dan lokasi.** Dengan itu bahaya keselamatan tidak lagi diperlakukan sama dengan meja berdebu, dan laporan bisa menjawab "area mana yang paling sering bermasalah".
- **Petugas bisa meminta perbaiki ulang** bila foto perbaikan belum menunjukkan perbaikan, bukan hanya menyetujui.
- **Atasan langsung ikut diberi tahu**: seketika untuk temuan K3 berat, dan otomatis saat tenggat terlewat.
- **Pengingat sehari sebelum tenggat**, dan petugas diberi tahu saat foto perbaikan masuk.
- **Tanggapan mencatat cara perbaikan dan pencegahannya**, wajib untuk temuan berat.
- **Rekap** per orang, per lokasi, per kategori, tren bulanan, dan temuan yang berulang di lokasi yang sama.

**Yang berubah bagi karyawan:** skor kebersihan Office Boy & Security dihitung dari **tingkat keparahan** temuan, bukan dari jumlah foto, mulai **periode bulan berikutnya setelah rilis**.

**Yang tidak dijanjikan:** tetap **bukan** Surat Peringatan dan **bukan** potongan gaji. Menahan clock-out tetap dorongan agar temuan ditanggapi.

## Deskripsi

*Satgas per-PIC ([[ADR - 0122 Satgas Per-PIC Input Bebas Gantikan Form Builder, SLA Temuan dan Skor dari Approval]]) ditambah atribut temuan yang lazim (kategori, prinsip 5R, keparahan, lokasi), siklus CAPA ringan (keterangan perbaikan + pencegahan), jalan balik "perbaiki ulang", eskalasi berjenjang ke atasan langsung, pengingat, dan rekap untuk perbaikan berkelanjutan. Skor KPI diturunkan dari keparahan.*

- **Status**: 🟢 Diterima, belum diimplementasikan
- **Tanggal**: 2026-10-23
- **Dasar desain**: Figma `BUV8afcBrNSbkmm0qI8EYz` halaman "Satgas (Petugas)" (MyBharata petugas S1-S11, OB/Security O1-O7) dan `eYcaRMmESsa7XqacmyX13B` halaman "Satgas (Petugas)" (Web W1-W7), diperbarui mengikuti ADR ini.

## Context

1. ADR 0122 sudah memenuhi inti inspeksi: temuan berfoto, tenggat, bukti perbaikan, verifikasi petugas, skor bulanan. Dibandingkan praktik umum audit 5S dan inspeksi K3 (temuan → PIC + atasan → perbaikan bertenggat → verifikasi → eskalasi berjenjang → rekap dan pencegahan), ada tujuh lubang yang tercatat di sesi 2026-10-23:
   - petugas tak bisa menolak foto perbaikan yang belum memadai (`handleSatgasFindingApprove` hanya responded → approved);
   - atasan tak pernah dilibatkan; satu-satunya eskalasi adalah menahan clock-out;
   - tak ada tingkat keparahan, jadi bahaya K3 tak punya jalur cepat;
   - tak ada lokasi maupun kategori;
   - tak ada pengingat sebelum tenggat, dan petugas tak diberi tahu saat foto masuk;
   - tak ada catatan sebab/pencegahan;
   - tak ada rekap per area dan tren.
2. Notifikasi yang ada hanya dua, keduanya ke orang yang terkena temuan: saat dicatat (`satgas_finding.go:239`) dan saat clock-out ditahan (`satgas_finding_escalate.go:192`).
3. Resolusi atasan per department sudah ada di employee-service (`SupervisedDepartmentsStrict`, dipakai [[ADR - 0111 Inspeksi 5R Area per Department sebagai Catatan Non-KPI dengan Peringatan ke Supervisor]]); atasan langsung dari `work_data` (`is_supervisor` + `department`).
4. Peraturan Perusahaan tidak mengatur inspeksi 5R/K3 (ADR 0122 Context 6). Perubahan ini menyentuh skor KPI, bukan uang atau sanksi, jadi tidak ada pasal yang dilanggar; ADR ini catatannya.

## Decision

### 1. Atribut temuan: kategori, prinsip 5R, keparahan, lokasi

Field baru di `satgas_finding` (semua ditulis petugas saat mencatat):

| Field | Nilai | Wajib |
|---|---|---|
| `kategori` | `5r` \| `k3` | ya |
| `prinsip` | `ringkas` \| `rapi` \| `resik` \| `rawat` \| `rajin` (5R) | opsional, hanya untuk `5r` |
| `keparahan` | `ringan` \| `sedang` \| `berat` | ya |
| `lokasi` | teks bebas, mis. "Toilet pria lt. 2", ≤ 120 karakter | ya |
| `lokasi_department` | nama ASLI master department (bukan label grup HRGA) | opsional |

Temuan lama tanpa atribut ini dibaca `kategori=5r`, `keparahan=sedang`, `lokasi` kosong.

### 2. Tenggat bawaan mengikuti keparahan

Bawaan: ringan **3 hari**, sedang **2 hari**, berat **1 hari**. Petugas boleh mengubahnya, kecuali temuan **berat** yang paling lama 1 hari.

### 3. Perbaiki ulang (jalan balik verifikasi)

`POST /satgas-findings/:id/revisi {alasan, tenggat_hari}` oleh petugas.
- Transisi `responded` → `open`, dengan `deadline` baru. Riwayatnya disimpan di `revisi[] {alasan, oleh, pada, deadline_baru}`, dan orangnya diberi tahu.
- Paling banyak **2 kali** per temuan. Sesudah itu petugas wajib memilih setujui atau tutup gagal, supaya tak ada bolak-balik tanpa ujung.
- Foto perbaikan lama tetap tersimpan; foto baru ditambahkan.

### 4. Tanggapan = foto + keterangan perbaikan + pencegahan (CAPA ringan)

Tanggapan karyawan menambah dua field: `response.keterangan` (apa yang diperbaiki) dan `response.pencegahan` (agar tidak terulang).
- Keduanya **opsional** untuk ringan dan sedang.
- `pencegahan` **wajib** untuk keparahan **berat**: status baru berpindah ke `responded` bila foto **dan** pencegahan sudah ada.

### 5. Eskalasi berjenjang ke atasan langsung

| Kejadian | Diberi tahu |
|---|---|
| Temuan dicatat | Orang yang terkena temuan (sudah ada) |
| Temuan **K3 berat** dicatat | + **atasan langsung** orang itu, seketika |
| H-1 tenggat, belum ada tanggapan | Orang yang terkena temuan (pengingat) |
| Foto perbaikan masuk | **Petugas pencatat** |
| Diminta perbaiki ulang | Orang yang terkena temuan |
| Tenggat lewat tanpa tanggapan | + **atasan langsung**, otomatis, sekali |
| Clock-out ditahan | Orang yang terkena temuan (sudah ada) + atasan langsung |
| Disetujui | Orang yang terkena temuan |

- **Atasan langsung** = supervisor department orang itu, lewat resolver yang sudah ada. Tak ada penyalinan aturan hierarki ke modul Satgas.
- Atasan **membaca** temuan bawahannya (web dan MyBharata) tanpa bisa mencatat atau menyetujui. Cakupannya `SupervisedDepartmentsStrict`, sama dengan ADR 0111.
- Notifikasi memakai kategori inbox `satgas-temuan` yang sudah terdaftar. Pemetaan label/ikon/tujuan di MyBharata wajib eksplisit (team-memory § kategori inbox).
- Tindakan saat tenggat lewat **tetap pilihan petugas** (tahan clock-out / tutup gagal, ADR 0122 §3). Yang otomatis hanya pemberitahuan ke atasan.

### 6. Skor KPI dari keparahan (mengganti ADR 0122 §5)

Skor bulanan = `max(0, 100 − Σ potongan)`; tanpa temuan = 100 (tetap).

| Penyelesaian | Ringan | Sedang | Berat |
|---|---|---|---|
| Disetujui, foto masuk sebelum tenggat terakhir | 2 | 5 | 10 |
| Ditutup gagal, atau lewat tenggat tanpa tanggapan | 10 | 20 | 30 |
| Tambahan per perbaiki ulang | +2 | +2 | +2 |

- Temuan `open` yang masih dalam tenggat **menunggu**, tidak dipotong (tetap).
- Rumus ini berlaku untuk temuan yang dicatat **mulai periode bulan berikutnya setelah rilis BE**. Temuan sebelum itu tetap dihitung dengan rumus ADR 0122 supaya skor bulan berjalan tidak berubah di tengah jalan.
- Satu fungsi skor di sumber KPI (`kpi_sumber_inspeksi_satgas.go`); rekap §7 memanggil fungsi yang sama, tanpa rumus kedua.

### 7. Rekap untuk perbaikan berkelanjutan

`GET /satgas-findings/rekap?period=YYYY-MM` untuk pemegang `kepatuhan.satgas.view`/`.input` (seluruh perusahaan) dan atasan (cakupan bawahannya). Isinya:
- skor per orang;
- jumlah temuan per lokasi dan per kategori/prinsip;
- tren 6 bulan;
- **temuan berulang**, yaitu lokasi yang sama dengan ≥ 2 temuan dalam 30 hari.

Web menampilkannya di tab **Rekap**; MyBharata cukup ringkasan kecil di daftar.

### 8. Tetap sama dari ADR 0122

Pencatatan bebas tanpa form, subjek orang (OB/Security), foto maks 15, tahan clock-out sebagai dorongan, tutup gagal, dan kategori inbox `satgas-temuan`.

### 9. Sengaja tidak dilakukan

- Modul P2K3 atau komite K3.
- Audit checklist terjadwal per area (itu track Inspeksi Area, ADR 0111).
- Sanksi atau potongan gaji.
- Penilaian manual angka oleh petugas.

## Consequences

### Yang membaik
- Bahaya keselamatan (K3 berat) punya jalur cepat dan sampai ke atasan seketika.
- Verifikasi bermakna: foto yang tidak memadai bisa dikembalikan, bukan terpaksa disetujui.
- Atasan ikut bertanggung jawab atas area dan timnya, seperti praktik umum.
- Rekap per lokasi dan temuan berulang memberi bahan perbaikan struktural (alat, jadwal, pembagian tugas), bukan sekadar menghukum orang.

### Yang memburuk atau tetap terbuka
- ⚠️ **Skor KPI berubah rumus** mulai periode berikutnya. Harus diumumkan ke Office Boy, Security, dan atasan sebelum berlaku.
- Form pencatatan bertambah empat isian. Ini diimbangi bawaan tenggat otomatis dan pilihan berbentuk chip.
- Cakupan atasan bergantung pada data `is_supervisor` + `department` yang benar. Department tanpa supervisor tidak punya penerima eskalasi: pemberitahuan dicatat sebagai terlewat, bukan galat.

### Konsekuensi deploy
- BE dulu (employee-service: model, revisi, notifikasi, rekap, sumber KPI), lalu web dan MyBharata.
- Kategori inbox tidak bertambah, jadi notification-service tidak perlu naik bersama.
- Pengingat H-1 dan pemberitahuan tenggat lewat butuh penjadwal di employee-service (pola cron yang sudah ada).

## Dokumen Terkait
- [[ADR - 0122 Satgas Per-PIC Input Bebas Gantikan Form Builder, SLA Temuan dan Skor dari Approval]] — yang dilanjutkan dan diubah §4/§5
- [[ADR - 0111 Inspeksi 5R Area per Department sebagai Catatan Non-KPI dengan Peringatan ke Supervisor]] — resolusi supervisor per department yang dipakai ulang
- [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]] — mekanisme tahan clock-out
- [[ADR - 0071 Peta Kepatuhan Peraturan Perusahaan dan Kewajiban ADR untuk Penyimpangan]]
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]
