# ANALISA - Bukti Sisi Lawan Audit Internal

Papan kerja untuk [[ADR - 0075 Bukti Sisi Lawan Dilampirkan dan Angkanya Dicatat, Pembacaan Otomatis Menyusul]]. Keputusannya di ADR; ini pecahan kerjanya.

**Tanggal analisis**: 2026-09-03 · **Diperbarui**: 2026-09-03

**Status**: ⚠️ Fase 1 sebagian — T1.1, T1.2, T1.3 **selesai dan merged**; T1.4, T1.5, T1.6 belum. ⛔ Fiturnya **belum bisa dipakai siapa pun**: layarnya belum ada dan `MINIO_AUDIT_KEY` belum diisi di `.env` lingkungan mana pun.

## Yang perlu dipegang sebelum mulai

⛔ **Jangan berangkat dari "dua belas uji akan terbuka".** Sebelas dari dua belas belum punya penjalan, jadi fase 1 membuka **satu** uji: `jurnal_manual_besar`. Sisanya mendapat tempat yang sudah siap, bukan mesin yang berjalan. Rincian pengukurannya di ADR §Context.

⭐ **Acuan yang ditiru**: `services/finance/pajak_arsip.go` + `pajak_arsip_test.go`. Baca dua berkas itu **sebelum** menulis apa pun — keduanya sudah memuat batas ukuran, daftar-izin ekstensi, hex anti-timpa, dan gotcha `invalid access key`.

---

## Fase 1 — Tempat menaruh bukti (yang benar-benar di jalur kritis)

### ✅ T1.1 · Prefix MinIO `audit/` di file-service — SELESAI ([#1699](https://github.com/bip-itteam-internal/bip-erp/pull/1699))
`bip-erp/services/file/main.go` · `docker-compose.yml` · `.env`

Tambah `MINIO_AUDIT_KEY: "audit/"` ke peta tulis. ⛔ **TANPA kunci baca** — koreksi terhadap rancangan awal; alasannya di ADR 0075 §Consequences. Nama `MINIO_READ_AUDIT_KEY` juga terbalik dari konvensi (yang benar `MINIO_<MODUL>_READ_KEY`).

⚠️ **Env dibaca saat container DIBUAT.** Naikkan dengan `docker compose up -d --force-recreate file-service`, bukan `restart`. Kunci yang belum terpasang dijawab `invalid access key`, galat yang tak menyebut sebabnya.

**Verifikasi**: unggah satu berkas uji lewat gateway dengan kunci baru, lalu `/exist` menemukannya di bawah `audit/`. Dan **kontrol negatif**: kunci `pajak/` **ditolak** untuk objek ber-prefix `audit/` — tanpa uji ini, pemisahan prefixnya tak terbukti.

### ✅ T1.2 · Struktur `BuktiBaris` + penyimpanannya — SELESAI ([#1700](https://github.com/bip-itteam-internal/bip-erp/pull/1700))
`bip-erp/services/finance/audit_bukti.go` (baru) · `audit_kertas_kerja.go`

Field: item terpilih yang dijawab (kosong untuk Bentuk B), objek MinIO, nama berkas asli, oleh, pada, **angka yang dibaca beserta satuannya**.

⛔ `Tinjauan` **tidak** diperluas. Alasan adalah kesimpulan, bukti adalah bahan; satu baris punya banyak bukti dan satu kesimpulan.

⛔ **Angka jadi field tersendiri, jangan diselipkan ke teks alasan.** Angka yang hanya hidup di kalimat tak bisa dibandingkan mesin, dan perbandingan itu seluruh gunanya.

**Bergantung pada**: —

### ✅ T1.3 · Rute unggah + hapus bukti — SELESAI (#1700, empat rute)
`bip-erp/services/finance/audit_handler.go`

`POST /audit/periode/:periode/baris/:kode/bukti` dan `DELETE .../bukti/:id`. Digerbang `audit.tinjau` (bukan `audit.view`): melampirkan bukti adalah menulis.

Batas 4 MB dan daftar-izin ekstensi ditolak **lebih dulu di sini**, meniru `pajak_arsip.go` — file-service tetap yang berlaku, ini hanya menghasilkan pesan yang lebih baik.

⚠️ Wajib ada minimal satu test `app.Test(httptest.NewRequest(...))` untuk jalur galatnya. Test fungsi murni tidak menangkap cacat glue handler; form-builder pernah merged, deployed, dan mustahil dipakai 3 hari karena lapisan binding tak ikut diperbarui.

**Bergantung pada**: T1.1, T1.2

### T1.4 · `ujiJurnalManualBesar` membaca bukti
`bip-erp/services/finance/audit_uji_aturan.go`

Selama masih ada item `Terpilih` yang belum punya bukti → tetap `menunggu_data`, dengan ringkas yang menyebut **berapa** yang belum. Begitu semuanya terjawab → `bersih` atau `berbunyi` menurut kondisi idealnya.

⛔ **Tidak ada jalur di mana manusia menyatakan sendiri hasilnya bersih.** Manusia menyediakan bahan, mesin menyimpulkan.

**Bergantung pada**: T1.2

### T1.5 · Panel detail menampilkan dan menerima bukti
`audit-bharata/src/features/audit/components/detail-uji-panel.tsx`

Daftar item `Terpilih` dengan keadaan terjawab/belum, unggah per item, isian angka, dan tautan unduh berkasnya.

⚠️ **Digerbang `bolehTinjau`**, sama seperti tombol Tandai wajar. Paket `Audit: Direksi` dan `Audit: Pembaca` memegang `audit.view` dan rutin membuka panel ini, tetapi tak memegang izin tulisnya — kontrol unggah yang pasti dijawab 403 membuat pemakainya menyimpulkan sistemnya rusak.

⚠️ **BE naik sebelum FE.** Field bukti dirender hanya bila ada; tanpa itu panel tetap berfungsi.

**Bergantung pada**: T1.3

### T1.6 · Jalankan sekali lewat gateway, dengan berkas sungguhan
Bukan `curl` ke endpoint saja: **satu perjalanan utuh sebagai orang** — buka kertas kerja, buka `jurnal_manual_besar`, unggah dokumen sumber untuk tiap item terpilih, isi angkanya, lihat barisnya berpindah dari `menunggu data`.

⚠️ **Ukur berkas sungguhan terhadap batas 4 MB di sini**, dan catat hasilnya ke TBD [[Finance - Audit Internal]] apa pun jawabannya. Angka nol yang mencurigakan diperlakukan sebagai pertanyaan.

**Bergantung pada**: T1.5

---

## Fase 2 — Penjalan untuk sebelas uji sisanya

Tiap uji satu task tersendiri, dan **inilah yang benar-benar membuka dua belas uji itu** — bukan fase 1. Diurutkan menurut nilainya, bukan menurut kemudahannya.

- **T2.1 `rekonsiliasi_bank`** — Bentuk B. Yang paling sering ditanya dan yang memicu seluruh analisis ini.
- **T2.2 `rekonsiliasi_pajak`** — Bentuk B. Sisi ERP-nya sudah ada di arsip pajak finance-service.
- **T2.3 `penyesuaian_persediaan`**, **T2.4 `kapitalisasi_vs_beban`**, **T2.5 `retur_penjualan`**, **T2.6 `pisah_batas_penjualan`**, **T2.7 `penjualan_pt_ke_cv`** — Bentuk A, seluruhnya memakai `Terpilih` seperti `jurnal_manual_besar`, jadi polanya sudah jadi setelah T1.4.
- **T2.8 `kas_rekening_cv`**, **T2.9 `piutang_iklan_ke_cv`** — Bentuk B, tapi ⚠️ **bersinggungan dengan [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]]**; periksa dulu apakah sisi ERP-nya datang dari FINCON, bukan Accurate.
- **T2.10 `kalender_kepatuhan`**, **T2.11 `daftar_pihak_berelasi`** — dokumennya berumur panjang (akta, bukti lapor), bukan per-periode. ⚠️ Model penyimpanan per-periode mungkin tidak muat; putuskan sebelum menulis.

---

## Fase 3 — Pembacaan otomatis (BERPRASYARAT, jangan dimulai)

⛔ **Tidak dimulai sampai ada persetujuan tertulis Direksi** untuk mengirim rekening koran ke layanan di luar perusahaan. Pemilik pekerjaan menyatakan itu dapat diterima *dengan* persetujuan tersebut (2026-09-03); persetujuannya belum ada.

- **T3.1 · Pengurai deterministik CSV/XLS.** Dikerjakan **lebih dulu dan terpisah**, dan tidak butuh persetujuan apa pun karena tak ada data yang keluar. Bila bank memberi e-statement tabel, model tidak dipakai sama sekali.
- **T3.2 · Pengurai PDF berteks.** Rapuh terhadap perubahan tata letak bank; kunci bentuk keluarannya dengan test atas berkas contoh sungguhan.
- **T3.3 · Model penglihatan lewat API luar**, hanya untuk dokumen tanpa teks terbaca mesin. Klien LLM **belum ada di mana pun di bip-erp** — ini infrastruktur baru, bukan menyambung kabel. VPS prod tanpa GPU, jadi tidak ada pilihan self-hosted yang sepadan.
  - ⛔ **PDF WAJIB dirender jadi gambar per halaman lebih dulu.** Diukur 2026-09-03: relay AI internal MENELAN lampiran PDF, dan lewat `/v1/chat/completions` ia membalas 200 dengan angka KARANGAN alih-alih galat. Gambar (PNG) terbaca benar. Rinciannya di ADR 0075 §4.
  - ⛔ **Patok id model `cc/claude-*` eksplisit.** Id `Claude` dan `token-router/*` membiarkan router memilih penyedia sendiri, jadi rekening koran bisa mendarat di penyedia yang tak seorang pun pilih.
  - ⚠️ Endpoint default-nya SSE; `stream:false` wajib eksplisit untuk klien Go.
- **T3.4 · Gerbang konfirmasi.** ⛔ Keluaran T3.1–T3.3 mengisi field angka sebagai **draf** dan **wajib** dikonfirmasi auditor sebelum dipakai — termasuk keluaran pengurai deterministik. Yang membedakan bukti dari tebakan adalah ada orang yang menyatakan angkanya benar, dan temuan modul ini bisa jadi dasar sanksi Rp 5 miliar.

---

## Dokumen Terkait

- [[ADR - 0075 Bukti Sisi Lawan Dilampirkan dan Angkanya Dicatat, Pembacaan Otomatis Menyusul]]
- [[Finance - Audit Internal]] · [[APP - Audit Internal]] · [[Microservices - File Service]]
- [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]] — bila §1 jalan lebih dulu, prefix MinIO dan rute unggah ikut pindah
