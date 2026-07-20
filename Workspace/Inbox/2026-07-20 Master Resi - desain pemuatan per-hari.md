---
publish: false
---

# Master Resi — Pemuatan Per-Hari & Pencarian Sisi Server

Tanggal: 2026-07-20
Status: desain disetujui, siap masuk tahap perencanaan implementasi (belum dibangun)

> Terkait: [[2026-07-17 Temuan - Reject retur menambah stok FG]] — sama-sama menyentuh
> alur retur di Gudang FG.

## Masalah

Menu Master Resi (WMS / modul manufacture) sangat lambat dibuka di produksi, di mana
koleksi resi berjumlah puluhan ribu dokumen dan terus bertambah.

Penyebabnya **bukan** proses sync. Sync sudah bekerja benar: job `sync-resi-wms`
berjalan tiap 10 menit, melakukan upsert per `no_resi` ke koleksi `manufacture_resi`
(`services/manufacture/resi.go`, `upsertResiFeed`), dan `ListResi` murni membaca Mongo
tanpa pernah memanggil marketplace.

Penyebab sebenarnya ada di jalur baca:

1. `GET /api/manufacture/resi?since=<hari ini - 60>` menarik seluruh resi 60 hari dalam
   satu response (`erp-frontend/src/features/manufacture/manufacture-app.tsx`, `muatResi`).
2. `ListResi` tidak punya `limit`/`offset`/cursor — semua dokumen yang cocok dikirim.
3. Pengelompokan per hari di UI murni client-side, atas data yang sudah terlanjur di memori.
4. Pencarian client-side atas data tersebut, dibatasi 500 hasil.
5. `GET /resi/days` sudah ada di backend tapi tidak dipakai frontend sama sekali.
6. `muatResi` dipanggil saat **modul di-mount**, bukan saat tab Master Resi dibuka.

## Sasaran

- Menu Master Resi terbuka dalam hitungan detik pertama pada data produksi.
- Tidak ada perubahan perilaku apa pun pada menu Gudang FG (dikerjakan orang lain).

## Batasan Lingkup

Menu Gudang FG (`GudangBarangJadiView.tsx`) sedang dikerjakan pengembang lain. File itu
**tidak boleh disentuh** pada fase ini. Karena itu pekerjaan dipecah dua fase; fase 2
menunggu pekerjaan tersebut selesai di-merge.

## Keputusan Desain

| Topik | Keputusan | Alternatif yang ditolak |
|---|---|---|
| Lokasi cache | Pagination sisi server, tanpa cache persisten | IndexedDB — first-load tetap berat, kompleksitas sinkronisasi |
| Tampilan awal | Grup per hari; isi hari ditarik saat dibuka | Halaman datar lintas tanggal; muat N hari terakhir |
| Filter rentang | Komponen `DateRangeFilter` milik Gross Profit + prop `presets` opsional | Pakai apa adanya (tanpa 14 hari & "Semua") |
| Pencarian | Ke server, cakupan ikut rentang aktif, prefix `no_resi` | Client-side; selalu seluruh riwayat |

## Fase 1 — Lingkup pekerjaan ini

### Backend (`services/manufacture/resi.go`)

Jalur sync tidak diubah sama sekali.

**1. `GET /resi/days?from=&to=`** — sudah ada, ditambah filter rentang.

Mengembalikan daftar tanggal + jumlah resi per tanggal. Inilah yang membuat menu ringan:
rentang 3 bulan menghasilkan ~90 baris, bukan puluhan ribu dokumen. Tanpa `from`/`to`
berarti seluruh riwayat (preset "Semua"), dan tetap ringan karena hasilnya tetap satu
baris per tanggal.

`dayKey` memakai definisi yang sudah ada: 10 karakter pertama `tanggal_rts`, jatuh ke
`tanggal_pesanan` bila kosong.

**2. `GET /resi?date=YYYY-MM-DD`** — sudah ada, dipakai mengambil isi satu hari.

Ditambah mode rentang **`GET /resi?from=&to=`** untuk keperluan export, yang memang perlu
mengambil seluruh rentang aktif sekaligus. Batas atas `to` bersifat inklusif, memakai
`dayKey` yang sama dengan `/resi/days`. Mode ini khusus export dan tidak dipakai untuk
menampilkan tabel — pemuatan tabel tetap per hari.

**3. `GET /resi?q=...&from=&to=&limit=100`** — baru.

`q` dicocokkan ke `no_resi` sebagai prefix (regex ter-anchor `^ABC`) sehingga tetap
memakai index `no_resi` yang sudah ada. Nomor pesanan dan nama toko dapat menyusul;
sesuai kebutuhan operator, no. resi diprioritaskan.

**Yang dihapus:** mode `GET /resi` tanpa parameter (menarik seluruh koleksi). Setelah
ketiga endpoint di atas ada, tidak ada lagi yang membutuhkannya. Mode `?since=` tetap
dipertahankan sampai fase 2, karena masih dipakai `muatResi` untuk menyuplai Gudang FG.

**Kontrak urutan (wajib).** Fitur "Ambil Rentang" di Keluar FG mengambil resi berdasarkan
nomor urut ke-N dalam satu tanggal. Saat ini `ListResi` memanggil `FindMany` dengan opsi
`nil`, sehingga urutannya adalah natural order Mongo — tidak dijamin. Selama Master Resi
dan FG berbagi satu response besar yang sama, hal ini tidak terlihat. Begitu keduanya
memanggil endpoint terpisah, selisih urutan sekecil apa pun membuat "ambil no. 5–10"
menarik resi yang salah **tanpa memunculkan error**.

Karena itu urutan dalam satu hari ditetapkan eksplisit di server: `_id` menaik
(deterministik dan stabil). Kedua layar wajib memakai response yang sama.

**Index:** tidak ada index baru. Pencarian bertumpu pada `no_resi` (sudah unik terindeks);
navigasi per hari bertumpu pada `tanggal_rts_idx` / `tanggal_pesanan_idx` yang sudah ada.

### Frontend

File yang disentuh hanya `manufacture-app.tsx` dan `ResiMasterView.tsx` — keduanya di luar
pekerjaan pengembang lain.

**Alur saat menu dibuka:**

1. Satu request ringan `/resi/days` sesuai rentang aktif.
2. Grup per hari tampil semua beserta jumlahnya, dalam keadaan tertutup. Layar terisi
   hampir seketika.
3. Hari terbaru yang berdata otomatis terbuka dan isinya ditarik, sehingga operator tetap
   langsung melihat data tanpa klik.
4. Hari lain ditarik saat dibuka, lalu disimpan di memori selama sesi. Buka-tutup lagi
   tidak memicu request ulang.

**Filter rentang.** Memakai `DateRangeFilter`
(`erp-frontend/src/features/integration/ads-analytics/components/date-range-filter.tsx`),
komponen yang sama dengan Gross Profit dan 4 halaman lain, ditambah prop `presets`
opsional. Prop bersifat opsional sehingga kelima pemakai lama tidak berubah perilakunya.

Preset Master Resi: **Hari Terbaru (default), 7 Hari, 14 Hari, 30 Hari, 60 Hari, 90 Hari,
Semua**, ditambah Rentang Kustom bawaan komponen.

"Hari Terbaru" berarti hari terakhir yang benar-benar punya resi, bukan tanggal hari ini —
supaya layar tidak pernah kosong saat belum ada RTS masuk.

**Pencarian.** Dikirim ke server, cakupan mengikuti rentang aktif, dicocokkan ke `no_resi`
sebagai prefix. Hasil tampil sebagai daftar datar, bukan dikelompokkan per hari, dengan
debounce ~300ms.

**Export Excel — ada perubahan perilaku.** Saat ini export mengambil apa pun yang kebetulan
ada di memori. Karena memori nantinya hanya berisi hari-hari yang dibuka, export akan
menarik ulang seluruh rentang aktif dari server lewat `GET /resi?from=&to=` sebelum menulis
file. Hasilnya menjadi
sesuai rentang yang terlihat di filter, bukan sesuai riwayat klik operator. Export rentang
lebar akan terasa lambat sejenak, jadi perlu indikator progres.

**Tombol "Muat semua riwayat" dihapus**, digantikan preset "Semua".

**Yang tidak berubah:** tampilan tabel, kolom, form tambah/edit/hapus resi, tombol sync
TikTok/Shopee.

**Kompatibilitas Gudang FG.** `muatResi` yang lama tetap dipertahankan apa adanya khusus
untuk menyuplai `resiList` ke `GudangBarangJadiView`. Perilakunya tidak disentuh, sehingga
tidak ada risiko regresi. Konsekuensi yang diterima secara sadar: load 60 hari masih
berjalan di latar belakang sampai fase 2 selesai, sehingga perbaikan fase 1 terasa pada
kecepatan tampil layar, belum pada beban jaringan.

## Fase 2 — Ditunda sampai pekerjaan Gudang FG di-merge

Semua item di bawah menyentuh `GudangBarangJadiView.tsx`.

1. **`lookupResi` (form Retur) dan `f4LookupResi` (Keluar FG) pindah ke
   `GET /resi/lookup/:resi`.** Endpoint ini sudah ada dan belum dipakai frontend sama
   sekali. Scan barcode memang lookup satu resi; tidak pernah butuh daftar penuh.

   Ini sekaligus memperbaiki dua bug yang sudah ada sekarang:
   - Resi di luar jendela 60 hari selalu dinyatakan "tidak terdaftar di master", padahal
     ada di DB. Di form Retur pesannya berbunyi "tambah barang manual", sehingga operator
     menghasilkan data retur manual yang tidak ter-join ke master resi — gagal tanpa jejak.
   - `muatResi` dipanggil fire-and-forget, sehingga scan sebelum load selesai memberi hasil
     "tidak terdaftar" yang keliru.

   Bedakan 404 (benar-benar tidak ada) dari kegagalan jaringan agar pesannya tidak lagi
   menyesatkan.

2. **`f4RtsDays` pindah ke `GET /resi/days`**, `f4RangeList` ke fetch per-hari. Perhatikan
   kontrak urutan di Fase 1.

3. **Hapus `muatResi` global** beserta mode `?since=` di backend bila sudah tak ada pemakai.

4. **Bug panel LOG DATA RETURN EKSPEDISI.** `GudangBarangJadiView.tsx` menyuntikkan
   `row.return_sn || row.order_id` ke field No Resi form retur, lalu mencocokkannya ke
   master resi. Pencocokan ini gagal 100% untuk semua baris retur, karena `return_sn`
   (Shopee Return Serial Number / TikTok return_id) adalah jenis identifier yang berbeda
   dari `no_resi` (AWB kurir). Kolom itu juga dilabeli seolah-olah nomor resi.

   Perbaikan minimal: beri label kolom yang benar dan hentikan penyuntikan ke field No Resi.
   Perbaikan yang lebih berguna: enrich baris retur dengan resi asli lewat join
   `return.order_id → manufacture_resi.nomor_pesanan` — relasinya sudah tersedia karena
   sub-dokumen `return` hidup di dalam dokumen order itu sendiri.

   Catatan: reverse waybill Shopee yang sesungguhnya tersedia di API
   (`shopee_returns_client.go`, field `tracking_number` / `rts_tracking_number`) tapi tidak
   pernah dipersist — hanya dipakai sekilas untuk menghitung waktu tiba.

## Verifikasi

Backend dikerjakan sampai bisa diuji langsung lewat container, baru frontend, supaya
kesalahan ketahuan di lapisan yang benar.

**Backend:**
- `/resi/days` dengan dan tanpa rentang — jumlah per tanggal cocok dengan hitungan langsung
  di Mongo.
- `/resi?date=` — urutan dalam satu hari deterministik dan identik antar pemanggilan.
- `/resi?q=` — prefix `no_resi` benar-benar memakai index (verifikasi lewat `explain`,
  pastikan bukan COLLSCAN), termasuk saat rentang = "Semua".
- Rentang kosong, tanggal tanpa data, dan `q` tanpa hasil mengembalikan daftar kosong yang
  wajar, bukan error.

**Frontend (lewat browser, bukan sekadar lolos typecheck):**
- Buka menu → ukur waktu sampai layar terisi, bandingkan dengan kondisi sekarang. Ini angka
  yang membuktikan pekerjaan ini berhasil.
- Ganti-ganti preset rentang, termasuk "Semua".
- Buka beberapa hari, tutup, buka lagi → tidak ada request ulang.
- Cari no. resi yang berada di hari yang belum pernah dibuka → harus ketemu.
- Export → isinya sesuai rentang aktif, bukan sesuai hari yang diklik.
- **Regresi Gudang FG**: buka `/manufacture/finished-goods` langsung, scan resi di form
  Retur dan Keluar FG, coba "Ambil Rentang" → semua berperilaku persis seperti sebelumnya.

**Ukuran keberhasilan:** menu Master Resi terbuka dalam hitungan detik pertama di data
produksi, dan tidak ada perubahan perilaku apa pun di Gudang FG.

## Berkas Terkait

| Peran | Path |
|---|---|
| Handler & repo resi | `bip-erp/services/manufacture/resi.go` |
| Registrasi route & index | `bip-erp/services/manufacture/main.go` |
| Model `Resi` | `bip-erp/shared-library/models/manufacture/models.go` |
| Container & state modul | `erp-frontend/src/features/manufacture/manufacture-app.tsx` |
| Tampilan Master Resi | `erp-frontend/src/features/manufacture/components/ResiMasterView.tsx` |
| Filter rentang (dipakai ulang) | `erp-frontend/src/features/integration/ads-analytics/components/date-range-filter.tsx` |
| Gudang FG (fase 2, jangan disentuh sekarang) | `erp-frontend/src/features/manufacture/components/GudangBarangJadiView.tsx` |
| Job sync (tidak diubah) | `bip-erp/services/integration/internal/worker/tasks/sync_resi_wms.go` |
