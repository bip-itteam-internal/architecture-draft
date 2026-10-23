> **Status**: 🟢 **Diterima**, 2026-10-23, oleh **Supervisor Quality** (jawaban diteruskan lewat IT, ditegaskan sebagai jawaban Pemutus pada 2026-10-23). Keputusan K-5 di [[ANALISA - Fondasi Manufaktur]]. Kartu stok menunggu contoh form kertas; lini Pangan ditunda.

## Untuk Manajemen

**Apa yang perlu diputuskan.** Dokumen apa yang harus bisa **dicetak dari ERP** dan dalam bentuk apa, supaya pabrik boleh berhenti mengisi kartu stok dan Batch Record di kertas tanpa melanggar kebutuhan pemeriksaan BPOM.

**Usulan singkat.**
1. **Bentuk cetak meniru form kertas yang berlaku hari ini**, kolom demi kolom, termasuk nomor dokumen dan revisinya. Tidak ada format baru yang harus dikenalkan ke pemeriksa.
2. **Batch Record**: ERP sudah mencetak tujuh lembar yang meniru kertas. Yang diputuskan tinggal apakah cetakan itu diterima, dan bagaimana tanda tangannya.
3. **Kartu stok**: ERP belum bisa mencetaknya. Dibangun sesudah Supervisor Quality mengirim contoh kartu stok kertas yang berlaku (kosmetik dan obat tradisional).
4. **Kertas dan ERP berjalan bersama** sampai Supervisor Quality menyatakan cetakan ERP diterima; keputusan berhenti memakai kertas ada di tangan Supervisor Quality.

**Siapa yang terdampak.** Quality (QC, QA, Penanggung Jawab Teknis), gudang RM dan FG (kartu stok), Admin Produksi (Batch Record).

**Kenapa perlu ditulis sekarang.** Kuesioner pemakai mencatat dokumen kertas tetap wajib untuk audit BPOM, dan syarat meninggalkan kertas adalah ERP mencetak dokumen dalam format yang diterima ([[Manufacture - Kajian Fondasi Sistem]] Temuan 3). Selama syarat itu belum jelas, setiap catatan di ERP adalah ketikan kedua dari kertas. Butir M-17 (kartu stok per lot, bip-itteam-internal/erp-frontend#1867) menunggu keputusan ini.

**Apa yang tidak dijanjikan.** Persetujuan dari BPOM sendiri: dokumen ini hanya mencatat apa yang **Supervisor Quality** nyatakan cukup. Format COA (Certificate of Analysis) keluar (keputusan K-8). Lini Pangan sampai ada jawaban pertanyaan 4.

**Perkiraan besaran kerja.** Kartu stok: sedang (estimasi), bergantung pada bentuk kertas yang dikirim. Batch Record: ringan bila cetakannya diterima seperti sekarang.

## Pertanyaan untuk Pemutus

Rekomendasi disertakan; Pemutus boleh memilih lain.

| # | Pertanyaan | Pilihan | Rekomendasi |
|---|---|---|---|
| 1 | Cetakan Batch Record dari ERP (7 lembar, meniru form kertas, lihat Context) | (a) diterima apa adanya, dengan paraf digital (nama, posisi, tanggal-waktu); (b) diterima, tetapi ditandatangani basah sesudah dicetak; (c) belum diterima, perlu perubahan (sebutkan lembar dan kolomnya) | **(b)** untuk masa peralihan. Tanda tangan basah di atas cetakan ERP tidak mengubah apa yang dilihat pemeriksa; paraf digital bisa dipakai sendiri sesudah Supervisor Quality yakin |
| 2 | Bentuk kartu stok | (a) satu kartu per bahan per nomor lot (lot pemasok dan tanggal kedaluwarsa); (b) satu kartu per bahan, dengan kolom nomor lot dan kedaluwarsa di tiap baris; (c) ikut kertas yang berlaku | **(c)**. Mohon kirim foto kartu stok kertas yang dipakai sekarang, kosmetik dan obat tradisional; ERP meniru kolomnya persis |
| 3 | Bahan kemas (tidak ber-ED) | (a) kartu yang sama tanpa kolom kedaluwarsa; (b) kartu tersendiri | **(a)**, kecuali form kertasnya memang berbeda |
| 4 | Lini Pangan | (a) perlu kartu stok dan Batch Record sendiri; (b) sama dengan kosmetik; (c) belum diproduksi lewat ERP, ditunda | Mohon dijawab; kajian mencatat lini Pangan belum terwakili di ERP. Bila belum ada produksi Pangan yang akan dicatat di ERP, **(c)** |
| 5 | Kapan kertas boleh dilepas | (a) sesudah satu bulan berjalan bersama tanpa temuan; (b) sesudah satu audit internal atau inspeksi menerima cetakan ERP; (c) ditentukan Supervisor Quality kemudian | **(b)**, dengan Supervisor Quality yang menyatakannya. Batas waktu saja tidak membuktikan cetakan itu diterima pemeriksa |

*Dicocokkan ke vault, kode `origin/main`, dan data prod 2026-10-23 sebelum dikirim, supaya Pemutus tak ditanya hal yang sudah tertulis.*

### Jawaban (2026-10-23, disampaikan lewat IT)

| # | Jawaban | Arti untuk keputusan |
|---|---|---|
| 1 | Setuju | (b): Batch Record dicetak dari ERP lalu ditandatangani basah selama peralihan |
| 2 | "Itu nanti gunakan sementara" | Kartu stok ERP memakai bentuk form kertas yang berlaku **sebagai bentuk sementara**; bentuknya boleh direvisi kemudian. Contoh form kertasnya tetap dibutuhkan untuk membangunnya |
| 3 | Ya | (a): bahan kemas memakai kartu yang sama tanpa kolom kedaluwarsa |
| 4 | Pangan tunda | (c) |
| 5 | Setuju | (b): kertas dilepas sesudah satu audit internal atau inspeksi menerima cetakan ERP, dinyatakan Supervisor Quality |

Semua pertanyaan terjawab dan ditegaskan sebagai jawaban Supervisor Quality pada 2026-10-23.

## Deskripsi

*Kartu stok dan Batch Record dicetak dari ERP dengan bentuk meniru form kertas yang berlaku (nomor dokumen dan revisi ikut); Batch Record sudah tercetak tujuh lembar dan tinggal dinyatakan diterima, kartu stok dibangun dari contoh kertas yang dikirim Supervisor Quality; kertas dilepas sesudah Supervisor Quality menyatakan cetakan diterima.*

- **Status**: lihat blockquote di baris pertama dokumen ini
- **Keputusan papan**: K-5; membuka M-17 di [[ANALISA - Fondasi Manufaktur]]
- **Issue**: bip-itteam-internal/erp-frontend#1867 (kartu stok per lot)
- **Terkait**: [[Manufacture - Dokumen Produksi Batch]], M-02 (uji coba Batch Record pada batch nyata, paralel dengan kertas)
- **Tanggal**: 2026-10-23

## Context

Diukur di kode `erp-frontend` `origin/main` (e64973711) dan `bip-erp` `origin/main` (171e6f88b), 2026-10-23.

**Yang sudah dikatakan pemakai** ([[Manufacture - Kajian Fondasi Sistem]] Temuan 3): dokumen kertas tetap wajib untuk audit BPOM (Batch Record fisik, kartu stok); ERP dianggap salinan kerja. Ada **dua kartu stok**, kosmetik dan obat tradisional. **Bahan kemas tidak ber-ED.** Stock opname mingguan.

**Batch Record sudah tercetak** (`src/features/manufacture/components/BatchRecordPrint.tsx`), meniru form kertas lengkap dengan kop dan nomor dokumen:

| Lembar | Judul | No. dokumen di cetakan |
|---|---|---|
| 1 | Ceklis Kelengkapan Dokumen Produksi | - |
| 2 | Daftar Kesiapan Ruang Pengolahan | PR/04/PD/011/03 |
| 3 | Catatan Pengolahan Batch | PR/SOP/007/01/F/02 rev. 02 |
| 4 | Daftar Kesiapan Ruang Pengemasan | PR/04/PD/011/04 |
| 5 | Catatan Pengemasan Batch | PR/SOP/007/01/F/01 rev. 01 |
| 6 | Catatan Pengujian | - |
| 7 | Lembar Keputusan | - |

- Tanda tangan berbentuk **stempel paraf digital** (`ParafStempel.tsx`): nama, posisi, dan tanggal-waktu orang yang memaraf dari akunnya.
- Spesifikasi produk (dasar COA) sudah ditambahkan ke Batch Record (M-03, ter-deploy prod 2026-10-19).
- Kajian Temuan 6 membandingkan satu Batch Record kertas lengkap dengan model ERP; semua bagian kertas sudah ada di ERP kecuali daftar peralatan.
- Prod: `batch_record` 0 dokumen; belum pernah dicetak untuk batch nyata.

**Kartu stok belum tercetak.**
- Lot bahan sudah dimodelkan (`LotBahan` di `shared-library/models/manufacture/models.go:1092`: nomor lot pemasok, tanggal masuk, tanggal kedaluwarsa, qty masuk dan sisa), dengan layar Lot Bahan dan Dashboard FIFO/FEFO. Prod: `lot_bahan` 0 dokumen.
- Layar Tarikan Mutasi (`MutasiView.tsx`, `GET /mutasi`) menampilkan dan mengekspor kartu mutasi **per bahan per periode**, bukan per lot, dan bukan dalam bentuk form kertas.
- Tidak ada komponen cetak kartu stok di frontend (`git grep -i "kartu stok"` di `src/features/manufacture` hanya menemukan komentar di layar KPI gudang).

**Celah yang membuat kartu stok per lot belum bisa dipercaya** (kajian Temuan 2 baris 7): `qty_sisa` lot hidup terpisah dari stok, dan hanya satu dari sembilan jalur penulis stok yang menggerakkan lot. Kartu stok per lot yang dicetak sebelum celah ini ditutup akan menunjukkan sisa yang berbeda dari stok. Ini bagian M-12 dan M-17, bukan keputusan Pemutus.

## Decision

*Diterima 2026-10-23.*

1. **Bentuk cetak = form kertas yang berlaku**, termasuk nomor dokumen dan revisi. Perubahan form kertas (revisi baru) diikuti ERP sebagai perubahan tersendiri.
2. **Batch Record** dicetak dari ERP sesuai jawaban pertanyaan 1. Bila (b), cetakan menyediakan ruang tanda tangan basah di samping paraf digital.
3. **Kartu stok** dibangun sesudah contoh kertasnya diterima (pertanyaan 2 dan 3): satu bentuk untuk kosmetik dan satu untuk obat tradisional bila kertasnya berbeda. Isinya diambil dari pergerakan stok dan lot yang sama dengan angka stok, sesudah celah lot ditutup (M-12).
4. **Peralihan**: kertas dan ERP berjalan bersama; uji coba Batch Record M-02 menjadi bagian masa ini. Kertas dilepas per dokumen sesuai pertanyaan 5, dinyatakan Supervisor Quality.
5. **Lini Pangan** mengikuti jawaban pertanyaan 4.

## Consequences

**Yang didapat.** Pemeriksa melihat bentuk dokumen yang sudah dikenalnya; pabrik berhenti mengetik dua kali begitu kertas dilepas; kartu stok dan angka stok berasal dari pergerakan yang sama sehingga tak bisa menyimpang.

**Yang harus diterima.**
- Selama masa peralihan pekerjaan bertambah: kertas tetap diisi, ERP juga.
- Tiap revisi form kertas berarti perubahan di ERP.
- Kartu stok per lot menunggu celah lot ditutup; mencetaknya lebih dulu menghasilkan sisa yang berbeda dari stok.

## Alternatif yang ditolak

- **Format cetak baru rancangan ERP.** Menuntut pemeriksa dan Quality mempelajari bentuk baru, padahal form kertas yang berlaku sudah diterima.
- **Langsung berhenti memakai kertas begitu fitur cetak ada.** Tidak ada bukti cetakan diterima sebelum dicoba pada batch nyata dan diperiksa.
- **Mencetak kartu stok dari ekspor Tarikan Mutasi yang ada.** Ekspor itu per bahan per periode, tanpa lot dan kedaluwarsa, dan bukan bentuk form kertas.
