# ANALISA - Serapan Anggaran per Departemen dan Pagu Gabungan

Papan kerja hasil `/analisa-kebutuhan` atas permintaan Cost Control untuk tabel Serapan per pos, 2026-10-15. Keputusannya di [[ADR - 0178 Serapan Anggaran per Departemen Jurnal, Seluruh Perusahaan Dihapus, Pagu Gabungan per Departemen]] (🟢 Diterima 2026-10-15). Cara kerjanya di [[Finance - Serapan Anggaran dan Cost Control]].

## Kebutuhan sebenarnya, dipisah dari yang diminta

**Yang diminta:** tujuh perubahan pada tabel.
1. Kelompok per divisi.
2. Terpakai di kiri, Anggaran di kanan.
3. Sisa diganti Varians.
4. % Varians.
5. Anggaran gabungan.
6. KPI = total seluruhnya.
7. Arti "Seluruh perusahaan".

**Yang sebenarnya dibutuhkan:** Cost Control harus bisa melihat, **per divisi per bulan**, apakah belanja masih dalam **pagu yang memang mereka tetapkan**. Pagu itu sering berupa kelompok akun, bukan per akun Accurate.

Sistem saat ini menyimpan seluruh RAPB Oktober sebagai "Seluruh perusahaan" (38 dari 38 baris, prod 2026-10-15). Akibatnya pemantauan per divisi mustahil, apa pun bentuk tabelnya.

## Jawaban Finance yang sudah didapat

- "Seluruh perusahaan" itu inputan awal sistem. Laporan harus mengikuti tag departemen jurnal, dirinci UMUM dan marketing, tanpa baris seluruh perusahaan.
- RAPB diinput per divisi per bulan.
- Pagu gabungan berlaku per divisi per bulan.
- Rumus varians: Varians = Terpakai − Anggaran; minus berarti anggaran masih tersedia.

## Masih ditanyakan ke Finance

Tidak menahan T1–T3.

1. Apakah "Packing Sadewa" = 6109 Beban Packing Pihak Ketiga?
2. Daftar akun persis untuk pagu "lain-lain marketing", termasuk status 6102 Bonus & Insentif.
3. % Varians saat anggaran 0: tampil "—" atau 0%?
4. Nama pagu supaya tidak bentrok dengan akun 6111 "Beban Lain-lain Marketing".

## Task berurutan

Setiap task satu repo dan satu PR. ADR 0178 🟢 Diterima 2026-10-15 (Azzerith). Issue induk bip-erp#3102; sub-issue: T1 erp-frontend#2438, T2 bip-erp#3103, T3 erp-frontend#2439, T4 bip-erp#3104, T5 erp-frontend#2440.

| # | Repo | Task | Bergantung | Catatan |
|---|---|---|---|---|
| T0 | (Finance, manual) | Unggah ulang RAPB Oktober dan seterusnya **dengan kolom Departemen** (UMUM, MARKETING - KY + GB, MARKETING - BEAUTYHACKS, MARKETING - BAHAN PANGAN) | — | Template sudah punya kolom Departemen. Prasyarat T2 naik prod |
| T1 | erp-frontend | Tampilan tabel Serapan: kelompok per divisi + subtotal, kolom Terpakai → Anggaran, Varians = Terpakai − Anggaran dan % Varians dihitung di **satu** fungsi di `lib/serapan.ts`, berlaku juga di sheet rincian pos | ADR Diterima | Field `varians` backend **tidak** dibalik. Konsumen lain tetap bertanda lama. Anggaran 0 → "—" (sambil menunggu jawaban Finance 3) |
| T2 | bip-erp (integration) | Baris departemen kosong tidak lagi keluar di `/accounting/anggaran/varians` dan tidak ikut `RingkasVarians`. Upload dan form anggaran menolak baris tanpa departemen. Realisasi tanpa departemen tampil sebagai "Tanpa departemen" | ADR Diterima | Periksa konsumen baris (akun, ""): `cariPos` sisa pos pengajuan, panel OPEX Marketing, sumber KPI `varians_anggaran`. **Deploy sesudah T0** |
| T3 | erp-frontend | Sesuaikan konsumen yang bersandar pada baris "Seluruh perusahaan": `cariPos`/kotak sisa pos, kartu Anggaran pengajuan, sheet rincian pos, label dropdown departemen di form anggaran | T2 | Deploy sesudah T2 |
| T4 | bip-erp (integration) | Pagu gabungan: entitas + upload/CRUD (nama, departemen, tahun, bulan, nominal, akun anggota). Varians pagu = Σ realisasi anggota di departemen itu. Satu akun per departemen per bulan hanya satu pagu dan tidak beranggaran sendiri. Pagu ikut `RingkasVarians` | T2, jawaban Finance 1, 2, 4 | Kontrak baru → BE dulu |
| T5 | erp-frontend | Pagu gabungan di layar: baris pagu di tabel Serapan (kelompok divisi), rincian anggota di sheet, isian/upload pagu di tab Anggaran Bulanan | T4 | — |

## Verifikasi per tahap

- **T2:** total kartu dan KPI `varians_anggaran` Oktober tidak lagi memuat baris kosong. Ukur prod sebelum dan sesudah, lalu bandingkan dengan Σ baris per departemen.
- **T4:** satu akun yang menjadi anggota pagu **dan** punya anggaran sendiri ditolak saat upload; ada test-nya.
- **Semua:** cek layar di browser oleh Cost Control dengan RAPB yang sudah per departemen.
