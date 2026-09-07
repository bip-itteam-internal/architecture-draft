## Deskripsi

*Peta kesiapan **otomasi skor KPI** untuk posisi-posisi departemen **Manufaktur** (produksi + gudang). Temuan intinya kontra-intuitif: **source & endpoint KPI-nya sudah nyaris lengkap di kode, tapi DORMAN** — koleksi data operasionalnya kosong karena **sistem WMS belum dipakai (masih dirancang)**. Yang sudah live hanya alur **return** di gudang. Dokumen ini merangkum, per posisi, apa yang bisa diotomasi, apa yang menunggu data WMS, dan apa yang memang tak bisa otomatis — plus gerbang verifikasi yang wajib dilewati saat WMS mulai jalan.*

- **Status**: ⚠️ Implemented (dorman) — infrastruktur otomasi (source di `employee-service` + endpoint `/kpi/*` di `manufacture-service`) SUDAH ADA; datanya belum. Diukur ke prod **2026-09-03**.
- **Path di repo**: sumber KPI = `bip-erp/services/employee/kpi_sumber_*.go`; endpoint agregat = `bip-erp/services/manufacture/kpi_*.go`; koleksi = `manufacture_db`.
- **Sumber kebenaran mesin skor**: [[HRIS - Otomasi Skor KPI]] · [[Microservices - Employee Service]] · [[Microservices - Manufacture Service]]. Penamaan metrik/sumber: [[REF - Penamaan Metrik & Sumber KPI]].

## Temuan Inti

**Otomasi KPI manufaktur bukan masalah backend — ia terkunci di adopsi WMS.** `employee-service` sudah mendaftarkan sumber untuk hampir semua metrik lantai produksi & gudang, dan `manufacture-service` sudah punya endpoint `/kpi/*` yang mengagregasinya. Tetapi koleksi yang menjadi bahan bakunya (`production_log`, `batch_record`, `cycle_count`, dst.) **kosong di prod** karena WMS-nya belum dipakai.

Konsekuensi yang harus disadari: **Leader Production sudah dikonfigurasi memakai `kinerja_produksi`, tetapi `production_log`/`batch_record` kosong → metrik itu hidup tapi menghasilkan nol/gagal.** Otomasi terpasang di atas data yang belum ada.

## Status Data Prod (`manufacture_db`, 2026-09-03)

| Ada data | Kosong / belum ada koleksi (menunggu WMS) |
|---|---|
| `manufacture_resi` (412.979) — status fulfillment MARKETPLACE | `manufacture_production_log` ⛔ |
| `manufacture_saldo_awal_bulanan` (1.590) — sisi SISTEM | `manufacture_batch_record` ⛔ |
| `manufacture_stok` (530) — sisi SISTEM | `manufacture_cycle_count` + `manufacture_jadwal_cycle_count` ⛔ |
| `manufacture_transaksi` (12.453) — RETURN-inbound saja | `manufacture_gmp_ceklis`, `manufacture_apd_ceklis` ⛔ |
| `manufacture_accurate_push` (12.453) | `manufacture_accident_report` ⛔ |
| `manufacture_master_*`, `formula`, `sku_mapping` | `manufacture_mutasi_gudang`, `manufacture_lot_bahan`, `manufacture_selisih_rm`, `manufacture_material_order` ⛔ |

**Catatan bentuk data yang sudah diadu (penting — mematahkan asumsi "quick-win"):**
- `manufacture_stok` & `saldo_awal_bulanan` = **sisi sistem saja**, TANPA angka fisik. "Selisih fisik vs sistem" **tak bisa** dihitung sampai opname (`selisih_rm`/`cycle_count`) terisi.
- `manufacture_transaksi` = **semua `INBOUND` `status: REUSE`** (tak ada outbound/konsumsi). Inventory turnover **tak bisa** dihitung. Rasio kelengkapan return **selalu 100%** (semua REUSE) → degenerate, tak layak jadi KPI.
- `manufacture_resi` = status **order marketplace** (COMPLETED/IN_TRANSIT/…), digerakkan kurir+marketplace, tanpa atribusi orang gudang → bukan KPI kinerja orang. Domainnya fulfillment/packing (warehouse-service), bukan gudang RM manufaktur.

## Peta Kesiapan per Posisi (Manufaktur)

Diukur dari template KPI aktif prod (2026-09-03). "Nunggu data" = **source sudah ada**, cukup konfigurasi + isi datanya lewat WMS.

| Posisi | Bisa otomatis SEKARANG | Nunggu data WMS | Manual / subjektif |
|---|---|---|---|
| Operator Production | — | Proses produksi, Waste, Lolos QC | CAPA (kualitatif) |
| Leader Production | KPI Team (`skor_tim`) ✓ | Proses/Waste/QC (`kinerja_produksi`) | CAPA |
| Manufacturing Supervisor | KPI Team (`skor_tim`) ✓ | Jumlah produksi, rework/scrap, waste, K3, GMP, biaya variabel | Kualitas GMP/SOP, dokumen |
| Admin Production | — | (cek "log sudah diisi?") | Dokumen produksi, dokumen BPOM |
| Admin Warehouse | — | Selisih opname, kartu stok | Dokumen, komplain |
| Warehouse Leader | — | Cycle count, FIFO/FEFO, over-dispensing, GMP, kartu stok | — |
| Warehouse Staff | — | GMP | Ketepatan picking (belum ada koleksi picking) |
| PPIC | — | Stok sistem-vs-fisik, material availability | Kepuasan pelanggan (butuh survei) |
| Admin Return | — | — | Return (data ada tapi degenerate — lihat catatan) |

## Sumber KPI yang Sudah Ada (menunggu koleksi WMS)

Semua sumber ini **sudah terdaftar** di `employee-service` (init) dan **sudah punya endpoint** di `manufacture-service`. Yang kurang cuma datanya.

| Sumber (`employee`) | Endpoint (`manufacture`) | Koleksi bahan | Data prod |
|---|---|---|---|
| `kinerja_produksi` | `/kpi/produksi` | `production_log`, `batch_record` (+ saldo, transaksi) | ⛔ kosong |
| `cycle_count_gudang` | `/kpi/cycle-count` | `cycle_count`, `jadwal_cycle_count` | ⛔ kosong |
| `kartu_stok_gudang` | `/kpi/kartu-stok` | `saldo_awal`(ada), `transaksi`(ada), `cycle_count`(kosong) | ⚠️ parsial |
| `fifo_fefo_gudang` | `/kpi/fifo-fefo` | `mutasi_gudang`, `lot_bahan` | ⛔ kosong |
| `over_dispensing_rm` | `/kpi/over-dispensing` | `batch_record`, `ember_sediaan`(2) | ⛔ ~kosong |
| `material_loss_opname` | `/kpi/material-loss` | `selisih_rm`, `saldo_awal` | ⛔ kosong (selisih) |
| `gmp_capa` | `/kpi/gmp` | `gmp_ceklis` | ⛔ kosong |
| `k3` | `/kpi/k3` | `accident_report`, `apd_ceklis` | ⛔ kosong |
| `kinerja_po_marketing` | `/kpi/po-marketing-akurasi` | `marketing_po`(2) | ⛔ ~kosong |

> ⚠️ Jangan bingung dengan sumber **packing** `dispatch_gudang_packing` / `komplain_gudang_packing` / `retur_gudang_packing` / `stok_gudang_packing` — itu untuk **gudang fulfillment marketplace** (`warehouse-service`), BUKAN gudang produksi manufaktur.

## Yang Bisa Dikerjakan SEKARANG (tanpa WMS)

Metrik operasional menunggu WMS, tetapi metrik **penilaian manusia** tidak:

- **GMP/kebersihan, kualitas kerja, kedisiplinan, dokumen** → **form penilaian** (atasan menilai bawahan), memakai infrastruktur `nilai_layanan_pribadi` / `indeks_layanan_tim` yang **sudah terbukti** untuk Security/Office Boy. Otomatis-terukur tanpa WMS.
- Sisanya (output, waste, QC, cycle count, FIFO/FEFO) → tetap **manual** sampai WMS live.

Pola realistis manufaktur sementara ini = **survey/penilaian untuk yang kualitatif, manual untuk operasional**, lalu geser ke otomasi WMS bertahap.

## ⚠️ Gerbang Verifikasi saat WMS Live

Source di atas ditulis terhadap **bentuk data yang DIASUMSIKAN** (schema `production_log`/`batch_record`/`cycle_count` versi rancangan). Saat WMS benar-benar jadi, **bentuk nyatanya bisa berbeda** — persis seperti asumsi `resi`/`stok` yang meleset saat diadu data nyata 2026-09-03 (lihat catatan bentuk data). Maka:

1. **Jangan anggap source pra-bangun "pasti jalan".** Saat WMS mengisi datanya, **adu output nyata WMS ke tiap endpoint `/kpi/*`** lebih dulu.
2. **Buktikan lewat gateway**, bukan `docker ps`: panggil `GET /kpi/auto-values` untuk satu orang manufaktur, pastikan `auto_value`/`auto_rincian` konsisten dengan data WMS.
3. Baru setelah itu **konfigurasi template** (map metrik → sumber) dan klaim metrik otomatis.

## Dokumen Terkait

- [[HRIS - Otomasi Skor KPI]] — mesin skor KPI (reduksi, arah, target)
- [[Microservices - Manufacture Service]] — endpoint `/kpi/*` + `manufacture_db`
- [[Microservices - Employee Service]] — pendaftaran sumber KPI
- [[Manufacture - Stock & Material Management]] · [[Manufacture - Stok Pengecekan Fisik (Flow Source)]] · [[WH - Management System]] — desain WMS yang ditunggu
- [[REF - Penamaan Metrik & Sumber KPI]] — konvensi nama sumber/metrik
