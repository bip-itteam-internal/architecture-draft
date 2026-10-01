> **Tipe:** Log operasional (hasil kerja agent backlog otonom), bukan dokumentasi arsitektur.
> **Periode:** Oktober 2026 · **Konteks arsitektur:** [[RUN - Agent Backlog Otonom]] · [[ADR - 0143 Backlog Pindah dari Linear ke GitHub Project]] · Bulan sebelumnya: [[LOG - Agent Backlog Otonom 2026-09]]

# Agent Backlog Otonom, Oktober 2026

Satu baris per issue yang disentuh agent. "Selesai" berarti PR terbuka (In Review), bukan Done: Done diisi manusia setelah terbukti dipakai.

## Pekerjaan

| Tanggal | Issue | Hasil | Mulai | Estimasi Selesai | Selesai | Ketepatan | Sebab terlambat | Pelajaran |
|---|---|---|---|---|---|---|---|---|
| 2026-10-01 | erp-frontend#1819 (slip gaji web tanpa PIN) | Butuh Info | - | - | - | - | - | Perbaikan keamanan, rincian di issue. Issue meminta memilih satu dari dua opsi; salah satunya ternyata juga menyentuh notification-service, jadi pilihannya dikembalikan ke manusia. |
| 2026-10-01 | bip-erp#2178 (masa evaluasi ke kontrak) | Butuh Info | - | - | - | - | - | Tiga butir lintas recruitment + employee + FE, masing-masing butuh keputusan (jarak pengingat, bentuk usulan kontrak, kunci peserta). Diusulkan dipecah tiga. |
| 2026-10-01 | bip-erp#2172 (toko Care Space Skin berhenti order) | Butuh Info | - | - | - | - | - | Pemeriksaan operasional (Seller Center, log sync prod), bukan perubahan kode. |
| 2026-10-01 | bip-erp#2190 (QC barang masuk tertaut penerimaan) | Butuh Info | - | - | - | - | - | Penyatuan dua register QC adalah keputusan tanpa ADR. |
| 2026-10-01 | bip-erp#2191 (CAPA dari komplain) | Butuh Info | - | - | - | - | - | Prasyarat bip-erp#2251 sedang In Progress dipegang orang lain. |
| 2026-10-01 | bip-erp#2194 (stok FG keluar dari order otomatis) | Butuh Info | - | - | - | - | - | Titik pemicu, hubungan dengan Accurate, dan backfill belum diputuskan. |
| 2026-10-01 | bip-erp#2195 (rantai rencana produksi sampai batch record) | Butuh Info | - | - | - | - | - | Empat dokumen dan status MO baru tanpa ADR; diusulkan dipecah per sambungan. |
| 2026-10-01 | bip-erp#2254 (kalender jatuh tempo pajak & reminder) | Butuh Info | - | - | - | - | - | Sudah ada di kode lewat modul Tax Control (feed `tax_due`, pengingat H-7/H-3). Audit salah menunjuk `obligation_templates` calendar-service (mesin sesi wajib karyawan), sehingga angka nol di sana terbaca seperti fitur yang belum ada. Manusia diminta memindahkan status. |
| 2026-10-01 | bip-erp#2298 (reminder piutang jatuh tempo) | Butuh Info | - | - | - | - | - | Penerima, ambang, cakupan, dan kanal belum diputuskan; deskripsinya sendiri sudah menyatakan butuh keputusan. |
| 2026-10-01 | erp-frontend#1873 (perbandingan quotation antar vendor) | Butuh Info | - | - | - | - | - | Banding harga antar pemasok sudah ada di dialog Harga pemasok (data historis Accurate). Yang belum jelas: cukup pintu masuk sendiri, atau penawaran baru per pengajuan (butuh ADR). |
| 2026-10-01 | bip-erp#2280 (dashboard status temuan audit) | Butuh Info | - | - | - | - | - | Temuan tak punya status tindak lanjut sejak [[ADR - 0098 Audit Internal Beralih ke Uji Petik Dua Arah Manual]], dan layar audit pindah ke aplikasi `audit-bharata`. Arti "open/closed" harus diputuskan dulu. |
| 2026-10-01 | erp-frontend#1860 (arsip bukti potong / faktur pajak) | Butuh Info | - | - | - | - | - | Arsip BPE + bukti bayar per kewajiban sudah ada; bukti potong dan faktur pajak belum, dan arah/metadata-nya perlu diputuskan. |
| 2026-10-01 | bip-erp#2224 (dashboard KPI integrasi) | Butuh Info | - | - | - | - | - | Metrik dan pembaca tidak disebut. |
| 2026-10-01 | bip-erp#2242 (dashboard legal/sekretariat) | Butuh Info | - | - | - | - | - | Bergantung pada bip-erp#2258/#2259 yang sedang dikerjakan manusia; register masih kosong. |
| 2026-10-01 | bip-erp#2246 (dashboard KPI quality) | Butuh Info | - | - | - | - | - | Rumus reject rate dan sumber komplain belum ditentukan; model CAPA sedang berubah di issue lain. |
| 2026-10-01 | bip-erp#2284 (rasio likuiditas otomatis) | Butuh Info | - | - | - | - | - | Neraca Accurate bisa dibaca, tetapi daftar rasio, penggolongan akun lancar, dan tempat tampilnya belum diputuskan. |
| 2026-10-01 | bip-erp#2287 (budget per project) | Butuh Info | - | - | - | - | - | Arti "project" dan granularitas anggaran belum diputuskan. |
| 2026-10-01 | erp-frontend#1858 (jadwal audit periodik per divisi) | Butuh Info | - | - | - | - | - | Modul audit sudah pindah ke `audit-bharata`; cakupan audit non-finance dan visibilitas di kalender belum diputuskan. |
| 2026-10-01 | erp-frontend#1861 (rekonsiliasi pajak vs accounting) | Butuh Info | - | - | - | - | - | Pasangan yang direkonsiliasi dan akun per jenis pajak belum ditentukan; butuh BE juga. |
| 2026-10-01 | erp-frontend#1862 (alert realisasi melebihi budget) | Butuh Info | - | - | - | - | - | Ambang, penerima, dan kanal belum diputuskan. |
| 2026-10-01 | erp-frontend#1864 (jadwal bayar vendor & reminder) | Butuh Info | - | - | - | - | - | Tampilan saja vs rencana bayar yang ditetapkan belum jelas; bersinggungan dengan payment request erp-frontend#1866 yang sedang dikerjakan. |
| 2026-10-01 | erp-frontend#1882 (audit trail login & perubahan data) | Butuh Info | - | - | - | - | - | Arsitektur audit trail lintas modul adalah lubang yang belum diputuskan di [[REF - PRD ERP]]; layak ADR dulu. |
| 2026-10-01 | bip-erp#2316 (kontrak vendor & reminder) | Butuh Info | - | - | - | - | - | Pola pengingat kontrak sedang dibuat manusia di bip-erp#2258; dikerjakan paralel berisiko melahirkan dua pola. |
| 2026-10-01 | bip-erp#2304 (stok opname gudang packing) | Butuh Info | - | - | - | - | - | Belum ada modul opname dan stok sistem gudang packing kosong; opname gudang material sedang dikerjakan di erp-frontend#1868. |

## Pelajaran

- 2026-10-01 · bip-erp#2262 (dipegang manusia) lewat Estimasi Selesai 2026-09-30 tanpa PR tertaut. Diperlakukan sama dengan issue hasil migrasi sebelumnya: komentar "Terlambat" ke assignee, tanggal tidak diubah agent.
- 2026-10-01 · Putaran ini tidak menghasilkan PR. Dari 42 kandidat Low/Medium tanpa assignee: 17 punya PIC manusia di badannya; 16 issue induk atau sub-issue (terblokir sub-issue BE berlabel Butuh Info, induknya sudah In Review, atau induknya dipegang orang lain); satu sudah dikerjakan PR lain dan menunggu manusia memindahkan statusnya (erp-frontend#1836); satu terblokir toolchain (my-bharata#170, mesin tanpa Flutter); dan tujuh issue hasil audit yang semuanya butuh keputusan. Kolam kandidat yang bisa dikerjakan agent tanpa keputusan baru sudah habis; putaran berikutnya hanya produktif bila ada jawaban di issue Butuh Info atau issue baru yang spesifikasinya sudah diputuskan.
- 2026-10-01 (putaran kedua) · Kembali nol PR. Ke-17 kandidat audit yang tersisa diberi label Butuh Info dengan pertanyaan spesifik, supaya putaran berikutnya tidak membaca ulang issue yang sama tanpa hasil. Satu temuan yang perlu diingat: deskripsi audit bisa menunjuk **mesin yang salah**. bip-erp#2254 ditulis "mesin kewajiban ada, 0 template terisi", padahal fiturnya sudah hidup di modul lain (Tax Control); grep nama domain (`pajak_*`) di service pemiliknya menemukan itu dalam satu perintah.
- 2026-10-01 · Issue Butuh Info tidak diberi Mulai/Estimasi Selesai dan tidak diumumkan ke grup WA, karena keputusan "ragu" sudah bisa diambil dari membaca issue + mengukur `origin/main`, sebelum pekerjaan dimulai.
