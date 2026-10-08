> Papan kerja hasil `/analisa-kebutuhan` 2026-10-08. Keputusannya di [[ADR - 0158 Scan Retur Gudang Dijaga Satu Kali dan Selaras dengan Pembukuan, Koreksi Bertahap]], cara kerja alurnya di [[Microservices - Manufacture Service]]. Berkas ini berubah tiap item selesai; keduanya di atas tidak.

# Daftar Task

Tahap **pagar** (T1–T4) berdiri sendiri dan boleh jalan lebih dulu. Tahap **koreksi** (T6–T8) **tidak boleh dimulai** sebelum T5 (dua keputusan) selesai. Aturan tim: perubahan yang menyentuh dua repo wajib berupa **satu issue induk di `bip-erp` + satu sub-issue `[BE]` dan `[FE]`**, tiap sub-issue satu brief dan satu PR; label `Siap Agent` dipasang manusia setelah ADR 0158 berstatus Diterima.

Dua brief draft sudah ada di `.task-plans/briefs/` (`2026-10-08-wms-retur-fe-kurang-dan-sisa.md`, `2026-10-08-wms-retur-be-batas-qty.md`) dan harus direvisi mengikuti ADR ini sebelum `/kerjakan` (lihat T0).

---

## Persiapan

### T0. Revisi kedua brief dan buat issue

Kedua brief ditulis sebelum analisa ini selesai dan memuat dua kekeliruan: `Sumber` menulis "tidak ada" (padahal ADR 0025 Decision #9 sudah memutuskan jumlah kurang hanya disorot, dan yang kita lakukan mengamandemennya), dan premisnya mengira penyebab duplikat adalah scan ulang (terukur: simpan ganda ≤60 detik 77%). Revisi: `Sumber` menunjuk ADR 0158 (setelah Diterima), tambah kriteria kunci Simpan dan idempotensi, tambah penanganan gagal-di-tengah-loop. Lalu buat issue induk + dua sub-issue.

Dependensi: ADR 0158 disetujui (✅ Diterima 2026-10-08).

---

## Pagar (D1–D5)

### T1. Kunci Simpan dan penanganan gagal di tengah [FE]

D1 dan bagian D5. Tombol Simpan form retur terkunci selama proses penyimpanan; bila satu baris gagal, baris itu tetap di form dan petugas melihat daftar yang gagal (pola yang sudah ada di form penerimaan surat jalan di layar yang sama). Fungsi murni dipisah dan diuji dengan kontrol negatif. Teks baru lewat i18n id+en.

Dependensi: T0.

### T2. Idempotensi dan batas kumulatif di layanan gudang [BE]

D1 (sisi server), D3, D4. Permintaan retur tertaut dengan referensi identik tidak menambah stok; total per (order, SKU) tidak boleh melebihi klaim per komponen (klaim per SKU listing dikali isi paket dari pemetaan paket yang sudah ada di layanan gudang); konfirmasi ke pembukuan membawa jumlah kumulatif. Ditolak = tidak ada transaksi dan stok tidak berubah. Uji lewat handler (bukan hanya fungsi murni). **Berhenti dan lapor** bila data klaim per komponen ternyata tidak tersedia di layanan gudang tanpa mengubah pembukuan, jangan menebak.

Dependensi: T0. Tidak bergantung pada T1; titik temunya hanya jalur galat penyimpanan (kontrak identik di kedua brief).

### T3. Konfirmasi saat kurang dan tawarkan hanya sisa [FE]

D2 dan D5. Jumlah kurang membuka konfirmasi yang menyebut barang dan selisihnya (jumlah lebih tetap diblokir); paket sebagian tercatat hanya menawarkan SKU yang belum tercatat, memakai daftar yang sudah dikirim backend (tipe layar perlu ditambah). Tanpa alasan yang disimpan.

Dependensi: T1 (berkas dan fungsi murni yang sama).

### T4. Ukur frekuensi jumlah kurang pada komponen paket (baca-saja)

Tidak menahan T1–T3. Mengisi celah ukur di ADR: berapa persen retur paket yang discan kurang dari klaim per komponen. Hasilnya masuk ADR 0158 sebagai koreksi bila angkanya mengubah asumsi D2.

Dependensi: tidak ada.

---

## Gerbang keputusan

### T5. Keputusan untuk membuka tahap koreksi

**Blocking untuk T6–T8.** (1) ✅ Tanggal dokumen saat koreksi: **mengikuti tanggal koreksinya** (diputuskan bagusizzanm, 2026-10-08; alasan dan konsekuensi di ADR 0158 §Sudah diputuskan). Sisa: kabari finance aturan ini sebelum T7 dibangun. (2) Aturan koreksi ke nol di pembukuan, masih terbuka. Hasilnya ditulis ke ADR 0158 §Belum diputuskan lalu status D6 diperbarui.

Dependensi: tidak ada.

---

## Koreksi (D6), setelah T5

### T6. Tinjau gerbang kewenangan jalur Proposal koreksi [repo kode, privat]

Prasyarat D6: pemeriksaan gerbang persetujuan pada jalur Proposal dikerjakan sebagai item terpisah dan **rincian temuannya hanya ditulis di issue repo kode (privat), bukan di vault** (vault publik). Setelah itu tentukan siapa yang boleh menyetujui koreksi urusan gudang.

Dependensi: T5.

### T7. Pembukuan menerima koreksi turun dan nol [BE integration]

Sesuai keputusan T5(2) dan aturan tanggal T5(1). Menyentuh pembukuan, jadi urutan deploy: pembukuan, layanan gudang, layar.

Dependensi: T5.

### T8. Proposal koreksi meneruskan jumlah kumulatif ke pembukuan [BE manufacture + FE]

D6. Setelah koreksi disetujui, jumlah transaksi, stok, dan jumlah yang dipegang pembukuan berubah dalam satu langkah; penolakan membatalkan semuanya. Layar riwayat membedakan koreksi retur tertaut dari koreksi biasa.

Dependensi: T6, T7.

---

## Dokumentasi

### T9. Prosedur manusia dan pembaruan dok

D7. Tulis prosedur gudang dan finance (periksa fisik, input hanya SKU yang belum tercatat, jangan scan ulang, kabari IT bila edit manual di Accurate) di tempat yang dibaca finance dan gudang, lalu koreksi pernyataan "tak ada jalur edit" di [[APP - Web ERP]] dan perbarui [[Microservices - Manufacture Service]] setelah T2 dan T3 deploy. Catatan: status [[ADR - 0144 Retur yang Sudah Dibukukan Manual oleh Finance Ditandai per Order dan Dihormati Semua Jalur Auto-Sync]] di vault tertinggal dari kode (endpoint 409 sudah ada); perbarui lewat `/sync-docs`, bukan di sini.

Dependensi: T2 dan T3 deploy untuk bagian pembaruan dok; prosedur manusia boleh terbit lebih dulu.

---

## Perintah pertama

`/brief` ulang untuk T0 setelah ADR 0158 disetujui, atau `/start-task T4` (pengukuran, baca-saja) bila ingin mulai tanpa menunggu persetujuan.
