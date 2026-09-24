## Deskripsi

*Sistem pemeliharaan gedung — penanganan kerusakan, kebersihan, dan sanitasi gedung. Item #14 pada [[GA - Big Pictures]].*

- **Status**: 🟡 Draft / Direncanakan (modul khususnya belum ada). Pelaporan kerusakan saat ini berjalan lewat tiket Manajemen Tugas, lihat di bawah. **Diperbarui 2026-09-24**: sisi **perawatan berkala** kini punya keputusan sendiri, [[ADR - 0123 Preventive Maintenance Berjadwal per Aset di Inventory Service, Skor dari Penyelesaian Berbukti]] (🟡 Diusulkan, kode belum ada).

## Yang Sudah Berjalan (tanpa modul khusus)

Diukur di prod 2026-09-17:

- **Kerusakan gedung dilaporkan sebagai tiket** di space task-management **`Building Maintenance`** (divisi General Affair; anggota: dua `GA Staff`; stage Request → Todo → On Going → Done; tanpa tipe tiket; prioritas tanpa jam SLA). Isinya **9 tiket** Juni-September 2026, 3 Done dan 6 Todo. Beberapa tiket bukan pekerjaan gedung (uji penugasan, simpan dokumen, alat kosmetik), jadi space ini belum dipakai secara disiplin. Aplikasinya [[Microservices - Task Management Service]].
- **Pengaju menilai perbaikan** (CSAT 1..5) di web ERP atau MyBharata begitu tiket Done; hanya pembuat tiket yang boleh menilai.
- 🟡 **KPI kerusakan dihitung dari tiket itu**: sumber `kinerja_tiket` metrik `selesai_dinilai` = tiket selesai yang dinilai pengaju (bukan penangannya sendiri) ÷ tiket ditugaskan (bip-erp PR [#1962](https://github.com/bip-itteam-internal/bip-erp/pull/1962) + erp-frontend PR [#1638](https://github.com/bip-itteam-internal/erp-frontend/pull/1638), merged 2026-09-17, terverifikasi DEV, belum deploy PROD). Metrik biaya belum punya sumber; metrik preventive kini punya rancangan ([[ADR - 0123 Preventive Maintenance Berjadwal per Aset di Inventory Service, Skor dari Penyelesaian Berbukti]]) tetapi belum ada kodenya. Rinciannya di [[HRIS - Matriks KPI per Departemen]].
- ⛔ **Metrik preventive dinilai tanpa dasar apa pun sampai rancangan itu dibangun.** Diukur di `employee_db` prod 2026-09-24: periode 2026-08, metrik `Realisasi Preventif Maintenance Building & Fasilitas` (bobot 0,30) bernilai **100** sementara tidak ada satu pun catatan jadwal maupun realisasi di sistem yang bisa menghasilkan angka itu. Ia bukan metrik kosong yang terlihat kosong, melainkan metrik kosong yang **terlihat bekerja**.
- **Belum terjawab (TBD), dipersempit 2026-09-24:** [[ADR - 0123 Preventive Maintenance Berjadwal per Aset di Inventory Service, Skor dari Penyelesaian Berbukti]] menetapkan **perawatan berkala** tinggal di [[Microservices - Inventory Service]], bersebelahan dengan `repair_history` dan `ga_opname`. Yang **masih terbuka** hanya sisi **perbaikan kerusakan**: tiket Manajemen Tugas atau `repair_history` yang menjadi catatan resmi GA. Keduanya masih mencatat hal yang sama.

## Perawatan Berkala (preventive) — cara kerjanya

🟡 **Dirancang, belum ada kodenya.** Keputusan dan alasannya di [[ADR - 0123 Preventive Maintenance Berjadwal per Aset di Inventory Service, Skor dari Penyelesaian Berbukti]]; bagian ini menyimpan cara kerjanya.

Metriknya rasio, jadi sistemnya menyimpan **dua** hal, dan selama ini yang ada nol-duanya:

| Bagian | Isinya | Perannya |
|---|---|---|
| `pm_jadwal` | per aset: pekerjaan + frekuensi (bulanan, triwulan, semesteran, tahunan) | **penyebut** — jatuh tempo diturunkan dari sini, tidak diketik |
| `pm_realisasi` | penyelesaian + tanggal + pelaksana + **foto sebelum/sesudah wajib** + status verifikasi | **pembilang** |

```
Realisasi PM = realisasi terverifikasi ÷ jatuh tempo pada periode × 100
```

Tiga aturan yang menentukan dan mudah tergerus kalau tidak ditulis:

- **Bukti wajib.** Realisasi tanpa foto tidak sah. Tanpa ini, "menandai selesai" kembali jadi swa-nilai berbaju baru.
- **SPV menolak bukti, bukan memberi nilai.** Perannya menjaga bukti, bukan menaksir kinerja. Itu yang membedakan cacahan dari pendapat.
- ⛔ **Berbasis penyelesaian, bukan pengecualian.** Tanpa bukti bernilai **nol**, bukan seratus. Ini sengaja berbeda dari [[ADR - 0122 Satgas Per-PIC Input Bebas Gantikan Form Builder, SLA Temuan dan Skor dari Approval]] §5 yang menetapkan "tanpa temuan → penuh". Model itu benar untuk inspeksi kebersihan dan **terbalik arah** untuk perawatan berkala: "tidak ada yang mencatat" akan bernilai 100, padahal itu justru keadaan gagalnya.

Realisasi yang masih `menunggu` saat periode tutup **keluar dari pembilang dan penyebut**, supaya kepatuhan teknisi tidak ditentukan kecepatan SPV memverifikasi. Konsekuensinya tunggakan harus terlihat beserta umurnya di layar verifikasi.

⚠️ **Ukuran keberhasilannya bukan modulnya jadi.** Pekerjaan teknisi hari ini tercatat di dokumen Google bulanan (tab per bulan sejak Desember 2025, berisi tanggal, keterangan, lokasi, foto sebelum/sesudah), dan ada dokumen kedua berisi daftar aset yang dirawat. Selama dokumen itu masih dipakai, sistemnya hanya menambah tempat keempat untuk mengetik. Daftar aset di dokumen kedua itu pula yang menjadi isi awal `pm_jadwal`, dan mengisinya pekerjaan GA, bukan dev.

## Ruang Lingkup

- **Kerusakan gedung**: pelaporan → perbaikan (corrective)
- **Kebersihan & sanitasi** gedung (jadwal & pemantauan)
- **Preventive maintenance** elemen gedung

## Fitur / Proses yang Direncanakan

- Lapor kerusakan (lokasi, foto) → tindak lanjut perbaikan; bila butuh barang/jasa → [[GA - Procurement System]] (rujukan form: *Form Perbaikan Barang GA*)
- Jadwal kebersihan & sanitasi + checklist ([[GA - Checklist Management]])
- Riwayat pemeliharaan per area/aset gedung (terkait [[GA - Inventory Management]])

## Dependensi / Dokumen Terkait

- [[GA - Big Pictures]]
- [[ADR - 0123 Preventive Maintenance Berjadwal per Aset di Inventory Service, Skor dari Penyelesaian Berbukti]] (perawatan berkala) · [[ADR - 0122 Satgas Per-PIC Input Bebas Gantikan Form Builder, SLA Temuan dan Skor dari Approval]] (cetakan approve, model skor yang sengaja dibedakan)
- [[GA - Procurement System]] · [[GA - Inventory Management]] · [[GA - Checklist Management]] · [[GA - Audit Internal System]]
- [[Microservices - Task Management Service]] · [[Microservices - Inventory Service]] · [[HRIS - Matriks KPI per Departemen]] · [[GA - Dashboard per Posisi]]
