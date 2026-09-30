> **Tipe:** Log operasional (hasil kerja agent backlog otonom), bukan dokumentasi arsitektur.
> **Periode:** September 2026 · **Konteks arsitektur:** [[RUN - Agent Backlog Otonom]] · [[ADR - 0143 Backlog Pindah dari Linear ke GitHub Project]]

# Agent Backlog Otonom, September 2026

Satu baris per issue yang disentuh agent. "Selesai" berarti PR terbuka (In Review), bukan Done: Done diisi manusia setelah terbukti dipakai.

## Pekerjaan

| Tanggal | Issue | Hasil | Mulai | Estimasi Selesai | Selesai | Ketepatan | Sebab terlambat | Pelajaran |
|---|---|---|---|---|---|---|---|---|
| 2026-09-29 | erp-frontend#1818 (21 panggilan `t()` ke key yang tak ada di kamus) | PR https://github.com/bip-itteam-internal/erp-frontend/pull/1888 | 2026-09-29 | 2026-09-30 | 2026-09-29 | tepat waktu | - | Uji coba pertama. Putaran awal berhenti karena gerbang dijalankan di latar belakang dalam mode headless; dilanjutkan dengan `--resume`, lalu prompt runner melarang perintah latar belakang. |
| 2026-09-29 | my-bharata#170 (detail perjalanan dinas masih menampilkan Uang Saku) | gagal (toolchain) | 2026-09-29 | 2026-09-30 | - | - | - | Mesin runner tak punya Flutter/Dart SDK, jadi gerbang `dart analyze` + `flutter test` pasti gagal; berhenti sebelum eksekutor. Temuan sudah diverifikasi ke kode dan brief siap dipakai (lokasi di komentar issue). Issue kembali ke Backlog. |
| 2026-09-29 | erp-frontend#1814 (label "Sesi organik" di halaman Live) | PR https://github.com/bip-itteam-internal/erp-frontend/pull/1902 | 2026-09-29 | 2026-09-30 | 2026-09-29 | tepat waktu | - | Gerbang test menuduh 9 kegagalan "baru" karena baseline berumur dua hari. Segarkan baseline di worktree bersih macet dua kali (vitest diam, CPU 1-2%), jadi dibuktikan tertarget: kegagalan yang sama muncul di basis tanpa diff. |
| 2026-09-29 | bip-erp#2171 (toko Lazada tanpa status nonaktif) | Butuh Info | - | - | - | - | - | Pola galat auth Lazada belum pernah terbukti dari kejadian nyata; pola Shopee/TikTok di `authDeadPatterns` diambil dari log, jadi pola Lazada tidak boleh dikarang. |
| 2026-09-29 | erp-frontend#1821 (halaman persetujuan koreksi presensi dan tukar shift tanpa pintu masuk) | Butuh Info | - | - | - | - | - | `/portal/persetujuan` (ADR 0114) sudah memuat Koreksi dan Tukar; nasib dua halaman lama dan sumber data penyetuju bagi pemohon belum diputuskan. |
| 2026-09-29 | bip-erp#2177 (jadwal sesi seleksi di luar kalender terpusat) | Butuh Info | - | - | - | - | - | Siapa "HR" di penyaringan feed kalender, template email ubah/batal untuk kandidat, dan definisi "batal" di data belum diputuskan. |
| 2026-09-29 | bip-erp#2173 (kunci simpan ulang skor KPI periode beku) | Butuh Info | - | - | - | - | - | Definisi "beku", tempat jejak alasan, dan pemecahan BE/FE belum ada. |
| 2026-09-29 | bip-erp#2176 (integritas data rekrutmen, lima masalah) | Butuh Info | - | - | - | - | - | Lima masalah dalam satu issue; tiga siap dikerjakan, dua butuh keputusan. Diminta dipecah supaya satu PR tidak menutup semuanya. |

## Pelajaran

- 2026-09-29 · erp-frontend#1818: test penuh erp-frontend sekitar 14 menit, jadi satu issue FE kecil memakan sekitar 30-40 menit dari brief sampai PR. Pakai angka ini sebagai dasar estimasi issue FE berikutnya.
- 2026-09-29 · 14 issue In Progress hasil migrasi Linear (erp-frontend #1845 #1859 #1866 #1867 #1877 #1878 #1879 #1880; bip-erp #2271 #2273 #2275 #2285 #2296 #2302) sudah lewat Estimasi Selesai tanpa PR tertaut. Empat di antaranya punya Estimasi Selesai lebih awal dari Mulai, jadi tanggalnya tenggat bawaan migrasi, bukan estimasi. Semuanya dipegang manusia, jadi agent menulis komentar "Terlambat" berisi fakta terukur dan meminta sebab + estimasi baru dari assignee, tanpa mengubah tanggalnya sendiri.
- 2026-09-29 · erp-frontend#1814: dari brief sampai PR sekitar 3 jam, bukan 30-40 menit. Suite penuh 20 menit di gerbang, ditambah percobaan menyegarkan baseline yang macet dua kali. Estimasi issue FE berikutnya perlu cadangan untuk baseline yang basi; menyegarkan baseline sebaiknya dilakukan runner sebelum putaran, bukan di tengah issue.
- 2026-09-29 · Issue hasil audit sering memuat beberapa masalah atau satu keputusan yang belum diambil ("Putuskan: …"). Pada putaran ini 5 dari 7 kandidat bug berakhir Butuh Info karena itu, bukan karena kodenya sulit.
