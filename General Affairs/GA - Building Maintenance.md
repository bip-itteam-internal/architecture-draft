## Deskripsi

*Sistem pemeliharaan gedung — penanganan kerusakan, kebersihan, dan sanitasi gedung. Item #14 pada [[GA - Big Pictures]].*

- **Status**: 🟡 Draft / Direncanakan (modul khususnya belum ada). Pelaporan kerusakan saat ini berjalan lewat tiket Manajemen Tugas, lihat di bawah.

## Yang Sudah Berjalan (tanpa modul khusus)

Diukur di prod 2026-09-17:

- **Kerusakan gedung dilaporkan sebagai tiket** di space task-management **`Building Maintenance`** (divisi General Affair; anggota: dua `GA Staff`; stage Request → Todo → On Going → Done; tanpa tipe tiket; prioritas tanpa jam SLA). Isinya **9 tiket** Juni-September 2026, 3 Done dan 6 Todo. Beberapa tiket bukan pekerjaan gedung (uji penugasan, simpan dokumen, alat kosmetik), jadi space ini belum dipakai secara disiplin. Aplikasinya [[Microservices - Task Management Service]].
- **Pengaju menilai perbaikan** (CSAT 1..5) di web ERP atau MyBharata begitu tiket Done; hanya pembuat tiket yang boleh menilai.
- 🟡 **KPI kerusakan dihitung dari tiket itu**: sumber `kinerja_tiket` metrik `selesai_dinilai` = tiket selesai yang dinilai pengaju (bukan penangannya sendiri) ÷ tiket ditugaskan (bip-erp PR [#1962](https://github.com/bip-itteam-internal/bip-erp/pull/1962) + erp-frontend PR [#1638](https://github.com/bip-itteam-internal/erp-frontend/pull/1638), dibuka 2026-09-17, belum merge). Metrik preventive dan biaya belum punya sumber. Rinciannya di [[HRIS - Matriks KPI per Departemen]].
- **Belum terjawab (TBD):** riwayat perbaikan aset di [[Microservices - Inventory Service]] (`repair_history`) juga mencatat perbaikan. Mana yang menjadi catatan resmi GA untuk kerusakan gedung belum diputuskan.

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
- [[GA - Procurement System]] · [[GA - Inventory Management]] · [[GA - Checklist Management]] · [[GA - Audit Internal System]]
- [[Microservices - Task Management Service]] · [[Microservices - Inventory Service]] · [[HRIS - Matriks KPI per Departemen]] · [[GA - Dashboard per Posisi]]
