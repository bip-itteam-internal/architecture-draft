## Deskripsi

*Rancangan isi dashboard per posisi untuk divisi **Manufaktur**, delapan posisi (52 metrik, jumlah terbanyak kedua di perusahaan). Diturunkan mengikuti [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]].*

- **Status**: 🟡 **Rancangan**. Tak satu pun posisi di divisi ini punya lembar dashboard.
- **Angka KPI diukur 2026-08-28**, sel PPIC diralat **2026-09-02** (sumber: [[HRIS - Matriks KPI per Departemen]]). **Ukur ulang sebelum dipakai mengambil keputusan.**

## Temuan utama: divisi ini terbelah dua

Sisi **gudang** adalah kelompok posisi paling terinstrumentasi di perusahaan di luar Finance dan IT. Sisi **produksi** hampir seluruhnya terkunci pada satu koleksi kosong.

| Kelompok | Posisi | Metrik | Bersumber | Rancangan |
|---|---|---:|---:|---|
| **Gudang** | Admin Warehouse (2 lokasi), Warehouse Leader, Warehouse Staff | 24 | 17 | ✅ bisa dibangun |
| **Produksi** | Admin Production, Leader Production, Manufacturing Supervisor, Operator Production | 23 | 3 | ⛔ terkunci batch record |
| **Perencanaan** | PPIC | 5 | 0 | ⛔ salah petak berlapis |

Sumber yang sudah tebal dan siap dipakai sisi gudang:

| Sumber | Baris |
|---|---:|
| `manufacture_resi` | 328.272 |
| `warehouse_db.fulfillment_orders` (event pick/pack/handover) | 38.949 |
| `accurate_daily_returns` | 3.351 |
| `manufacture_stok` + `saldo_awal_bulanan` (+ `POST /stok/reconcile`, `GET /selisih`) | 530 + 530 |

**Rekomendasi urutan**: bangun keempat posisi gudang lebih dulu. Mereka bisa jadi sekarang, dan tidak menunggu siapa pun.

## Sisi gudang: bisa dibangun sekarang

### Warehouse Staff

**Dinilai dari** (template `STAFF WAREHOUSE`, 4 metrik):

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,3 | Zero miss-pick, stock check berkala | `manufacture_resi` + `fulfillment_orders` | ✅ |
| 0,3 | Ketepatan picking (item, batch, quantity) | `manufacture_resi` + `fulfillment_orders` | ✅ |
| 0,2 | Ketepatan loading & unloading | `manufacture_resi` + `fulfillment_orders` | ✅ |
| 0,2 | Kerapihan & kebersihan area (GMP) | modul checklist belum ada | ❌ |

**Posisi paling siap di seluruh divisi.** Tiga metrik berbobot total 0,8 bersumber pada data event yang tebal.

- **Visual utama**: tren ketepatan picking harian atau mingguan terhadap ambang. Event `pick`/`pack`/`handover` memberi deret waktu yang benar-benar bergerak.
- Antrean order yang menunggu picking hari ini, dari `fulfillment_orders`.
- Kartu miss-pick bulan berjalan.

### Warehouse Leader

**Dinilai dari** (template `LEADER WAREHOUSE`, 8 metrik):

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,2 | Cycle count mingguan sesuai jadwal, akurasi 100% | `manufacture_stok` + `GET /selisih` | ✅ |
| 0,15 | Kepatuhan FIFO/FEFO ≥ 98% | `manufacture_stok` | ✅ |
| 0,15 | Over-dispensing ≤ 0,5% (serbuk & cair) | `manufacture_stok` | ✅ |
| 0,15 | Over-dispensing ≤ 0,5%, entri kedua | `manufacture_stok` | ✅ |
| 0,15 | Kerusakan bahan baku turun ≥ 5% | belum dipetakan | ❌ |
| 0,1 | GMP warehouse comply checklist bulanan | modul checklist belum ada | ❌ |
| 0,05 | Kartu stok ter-update ≤ H+1 | `manufacture_stok` | ✅ |
| 0,05 | 1-on-1 bulanan 100% | tidak ada log 1-on-1 | ❌ |

**Bisa ditampilkan sekarang.** Lima metrik, bobot total 0,7.

- **Visual utama**: selisih stok fisik terhadap sistem per siklus opname, terhadap ambang akurasi. `GET /selisih` sudah menyediakannya.
- Kartu kepatuhan FIFO/FEFO terhadap 98%, kartu over-dispensing terhadap 0,5%.
- Sebaran skor KPI anggota gudang.

⚠️ **Dua metrik over-dispensing identik berbobot 0,15 masing-masing.** Target, redaksi, dan sumbernya sama persis. Kemungkinan besar entri ganda di master data, dan bila benar maka 0,3 dari nilai Warehouse Leader ditentukan satu pengukuran yang dihitung dua kali. **Gambarkan satu kartu, bukan dua**, dan angkat pertanyaannya ke pemilik KPI.

### Admin Warehouse

⚠️ Nama posisi ini dipakai **dua template berbeda untuk dua lokasi**: `ADMIN WAREHOUSE 2` dan `ADMIN WAREHOUSE TINGGARJAYA`, masing-masing 6 metrik. Sama seperti GA Staff di [[GA - Dashboard per Posisi]], keduanya berbagi satu nama posisi sehingga **tidak dapat dibedakan dari `work_data`**. Memisahkan lembarnya menuntut master data dipecah lebih dulu.

**Lokasi 2** punya 5 dari 6 metrik bersumber (arus stok, rekonsiliasi, FIFO/FEFO, akurasi opname, barang reject), bobot total 0,9. **Tinggarjaya** punya 4 dari 6 (inbound/outbound, stock opname, dokumen retur, pemetaan resi ke ekspedisi), bobot 0,7.

- **Visual utama untuk keduanya**: selisih stok fisik vs sistem per bulan terhadap ambang. Ia inti pekerjaan keduanya dan muncul di kedua template.
- Tinggarjaya menambahkan daftar resi yang belum diserahkan ke ekspedisi, dari `manufacture_resi`.

**Yang menunggu**: komplain customer (Tinggarjaya, 0,2) dan kas gudang (0,1) belum dipetakan sama sekali.

## Sisi produksi: terkunci satu koleksi kosong

⛔ **Batch Record & Production Log ada di kode tetapi KOSONG di produksi (0 dokumen)**, dan itu mengunci **11 metrik** di keempat posisi produksi:

| Posisi | Metrik terkunci batch record | Bobot terkunci |
|---|---:|---:|
| Operator Production | 2 dari 5 | 0,50 |
| Leader Production | 3 dari 7 | 0,45 |
| Manufacturing Supervisor | 3 dari 7 | 0,40 |
| Admin Production | 2 dari 4 | 0,50 |

Ini penghambat yang sama persis dengan divisi Quality ([[QA - Dashboard per Posisi]]), dan **kedua divisi akan terbuka bersamaan** begitu batch record dipakai. Sekali lagi: ini bukan permintaan fitur, koleksinya sudah ada. Yang belum ada isinya.

**Yang tetap bisa dirancang sekarang di sisi produksi**, dan hanya itu:

- **Manufacturing Supervisor** dan **Leader Production**: sebaran skor KPI anggota terhadap ambang 70 (`skor_tim`, bobot 0,3 dan 0,15). Satu kartu, dan itu jujur.
- **Operator Production**: kesesuaian stok opname (0,15) dari `manufacture_stok`.

⛔ **Admin Production tidak direkomendasikan dibuatkan dashboard**: nol dari empat metriknya bersumber.

⚠️ **Dua metrik Leader Production bernama `Kaizen` TIDAK dilayani sumber Kaizen.** `Kaizen 1` mengukur jumlah CAPA produksi, `Kaizen 2` mengukur persentase kualitas produk sesuai SOP QC. Menyambungkan keduanya ke `kaizen_ide_diajukan` akan menghitung hal yang sama sekali lain. Pola penamaan ini sudah muncul di tiga divisi, dan tiap kali namanya membuat pemetaan yang keliru terasa benar.

## PPIC: salah petak berlapis

⛔ **Nol dari lima metrik dapat dipakai, dan sebabnya bukan ketiadaan data melainkan pemetaan yang keliru.**

| Bobot | Metrik | Sumber tertulis | Masalah |
|---:|---|---|---|
| 0,25 | Stock accuracy 98-100% | belum dipetakan | tak ada sumber |
| 0,2 | OTIF / fill rate finished good ke WH | `tt_business_gmv_max_performance_reports` | ⛔ data iklan TikTok |
| 0,2 | Inventory Turnover Ratio | diralat 2026-09-02, sel sebelumnya salah tempel | perlu diperiksa ulang |
| 0,2 | Stockout rate | tanpa modul demand planning tak terdefinisi | ❌ |
| 0,15 | Factory utilization | tracker BPOM/CAPA | ⛔ tak berhubungan |

**Metrik OTIF dipetakan ke data iklan TikTok**, persis kesalahan yang sama dengan Staff Inventory Procurement di [[GA - Dashboard per Posisi]]. Ketepatan pengiriman finished good ke gudang tidak ada hubungannya dengan performa kampanye marketplace, dan sumbernya berisi 712.855 baris sehingga akan menghasilkan angka mulus yang sepenuhnya keliru.

**Metrik factory utilization** dipetakan ke tracker pajak dan izin BPOM, yang juga tak berhubungan.

⚠️ Sel Inventory Turnover Ratio di matriks **sudah pernah salah tempel dan diralat 2026-09-02**. Fakta bahwa satu sel di posisi ini terbukti salah membuat empat sel lainnya patut dicurigai sebelum dipakai.

**Rekomendasi**: jangan merancang layar PPIC sampai kelima pemetaannya ditinjau ulang oleh pemilik KPI. Ironisnya data yang benar kemungkinan besar sudah ada, di `manufacture_stok` dan `fulfillment_orders` yang dipakai posisi gudang di atas.

## Kebutuhan backend, terurut

1. **Isi Batch Record & Production Log di produksi.** Membuka 11 metrik di 4 posisi Manufaktur **plus 6 metrik di 4 posisi Quality**. Tujuh belas metrik lintas dua divisi dari satu hal, dan koleksinya sudah ada. Daya ungkit tertinggi di seluruh keluarga dokumen ini.
2. **Tinjau ulang kelima pemetaan PPIC.** Keputusan pemilik KPI. Dua di antaranya menunjuk data yang jelas tak berhubungan.
3. **Periksa dua metrik over-dispensing kembar** di Warehouse Leader. Bila entri ganda, 0,3 nilai orangnya ditentukan satu pengukuran.
4. **Modul checklist berjadwal** ([[GA - Checklist Management]]), mengunci 4 metrik GMP dan K3 di divisi ini. Dipakai bersama [[GA - Dashboard per Posisi]].
5. **Pemetaan komplain customer dan kas gudang** untuk Admin Warehouse Tinggarjaya.
6. **Modul demand planning** untuk stockout rate PPIC dan monitoring limbah Admin Warehouse.
7. **Log 1-on-1** untuk Warehouse Leader. Bobot terkecil di daftar (0,05), sebut hanya supaya tidak hilang.

## Dokumen Terkait

- [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] — prinsip penurunannya
- [[REF - Layout Dashboard erp-frontend]] — cara menyusunnya di layar
- [[HRIS - Matriks KPI per Departemen]] — sumber angka di dokumen ini
- [[Manufacture - Kesiapan Otomasi KPI (menunggu WMS)]] — analisis kesiapan otomasi divisi ini
- [[Manufacture - Dokumen Produksi Batch]] — koleksi yang mengunci sisi produksi
- [[Manufacture - Stock & Material Management]] · [[Manufacture - Stok Pengecekan Fisik (Flow Source)]] — sumber angka gudang
- [[WH - Fulfillment Flow & WMS Tinggarjaya]] — sumber `fulfillment_orders`
- [[QA - Dashboard per Posisi]] — divisi yang terbuka bersamaan lewat batch record
- [[GA - Dashboard per Posisi]] — berbagi kebutuhan modul checklist
