---
publish: false
---

# Laporan Progres Tim IT

- **Tanggal**: 2026-06-26
- **Jenis**: Meeting internal tim IT (progres per area)

---

## Marketing Integration
- **Kondisi**: Penanganan rate limit Shopee berjalan, data sudah masuk ke Shopee. Sedang mengerjakan filter toko per tim marketing, analisis status cancel (by user/system), dan perbandingan revenue sesuai waktu.
- **Kendala**: Limit API & webhook harus jaga success rate >90% selama 7 hari berturut; beberapa fitur tertahan menunggu meeting intensif dengan user & manufaktur.
- **Rencana**: Jaga kestabilan webhook untuk lewati ambang 7 hari; jadwalkan meeting dengan user & manufaktur untuk requirement filter/analisis.

## Finance Integration
- **Kondisi**: Finance rewrite/integrasi berjalan, engine siap menunggu data product.
- **Kendala**: Data product belum terisi.
- **Rencana**: Data product diisi tim finance via sheet/CSV/manual.

## HR
- **Kondisi**: Shift exchange & attendance correction sudah di production. Modul recruitment & landing page recruitment dalam pengembangan.
- **Kendala**: Integrasi attendance & shift exchange ke MyBharata belum jalan.
- **Rencana**: Lakukan integrasi attendance & shift exchange ke MyBharata.

## WMS
- **Kondisi**: Sedang testing di server testing; anggota baru mulai ikut terlibat.
- **Kendala**: Validasi alur terhambat menunggu input user.
- **Rencana**: Jadwalkan meeting intensif dengan user.

## Infra
- **Kondisi**: CI/CD dengan Harness & Docker agent berjalan; migrasi server ke cloud sedang proses; titik CCTV gudang baru sudah dikirim.
- **Kendala**: Sering mati listrik & internet down (di luar kontrol IT) → webhook Shopee & TikTok terputus, padahal harus selalu on untuk data transaksi realtime & success rate >90%; absensi ikut terganggu.
- **Rencana**: Percepat migrasi cloud agar layanan tak bergantung listrik/internet kantor.

---

## Catatan relevansi (pekerjaan attendance/koreksi)

- **"Shift exchange & attendance correction sudah di production"** — perbaikan terbaru (pertahankan jam clock-in asli, apply tukar shift sinkron, notif Bahasa Indonesia, comment "disetujui oleh approver") masih di branch `feat/recruitment-service` / **PR #156** — pastikan apakah sudah ikut ter-deploy ke production atau belum. Lihat [[HRIS - Attendance Correction]] & [[HRIS - Tukar Jadwal Kerja]].
- **"Integrasi attendance & shift exchange ke MyBharata belum jalan"** — termasuk follow-up tertunda: **MyBharata kirim `employee_id` di guestbook internal** (mengaktifkan guard anti-fraud koreksi telat end-to-end). Deploy BE dulu sebelum FE kirim (handler `DisallowUnknownFields`).

## Tindak lanjut lintas-tim (capture)
- [ ] Meeting requirement filter/analisis Marketing dengan user & manufaktur
- [ ] Tim finance isi data product (sheet/CSV)
- [ ] Integrasi attendance + shift exchange → MyBharata (sinkron dengan deploy BE)
- [ ] Meeting validasi alur WMS dengan user
- [ ] Percepat migrasi cloud (mitigasi mati listrik/internet)
