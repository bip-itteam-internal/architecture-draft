# RUN - Panduan WMS Fulfillment Gudang Tinggarjaya

> Panduan operasional untuk admin gudang: cara memproses pesanan marketplace
> (TikTok Shop & Shopee) dari pesanan masuk sampai serah terima ke kurir,
> memakai menu **Warehouse** di ERP.
>
> Arsitektur & detail teknis: [[WH - Fulfillment Flow & WMS Tinggarjaya]] ·
> [[API - Warehouse Service]] · [[Microservices - Warehouse Service]]
>
> Terakhir diperbarui: 17 Juli 2026

---

## Gambaran Alur Kerja

```
Pesanan Masuk (otomatis)
      │
      ▼
[1] ANTRIAN PESANAN  — terima (approve) pesanan
      │
      ▼
[2] PENGAMBILAN BARANG — pilih tim packer → UNDUH DATA (wajib) → ambil barang
      │
      ▼
[3] PENGEMASAN — ceklis pesanan → CETAK RESI (satu klik) → tempel resi
      │
      ▼
[4] SERAH TERIMA KURIR — konfirmasi paket diserahkan
      │
      ▼
[✓] Selesai — audit kapan pun lewat RIWAYAT CETAK RESI
```

Prinsip penting yang dijaga sistem:

1. **Unduh data dulu, baru bisa cetak resi.** Pesanan yang belum pernah
   diunduh (belum masuk rekap rekon) akan **ditolak** saat diproses. Ini
   memastikan tidak ada pesanan yang lolos dari rekap.
2. **Rekon per batch.** Unduhan hanya berisi pesanan yang *belum pernah
   ditarik* — unduhan siang tidak akan membawa data batch pagi, jadi tidak
   ada dobel hitung.
3. **Setiap resi tercatat**: siapa yang cetak, tim mana yang mengemas,
   kapan dicetak, kapan diserahkan ke kurir, dan berapa kali dicetak ulang.

---

## Menu di Sidebar Warehouse

| Menu | Fungsi |
|---|---|
| **Dashboard** | Ringkasan jumlah pesanan per tahap |
| **Antrian Pesanan** | Melihat semua pesanan, menerima (approve) pesanan baru |
| **Pengambilan Barang** | Picklist barang + **unduh data rekon** (pilih tim packer di sini) |
| **Pengemasan** | Ceklis pesanan + **cetak resi satu klik** |
| **Riwayat Cetak Resi** | Audit resi yang sudah dicetak + cetak ulang |
| **Serah Terima Kurir** | Konfirmasi paket diserahkan ke kurir |
| **Master Produk** | Kelola daftar SKU, barcode, lokasi rak |

Angka oranye di samping menu = jumlah pesanan yang **menunggu dikerjakan**
di tahap itu.

---

## Langkah 1 — Terima Pesanan (Antrian Pesanan)

Pesanan dari TikTok/Shopee masuk **otomatis** ke tab **Pesanan Baru**
(tidak perlu tarik manual dari seller center).

1. Buka menu **Antrian Pesanan**, tab **Pesanan Baru**.
2. Gunakan alat bantu bila perlu:
   - **Cari** nama/SKU produk atau nomor pesanan
   - **Filter Toko** — pilih per marketplace, bisa centang semua toko satu channel sekaligus
   - **Filter Tanggal** — preset cepat (Hari Ini / Kemarin / 7 / 30 / 90 hari)
     atau pilih tanggal + jam sendiri
3. Centang pesanan yang mau diterima (bisa **Pilih Semua**), klik **Approve**.
4. Pesanan pindah ke tab **Disetujui** dengan badge kuning **"Belum Ditarik"**.

> Pesanan mencurigakan bisa ditahan (HELD) dan dibatalkan otomatis bila
> dibatalkan pembeli di marketplace.

---

## Langkah 2 — Unduh Data & Ambil Barang (Pengambilan Barang)

Ini **langkah wajib** sebelum resi bisa dicetak.

1. Buka menu **Pengambilan Barang**.
2. **Pilih Tim Packer** di kanan atas: klik **T1** atau **T2** — tim yang akan
   mengerjakan batch ini. Pilihan diingat per komputer, cukup ganti saat
   ganti shift/tim.
3. Klik **Unduh** → pilih **"Unduh Pesanan Baru"**.
   - File Excel terunduh berisi rekap: nomor pesanan, tanggal, SKU, nama
     barang, qty, toko, ekspedisi, **kode packer (sudah terisi otomatis
     sesuai tim yang dipilih)**, dan kolom keterangan.
   - **Satu baris per produk** — siap dipakai rekap rekon tanpa scan satu-satu.
   - Pesanan yang ikut terunduh otomatis tercap **"Sudah Ditarik"**.
4. Ambil barang sesuai **Picklist SKU** (jumlah total per SKU, dari semua
   pesanan sekaligus — satu putaran ambil untuk banyak pesanan).

**Aturan penting soal Unduh:**

- **"Unduh Pesanan Baru"** = hanya pesanan yang belum pernah ditarik →
  dipakai untuk rekon per batch. Ini yang dipakai sehari-hari.
- **"Unduh Semua"** = semua pesanan termasuk yang sudah ditarik → hanya
  untuk keperluan khusus (mis. cetak ulang rekap yang hilang).
- **Jangan klik Unduh kalau tidak berniat memproses batch itu** — pesanan
  yang terunduh dianggap sudah masuk rekap dan tidak akan muncul lagi di
  "Unduh Pesanan Baru" berikutnya.
- Kolom lokasi rak di picklist akan terisi otomatis kalau **Master Produk**
  sudah diisi lokasi raknya (saat ini belum diterapkan — tampil
  "Lokasi rak belum diatur").

---

## Langkah 3 — Cetak Resi (Pengemasan)

1. Buka menu **Pengemasan**. Semua pesanan yang siap diproses tampil di sini
   (yang baru disetujui maupun yang gagal sebelumnya).
2. Pastikan **Tim Packer** di kanan atas sudah benar (T1/T2).
3. Centang pesanan yang barangnya sudah siap — atau klik **Pilih Semua**.
   - Pesanan dengan badge **"Belum Ditarik — unduh data dulu"** tidak bisa
     dipilih → kembali ke Langkah 2 dulu.
   - Pesanan TikTok dengan peringatan **"⚠ Package ID belum tersedia"**
     kemungkinan gagal — tunggu sinkronisasi atau laporkan ke tim IT.
4. Klik **"Cetak Resi (N) — Tim T1"**. Sistem otomatis:
   - **Mengatur pengiriman (RTS)** ke marketplace untuk pesanan yang belum →
     nomor resi (AWB) terbit;
   - **Mengambil dokumen resi** dari marketplace;
   - Mencatat tim packer ke semua pesanan dalam batch.
5. Lihat panel **"Hasil Proses Terakhir"**:
   - **Buka Resi** → resi terbuka di tab baru, siap di-print. Ada juga
     **"Buka Semua Resi"** untuk membuka sekaligus.
   - **"Diproses marketplace..."** (khusus Shopee — resinya dibuat asinkron)
     → tunggu beberapa detik, klik **Coba Lagi**.
   - **Gagal** → baca alasannya, klik **Coba Lagi**; kalau berulang,
     laporkan ke tim IT.
6. Print resi → **tempel ke paket sesuai rekap** → paket siap diserahkan.

> Panel hasil tetap tampil walau daftar pesanan sudah berubah — resi tidak
> akan "hilang" sebelum sempat dibuka.

---

## Langkah 4 — Serah Terima Kurir

Saat kurir datang mengambil paket:

1. Buka menu **Serah Terima Kurir**.
2. Centang pesanan yang paketnya benar-benar diserahkan (bisa Pilih Semua).
3. Klik konfirmasi → status pesanan menjadi **Selesai**.

Langkah ini penting untuk audit: paket yang resinya dicetak tapi **tidak
pernah dikonfirmasi serah terima** akan terlihat mencolok di Riwayat.

---

## Audit & Kasus Terlambat — Riwayat Cetak Resi

Saat ada komplain pesanan terlambat, buka menu **Riwayat Cetak Resi**:

| Kolom | Menjawab |
|---|---|
| Waktu Cetak + Dicetak Oleh | "Resinya sudah dicetak orang gudang belum? Siapa? Kapan?" |
| Tim Packer | "Tim mana yang mengemas?" (bahan evaluasi salah kirim/qty kurang) |
| Cetak Ulang | Berapa kali resi dicetak ulang (dan kapan terakhir) |
| Serah Kurir | "Paketnya benar diserahkan ke kurir?" |
| **Cetak → Serah** | Selisih waktu; **merah** bila > 24 jam; **"belum diserahkan"** = paket masih di gudang |

Cara membaca kasus terlambat:

- **Tidak ada di riwayat** → resi belum pernah dicetak → hambatan di gudang.
- **Ada, tapi "belum diserahkan"** → resi dicetak tapi paket tidak ikut
  pickup kurir → cek fisik paket di gudang.
- **Ada dan sudah diserahkan** → masalah di pihak kurir/ekspedisi →
  komplain ke marketplace dengan bukti waktu serah.

Fitur lain di halaman ini:

- **Cari** nomor pesanan / nomor resi + filter rentang tanggal.
- **Unduh** → file Excel riwayat dengan **kode packer terisi otomatis** —
  bahan evaluasi per tim.
- **Cetak Ulang** per baris → resi lama dicetak lagi (tercatat di kolom
  Cetak Ulang). Juga dipakai bila resi Shopee tadi masih "diproses" dan
  halaman Pengemasan sudah ditutup.

---

## Master Produk

Kelola daftar SKU di menu **Master Produk**: barcode, nama produk, dan
lokasi rak. Bisa tambah satu-satu atau **import Excel** massal (kolom:
`sku`, `barcode`, `nama`, `lokasi_rak` — import ulang aman, tidak dobel).

- **Nama produk** dari master dipakai di picklist dan file rekap.
- **Lokasi rak** — begitu diisi, picklist Pengambilan Barang otomatis
  terkelompok per rak. Belum wajib diisi sekarang.

---

## Pertanyaan Umum (FAQ)

**T: Kenapa tombol Cetak Resi menolak dan muncul pesan "data pesanan belum ditarik"?**
J: Pesanan itu belum masuk rekap rekon. Buka Pengambilan Barang → pilih tim
→ Unduh Pesanan Baru → ulangi cetak. Ini disengaja agar tidak ada pesanan
lolos rekap.

**T: Apakah klik Unduh mengubah status pesanan / meng-approve otomatis?**
J: Tidak. Unduh hanya menandai "Sudah Ditarik". Approve tetap manual di
Antrian Pesanan, dan status pesanan tidak berubah karena unduhan.

**T: Salah pilih tim packer saat unduh, bagaimana?**
J: Kode tim pertama yang tercatat tidak tertimpa otomatis. Catat di kolom
Keterangan file rekap, dan laporkan ke leader/SPV bila perlu dikoreksi.

**T: Resi Shopee tidak langsung keluar?**
J: Normal — Shopee membuat dokumen resi secara asinkron. Tunggu beberapa
detik lalu klik "Coba Lagi" di panel hasil (atau "Cetak Ulang" di Riwayat).

**T: Kenapa scan barcode tidak ada lagi?**
J: Dihilangkan atas permintaan tim gudang — dengan 100+ resi per hari, scan
per pesanan terlalu lama. Kontrol kualitas dilakukan lewat rekap rekon +
evaluasi kode packer per tim.

**T: Pesanan dibatalkan pembeli, apakah harus dibatalkan manual?**
J: Tidak — pembatalan dari marketplace masuk otomatis; pesanan yang belum
dikirim akan berpindah ke tab Dibatalkan.

---

## Lampiran: Detail Perubahan Sistem

Ringkasan seluruh perubahan pada modul Warehouse (per 16 Juli 2026):

### Alur & Proses

1. **Alur cepat tanpa scan** — pesanan bisa langsung diproses:
   approve → unduh → cetak, tanpa melewati scan picking/packing.
   Jalur scan lama tetap ada di sistem (opsional, via URL) tapi UI-nya
   dihilangkan dari menu.
2. **Gerbang rekon** — RTS/cetak resi ditolak (error 422) untuk pesanan yang
   belum pernah diunduh datanya. Pesanan yang terunduh dicap
   `exported_at`/`exported_by` (sekali, tidak tertimpa).
3. **Unduh satu pintu** — tombol Unduh hanya di Pengambilan Barang
   (dihapus dari Antrian Pesanan agar tidak salah cap dari tab lain).
   Mode "Pesanan Baru" (rekon per batch) dan "Semua".
   Cakupan diperluas ke pesanan lama di tahap scan
   (APPROVED + PICKING + PACKED + RTS_FAILED) agar tidak ada yang terkunci.
4. **Kode Packer T1/T2** — dipilih saat unduh di Pengambilan Barang;
   langsung terisi di kolom file rekap dan tercatat ke pesanan.
   Pengemasan dan cetak resi tidak menimpa kode yang sudah ada.

### Menu & Halaman

5. **Penamaan menu dibakukan**: Antrian Pesanan, Pengambilan Barang,
   Pengemasan, Riwayat Cetak Resi, Serah Terima Kurir, Master Produk.
   Menu "Atur Pengiriman" dan "Cetak Label" lama dihapus (fungsinya melebur
   ke Pengemasan dan Riwayat).
6. **Pengemasan dirombak total**: ceklis pesanan + Pilih Semua + Tim Packer
   + tombol **Cetak Resi satu klik** (RTS otomatis lalu ambil resi) +
   panel "Hasil Proses Terakhir" yang bertahan + tombol Coba Lagi per pesanan.
7. **Riwayat Cetak Resi (menu baru)**: tabel audit lengkap (waktu cetak,
   dicetak oleh, tim packer, cetak ulang, serah kurir, selisih cetak→serah),
   pencarian + filter tanggal, tombol **Unduh xlsx** (kode packer otomatis)
   dan **Cetak Ulang** per baris.
8. **Badge sidebar diperbaiki**: angka kini menunjukkan antrian yang
   *menunggu dikerjakan* di tiap tahap (sebelumnya salah menampilkan status
   hasil tahap).

### Antrian Pesanan

9. **Filter tanggal + jam** (format WIB, batas menit inklusif) dengan preset
   Hari Ini / Kemarin / 7 / 30 / 90 hari.
10. **Filter toko dua kolom per marketplace** dengan centang semua per channel.
11. **Badge "Sudah Ditarik / Belum Ditarik"** di tab Disetujui.

### Backend / Teknis

12. Endpoint baru: `GET /fulfillment/queue/export` (xlsx rekon + penandaan +
    `only_new` + `packer_code` + multi-status), `GET /fulfillment/labels/history`
    (+ `/export`) untuk riwayat.
13. State machine: `APPROVED → RTS_OK` dan `PICKING → RTS_OK` (jalur cepat);
    jalur scan tetap valid.
14. `POST /labels`: menerima `packer_code` per batch; cetak ulang tercatat di
    history pesanan (`"cetak ulang resi"`).
15. `package_id` TikTok tersimpan dari webhook/reconciler (untuk RTS & cetak
    resi); Shopee memakai nomor pesanan + shop_id, tanpa package_id.
16. Field `packed_by` (user login) tetap tercatat sebagai jejak audit di
    samping `packer_code` (tim harian/freelance).

### Catatan Deploy

- Backend (`bip-erp` main) + frontend (`erp-frontend` dev) harus dideploy
  **bersamaan** — gerbang rekon dan kode packer saling bergantung.
- Setelah deploy pertama: lakukan **satu kali "Unduh Semua"** di Pengambilan
  Barang agar pesanan lama yang sudah disetujui tercap dan bisa diproses.
- Order TikTok lama perlu **backfill `package_id`** (via `cmd/ttorderbackfill`
  di VM) agar bisa RTS.
