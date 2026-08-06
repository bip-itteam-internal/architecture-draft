## Deskripsi

*Sistem pengajuan barang & pengadaan (procurement) online untuk menggantikan proses paper-based yang lambat, terintegrasi dengan [[GA - Inventory Management]].*

- **Status**: 🟡 Konsep / Direncanakan. **Digantikan sebagai acuan kerja** oleh [[GA - Form Pengadaan dan Pengajuan Dana]], yang bertumpu pada dua form kertas yang benar-benar dipakai. Dokumen ini dipertahankan karena memuat pertimbangan urutan pengerjaan yang masih berlaku (lihat bab Pertimbangan).

## Latar Belakang

Saat ini pengajuan barang di perusahaan masih _paper-based_ dan ini memakan waktu lama untuk _approval_ dan dokumen _paper_ menumpuk. Diperlukan sistem pengajuan online yang handal dan terintegrasi dengan [[GA - Inventory Management]] 

## Fitur

* Pengajuan online melalui mobile app
- _Approval_ ditujukan ke principal yang berkaitan (SPV masing-masing divisi, GA, Finance, dan Dirut)
- Setiap pengadaan yang sudah di _approve_, dan barang diterima, dilakukan verifikasi dahulu di GA untuk dilakukan pencatatan yang masuk ke [[GA - Inventory Management]] baru diserahkan ke yang bersangkutan

## Pertimbangan

Fitur GA ini membutuhkan Finance System baru yang dibangun khusus untuk ini, yang secara praktik kurang baik, karena kita kemungkinan akan terburu-buru membangun kedua sistem, dan mereka akan kebingungan dengan sistem mereka secara keseluruhan

Lebih baik kita membuat dulu beberapa fitur yang khusus digunakan oleh GA dan Finance sehingga kita bisa memperkenalkan mereka ke sistem mereka, alih-alih membebani mereka dengan fitur ini sebagai fitur pertama mereka

## Kebutuhan

- [ ] Employee Master Data
- [ ] Asset Master Data

## Dependensi

- [ ] [[GA - Inventory Management]] (sebagai lookup untuk barang yang harus selalu tersedia)
