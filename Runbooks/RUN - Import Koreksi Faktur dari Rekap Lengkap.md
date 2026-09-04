> **Status**: 🟡 Draft — mesinnya sudah merge (bip-erp PR [#1712](https://github.com/bip-itteam-internal/bip-erp/pull/1712), erp-frontend PR [#1453](https://github.com/bip-itteam-internal/erp-frontend/pull/1453)), tapi **pemangkasan lingkupnya belum** (bip-erp [#1717](https://github.com/bip-itteam-internal/bip-erp/pull/1717), erp-frontend [#1455](https://github.com/bip-itteam-internal/erp-frontend/pull/1455)). Prosedur ini belum pernah dijalankan di produksi. Jadikan ✅ setelah uji pasca-deploy di bawah lulus.

## Tujuan

Memperbaiki isi faktur Auto-Sync di Accurate secara massal dengan menyunting file Excel **Download Rekap Lengkap**, tanpa membuka satu per satu dialog koreksi per pesanan.

## Kapan dipakai

Saat rekonsiliasi bulanan menemukan lebih dari beberapa baris yang keliru pada faktur yang sudah terbit, misalnya:

- pesanan tercatat di **hari yang salah**;
- **kode barang** Accurate salah untuk sebuah SKU marketplace (mapping keliru atau belum ada);
- **harga jual master** salah sehingga nilai faktur meleset;
- SKU **paket** yang isi per unitnya salah, sehingga qty faktur menggelembung atau kurang.

Untuk satu-dua pesanan saja, dialog koreksi per pesanan di tab Faktur lebih cepat. Untuk masalah yang berakar di master data (kode/harga/isi paket), impor ini yang benar karena perbaikannya ikut tersimpan di master, bukan hanya di satu faktur.

**Bukan lewat prosedur ini:** mengeluarkan pesanan dari faktur (menu koreksi pada baris fakturnya) dan vonis fake order massal (tab **Order FO** → **Import Excel**, cukup unggah daftar nomor pesanan). Sel `Accurate Number` yang kosong atau berisi `FO` **ditolak** — kolom itu bisa kosong sejak diunduh, jadi ia sengaja tidak diperlakukan sebagai perintah.

## Prasyarat

- Akses menu **Auto-Sync** (`/integration-accurate/auto-sync`) — role `finance` atau `integration`.
- Untuk mengoreksi **harga jual**: role admin/supervisor modul integration atau finance (gerbang yang sama dengan Upload Massal Harga Jual). Tanpa itu, baris harga ditolak dengan alasannya, koreksi lain tetap jalan.
- Kode barang tujuan (kolom `Code`) sudah ada di **Master Data → Product**. Impor tidak membuat master baru.
- Microsoft Excel / LibreOffice yang menyimpan kembali sebagai `.xlsx`.

## Langkah

1. **Unduh berkasnya.** Tab **Faktur Penjualan** → tombol **Download Rekap Lengkap** → pilih channel, toko (boleh banyak), dan rentang hari kirim. Berkas bernama `raw_<channel>_<dari>_<sampai>.xlsx`, satu baris per item pesanan.
2. **Sunting hanya kolom prefix Accurate.** Enam kolom pertama: `Accurate Number` · `Code` · `Name` · `Unit Price` · `Quantity (Daily Sales)` · `Amount`. Arti tiap suntingan:

   | Suntingan | Artinya |
   |---|---|
   | `Accurate Number` diganti nomor faktur lain, toko sama | pindahkan pesanan ke hari faktur itu |
   | `Accurate Number` dikosongkan atau diisi `FO` | **ditolak** — pakai menu koreksi baris faktur / tab Order FO |
   | `Code` diganti | tulis Mapping SKU: SKU listing → kode master |
   | `Unit Price` diganti | tulis Harga Jual berlaku sejak hari faktur, lalu kirim ulang faktur di berkas ini |
   | `Quantity (Daily Sales)` diganti (SKU paket) | ubah isi per unit di Mapping SKU; wajib kelipatan qty pesanan |
   | `Name` / `Amount` | diabaikan |

   Baris yang **dihapus** dari berkas tidak berarti apa-apa, jadi Anda boleh menyisakan baris yang dikoreksi saja. Jangan menghapus **kolom**: sistem mencari kolom lewat judulnya, jadi urutan boleh berubah tapi judul kolom nomor pesanan dan SKU penjual harus tetap ada. Simpan sebagai `.xlsx`.
3. **Unggah.** Tombol **Import Koreksi** (di samping Download Rekap Lengkap) → pilih **channel yang sama** dengan unduhan → pilih berkas → isi **alasan batch** (wajib; tersimpan di riwayat koreksi tiap pesanan) → **Preview**.
4. **Baca pratinjau.** Tabel menampilkan tiap koreksi beserta `Sebelum → Sesudah` dan vonisnya (`SIAP` · `PERLU_PERSETUJUAN` · `DITOLAK` · `DIABAIKAN`). Kartu ringkasan di atas tabel berfungsi sebagai penyaring. Belum ada apa pun yang ditulis pada tahap ini.
5. **Setujui perubahan master.** Koreksi `Code`/`Quantity`/`Unit Price` muncul di kotak kuning **Perubahan master-data** dengan centang terpisah (**Tulis Mapping SKU**, **Tulis Harga Jual**). Yang tidak dicentang akan dilewati. Centang hanya yang Anda yakini — perubahan master berlaku untuk seluruh faktur yang memuat SKU itu saat dikirim ulang.
6. **Terapkan.** Tombol **Terapkan N koreksi**. Sistem menulis dengan urutan: mapping → riwayat harga → penanda pindah hari → kirim ulang tiap faktur **sekali**, termasuk faktur asal dan tujuan pindah hari.

## Verifikasi

- Layar hasil: kartu **Diterapkan** sesuai jumlah yang Anda setujui, **Gagal** = 0, dan daftar **Dokumen Accurate yang disentuh** semuanya `RESENT` (atau `SKIPPED` bila memang sudah sesuai).
- Buka satu faktur yang dikoreksi di tab Faktur → modal detail → nilainya sudah berubah; bandingkan dengan dokumen yang sama di Accurate.
- Unduh ulang **Rekap Lengkap** untuk rentang yang sama, lalu unggah kembali **tanpa menyunting apa pun**: pratinjau harus melaporkan **0 koreksi**. Ini uji terbaik bahwa berkas dan faktur sudah sinkron.
- Riwayat: tombol **Riwayat import** di modal (arsip batch: siapa, kapan, berkas apa, hasil tiap baris), dan riwayat koreksi per pesanan di dialog koreksi order.

## Bila gagal / Rollback

| Pesan | Artinya & tindakan |
|---|---|
| `File berubah sejak preview` (409) | Berkas tersimpan ulang setelah pratinjau. Tekan **Preview** lagi, lalu Terapkan. |
| Baris ditolak karena `Accurate Number` kosong / `FO` | Bukan perintah yang dikenali berkas ini. Kalau kolom itu kosong di banyak baris, kemungkinan unduhannya gagal memuat nomor faktur — unduh ulang Rekap Lengkap. Untuk benar-benar mengeluarkan pesanan atau memvonis fake order, pakai tuasnya masing-masing. |
| `kolom "…" tidak ada di header` | Channel yang dipilih beda dengan channel unduhan. Pilih channel yang benar; kolom kunci tiap marketplace berbeda nama (Shopee `No. Pesanan` + `SKU Induk`, TikTok `Order ID` + `Seller SKU`, Lazada `Lazada ID` + `Seller SKU`). |
| `koreksi menyentuh N faktur — batas 150` / `lebih dari 60.000 baris` | Pecah berkas per toko atau per minggu. |
| Baris `DITOLAK` lainnya | Alasannya tertulis di kolom Keterangan: paket multi-komponen (ubah di Mapping SKU), qty pada SKU biasa (tak ada tuas), faktur sudah dibayar (lepas penerimaan atau balik lewat retur), faktur diakui manual / menunggu Kotak Adopsi / IMPORTED / dihapus, pesanan pra-cutover 10 Juli 2026, kode belum ada di master. |
| Baris `GAGAL` setelah Terapkan | Master/penanda **sudah tersimpan**, yang gagal kirim ulangnya. Perbaiki penyebab di layar faktur lalu tekan **Retry** pada fakturnya — jangan mengunggah ulang berkas yang sama, koreksinya sudah tercatat. |

**Rollback** tidak otomatis: impor ini tidak punya tombol batal. Yang bisa dilakukan — kembalikan nilainya lewat impor kedua (mis. kembalikan `Accurate Number` ke nomor faktur semula, atau tulis ulang `Code`/`Unit Price` yang benar), atau perbaiki langsung di Master Data → Mapping SKU / Harga Jual lalu Retry fakturnya. Karena itu pratinjau wajib dibaca sebelum Terapkan.

## Catatan

- Sejak PR #1712, enam kolom prefix Accurate pada Rekap Lengkap = **baris faktur yang benar-benar dibukukan** (kode master hasil mapping, harga riwayat pada hari faktur, qty terekspansi isi paket). Sebelumnya kolom itu memakai harga master hari ini tanpa riwayat dan tanpa mapping — angka lama karena itu bisa berbeda dari nilai faktur.
- Harga yang dikoreksi hanya dikirim ulang ke faktur **yang ada di berkas**. Faktur lain dengan SKU sama tidak disentuh otomatis; bila perlu, unggah rentang yang lengkap atau pakai halaman Harga Jual → Dampak Harga.
- **Gudang belum bisa dikoreksi lewat prosedur ini maupun lewat layar mana pun.** Gudang faktur selalu diambil dari config toko, dan perubahannya tidak memicu kirim ulang karena tidak ikut dihitung sebagai "isi faktur". Lihat catatan di [[ADR - 0077 Koreksi Faktur via Impor Rekap Lengkap Mengalir ke Master-Data, Bukan Override per Baris]].

## Dokumen Terkait

- [[ADR - 0077 Koreksi Faktur via Impor Rekap Lengkap Mengalir ke Master-Data, Bukan Override per Baris]] — kenapa koreksi mengalir ke master, bukan disimpan per baris faktur.
- [[Microservices - Integration Service]] · [[API - Integration Service]] · [[APP - Web ERP]]
- [[ADR - 0018 Faktur Permanen - Semua Pembalikan via Retur]] · [[External - Accurate]]
