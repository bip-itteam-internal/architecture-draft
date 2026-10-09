# ADR - 0162 Receipt Lazada Mengikuti Uang yang Benar-benar Cair, Selisih terhadap Hitungan Order Ditandai

> **Status**: 🟡 **Diusulkan**, 2026-10-09, oleh agent (AI Engineering Loop) atas jawaban tim Finance tanggal yang sama. **Belum Diterima**: butir 1 dan 2 adalah jawaban Finance; bentuk penanda, akun penempatan selisih, dan perlakuan receipt lama (§ Pertanyaan Terbuka) menunggu keputusan Finance dan persetujuan Tech Development. Belum ada kode. Nomor 0162 diklaim saat push; bila sudah terpakai, geser ke nomor bebas berikutnya.

%% Status di blockquote atas supaya terbaca VAULT-INDEX.json (15 baris pertama). %%

%% Vault ini PUBLIK. Tak ada kredensial, nama orang/toko, atau nomor dokumen asli di dok ini. %%

## Untuk Manajemen

**Masalahnya.** Untuk toko Lazada, sistem membuat penerimaan (receipt) di Accurate dari jumlah per-order yang dihitungnya sendiri. Bila uang yang benar-benar cair berbeda dari jumlah itu, sistem memakai hitungannya sendiri dan membuang angka uang cair, hanya menulis peringatan di log. Pada satu kasus yang diukur, penerimaan tercatat sekitar Rp22 ribu lebih besar dari uang yang masuk. Finance menyatakan selisih itu adalah biaya affiliate yang belum terbaca sistem.

**Yang diputuskan Finance.** Penerimaan **mengikuti uang yang benar-benar cair**. Bila ada selisih terhadap hitungan sistem, selisihnya **tetap ditandai** supaya Finance bisa memastikan biayanya ditempatkan di tempat yang benar: biayanya belum tentu selalu affiliate, bisa berbeda per kasus.

**Yang berubah bagi Finance.** Angka kas di penerimaan cocok dengan uang yang masuk. Selisih tidak lagi hilang diam-diam; ia muncul sebagai tanda untuk diperiksa.

**Yang belum diputuskan.** Ke akun mana selisih dibukukan sementara, seperti apa tandanya, dan bagaimana penerimaan lama yang sudah terkirim dibereskan (§ Pertanyaan Terbuka).

## Deskripsi

*Mengubah dasar `chequeAmount` receipt Lazada dari jumlah hitungan per-order menjadi payout (uang cair), menandai selisih payout terhadap hitungan, dan membukukan selisihnya ke akun yang harus diputuskan Finance.*

- **Tanggal**: 2026-10-09
- **Hubungan**: audit BHA-297 (GitHub bip-erp#2199, butir C7). Berkaitan dengan [[ADR - 0119 Kompensasi TikTok Dipisah Menurut Sudah atau Belum Ada Uang Masuk]] (prinsip serumpun: uang yang benar-benar masuk menjadi dasar). Dokumentasi layanan: [[Microservices - Integration Service]].

## Context

- **Perilaku sekarang** (dibaca dari kode, audit 2026-09-30): bila payout Lazada berbeda dari jumlah per-order, cheque memakai jumlah per-order dan payout dibuang. Hanya ada peringatan log tanpa notifikasi, dan komentar kodenya menyebut sumbernya "pembulatan", padahal selisih yang diukur adalah uang nyata.
- **Diukur 2026-10-09** (baca-saja, produksi): 13 receipt Lazada punya payout berbeda dari jumlah per-order. Selisihnya **berpasangan antar hari**: biaya yang tiba sehari kemudian membuat satu hari berlebih dan hari berikutnya berkurang, dan jumlah bersihnya **Rp0**. Jadi masalahnya terutama pergeseran waktu pembukuan, bukan kehilangan uang.
- **Sebab pergeserannya**: baris keuangan Lazada kadang terbit **susulan**, sesudah receipt terkirim (contoh yang terbukti: biaya "Sponsored Affiliates" terbit sehari sesudah baris biaya lain pada order yang sama). Penghitungan ulang income Lazada saat baris susulan masuk sudah ada, tetapi dibatasi tanggal cair lewat konfigurasi `lazada-income-recompute-from` (keputusan 2026-09-29: receipt yang sudah ditutup buku Finance tidak boleh berubah diam-diam). Receipt yang sudah terkirim sebelum baris susulan tiba tetap membawa angka lama.
- **Jawaban Finance, 2026-10-09**: (1) uang yang seharusnya masuk adalah angka payout; selisihnya seharusnya tercatat sebagai biaya affiliate, tetapi sistem belum membacanya; (2) pada kasus lain biayanya bisa berbeda, jadi receipt mengikuti uang yang benar-benar cair dan **selisihnya tetap ditandai** untuk memastikan penempatan biayanya; (3) tidak ada syarat lain.
- **Kendala identitas receipt** (dari komentar rancangan `buildReceiptPayload`): jumlah pembayaran per faktur harus sama dengan cheque. Karena itu cheque yang mengikuti payout tidak bisa begitu saja berbeda dari jumlah per-order; selisihnya harus dibukukan ke sebuah baris, dan baris itu butuh akun.

## Decision

1. **Cheque receipt Lazada = payout (uang yang benar-benar cair)**, bukan jumlah hitungan per-order. (Finance, 2026-10-09.)
2. **Bila payout berbeda dari jumlah hitungan per-order, selisihnya ditandai** supaya Finance dapat memeriksa penempatan biayanya. Penanda **tidak menahan** receipt: uang yang benar-benar masuk tetap dibukukan. (Finance, 2026-10-09.)
3. Tidak ada syarat tambahan dari Finance. (Finance, 2026-10-09.)

## Pertanyaan Terbuka

Tidak diisi dengan tebakan; tiap butir butuh jawaban sebelum kode ditulis.

1. **Akun penempatan selisih** (Finance). Karena jumlah pembayaran per faktur harus sama dengan cheque, selisih payout terhadap hitungan perlu dibukukan ke satu akun sementara. Akun mana, dan apakah sama untuk semua sebab selisih atau berbeda per jenis biaya?
2. **Bentuk penanda** (Finance + Tech). Pilihan yang masuk akal: field di receipt yang tampil di layar receipt atau Kotak Adopsi, pesan lewat notifier yang sudah ada, atau keduanya. Penanda bukan `hold_reason`, karena menahan berarti uang nyata tidak terbukukan.
3. **Ambang selisih yang ditandai**. Usulan: sama dengan ambang debu-float yang dipakai jalur receipt (Rp0,5), supaya pembulatan tidak membanjiri penanda.
4. **Receipt Lazada yang sudah terkirim** dengan angka lama. Tidak diubah otomatis (konsisten keputusan 2026-09-29); apakah dibereskan lewat Retry per dokumen atau koreksi manual Finance belum diputuskan. Belum diukur apakah penghitungan ulang sejak 2026-09-29 sudah menutup sebagian selisih yang diukur.

## Konsekuensi

- ✅ Kas di receipt cocok dengan uang yang benar-benar masuk; pergeseran antar hari berhenti menumpuk di satu sisi.
- ✅ Selisih tidak lagi hilang diam-diam di log.
- ⚠️ Mengubah jalur uang: butuh test yang mengunci identitas cheque = jumlah pembayaran, dan kontrol negatif bahwa selisih benar-benar ditandai.
- ⚠️ Receipt lama tidak ikut berubah; keadaan campuran (receipt lama berdasar hitungan, receipt baru berdasar payout) berlangsung sampai butir terbuka 4 diputuskan.
- Tidak ada perubahan kontrak untuk frontend atau mobile, kecuali bila penanda dipilih tampil di layar.

## Alternatif yang dipertimbangkan

- **Tetap memakai jumlah per-order, selisih hanya di log** (perilaku sekarang): ditolak Finance; selisih hilang tanpa jejak.
- **Menahan receipt bila ada selisih**: ditolak, karena uang yang benar-benar masuk tidak terbukukan sampai ada yang memeriksa.

## Dokumen Terkait

- [[Microservices - Integration Service]] · [[IT - Background Jobs & Schedulers]]
- [[ADR - 0119 Kompensasi TikTok Dipisah Menurut Sudah atau Belum Ada Uang Masuk]]
