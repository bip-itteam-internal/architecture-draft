---
tags: [adr, marketing-analytics, ai, frontend]
status: Accepted
tanggal: 2026-09-29
---

# ADR - 0139 Penjelasan Tiap Tabel dan Diagram Laporan Ditulis AI, Angkanya Rujukan ke Fakta Backend

> **Status**: ⚠️ **Implemented (ada catatan)** — diputuskan dan di-merge 2026-09-29 (bip-erp [#2329](https://github.com/bip-itteam-internal/bip-erp/pull/2329), erp-frontend [#1838](https://github.com/bip-itteam-internal/erp-frontend/pull/1838)); status deploy prod diukur ulang sebelum dipakai (lihat § Realisasi). Mengubah sebagian [[ADR - 0134 Sajian Laporan Asisten Analisa Berupa Blok Terstruktur, AI Memilih Bentuk, Angka dari Backend]] § Realisasi butir g (model tidak menulis teks apa pun untuk blok non-teks): larangan itu diganti mekanisme di bawah **khusus untuk penjelasan per blok**. Judul blok dan blok Ringkasan tetap dari aturan seperti sebelumnya.

## Context

Pemilik produk (2026-09-29): **setiap tabel, diagram, dan chart di laporan harus punya penjelasan ringkas**, dan penjelasannya **ditulis AI** (dipilih di antara tiga opsi: kalimat dari aturan backend, kalimat AI, atau keterangan baku saja).

Keadaan terukur di `origin/main` 2026-09-29: dari delapan dataset sajian, hanya tiga yang mengisi `catatan` (`angka_utama`, `roas_per_pekan`, `per_toko`), dan isinya sebatas **peringatan data** (settlement belum cair, angka perkiraan), bukan penjelasan apa yang ditunjukkan. Lima lainnya tanpa keterangan apa pun. FE sudah merender `dataset.catatan` di bawah tiap blok (layar dan PDF).

ADR 0134 butir g sengaja melarang model menulis teks untuk blok non-teks, dan alasannya tetap berlaku: model saat itu hanya menerima **metadata** dataset, bukan isinya, sehingga kalimat seperti "Lima toko teratas" atau "Sesuai target" adalah penilaian tanpa dasar. Validator pencocokan angka dalam teks bebas yang sempat dicoba juga **bocor ke banyak arah** (butir g, paragraf "Validator yang dicoba lebih dulu lalu dibuang"). Keputusan ini harus menutup kedua sebab itu, bukan sekadar membuka larangannya kembali.

Batas yang tetap berlaku: model tidak menerima baris mart mentah (ADR 0120 §4, ADR 0127 §5), dan angka yang tampil selalu hasil hitung backend.

## Decision

### §1 Backend menghitung FAKTA per dataset; model hanya merujuknya

Untuk tiap dataset beku, backend menghitung daftar **fakta**: id pendek, label bisnis, nilai beserta satuannya (mis. `f1` laba harian tertinggi dan tanggalnya, `f2` jumlah hari rugi, `f3` jumlah pekan ROAS di bawah target, `f4` perubahan revenue dibanding periode lalu, `f5` porsi revenue tiga toko teratas). Fakta dihitung dari **baris yang sama** dengan yang digambar diagramnya (satu fakta satu tempat), diformat sesuai satuannya oleh backend, dan ikut dibekukan di dokumen.

Model menerima fakta itu (agregat hasil hitung, sah menurut ADR 0127 §5), lalu menulis **penjelasan satu sampai dua kalimat per dataset** dalam bahasa bisnis Indonesia. Angka di penjelasan **hanya boleh berupa rujukan** `{f1}`, `{f2}` ke fakta dataset yang sama. Backend mengganti rujukan dengan nilai terformat saat menyusun sajian akhir, jadi angka yang tampil selalu identik dengan diagramnya.

### §2 Validator tegas, bukan pencocokan teks

Penjelasan model ditolak (dicatat di penolakan sajian, bukan dibuang diam) bila:

1. memuat **digit apa pun di luar rujukan** `{fN}` (larangan mutlak, bukan pencocokan; ini menutup kebocoran validator lama);
2. merujuk fakta yang tidak ada di dataset itu;
3. melebihi batas panjang (dua kalimat, batas karakter bernama);
4. merujuk dataset yang tidak ada di susunan akhir, atau memuat em dash atau token teknis (nama field, id).

Penjelasan hanya dievaluasi saat keputusan model berhasil (`StatusModel == siap`), pola yang sama dengan pilihan sajian (ADR 0134 butir j), dan bagian penjelasan diurai terpisah dari keputusan (`json.RawMessage`), sehingga penjelasan rusak tidak menjatuhkan keputusan.

### §3 Tiap blok SELALU punya penjelasan: cadangan dari aturan

Bila model gagal, habis waktu, atau penjelasan satu blok ditolak, blok itu memakai **kalimat baku cara membaca** per dataset milik backend (mis. "Batang menunjukkan laba kotor per hari; hari bertanda belum cair masih bisa berubah."). Tabel dan diagram tak pernah tampil tanpa penjelasan. Blok menyimpan `penjelasan` (kalimat final, rujukan sudah terisi) dan `sumber_penjelasan` (`model` | `aturan`).

Dua dataset yang dihitung ulang saat GET (`status_keputusan`, `keputusan_per_jenis`, ADR 0134 butir f) **selalu** memakai kalimat baku: angkanya bergerak setelah kiriman terbit, sehingga kalimat model yang dibekukan akan berbunyi basi.

### §4 FE menampilkan penjelasan di bawah tiap blok, bertanda sumbernya

Penjelasan dirender di bawah judul atau bagan setiap blok non-teks, di layar dan di PDF, di atas `catatan` peringatan data yang sudah ada. Penjelasan dari model diberi penanda kecil "AI" (i18n) supaya pembaca tahu kalimat mana yang ditulis model. Kiriman lama tanpa `penjelasan` tampil seperti sekarang.

## Consequences

- Kontrak `GET /keputusan-kiriman` bertambah `penjelasan` dan `sumber_penjelasan` per blok (aditif). **BE sebelum FE**.
- Keluaran model bertambah kira-kira satu sampai dua kalimat per dataset (enam dataset beku), masih dalam satu panggilan yang sama (ADR 0127 §5). Anggaran waktu model 4 menit (ADR 0127 § Realisasi butir o) tidak diubah.
- Kalimat model bisa terbaca kaku karena angka hanya lewat rujukan. Itu harga yang diterima sadar: "angka di penjelasan selalu cocok dengan diagram" lebih penting daripada gaya.
- Sampai AI benar-benar berhasil di prod (per 2026-09-29 belum pernah `siap`), yang tampil adalah kalimat baku §3. Bila penjelasan baku saja yang tampil berminggu-minggu, sebabnya ada di jejak model, bukan di fitur ini.

## Realisasi (2026-09-29)

| Sisi | PR | Isi |
|---|---|---|
| BE | bip-erp [#2329](https://github.com/bip-itteam-internal/bip-erp/pull/2329) | Fakta per dataset, kalimat baku, katalog + skema + instruksi model, validator, penerapan (§1-§3) |
| FE | erp-frontend [#1838](https://github.com/bip-itteam-internal/erp-frontend/pull/1838) | Penjelasan di bawah tiap blok layar + PDF, penanda "AI" (§4) |

Mekanisme: `services/marketing-analytics/sajian_fakta.go` (fakta, pemformat, kalimat baku, `datasetRecomputeSajian`, `batasKarakterPenjelasan` = 280), `keputusan_ai_penjelasan.go` (`uraiPenjelasanAI`, `validasiDanSubstitusiPenjelasan`, `terapkanPenjelasanSajian`), `keputusan_ai_sajian.go` (fakta di katalog, `instruksiPenjelasanSajian`), `sajian.go` (`BlokSajian.Penjelasan`/`SumberPenjelasan`, `DatasetSajian.Fakta`, `blokAturanSajian`, jalur GET).

a. **Kalimat baku SENGAJA netral terhadap bentuk** (tidak menyebut "batang", "garis", "tabel"): model boleh memilih bentuk lain dari `bentuk_diizinkan`, dan kalimat yang menyebut bentuk akan salah di bawah blok berbentuk lain.
b. **Fakta per toko menyebut penyebutnya**: "Porsi revenue N toko teratas di antara toko yang ditampilkan" dan fakta "Jumlah toko yang ditampilkan" (maks 15). Tanpa itu model menulis porsi yang terbaca sebagai porsi atas seluruh revenue.
c. **Rupiah ringkas memilih satuan SESUDAH pembulatan** (999.960.000 jadi "Rp 1,0 M", bukan "Rp 1000,0 jt"); di bawah satu juta format penuh dengan spasi seragam ("Rp 500.000").
d. **Batas 280 karakter diperiksa dua kali**: sebelum dan sesudah rujukan diganti nilai (nilai seperti nama toko bisa memanjangkan teks).
e. **Kiriman lama** (tanpa `sumber_penjelasan`) tidak diberi kalimat baku di jalur GET, sesuai §4.
f. **Belum ditegakkan validator**: larangan "token teknis (nama field, id)" di §2 butir 4 hanya lewat instruksi model; digit non-ASCII tidak ditolak.

**Belum terbukti**: penjelasan model baru muncul saat keputusan AI `siap`; per 2026-09-29 AI belum pernah `siap` di prod (lihat [[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]] § Realisasi butir o). Sampai itu, yang tampil kalimat baku §3.

## Terkait

- [[ADR - 0134 Sajian Laporan Asisten Analisa Berupa Blok Terstruktur, AI Memilih Bentuk, Angka dari Backend]]
- [[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]]
- [[ADR - 0120 Asisten Analisa Marketing Jadi Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI]]
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]
- [[Microservices - Marketing Analytics Service]]
