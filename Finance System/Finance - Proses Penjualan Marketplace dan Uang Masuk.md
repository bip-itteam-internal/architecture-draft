# Finance - Proses Penjualan Marketplace dan Uang Masuk

## Deskripsi

*Proses P3, penjualan marketplace dan uang masuk, dari [[Finance - Proses Bisnis dan Kebutuhan Sistem]]. Dok ini memuat tujuan, cara dikerjakan hari ini, yang sudah ada di ERP, alur target di sistem, celah yang harus ditutup, kontrol yang wajib dijaga, dan ukuran untuk membuktikan efisiensinya. Penilaian cakupan dan kesesuaiannya ada di dok induk.*

- **Status**: ⚠️ **Implemented (ada catatan)**. Sinkron marketplace ke Accurate berjalan; pemetaan toko ke CV dan penjualan per CV 🟡 direncanakan (T8).
- **Sumber**: survei alur kerja Finance (isian mandiri 14 sampai 16 September 2026, butir bertanda *survei 2026-09*), kode `bip-erp` dan `erp-frontend` di `origin/main` 2026-09-17. Keadaan prod bertanggal di tiap butir; ukur ulang sebelum dipakai memutuskan.
- **Kelompok celah**: **A** sudah ada, tinggal dipakai · **B** sudah ada, perlu diperbaiki · **C** belum ada, perlu dibangun (definisi di dok induk).

## Tujuan

Penjualan, potongan platform, dan penarikan saldo tercatat benar per toko dan per entitas tanpa rekap manual, lalu dipakai bersama pencatatan, pajak, dan pemeriksaan.

## Hari ini (*survei 2026-09*)

Penjualan diekspor dari ERP ke basis data kerja setiap hari; tiap awal bulan dashboard, ERP, dan Accurate dicocokkan; penarikan per CV direkap lewat alat web terpisah di luar ERP; data penarikan diolah ulang per CV (pecah bundling, kuantitas, HPP) untuk invoice CV dan omzet pajak. Data penarikan sering telat sampai ke pengolahnya.

## Sudah ada di ERP

Sinkron order marketplace dan pengiriman faktur harian, retur, serta penerimaan ke Accurate ([[Microservices - Integration Service]]); rute rekonsiliasi income dan rekap kuantitas (`bip-erp/services/integration/main.go:1780-1783`); dompet marketplace dengan saldo, penarikan, dan rekonsiliasi settlement (`main.go:1905-1907`). Halaman **Auto-Sync Penerimaan** (`erp-frontend/src/app/(main)/integration-accurate/receipts/page.tsx`) punya tab **Perlu Tindakan** berisi penerimaan `FAILED` sejak 1 September 2026 (`SEJAK_PERLU_TINDAKAN`, `receipts/lib/receipt-tabs.ts`; sebelum tanggal itu sudah disesuaikan manual). Jumlahnya tampil di badge tab, dan kolom Error diberi satu kalimat tindakan di atas galat teknisnya (`tindakanReceipt`, `receipts/lib/tindakan-receipt.ts`; erp-frontend #1705). Contoh: selisih nilai terhadap dana cair (beserta arah dan nominalnya, diperbaiki lewat Koreksi Manual lalu Retry), gangguan Accurate (cukup Retry), diubah manual di Accurate, atau menunggu settlement. Isi galat menang atas `hold_reason`, karena label `ACCURATE_OUTAGE` pernah menempel pada penerimaan yang sebenarnya tak balance. Pemberitahuannya sengaja di halaman ini, bukan Telegram (ditolak Finance) dan bukan menu Rekonsiliasi.

## Alur target

Toko dipetakan ke entitas CV di master CV → sistem menghasilkan penjualan, potongan, dan penarikan per CV → Junior Accountant memakainya untuk jurnal CV, Tax untuk omzet, Senior Accountant memeriksa. Tidak ada rekap ulang.

## Celah

- **C** Pemetaan toko ke CV dan penjualan per CV (T8). Hari ini `accurate_shops` tidak punya field CV ([[REF - Kepemilikan Data]] § Duplikasi).
- **C** Aturan kolom yang tidak boleh dijumlahkan ikut tertulis di rancangan ([[Finance - Buku Besar CV]] § Gerbang kolom).
- **TBD** Isi, aturan, dan pemilik alat web rekap penarikan CV ditelusuri sebelum T8 dirancang, supaya tidak membangun tandingannya dari nol.
- **TBD** Income yang belum masuk sinkron dan masih diinput manual: kanal dan penyebabnya belum diukur.
- **B** Penerimaan TikTok gagal tak balance karena potongan statement `DEDUCTIONS_INCURRED_BY_SELLER` pada order RETURNED tak terbawa ke penerimaan. Terukur prod 2026-09-23: penerimaan 16 dan 22 September, masing-masing selisih Rp10.000. Titik putusnya di penyusunan penerimaan belum ditemukan (**TBD**). Jalan sementaranya Koreksi Manual lalu Retry, sesuai kalimat tindakan di tab Perlu Tindakan. Dua penerimaan lain berselisih −Rp198.000 dan −Rp99.000 dengan sebab yang belum diurai (**TBD**).
- **B** Beban ongkir Shopee salah hitung pada pesanan yang punya `final_shipping_fee` — akun ongkir kelebihan dan kelebihannya mendarat di beban admin. Terukur prod 2026-09-22: **3.865 pesanan, Rp98.260.427**, masih bertambah ±Rp16 jt/bulan. Kas tidak terpengaruh, jadi tak pernah memunculkan galat. 🟡 [[ADR - 0118 Ongkir Shopee Dihitung Aktual Dikurangi Bagian Pembeli dan Subsidi]] (diusulkan, belum di kode).

## Kontrol wajib

Satu kolom dihitung sekali; kolom yang merupakan bagian dari kolom lain tidak dijumlahkan.

## Risiko pencatatan ganda

Faktur, retur, dan penerimaan marketplace sudah dikirim otomatis ke Accurate, sementara penjualan per CV juga dijurnal manual. Bila keduanya mencatat transaksi yang sama untuk entitas yang sama, penjualan terhitung dua kali. Buku mana yang menjadi dasar laporan CV masih TBD nomor 1 di [[Finance - Buku Besar CV]]; T8 wajib menjawabnya sebelum menerbitkan jurnal penjualan CV.

## Ukuran efisiensi

Jam rekap penjualan per hari; jumlah selisih dashboard, ERP, dan Accurate pada pencocokan awal bulan; tanggal data penarikan tersedia bagi pengolah.

Sumber data baseline: Hasil pencocokan tanggal 1 (selisih); catatan pelaku rekap (jam rekap dan tanggal data tersedia, TBD bentuknya).

## Dokumen Terkait

- [[Finance - Proses Bisnis dan Kebutuhan Sistem]] · [[Finance - Kalender dan Rantai Tenggat]] · [[Finance - Sambungan dan Permintaan Data Lintas Departemen]] · [[Finance - FAT Persona]]
- [[Microservices - Integration Service]] · [[REF - Kepemilikan Data]] · [[Finance - Buku Besar CV]]
