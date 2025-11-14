# Background

Saat ini pengajuan barang di perusahaan masih _paper-based_ dan ini memakan waktu lama untuk _approval_ dan dokumen _paper_ menumpuk. Diperlukan sistem pengajuan online yang handal dan terintegrasi dengan [[GA - Inventory Management]] 

## Features

 - Pengajuan online melalui mobile app
- _Approval_ ditujukan ke principal yang berkaitan (SPV masing-masing divisi, GA, Finance, dan Dirut)
- Setiap pengadaan yang sudah di _approve_, dan barang diterima, dilakukan verifikasi dahulu di GA untuk dilakukan pencatatan yang masuk ke [[GA - Inventory Management]] baru diserahkan ke yang bersangkutan

## Consideration

This feature of GA required new Finance System to be build exclusively for this, which is bad in pratice, as we would probbly rush both system, and they would be clueless with their system altogether

We're better off creating some feature that is exclusively used by GA and Finance first so we can introduce them to their system instead of heavy burdening them with this feature as their first feature

## Requirements

- [ ] Employee Master Data
- [ ] Asset Master Data

## Dependencies

- [ ] [[GA - Inventory Management]]
- [ ] [[DB - Employees Master Data]]