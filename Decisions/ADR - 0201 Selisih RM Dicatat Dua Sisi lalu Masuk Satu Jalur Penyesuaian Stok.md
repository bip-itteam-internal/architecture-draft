> **Status**: 🟢 **Diterima**, 2026-10-23, oleh **SPV Manufacture** (jawaban diteruskan lewat IT, ditegaskan sebagai jawaban Pemutus pada 2026-10-23). Keputusan K-11 di [[ANALISA - Fondasi Manufaktur]]. Batas waktu sisi terima berlaku dulu dan boleh diubah sesuai keadaan lapangan.

## Untuk Manajemen

**Apa yang perlu diputuskan.** Bila jumlah bahan baku yang dikirim gudang RM berbeda dengan yang diterima produksi, apakah selisih itu **hanya dicatat sebagai bukti**, atau **boleh mengubah angka stok** (sesudah disetujui). Kalau boleh, lewat jalur mana dan siapa yang menyetujui.

**Usulan singkat.**
1. Menu **Bukti Selisih RM** tetap dipakai untuk mencatat dua sisi (jumlah dikirim gudang RM dan jumlah diterima produksi) beserta foto dan keterangan.
2. Selisih yang sudah dicatat kedua sisi **tidak mengubah stok sendiri**, tetapi otomatis menjadi **usulan penyesuaian** di satu jalur penyesuaian stok yang sama dengan stock opname (butir M-12), dengan alasan baku.
3. Usulan disetujui **SPV Manufacture**, lalu **divalidasi FAT** (sesuai jawaban Finance untuk K-1: semua selisih wajib dicek FAT), baru mengubah stok ERP dan terkirim ke Accurate.
4. Selisih yang sebenarnya **salah satuan** (pemasok mengirim dalam liter, gudang menimbang dalam KG) tidak diperlakukan sebagai selisih, melainkan dicegah lewat faktor konversi di master bahan.

**Siapa yang terdampak.** Gudang RM (sisi kirim), Admin/Operator Produksi (sisi terima), SPV Manufacture (penyetuju), FAT (validasi), PPIC (angka stok untuk rencana).

**Kenapa perlu ditulis sekarang.** Hari ini ada **dua cara terpisah** yang menyentuh selisih stok bahan, dan keduanya belum pernah dipakai: Bukti Selisih RM hanya menyimpan catatan, sedangkan koreksi stok lewat Proposal berjalan sendiri. Begitu gudang dan produksi mulai mencatat di ERP (Fase 1), selisih yang sama bisa dibetulkan dua kali, atau tidak sama sekali, tanpa satu pun pesan galat. Butir M-12 (satu jalur penyesuaian stok) menunggu keputusan ini bersama K-1.

**Apa yang tidak dijanjikan.** Kapan stok bahan dianggap berkurang (zona WIP, keputusan K-2). Akun Accurate untuk tiap jenis penyesuaian (pertanyaan 4 di [[ADR - 0186 Stok Pabrik di ERP Jadi Stok Operasional, Accurate Menerima Penyesuaian Persediaan]]). Pemilik master bahan, tempat faktor konversi disimpan (K-7, [[ADR - 0136 Pemilik Master Barang dan Master Gudang]]).

**Perkiraan besaran kerja.** Ringan sampai sedang (estimasi): menyambungkan catatan selisih yang sudah ada ke jalur penyesuaian M-12. Jalur M-12 sendiri dikerjakan sekali untuk opname, selisih RM, dan barang rusak.

## Pertanyaan untuk Pemutus

Rekomendasi disertakan; Pemutus boleh memilih lain.

| # | Pertanyaan | Pilihan | Rekomendasi |
|---|---|---|---|
| 1 | Fungsi Bukti Selisih RM | (a) catatan bukti saja, stok tidak pernah berubah karenanya (seperti sekarang); (b) catatan bukti, dan selisih yang tercatat dua sisi otomatis menjadi usulan penyesuaian di satu jalur stok; (c) dihapus, diganti catatan serah terima bahan ke produksi | **(b)**. Bukti foto tetap ada, dan stok hanya punya satu cara untuk dibetulkan. (a) membuat selisih nyata tidak pernah sampai ke stok; (c) menunggu keputusan zona WIP (K-2) dan membuang fitur yang sudah jadi |
| 2 | Selisih dibebankan ke mana | (a) selalu dianggap salah hitung kirim: stok gudang RM dikoreksi; (b) selalu dianggap susut/hilang: dibebankan sebagai biaya; (c) penyetuju memilih per kasus dari dua alasan baku | **(c)**, dengan dua alasan: **"salah hitung kirim"** (stok RM dikoreksi) dan **"susut/hilang"** (dibebankan). Akun bebannya ditetapkan Finance di K-1 pertanyaan 4; Accurate sudah punya 5313 Laba/Rugi Selisih Persediaan dan 5104 Biaya Varian Produksi |
| 3 | Siapa menyetujui | (a) SPV Manufacture saja; (b) SPV Manufacture, lalu validasi FAT; (c) FAT saja | **(b)**. Finance sudah menjawab untuk K-1 bahwa semua selisih opname wajib dicek FAT; selisih RM diperlakukan sama |
| 4 | Batas waktu produksi mencatat sisi diterima | (a) hari yang sama, sebelum penimbangan Batch Record dimulai; (b) paling lambat 1 hari kerja; (c) tanpa batas | **(a)**, dengan pengingat bila catatan kirim masih "menunggu" lewat 1 hari kerja. Tanpa batas, selisih ditemukan saat bahan sudah terpakai dan tak bisa diperiksa lagi |
| 5 | Selisih karena satuan (liter dikirim, KG ditimbang) | (a) dicatat sebagai selisih biasa; (b) dicegah dengan faktor konversi satuan beli ke satuan stok di master bahan | **(b)**. Kajian mencatat sebagian selisih RM berasal dari sini; ia salah satuan, bukan barang hilang |

*Dicocokkan ke vault, kode `origin/main`, dan data prod 2026-10-23 sebelum dikirim, supaya Pemutus tak ditanya hal yang sudah tertulis.*

### Jawaban (2026-10-23, disampaikan lewat IT)

| # | Jawaban | Arti untuk keputusan |
|---|---|---|
| 1 | Setuju | (b): bukti dua sisi, selisih menjadi usulan penyesuaian di satu jalur stok |
| 2 | Setuju | (c): penyetuju memilih "salah hitung kirim" atau "susut/hilang" |
| 3 | Setuju (bagian dari jawaban 1: disetujui SPV Manufacture lalu dicek FAT) | (b) |
| 4 | Ditanyakan balik ("kenapa di hari yang sama?"), lalu usulan revisi disetujui: "ya dulu, nanti bisa diubah sesuai keadaan di lapangan" | Sisi terima dicatat **sebelum bahan ditimbang untuk batch** |
| 5 | Ya | (b): faktor konversi satuan di master bahan |

**Penjelasan pertanyaan 4.** Yang penting bukan hari kalendernya, melainkan **sebelum bahannya dipakai**. Selama bahan masih di kemasannya, selisih bisa ditimbang ulang dan difoto; begitu bahan ditimbang ke batch dan tercampur, selisih itu tak bisa diperiksa lagi dan yang tersisa hanya angka di kertas. Usulan direvisi: **sisi terima dicatat sebelum bahan ditimbang untuk batch** (bukan "hari yang sama"), dengan pengingat bila catatan kirim masih menunggu lewat 1 hari kerja. Bila bahan memang disimpan dulu di produksi beberapa hari sebelum dipakai, batasnya tetap "sebelum dipakai". Disetujui 2026-10-23 sebagai aturan awal; boleh diubah sesuai keadaan di lapangan.

## Deskripsi

*Bukti Selisih RM tetap menjadi catatan dua sisi (kirim gudang RM, terima produksi) berfoto; selisih yang tercatat lengkap menjadi usulan penyesuaian di satu jalur penyesuaian stok (M-12) dengan alasan baku, disetujui SPV Manufacture, divalidasi FAT, lalu mengubah stok ERP dan terkirim ke Accurate.*

- **Status**: lihat blockquote di baris pertama dokumen ini
- **Keputusan papan**: K-11; bersama K-1 membuka M-12 di [[ANALISA - Fondasi Manufaktur]]
- **Issue**: bip-itteam-internal/bip-erp#2252, bip-itteam-internal/erp-frontend#1849 (fitur Bukti Selisih RM); bip-itteam-internal/erp-frontend#1868 (opname, jalur yang sama)
- **Preseden**: [[ADR - 0186 Stok Pabrik di ERP Jadi Stok Operasional, Accurate Menerima Penyesuaian Persediaan]] (Diterima 2026-10-23; validasi FAT oleh Senior Accounting)
- **Tanggal**: 2026-10-23

## Context

Diukur di kode `bip-erp` `origin/main` (171e6f88b, 2026-10-23). Rujukan baris bisa bergeser sesudah tanggal itu.

**Bukti Selisih RM** (`services/manufacture/selisih_rm.go`, rute `services/manufacture/main.go:243-250`, model `SelisihRM` di `shared-library/models/manufacture/models.go:254`):
- Menurut komentar kepala berkasnya, ini **log bukti** (foto dan keterangan) selisih bahan antara yang dikirim gudang RM dan yang diterima produksi, **tanpa alur persetujuan**.
- Dua sisi: gudang RM mencatat jumlah dikirim (status MENUNGGU), produksi menempelkan jumlah diterima (status SELESAI). Produksi juga bisa mencatat penerimaan tanpa catatan kirim; selisihnya lalu tak bisa dihitung.
- Tidak menyentuh `stok_sekarang`, ledger, maupun Accurate.
- Gerbang tab `selisih_rm`; menurut komentar rute, Security ikut mencatat.
- Prod: 0 dokumen (diukur 2026-10-08, dikonfirmasi checklist IT 2026-10-23).

**Jalur lain yang menyentuh selisih stok** (lihat juga Context di [[ADR - 0186 Stok Pabrik di ERP Jadi Stok Operasional, Accurate Menerima Penyesuaian Persediaan]]):

| Jalur | Mengubah stok? | Persetujuan |
|---|---|---|
| Bukti Selisih RM | tidak | tidak ada |
| Cycle count (`cycle_count.go`, `PutuskanCycleCount`) | tidak; persetujuan SPV hanya mengubah status | SPV gudang |
| Impor hasil SO (`saldo_awal_so.go`) | menimpa saldo akhir bulanan, bukan `stok_sekarang` | tidak ada |
| Proposal koreksi (`proposal.go`, rute `main.go:424-429`) | ya, ledger dan stok | PPIC lalu SPV |
| Rekonsiliasi (`POST /stok/reconcile`) | menimpa dengan Σ ledger | tidak ada |

Kajian ([[Manufacture - Kajian Fondasi Sistem]] Temuan 2 baris 5) merangkum ini sebagai sembilan jalur yang menulis `stok_sekarang` dengan aturan berbeda; cycle count dan selisih RM tak pernah menjadi penyesuaian.

**Asal selisih yang sudah diketahui** (kajian Temuan 8, dari tiket SPV Manufacture): sebagian selisih RM berasal dari konversi satuan. Pemasok mengirim dalam liter, gudang menimbang dalam KG tanpa alat ukur liter. Master bahan belum punya faktor konversi satuan beli ke satuan stok.

**Akun Accurate yang tersedia** (dibaca dari Accurate prod 2026-10-23, baca saja): 5313 Laba/Rugi Selisih Persediaan, 5104 Biaya Varian Produksi, 5308 Biaya Barang Rusak; persediaan 1601 Bahan Baku, 1602 Bahan Kemas, 1603 Bahan Penolong. Pemilihan akunnya tetap milik Finance (K-1 pertanyaan 4).

## Decision

*Diterima 2026-10-23.*

1. **Bukti Selisih RM dipertahankan** sebagai catatan dua sisi berfoto. Ia sendiri tidak mengubah stok.
2. **Catatan berstatus SELESAI dengan selisih bukan nol** otomatis menghasilkan satu usulan penyesuaian di jalur tunggal M-12. Jalur itu dipakai bersama oleh stock opname, selisih RM, dan barang rusak/kedaluwarsa. Usulan membawa rujukan id catatan selisihnya, supaya penelusuran "selisih ini sudah dibukukan atau belum" bisa dijawab.
3. **Penyetuju memilih alasan baku** (pertanyaan 2): salah hitung kirim (stok RM dikoreksi) atau susut/hilang (dibebankan).
4. **Urutan persetujuan**: SPV Manufacture menyetujui, FAT memvalidasi, baru stok ERP berubah dan Penyesuaian Persediaan terkirim ke Accurate dengan akun dari Finance.
5. **Sisi terima dicatat sebelum bahan ditimbang untuk batch**, dengan pengingat bila catatan kirim masih menunggu lewat 1 hari kerja. Batas ini aturan awal dan boleh diubah sesuai keadaan lapangan.
6. **Faktor konversi satuan** disimpan di master bahan, sehingga penerimaan dalam satuan beli tercatat dalam satuan stok tanpa hitung tangan. Penempatannya mengikuti keputusan pemilik master barang (K-7).

## Consequences

**Yang didapat.** Satu selisih fisik punya satu jalan ke angka stok, dengan bukti foto dan dua penyetuju. Selisih karena salah satuan berhenti muncul sebagai kehilangan.

**Yang harus diterima.**
- Selisih tidak langsung memperbaiki stok; stok baru berubah sesudah SPV dan FAT selesai. Selama itu angka stok menyimpang dari fisik sebesar selisihnya.
- Produksi wajib mencatat sisi terima tepat waktu; catatan yang tak pernah diterima tidak menjadi usulan apa pun.
- Jalur M-12 harus jadi lebih dulu. Keputusan ini tidak berarti apa-apa sebelum K-1 Diterima.

## Alternatif yang ditolak

- **Selisih RM punya jalur penyesuaian sendiri.** Dua jalur penyesuaian untuk satu stok adalah keadaan hari ini yang hendak dibereskan M-12; selisih yang sama bisa dibukukan dua kali.
- **Bukti Selisih RM dihapus.** Kehilangan satu-satunya tempat foto dan keterangan dua sisi, padahal fitur itu sudah jadi.
- **Selisih langsung mengubah stok tanpa persetujuan.** Bertentangan dengan jawaban Finance untuk K-1 (semua selisih dicek FAT) dan membuat salah ketik langsung menjadi angka stok.
