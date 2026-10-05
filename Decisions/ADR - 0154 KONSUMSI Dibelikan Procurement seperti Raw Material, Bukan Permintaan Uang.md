# ADR - 0154 KONSUMSI Dibelikan Procurement seperti Raw Material, Bukan Permintaan Uang

> **Status**: 🟢 **Diterima**, 2026-10-05, oleh pengguna Tech Development dalam sesi kerja. Fase 1 (bagian §1 sampai §6) dikerjakan lebih dulu; §7 dicatat sebagai keputusan untuk fase berikutnya. Nomor 0154 diklaim saat push; bila sudah terpakai, geser ke nomor bebas berikutnya.

%% Vault ini PUBLIK. Nama orang dan employee_id tidak ditulis; yang disebut hanya angka agregat, departemen, dan posisi. %%

## Untuk Manajemen

**Masalahnya.** Konsumsi (pantry, jamuan, konsumsi rapat) selama ini diajukan sebagai **permintaan uang**: pengaju HRGA mengetik nominal sendiri, uangnya ditransfer, lalu dicatat sebagai pengeluaran kas. Tidak ada yang membandingkan harga, tidak ada yang mencatat barangnya datang, dan stok konsumsi GA tidak pernah bertambah dari pembelian itu.

**Yang diputuskan.** Konsumsi diperlakukan sebagai **pembelian barang**, sama seperti Raw Material: pengaju hanya menyebut barang dan jumlahnya, Procurement mengisi harga dan pemasok, persetujuan Finance dan Direktur memakai harga Procurement, lalu Gudang GA memeriksa dan menerima barangnya ke stok konsumsi GA. Tetap hanya HRGA yang mengajukan, dan tetap dibayar PT Bharata.

## Deskripsi

*Tipe pengajuan `KONSUMSI` dipindah dari cabang uang (seperti `DANA`) ke cabang pembelian (seperti `RAWMATERIAL`). Menggantikan bagian "rantai identik DANA" di [[ADR - 0090 KONSUMSI Eskalasi ke Direktur di Ambang Berbagi, Bukan Kebal]]; ambang Direktur berbagi dari ADR itu tetap berlaku, kini dihitung dari harga Procurement.*

- **Tanggal**: 2026-10-05
- **Sumber desain**: draf "Pembelian Barang Umum, Raw Material, dan Konsumsi" (artifact privat, 5 Oktober 2026), issue `bip-erp#2597` (Konsumsi), `#2595` (Raw Material), `#2596` (Barang Umum).
- **Diukur ke**: bip-erp `origin/main` (`services/procurement/pengajuan_barang_jenjang.go`, `pengajuan_barang_gate.go`, `pengajuan_barang_stok.go`, `pengajuan_barang_jurnal.go`), `services/inventory/`, data PROD baca-saja 2026-10-05.
- **Hubungan dengan dok lain**:
  - [[ADR - 0090 KONSUMSI Eskalasi ke Direktur di Ambang Berbagi, Bukan Kebal]]: §1 ("jenjang identik DANA") dan §4 ("yang identik rantai persetujuannya") **digantikan**. §2 (ambang berbagi Rp 5 juta) tetap.
  - [[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]]: Konsumsi kini memakai pola pembekuan dua tahap (`JenjangSetelahHarga`) milik tipe barang.
  - [[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]]: tidak ada tahap baru di fase 1, jadi peta penyetuju tidak berubah.

## Context

**Keadaan kode sebelum keputusan ini (terverifikasi `origin/main` 2026-10-05).**

- `JenjangUntukTipeBarang("KONSUMSI", …)` = `[pb_spv_divisi bila pengaju bukan SPV] → pb_finance_setujui_bayar → pb_spv_finance → [pb_direktur bila nominal ≥ ambang] → pb_ap_transfer → pb_spv_transfer → pb_accounting_catat`. Rantai ini dibekukan penuh saat diajukan karena nominalnya diketik pengaju.
- `PengajuMengisiHarga` mewajibkan harga per item dari pengaju; `tipePakaiTalangan` memuat KONSUMSI (penanda "sudah ditalangi" + lampiran wajib); `TipeMenerbitkanJurnal` memuat KONSUMSI (pembukuan Pembayaran Kas & Bank lewat Accounting).
- `departemenPerTipe[KONSUMSI]` = `Human Resource`, `General Affair`; `TipeSelaluDibayarPTBharata` memuat KONSUMSI.

**Data PROD 2026-10-05 (baca-saja).** Koleksi `pengajuan_barang` berisi **0 dokumen KONSUMSI** (juga 0 UMUM dan 0 RAWMATERIAL; yang ada hanya DANA 87 dan IKLAN 18). Tidak ada dokumen Konsumsi berjalan yang terdampak perubahan alur.

**Departemen HRGA di PROD.** `General Affair` ber-`supervised_by` `Human Resource`; `Human Resource` tak punya induk. Hanya **satu** orang ber-`is_supervisor` di kedua departemen itu, sehingga ia satu-satunya yang menaungi HRGA.

## Decision

### 1. KONSUMSI lewat Procurement, seperti RAWMATERIAL

`KONSUMSI` masuk `tipeLewatProcurement`. Jenjang awal yang dibekukan saat diajukan:

```
[pb_spv_divisi] → pb_procurement_beli
```

Sesudah Procurement mengisi harga, `JenjangSetelahHarga` membekukan sisanya dengan ekor gudang GA:

```
pb_finance_setujui_bayar → pb_spv_finance → [pb_direktur] → pb_ap_transfer → pb_qc_ga → pb_terima_ga
```

Ambang Direktur (Rp 5 juta, berbagi, inklusif) dihitung dari **nilai barang yang diisi Procurement**, bukan dari angka pengaju.

### 2. Atasan dilewati bila pengajunya SPV (menyimpang dari draf)

Draf desain meminta atasan HRGA **selalu** ada, seperti `pb_spv_manufactur`. Itu **ditolak** untuk fase ini: di PROD hanya satu orang yang menaungi HRGA, sehingga Konsumsi yang ia ajukan sendiri tak akan punya penyetuju (pengaju dilarang menindak tahap persetujuannya sendiri). Aturannya tetap seperti sekarang: `pb_spv_divisi` dilewati bila pengaju menaungi departemennya. Mata kedua tetap ada di Cost Control, SPV Finance, dan Direktur.

### 3. Pengaju menyebut barang dan jumlah, tanpa harga dan tanpa talangan

KONSUMSI keluar dari `PengajuMengisiHarga` dan dari `tipePakaiTalangan`. Harga nol sah saat diajukan, persis seperti UMUM/RAWMATERIAL. Konsumsi yang sudah dibayar dari kantong pengaju (penggantian) bukan lagi Konsumsi; itu diajukan sebagai **DANA**.

### 4. Pembukuan mengikuti pembelian, bukan jurnal Kas & Bank

KONSUMSI keluar dari `TipeMenerbitkanJurnal`, sehingga tidak lagi mendapat `pb_spv_transfer` dan `pb_accounting_catat`. Pembukuannya memakai jalur faktur pembelian yang sama dengan UMUM/RAWMATERIAL. Penyeragaman AP → SPV Finance → Accounting untuk ketiga tipe barang adalah §7, bukan fase ini.

### 5. Diterima ke stok konsumsi GA, bukan dilahirkan sebagai aset

Barang Umum di `pb_terima_ga` dilahirkan sebagai aset per unit (`AksiStokLahirkanAset`). Konsumsi tidak: ia **menambah angka `ga_stok`** (stok perlengkapan/konsumsi GA yang sudah ada). Karena inventory-service hari ini hanya punya jalur *mengurangi* `ga_stok` (`/internal/ga-stok/kurangi`) dan *melahirkan aset* (`/internal/stok-dari-pengajuan`), dibutuhkan jalur **menambah** `ga_stok` dengan bentuk yang sama: dipanggil antar-service, idempoten per kunci penerimaan. Aksi stok ditentukan oleh **tahap dan tipe**, bukan tahap saja.

QC dan Terima memakai izin yang sudah ada (`budget.terima.ga`, paket Budget: Gudang GA) di fase ini.

### 6. Yang TIDAK berubah

- Hanya departemen `Human Resource` dan `General Affair` yang boleh mengajukan KONSUMSI.
- KONSUMSI selalu dibayar PT Bharata (`TipeSelaluDibayarPTBharata`).
- KONSUMSI tetap tipe terpisah dari UMUM untuk pelaporan.

### 7. Diputuskan untuk fase berikutnya (belum dikerjakan)

Diambil dari draf desain, berlaku untuk UMUM, RAWMATERIAL, dan KONSUMSI sekaligus; tiap butir jadi issue sendiri:

1. Empat metode bayar (penuh di muka, DP, Tempo, COD) dipilih Procurement per pengajuan; "COD" didefinisikan ulang dari arti lamanya (tanpa uang muka) karena belum ada dokumen yang memakainya.
2. Tahap `pb_barang_tiba` untuk semua metode, dicatat gudang atau security (izin baru `budget.catat.kedatangan`), berulang per kedatangan; kedatangan boleh dicatat sejak transfer dikonfirmasi (penuh/DP) atau sejak persetujuan membeli (Tempo/COD) walau tahapnya belum sampai.
3. Pelunasan (sisa DP, Tempo) disetujui ulang Cost Control dan SPV Finance, plus Direktur bila sisa ≥ ambang; COD tidak.
4. Tiap transfer menempuh AP → konfirmasi SPV Finance → Accounting, sama dengan DANA; faktur pembelian dicatat Accounting sesudah barang diterima.
5. Penerimaan dan lolos QC sebagian; kelebihan bayar diputus Procurement (potong ke pembelian berikutnya atau pengembalian dana). Saldo uang muka pemasok bersumber dari **Accurate**, ERP hanya menampilkannya.
6. Izin QC gudang GA dipisah jadi `budget.qc.ga` (paket QC Gudang GA). Paketnya wajib terpasang ke orangnya sebelum deploy.
7. Barang bersifat konsumsi hanya boleh lewat tipe KONSUMSI; form Barang Umum menolaknya dan menunjuk ke Konsumsi.

## Consequences

### Yang membaik

- Harga konsumsi diisi orang yang tahu pasar dan pemasok, dan gerbang Direktur berdiri di atas harga itu, bukan perkiraan pengaju.
- Barang konsumsi yang dibeli tercatat masuk stok GA, sehingga stok konsumsi berhenti hanya berkurang.

### Yang memburuk atau tetap terbuka

- Penggantian uang konsumsi yang sudah ditalangi kini harus diajukan sebagai DANA. Pengaju yang terbiasa memilih Konsumsi untuk itu perlu diberi tahu.
- Konsumsi kehilangan pencatatan Accounting (`pb_accounting_catat`) sampai §7 butir 4 selesai, sama seperti UMUM/RAWMATERIAL hari ini.
- Draf mencatat beberapa kerusakan pada tahap gudang GA yang ikut dipakai Konsumsi (Serah/Terima GA ditolak inventory karena identitas pengguna ikut diteruskan, tombol Setujui tanpa penjaga di Procurement/QC). Kerusakan itu dikerjakan sebagai perbaikan terpisah; selama belum selesai, Konsumsi bisa mandek di tahap yang sama dengan Barang Umum.
