## Deskripsi

*Registrasi produk & **izin edar (NIE)** ke **BPOM** untuk Bharata International Pharmaceutical. **Scaffold** — definisi standar publik; daftar produk & nomor izin edar spesifik Bharata = (TBD).*

- **Status**: 🔴 Stub — kerangka; data izin edar Bharata belum ada
- **Induk**: [[QA - Big Pictures]]

## Latar Belakang

- Produk obat hanya boleh beredar bila punya **Nomor Izin Edar (NIE)** dari BPOM. NIE punya masa berlaku & wajib diperpanjang. Penjualan via marketplace ([[Sales - Marketplace Integration]]) tetap terikat aturan ini.

## Ruang Lingkup / Cakupan (business view)

- Daftar produk + status registrasi + NIE + masa berlaku — (TBD)
- Alur perpanjangan/registrasi baru + reminder kedaluwarsa NIE — (TBD; potensi kait ke [[Microservices - Notification Service]])
- Variasi/notifikasi perubahan ke BPOM — (TBD)

## Konsumen Data

- [[Sales - Marketplace Integration]] / [[Microservices - Integration Service]] — hanya produk ber-NIE valid yang boleh dijual (TBD enforcement)
- [[Microservices - Inventory Service]] — kaitan SKU ↔ NIE (TBD)

## Belum Diputuskan (TBD)

- Sumber data izin edar (spreadsheet QA? sistem BPOM?) & siapa pemiliknya.
- Apakah validasi NIE-aktif perlu jadi cek otomatis sebelum listing produk.

## Dokumen Terkait

- [[QA - Big Pictures]] · [[QA - CPOB (GMP)]] · [[REF - Glossary]]
- [[Sales - Marketplace Integration]] · [[Microservices - Integration Service]]
