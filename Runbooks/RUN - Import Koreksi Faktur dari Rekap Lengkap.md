> **Status**: ⚠️ Implemented — **deployed 2026-09-05** (bip-erp [#1712](https://github.com/bip-itteam-internal/bip-erp/pull/1712) + [#1717](https://github.com/bip-itteam-internal/bip-erp/pull/1717), erp-frontend [#1453](https://github.com/bip-itteam-internal/erp-frontend/pull/1453) + [#1455](https://github.com/bip-itteam-internal/erp-frontend/pull/1455)). Uji "unggah tanpa suntingan ⇒ 0 koreksi" **LULUS di prod 5 Sep** (satu toko TikTok, 4 Sep, 35 baris, 35 tidak berubah). Langkah **Terapkan** belum pernah dijalankan di produksi — jalankan pertama kali pada rentang kecil. 🟡 **Koreksi gudang** (kolom *Gudang Accurate*) ada di branch `feat/koreksi-gudang-import` bip-erp + erp-frontend, **belum merged/deployed** (2026-09-11) — bagian gudang di bawah baru berlaku setelah deploy.

## Tujuan

Memperbaiki isi faktur Auto-Sync di Accurate secara massal dengan menyunting file Excel **Download Rekap Lengkap**, tanpa membuka satu per satu dialog koreksi per pesanan.

## Kapan dipakai

Saat rekonsiliasi bulanan menemukan lebih dari beberapa baris yang keliru pada faktur yang sudah terbit, misalnya:

- pesanan tercatat di **hari yang salah**;
- **kode barang** Accurate salah untuk sebuah SKU marketplace (mapping keliru atau belum ada);
- **harga jual master** salah sehingga nilai faktur meleset;
- SKU **paket** yang isi per unitnya salah, sehingga qty faktur menggelembung atau kurang;
- pesanan tercatat di **gudang yang salah** (dikirim dari Gudang Sidareja tapi faktur mencatat Gudang Sadewa, atau sebaliknya) — 🟡 belum deploy.

Untuk satu-dua pesanan saja, dialog koreksi per pesanan di tab Faktur lebih cepat. Untuk masalah yang berakar di master data (kode/harga/isi paket), impor ini yang benar karena perbaikannya ikut tersimpan di master, bukan hanya di satu faktur.

**Bukan lewat prosedur ini:** mengeluarkan pesanan dari faktur (menu koreksi pada baris fakturnya) dan vonis fake order massal (tab **Order FO** → **Import Excel**, cukup unggah daftar nomor pesanan). Sel `Accurate Number` yang kosong atau berisi `FO` **ditolak** — kolom itu bisa kosong sejak diunduh, jadi ia sengaja tidak diperlakukan sebagai perintah.

## Prasyarat

- Akses menu **Auto-Sync** (`/integration-accurate/auto-sync`) — role `finance` atau `integration`.
- Untuk mengoreksi **harga jual**: role admin/supervisor modul integration atau finance (gerbang yang sama dengan Upload Massal Harga Jual). Tanpa itu, baris harga ditolak dengan alasannya, koreksi lain tetap jalan.
- Kode barang tujuan (kolom `Code`) sudah ada di **Master Data → Product**. Impor tidak membuat master baru.
- Microsoft Excel / LibreOffice yang menyimpan kembali sebagai `.xlsx`.

## Langkah

1. **Unduh berkasnya.** Tab **Faktur Penjualan** → tombol **Download Rekap Lengkap** → pilih channel, toko (boleh banyak), dan rentang hari kirim. Berkas bernama `raw_<channel>_<dari>_<sampai>.xlsx`, satu baris per item pesanan.
2. **Sunting hanya kolom prefix Accurate.** Enam kolom pertama: `Accurate Number` · `Code` · `Name` · `Unit Price` · `Quantity (Daily Sales)` · `Amount`, ditambah kolom **paling kanan** `Gudang Accurate`. Arti tiap suntingan:

   | Suntingan | Artinya |
   |---|---|
   | `Accurate Number` diganti nomor faktur lain, toko sama | pindahkan pesanan ke hari faktur itu |
   | `Accurate Number` dikosongkan atau diisi `FO` | **ditolak** — pakai menu koreksi baris faktur / tab Order FO |
   | `Code` diganti | tulis Mapping SKU: SKU listing → kode master |
   | `Unit Price` diganti | tulis Harga Jual berlaku sejak hari faktur, lalu kirim ulang faktur di berkas ini |
   | `Quantity (Daily Sales)` diganti (SKU paket) | ubah isi per unit di Mapping SKU; wajib kelipatan qty pesanan |
   | `Gudang Accurate` diganti (kolom paling kanan) | pesanan dikirim dari gudang lain: baris faktur hari itu **dipecah per gudang** dan **dokumen retur** pesanan itu ikut dipindah. Isi persis nama gudang terdaftar (`Gudang Sadewa` / `Gudang Sidareja`). **Memindah stok di Accurate.** |
   | `Name` / `Amount` | diabaikan |

   Kolom `Warehouse Name` di berkas TikTok berisi gudang yang sama tetapi **tidak dibaca** — sunting `Gudang Accurate`. Nilai kolom gudang = gudang **menurut ERP** (penanda koreksi, selain itu gudang toko), bukan dibaca dari Accurate: dokumen yang gudangnya pernah diubah langsung di Accurate (mis. faktur Juli) bisa tampil berbeda.

   Baris yang **dihapus** dari berkas tidak berarti apa-apa, jadi Anda boleh menyisakan baris yang dikoreksi saja. Jangan menghapus **kolom**: sistem mencari kolom lewat judulnya, jadi urutan boleh berubah tapi judul kolom nomor pesanan dan SKU penjual harus tetap ada. Simpan sebagai `.xlsx`.
3. **Unggah.** Tombol **Import Koreksi** (di samping Download Rekap Lengkap) → pilih **channel yang sama** dengan unduhan → pilih berkas → isi **alasan batch** (wajib; tersimpan di riwayat koreksi tiap pesanan) → atur **Koreksi gudang mulai tanggal** bila perlu (bawaan & paling awal 1 Agustus 2026; pesanan yang hari fakturnya lebih awal ditolak) → **Preview**.
4. **Baca pratinjau.** Tabel menampilkan tiap koreksi beserta `Sebelum → Sesudah` dan vonisnya (`SIAP` · `PERLU_PERSETUJUAN` · `DITOLAK` · `DIABAIKAN`). Kartu ringkasan di atas tabel berfungsi sebagai penyaring. Belum ada apa pun yang ditulis pada tahap ini.
5. **Setujui perubahan master.** Koreksi `Code`/`Quantity`/`Unit Price` muncul di kotak kuning **Perubahan master-data** dengan centang terpisah (**Tulis Mapping SKU**, **Tulis Harga Jual**, **Pindah gudang**). Yang tidak dicentang akan dilewati. **Pindah gudang** menampilkan jumlah pesanan dan nomor retur yang ikut dipindah; centang hanya bila berkasnya unduhan **terbaru** — berkas lama mengisi kolom gudang dengan nilai lama dan bisa mengembalikan gudang yang sudah dikoreksi. Centang hanya yang Anda yakini — perubahan master berlaku untuk seluruh faktur yang memuat SKU itu saat dikirim ulang.
6. **Terapkan.** Tombol **Terapkan N koreksi**. Sistem menulis dengan urutan: mapping → riwayat harga → penanda pindah hari → **dokumen retur dipindah gudangnya, lalu penanda gudang pesanan** → kirim ulang tiap faktur **sekali**, termasuk faktur asal dan tujuan pindah hari.

## Verifikasi

- Layar hasil: kartu **Diterapkan** sesuai jumlah yang Anda setujui, **Gagal** = 0, dan daftar **Dokumen Accurate yang disentuh** semuanya `RESENT` (atau `SKIPPED` bila memang sudah sesuai).
- Buka satu faktur yang dikoreksi di tab Faktur → modal detail → nilainya sudah berubah; bandingkan dengan dokumen yang sama di Accurate.
- Unduh ulang **Rekap Lengkap** untuk rentang yang sama, lalu unggah kembali **tanpa menyunting apa pun**: pratinjau harus melaporkan **0 koreksi**. Ini uji terbaik bahwa berkas dan faktur sudah sinkron. Terbukti di prod 2026-09-05: 35 baris dibaca, 35 tidak berubah, nol koreksi.
- Koreksi gudang: buka faktur & retur pesanan yang dipindah **di Accurate** — baris pesanan itu di gudang tujuan, qty/harga/nomor/tanggal tak berubah, dan untuk baris **paket** periksa gudang **komponennya** (perilaku ini belum terbukti di prod; wajib dicek pada uji pertama).
- Riwayat: tombol **Riwayat import** di modal (arsip batch: siapa, kapan, berkas apa, hasil tiap baris), dan riwayat koreksi per pesanan di dialog koreksi order.

## Bila gagal / Rollback

| Pesan | Artinya & tindakan |
|---|---|
| `File berubah sejak preview` (409) | Berkas tersimpan ulang setelah pratinjau. Tekan **Preview** lagi, lalu Terapkan. |
| Baris ditolak karena `Accurate Number` kosong / `FO` | Bukan perintah yang dikenali berkas ini. Kalau kolom itu kosong di banyak baris, kemungkinan unduhannya gagal memuat nomor faktur — unduh ulang Rekap Lengkap. Untuk benar-benar mengeluarkan pesanan atau memvonis fake order, pakai tuasnya masing-masing. |
| `kolom "…" tidak ada di header` | Channel yang dipilih beda dengan channel unduhan. Pilih channel yang benar; kolom kunci tiap marketplace berbeda nama (Shopee `No. Pesanan` + `SKU Induk`, TikTok `Order ID` + `Seller SKU`, Lazada `Lazada ID` + `Seller SKU`). |
| `koreksi menyentuh N faktur — batas 150` / `lebih dari 60.000 baris` | Pecah berkas per toko atau per minggu. |
| Baris `DITOLAK` lainnya | Alasannya tertulis di kolom Keterangan: paket multi-komponen (ubah di Mapping SKU), qty pada SKU biasa (tak ada tuas), faktur sudah dibayar (lepas penerimaan atau balik lewat retur), faktur diakui manual / menunggu Kotak Adopsi / IMPORTED / dihapus, pesanan pra-cutover 10 Juli 2026, kode belum ada di master. |
| Pindah gudang `GAGAL`: *retur gagal dipindah, gudang pesanan & faktur BELUM diubah* | Tak ada penanda yang disimpan untuk pesanan itu **dan pesanan lain yang berbagi dokumen retur**. Gangguan sementara → unggah ulang berkas yang sama (retur yang sudah pindah dilewati). Dokumen retur bermasalah di Accurate (SALAH-IKAT, retur sudah dihapus, mode retur kosong) → betulkan dokumennya dulu, lalu unggah ulang. |
| Pindah gudang ditolak: *retur … juga memuat pesanan … yang gudangnya …* | Satu dokumen retur hanya bisa satu gudang. Koreksi semua pesanan retur itu ke gudang yang sama di berkas yang sama (unduh rentang yang memuat semuanya). |
| Faktur *dikirim ulang, tapi belum tuntas: gudang tak bisa dipindah otomatis* | Faktur terkunci retur: sebagian barang sudah diretur sehingga barisnya tak bisa diturunkan. Pindahkan sisanya manual di Accurate, lalu tekan **Retry** pada faktur itu supaya catatan galatnya hilang. |
| Baris `GAGAL` setelah Terapkan | Master/penanda **sudah tersimpan**, yang gagal kirim ulangnya. Perbaiki penyebab di layar faktur lalu tekan **Retry** pada fakturnya — jangan mengunggah ulang berkas yang sama, koreksinya sudah tercatat. |

**Rollback** tidak otomatis: impor ini tidak punya tombol batal. Yang bisa dilakukan — kembalikan nilainya lewat impor kedua (mis. kembalikan `Accurate Number` ke nomor faktur semula, atau tulis ulang `Code`/`Unit Price` yang benar), atau perbaiki langsung di Master Data → Mapping SKU / Harga Jual lalu Retry fakturnya. Karena itu pratinjau wajib dibaca sebelum Terapkan.

## Catatan

- Sejak PR #1712, enam kolom prefix Accurate pada Rekap Lengkap = **baris faktur yang benar-benar dibukukan** (kode master hasil mapping, harga riwayat pada hari faktur, qty terekspansi isi paket). Sebelumnya kolom itu memakai harga master hari ini tanpa riwayat dan tanpa mapping — angka lama karena itu bisa berbeda dari nilai faktur.
- Harga yang dikoreksi hanya dikirim ulang ke faktur **yang ada di berkas**. Faktur lain dengan SKU sama tidak disentuh otomatis; bila perlu, unggah rentang yang lengkap atau pakai halaman Harga Jual → Dampak Harga.
- **Koreksi gudang (🟡 belum deploy)**: gudang faktur tetap diambil dari config toko, **kecuali** pesanan yang dikoreksi lewat kolom `Gudang Accurate` — penandanya dibaca setiap faktur/retur dirakit ulang, jadi kirim ulang berikutnya tak mengembalikan gudang. Faktur **Juli** selalu ditolak (sengaja dibiarkan di gudang lama, keputusan 2026-09-02). Rincian keputusan: [[ADR - 0077 Koreksi Faktur via Impor Rekap Lengkap Mengalir ke Master-Data, Bukan Override per Baris]] §1c. Untuk memindah **seluruh** dokumen satu periode sekaligus (bukan per pesanan), tim IT punya perkakas `cmd/gudangfix` — lihat [[Microservices - Integration Service]].

## Dokumen Terkait

- [[ADR - 0077 Koreksi Faktur via Impor Rekap Lengkap Mengalir ke Master-Data, Bukan Override per Baris]] — kenapa koreksi mengalir ke master, bukan disimpan per baris faktur.
- [[Microservices - Integration Service]] · [[API - Integration Service]] · [[APP - Web ERP]]
- [[ADR - 0018 Faktur Permanen - Semua Pembalikan via Retur]] · [[External - Accurate]]
