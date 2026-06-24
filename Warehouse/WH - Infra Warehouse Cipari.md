## Deskripsi

*Rencana **infrastruktur (upcoming)** untuk **warehouse baru di samping kantor utama**. Karena lokasinya bersebelahan dengan kantor utama, jaringannya dapat diperluas dari infra kantor yang sudah ada. Dokumen ini mencatat rencana; detail teknis (IP, jumlah perangkat, vendor) masih **TBD**.*

- **Status**: 🔜 Upcoming / Perencanaan
- **Lokasi**: bersebelahan dengan kantor utama (memudahkan extend jaringan & akses)
- **Cakupan**: Jaringan & WiFi · Server/NVR/CCTV · Integrasi ERP (attendance & inventory)

## Jaringan & WiFi

- [ ] Perluasan LAN dari kantor utama ke gedung warehouse (kabel/uplink switch) — TBD
- [ ] Pemasangan **WiFi AP** untuk area warehouse
- [ ] **Daftarkan MAC AP baru ke `company_wifi`** di [[Microservices - Attendance Service]] agar karyawan warehouse bisa **clock-in via mobile** (validasi geofencing WiFi kantor)
- [ ] Tentukan **koordinat GPS** warehouse (untuk validasi lokasi attendance jika perlu)
- [ ] Internet/koneksi cadangan — TBD

> Catatan: **tidak ada mesin fingerprint** yang direncanakan untuk warehouse baru — absensi mengandalkan **aplikasi mobile** ([[APP - MyBharata]]) dengan validasi WiFi/geofencing. Bila berubah, serial mesin perlu masuk allowlist attendance.

## Server / NVR / CCTV

- [ ] Perangkat **on-site** (server lokal / NVR / CCTV) — kebutuhan & spesifikasi TBD
- [ ] Penempatan & power/UPS, jaringan untuk NVR/CCTV — TBD
- [ ] Integrasi/akses ke inventaris VM & server (lihat [[IT - Server, VMs and Databases]]) bila ada perangkat baru yang perlu dicatat

## Integrasi ERP (attendance & inventory)

- [ ] **Attendance**: jadwal/shift warehouse (definisi shift Warehouse sudah ada di seeding attendance) + clock-in mobile via WiFi baru — lihat [[HRIS - Attendance System]]
- [ ] **Inventory / Warehouse module**: operasional stok/inbound-outbound di lokasi baru — lihat [[WH - Management System]], [[WH - Inbound (Receiving)]], [[WH - Outbound (Sending)]]
- [ ] Penyesuaian master data (lokasi/gudang) bila diperlukan

## Yang Perlu Diputuskan (TBD)

- Topologi jaringan: extend VLAN kantor utama vs subnet terpisah
- Jumlah & tipe WiFi AP + cakupan area
- Spesifikasi server/NVR/CCTV + vendor
- Apakah perlu koordinat GPS / radius geofencing khusus warehouse
- Timeline & PIC pemasangan

## Dokumen Terkait

- [[WH - Management System]]
- [[Microservices - Attendance Service]]
- [[IT - Server, VMs and Databases]]
- [[APP - MyBharata]]
