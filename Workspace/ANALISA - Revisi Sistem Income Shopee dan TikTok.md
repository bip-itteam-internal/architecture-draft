# ANALISA - Revisi Sistem Income Shopee dan TikTok

Papan kerja hasil `/analisa-kebutuhan` 2026-09-22, dari tiket finance **"Revisi Sistem Income"**.
Keputusannya ada di [[ADR - 0118 Ongkir Shopee Dihitung Aktual Dikurangi Bagian Pembeli dan Subsidi]]
dan [[ADR - 0119 Kompensasi TikTok Dipisah Menurut Sudah atau Belum Ada Uang Masuk]] — berkas ini
hanya papan kerja, bukan sumber keputusan.

## Angka dasar (diukur prod VPS Biznet, 2026-09-22, read-only)

| Pokok | Terdampak | Nilai | Masih bertambah? |
|---|---|---|---|
| Ongkir Shopee salah pos (6114 ↔ admin) | 3.865 pesanan | **Rp98.260.427** | ya, ±Rp16 jt/bulan |
| Kompensasi TikTok atas pesanan sudah cair | 14 pesanan | **Rp1.610.697** | pelan |
| *(kontrol)* kompensasi TikTok yang sudah benar | 360 pesanan | Rp34.872.894 | — jangan disentuh |

Prioritas mengikuti angka, bukan urutan di tiket: **Shopee ±60× lipat TikTok** dan tak menunggu
keputusan siapa pun lagi.

## Urutan kerja

**T1 — Ukur 96 pesanan Shopee yang menyimpang dari pola.** Read-only, tanpa kode. Dari 3.865
pesanan kelas bermasalah, 3.769 berpola `final = −bagian pembeli`; sisa **96** belum terjelaskan.
Cari polanya dan pastikan rumus baru tidak membuat mereka lebih salah. **Prasyarat T3** — jangan
menyalakan saklar sebelum ini terjawab.

**T2 — Perbaiki rumus ongkir Shopee.** Beban ongkir = aktual − (bagian pembeli + subsidi) +
proteksi + ongkir pengembalian; `final_shipping_fee` tidak dipakai. Sekalian: betulkan fixture
`TestShopeeTransformIncomeIdentity_RealSample` yang kehilangan `actual_shipping_fee`, tambah kasus
dari kelas bermasalah, dan **kontrol negatif** (mengembalikan rumus lama harus merah pada nilai
ongkirnya). Tambahkan penjaga residual bernilai untuk pesanan Shopee. Tanpa dependensi.

**T3 — Saklar tanggal + penerapan prod ongkir Shopee.** kv cutover dipasang di **seluruh** jalur
(kirim, pratinjau, ekspor) lewat satu penentu akun-per-hari. Urutan: deploy dengan kv kosong →
ukur → isi kv → beri tahu finance. ⛔ **Jangan** memanggil kirim-ulang dokumen lama: jalur itu
masih membawa cacat "menarik keluar pelunasannya sendiri". **Butuh T1 + T2. Eksekusi prod oleh
manusia.**

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

## Catatan cara mengukur ulang

Pengukuran dijalankan **read-only** di VPS Biznet lewat `docker exec Integration-MongoDB mongosh`,
kredensial dibaca dari `.env` setempat sehingga tidak perlu menyeberang ke mesin siapa pun.
⛔ Jangan memakai `10.10.10.120` sebagai pembanding — menyala, tapi tidak dipakai.
