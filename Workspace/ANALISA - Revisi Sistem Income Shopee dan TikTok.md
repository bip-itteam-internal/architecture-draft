# ANALISA - Revisi Sistem Income Shopee dan TikTok

Papan kerja hasil `/analisa-kebutuhan` 2026-09-22, dari tiket finance **"Revisi Sistem Income"**.
Keputusannya ada di [[ADR - 0118 Ongkir Shopee Dihitung Aktual Dikurangi Bagian Pembeli dan Subsidi]]
dan [[ADR - 0119 Kompensasi TikTok Dipisah Menurut Sudah atau Belum Ada Uang Masuk]] — berkas ini
hanya papan kerja, bukan sumber keputusan.

## Angka dasar (diukur prod VPS Biznet, 2026-09-22, read-only)

| Pokok | Terdampak | Nilai | Masih bertambah? |
|---|---|---|---|
| Ongkir Shopee salah pos (6114 ↔ admin) | 3.870 pesanan | **Rp96.826.227** | ya, ±Rp16 jt/bulan |
| Kompensasi TikTok atas pesanan sudah cair | 14 pesanan | **Rp1.610.697** | pelan |
| *(kontrol)* kompensasi TikTok yang sudah benar | 360 pesanan | Rp34.872.894 | — jangan disentuh |

⚠️ Angka ongkir Shopee **diperbaiki 2026-09-22 saat implementasi** — angka awal (3.865/Rp98.260.427)
memakai pendekatan bucket (Σ|final|) atas hipotesis yang belum tepat. Angka final di atas hasil
perbandingan langsung rumus lama vs rumus baru atas seluruh populasi. Lihat
[[ADR - 0118 Ongkir Shopee Dihitung Aktual Dikurangi Bagian Pembeli dan Subsidi]] § Context.

Prioritas mengikuti angka, bukan urutan di tiket: **Shopee ±60× lipat TikTok** dan tak menunggu
keputusan siapa pun lagi.

## Urutan kerja

**T1 — ~~Ukur 96 pesanan Shopee yang menyimpang dari pola~~ GUGUR.** Hipotesis "96 pesanan
menyimpang" hasil pendekatan bucket yang belum tepat (`final = −buyer`, cocok 97,5%). Diukur ulang
saat implementasi dengan hipotesis yang benar (`final = −(actual−rebate)`): cocok **100%**, nol
pengecualian, atas seluruh 90.194 dokumen. Rumus final (T2) tidak lagi bergantung pada
`final_shipping_fee` sama sekali, jadi populasi menyimpang itu tidak pernah ada. Detail:
[[ADR - 0118 Ongkir Shopee Dihitung Aktual Dikurangi Bagian Pembeli dan Subsidi]] § Consequences.

**T2 — ✅ SELESAI (kode).** Perbaiki rumus ongkir Shopee. Beban ongkir = aktual − bagian pembeli +
proteksi + ongkir pengembalian; `final_shipping_fee` **dan subsidi** tidak dipakai di rumus ini —
subsidi tetap di `TotalOtherIncome`, diurus mekanisme rebate-ke-ongkir yang sudah ada (ditemukan
saat implementasi: memasukkan subsidi ke rumus ini akan menghitungnya dua kali). Diimplementasikan
lewat `entity.OpsiTransformShopee` (bukan mengubah tanda tangan fungsi lama). Fixture
`TestShopeeTransformIncomeIdentity_RealSample` diperbaiki + kontrol negatif dijalankan manual (2×:
rumus dengan subsidi salah arah, dan rumus lama dikembalikan — dua-duanya merah pada sebab yang
tepat). Penjaga residual bernilai (WARN, ambang Rp500) terpasang di `transformShopeeIncome`.
Commit: `5db06269` (entity), `f457614d` (usecase, branch `fix/ongkir-shopee-rumus-resmi`).

**T3 — Gerbang per-order + penerapan prod ongkir Shopee.** ⚠️ **Bukan kv tanggal seperti rencana
awal** — income Shopee ditulis ulang dari escrow tiap sync, jadi kv tanggal akan retroaktif
(ditemukan saat implementasi). Gerbangnya `rumusOngkirBaruBerlaku` (per shop+hari, memakai
`ShopeeHariSudahDibukukan` — mekanisme yang sama dengan `bolehBukukanPenyesuaian`) — **sudah
terpasang di kode** (bagian dari T2). Yang tersisa di sini murni operasional: merge PR → deploy →
ukur order yang sudah dapat rumus baru pasca-deploy → buktikan satu penerimaan di Accurate cocok
dengan Subtotal Ongkos Kirim Shopee → beri tahu finance. **Eksekusi prod oleh manusia.**

**T4 — Kompensasi TikTok: pisahkan populasi + gerbang retur, SATU perubahan.** Pembedanya payout
pesanan itu sendiri (bukan payout + kompensasi). Payout ≈ 0 → perilaku sekarang. Payout > 0 →
baris Pendapatan Lain-lain tanpa mengisi nilai bayar, **dan** returnya kembali dibukukan. Pakai
ulang pola jalur Shopee yang sudah ada, jangan merancang baru. ⛔ Dua sisi ini **tidak boleh**
dipisah jadi dua PR. Tanpa dependensi ke T1–T3.

**T5 — Deploy TikTok + verifikasi lewat pesanan sungguhan.** Satu service, tanpa env baru. Buktikan
dengan menelusuri satu pesanan dari populasi tiket sampai ke dokumen Accurate — bukan berhenti di
"kode sudah benar". **Butuh T4. Eksekusi prod oleh manusia.**

## Utang yang ditemukan sepanjang analisa (di luar lingkup tiket)

- **54 penyesuaian TikTok tanpa pesanan padanan** — naik tajam dari 7 yang tercatat saat
  [[ADR - 0056 Penyesuaian Statement TikTok Menambah Payout Order]] ditulis. Sebab kenaikannya
  belum ditelusuri; uangnya nyata.
- **Retur TikTok lama yang menggantung** menunggu scan gudang atas barang yang takkan pernah
  datang, plus beberapa yang sudah terkirim padahal barangnya tak pernah kembali. Finance
  menyatakan lingkup perbaikan "sekarang dan ke depan", jadi ini **tidak** ikut — tapi tidak hilang
  sendiri.
- **14 pesanan TikTok yang sudah terlanjur salah catat** — tidak dibetulkan mundur. Perlu keputusan
  terpisah bila finance kelak menginginkannya.
- **Tuas koreksi pemindahan pelunasan ke akun GL** masih belum ada; kasus prod pernah ditolak
  sistem. Tertahan keputusan finance, lihat
  [[ADR - 0100 Penerimaan Beda dengan Accurate Diputus di Halaman Penerimaan]].
- **kv `settlement-adjustment` masih berbagi akun dengan biaya admin**, sehingga residual tetap
  tak bernama dan kelas "komponen kehilangan nama" bisa terulang.
- ✅ **Label server di vault sudah dibetulkan di sesi ini** — VPS Biznet kini ditandai sebagai
  produksi, dan `10.10.10.120` ditandai menyala-tapi-tidak-dipakai.

## Pertanyaan untuk Finance (disusun 2026-09-22)

Ditulis untuk tim Finance/FAT, bahasa bisnis. Nomor 1 dan 2 **menahan** T3; sisanya paralel.

**Ongkir Shopee**

1. ⛔ Selisih ongkir **pindah ke Beban Admin, bukan hilang**. Perbaikan membuat Biaya Ongkir jadi 0
   (sama dengan Subtotal Ongkos Kirim Shopee), tapi selisihnya berpindah ke baris Penyesuaian yang
   memakai akun **sama dengan Beban Admin E-Commerce (6112)** — ±Rp96,8 jt di ±3.870 pesanan. Tiket
   minta dua akun sama-sama benar; perbaikan ini menutup sisi ongkir tapi menambah sisi admin dulu.
   Boleh dinyalakan begitu, atau tunggu sisi admin beres?
2. ⛔ **Akun tersendiri untuk baris Penyesuaian** — sudah bisa diputuskan? Pertanyaan yang sama sudah
   menunggu SPV FAT di [[ADR - 0116 Setelan Akun Marketplace Bergerbang dan Berjejak, Komponen Tak Dikenal Wajib Terlihat]] (T5).
   Kalau akunnya dipisah, nomor 1 selesai sendiri.
3. **Ongkir pengembalian barang** selama ini tak pernah masuk Biaya Ongkir (nyangkut di Penyesuaian
   tanpa nama); perbaikan ini memberinya rumah di Biaya Ongkir. Pos yang benar?
4. **Periode yang sudah ditutup tidak diubah** — konfirmasi ini yang dimaksud "sekarang dan ke depan".
   Konsekuensinya laporan lama dan baru memakai dua cara hitung.
5. Pesanan **cair sebelum 1 September tapi belum dibukukan** hasilnya tidak 0 melainkan sebesar
   subsidinya (aturan potongan ongkir baru berlaku 1 September). Perlu perlakuan khusus?
6. **Proteksi pengiriman ±Rp7,4 jt (21.148 pesanan)** dan **ongkir balik ±Rp1,17 jt** masih tercatat
   di Beban Admin padahal sifatnya ongkir. Sekalian dipindah, atau terpisah?

**Kompensasi TikTok** (perlakuannya sudah dijawab tiket: Pendapatan Lain-lain, nilai bayar 0)

7. **14 pesanan yang terlanjur salah catat** (±Rp1,61 jt) — dibetulkan mundur atau berlaku maju saja?
8. **208 dokumen retur menggantung** menunggu scan atas barang yang takkan pernah datang (hilang di
   logistik, sudah diganti rugi), plus beberapa retur terkirim padahal barang tak pernah kembali
   sehingga stok Accurate bertambah untuk barang yang tak ada. Dijadwalkan pembersihannya?
9. **54 penyesuaian TikTok tanpa pesanan padanan** (naik tajam dari 7) — dibukukan sebagai Pendapatan
   Lain-lain tanpa pesanan, atau ditahan untuk ditelusuri?
10. Konfirmasi **360 pesanan kompensasi yang sudah benar** (±Rp34,87 jt) tidak disentuh.

## Catatan cara mengukur ulang

Pengukuran dijalankan **read-only** di VPS Biznet lewat `docker exec Integration-MongoDB mongosh`,
kredensial dibaca dari `.env` setempat sehingga tidak perlu menyeberang ke mesin siapa pun.
⛔ Jangan memakai `10.10.10.120` sebagai pembanding — menyala, tapi tidak dipakai.
