## Deskripsi

*Kajian fondasi sistem **Manufaktur** (produksi, PPIC, gudang bahan baku/FG, QC) sebelum menambah fitur baru. Menggabungkan empat sumber: SOP posisi, matriks KPI, kode `origin/main`, data prod, ditambah kuesioner ke pemakai dan spreadsheet operasional PPIC. Temuan intinya: **modul pabrik di ERP sudah dibangun tetapi belum pernah dipakai**, penyebabnya sosialisasi dan hak akses, bukan fiturnya; sementara **sistem yang benar-benar berjalan adalah satu Google Sheet PPIC** yang strukturnya bisa langsung menjadi cetak biru ERP. Dok ini mencatat temuan dan keputusan yang masih terbuka; belum ada keputusan final.*

- **Status**: 🟡 Konsep / kajian. Diukur **2026-10-13** (kode `origin/main` 2026-10-12, data prod baca-saja, kuesioner 14 responden dari 32).
- **Path di repo**: `bip-erp/services/manufacture/`, `bip-erp/services/employee/quality_*.go`, `bip-erp/services/procurement/`; FE `erp-frontend/src/features/manufacture/`.
- **Lanjutan dari**: [[Manufacture - Kesiapan Otomasi KPI (menunggu WMS)]] dan [[Manufacture - Dashboard per Posisi]], yang sudah menyimpulkan otomasi KPI terkunci di adopsi WMS.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| SPV Manufacture | penyetuju hampir semua alur produksi, gudang, PPIC (tak punya SOP) | modul manufacture | desktop |
| PPIC | rencana produksi, MRP, permintaan pengadaan | modul manufacture | desktop |
| Admin Produksi | menyalin Batch Record kertas dan hasil produksi | modul manufacture | desktop |
| Leader / Operator Produksi | mengisi Batch Record kertas di lantai produksi | tidak perlu input ERP (hasil kuesioner) | kertas |
| Leader / Admin / Staf Warehouse | penerimaan, karantina, keluar ke produksi, opname mingguan | modul manufacture (WMS) | desktop |
| QC Assistant / QC Production / QA | QC bahan masuk, pengujian IPC, rilis | modul quality | desktop |
| APJ / PJT | memutuskan rilis batch (OT dan kosmetik) | TBD, orangnya belum dipastikan | TBD |
| Finance (Supervisor FAT, Accounting, Cost Control) | validasi opname, persediaan di Accurate, HPP | modul finance | desktop |

- **Tujuan**: satu batch bisa ditelusuri dari rencana PPIC sampai FG masuk gudang, setiap data diketik sekali.
- **Pain point**: semua dicatat di kertas + kartu stok + Google Sheet; ERP tak dikenal; dashboard diminta tapi belum ada.
- **Aksi utama**: input penerimaan bahan, keluar ke produksi, hasil produksi per batch, rilis, kirim FG, opname.

## Temuan 1: Pemakaian ERP di prod (2026-10-13)

| Fitur | Pemakaian |
|---|---|
| Scan retur marketplace (Gudang FG) | aktif: 7.596 transaksi / 30 hari oleh 2 akun; semuanya INBOUND |
| MO Barang Jadi | aktif 2 hari (16-17 Sep), kini hanya 2 MO uji |
| Otomatis | sync resi, push stok ke Accurate (`ACCURATE_WMS_PUSH=true` di prod), tarik stok dari Accurate (default ON, 6 jam) |
| Sekali (Juli) | import 60 formula, snapshot saldo awal |
| **Belum pernah dipakai** | Batch Record, Laporan Hasil Produksi, Rekon MO, Material Order, PO Procurement, Proposal, Rencana Produksi, Cycle Count, Lot FIFO/FEFO, K3/GMP/APD, Mutasi/Konsinyasi, seluruh modul Quality (`quality_*` belum pernah terbentuk) |

Tidak ada satu pun gerakan bahan baku (terima, keluar ke produksi, opname) tercatat di ERP.

## Temuan 2: Tumpang tindih di fondasi kode

| # | Area | Keadaan (`origin/main`) | Arah penyederhanaan |
|---|---|---|---|
| 1 | Catatan produksi | `production_log` + `batch_record` + `POST /production` (tanpa pemanggil FE); konsumsi bahan tercatat 2x; potong stok dirakit FE lewat POST berantai non-atomik | satu Batch Record; server memotong bahan + menambah FG atomik |
| 2 | Rilis batch | `batch_record.keputusan_rilis` vs `quality_batch_release` (employee-service), tak tersambung | satu keputusan rilis di Batch Record |
| 3 | QC bahan masuk | `quality_incoming`, `quality_rm_check`, karantina di procurement; hanya procurement yang menahan stok; INBOUND via `/transaksi` manufaktur langsung siap pakai | satu gerbang karantina, QC, lalu stok |
| 4 | PO bahan | `manufacture_procurement_po` tak tersambung ke [[Microservices - Procurement Service]]; risiko bahan masuk 2x | PO hanya di procurement |
| 5 | Penyesuaian stok | 9 jalur menulis `stok_sekarang` dengan aturan berbeda; cycle count & selisih RM tak pernah menjadi penyesuaian | satu jalur penyesuaian ber-approval |
| 6 | Pemilik angka stok | tarik Accurate (`$set`, 6 jam) + push ledger (10 menit) + reconcile (Σ ledger) | putuskan satu pemilik (lihat TBD) |
| 7 | Lot/ED | `qty_sisa` lot hidup terpisah dari stok; 1 dari 9 jalur menggerakkan lot | lot ikut setiap gerakan |
| 8 | MO Marketing | 1 koleksi, 3 rute, 2 set handler | satu rute |
| 9 | FE | 4 berkas > 1.500 baris (terbesar 3.855); ID transaksi dibuat klien | logika stok ke server |

Tidak bermasalah: sumber KPI manufaktur di employee-service hanya adaptor `/kpi/*`, tidak ada hitung ganda. Dok [[Microservices - Manufacture Service]] dan [[API - Manufacture Service]] belum memuat batch-record, cycle-count, lot, K3/GMP, maupun `/kpi/*` (perlu `/sync-docs`).

## Temuan 3: Kuesioner pemakai (5 form, 32 penerima, 14 responden)

**Sudah cukup jelas**

- **ERP tak dipakai karena sosialisasi dan akses**: "belum dilatih / belum diperkenalkan / tidak tahu fiturnya ada" dan "belum punya akses menu".
- **Input cukup oleh Admin Produksi** dari kertas; operator tak perlu HP. Form ERP sebaiknya mengikuti urutan form kertas.
- **Dokumen kertas tetap wajib untuk audit BPOM** (Batch Record fisik, kartu stok). ERP = salinan kerja; syarat meninggalkan kertas: ERP mencetak dokumen dalam format yang diterima BPOM.
- **Karantina ada dalam praktik** walau SOP gudang tak menyebutnya: label kuning karantina, lalu **Lulus / Reject / Ditolak** (label merah, konfirmasi SPV Quality).
- **Bahan Ditolak QC tak pernah masuk stok**; langsung diretur Procurement (cocok dengan procurement-service yang hanya mengirim qty LULUS).
- **Stock opname mingguan** (SOP menyebut bulanan s.d. tahunan). **Dua kartu stok**: kosmetik dan obat tradisional. **Bahan kemas tak ber-ED**.
- **Bahan keluar** via Form Permintaan Produksi kertas, disetujui PPIC; sisa bahan kembali dipilah layak/rusak/reject.
- **Rilis batch: satu Batch Record** (5 lawan 3): QC menambah catatan pengujian di dalamnya, **APJ** memutuskan lulus di lembar keputusan rilis.
- **FG masuk stok** setelah rilis **dan** serah terima fisik.
- **Marketing ingin Production Order + MOQ**; Marketing boleh mengubah rencana 1x sebelum produksi dikunci.
- **Dashboard** diminta SPV Manufacture.

**Masih terbelah**

- **Kapan bahan terpakai**: selesai diolah (4) / pindah ke zona WIP atau diserahkan ke produksi (3) / lulus QC (2). Usulan penggabungan: stok gudang RM berkurang saat serah ke **zona WIP**; pemakaian final dihitung saat batch selesai; sisa kembali dengan 3 kategori.
- **Frekuensi perubahan rencana produksi**: "hampir setiap hari" vs "1-2x per bulan"; safety stock/ROP "lengkap" vs "sebagian".
- **Definisi KPI PPIC belum seragam** antarposisi (Stockout tertukar dengan Stock Accuracy; ITO belum dipahami di luar SPV). Definisi SPV: ITO = HPP / ((persediaan awal + akhir) / 2).

## Temuan 4: Spreadsheet PPIC = sistem yang benar-benar berjalan

Satu Google Sheet (±40 tab, data Jan-Okt 2026, dipelihara tim PPIC/gudang) mencakup hampir seluruh alur. Struktur tab ini menjadi daftar kebutuhan yang **sudah terbukti dipakai**:

| Proses | Isi tab | Volume 2026 | Padanan ERP |
|---|---|---|---|
| Penerimaan + QC | qty SJ / LULUS / REJECT, no. dokumen QC | 2.261 baris | Antrean RM + QC (tak dipakai) |
| Keluar ke produksi | SJ, no. memo permintaan | 4.950 | Material Order (tanpa status) |
| Pemakaian bahan | per produk per hari | 4.137 | konsumsi Batch Record |
| Hasil produksi | qty formula vs realisasi, no. batch | 2.217 (±1,72 jt pcs) | Batch Record / Laporan Hasil |
| FG keluar | SJ, tujuan, no. batch, kendaraan | 2.070 (±1,65 jt pcs) | Kirim FG |
| Mutasi + SO | saldo, masuk, keluar, SO fisik vs sistem/Accurate (7 kategori) | bulanan | sebagian (cycle count) |
| Formula | bahan, susut, lead time pengadaan + produksi | 2 tab | Formula/BOM |
| MRP + safety stock | kebutuhan vs stok; rata-rata/maks pemakaian, ROP, status | ±460-500 bahan | simulasi Rencana Produksi; ROP belum ada |
| Permintaan pengadaan | no. permintaan, qty, estimasi datang, kekurangan | 186 | belum ada |
| PO Marketing | per produk/bulan/brand vs terkirim | 89 produk | MO Barang Jadi (kosong) |
| Rencana vs realisasi | per tanggal/shift/tim | bulanan | belum ada |

Kualitas data spreadsheet perlu dibereskan sebelum dijadikan sumber: banyak `#N/A`/`#REF!`, tab duplikat, satuan KG dan gram bercampur, formula di dua tab.

## Belum Diputuskan (TBD)

1. **Pemilik angka stok pabrik**: ERP (push ke Accurate) atau Accurate. Jawaban pemakai bertentangan (Accurate vs stok fisik). Pemutus: Finance Supervisor. Syarat Finance: ERP mengikuti aturan pencatatan masuk/keluar (penjualan, retur, pembelian, pemakaian produksi); penyesuaian opname dibukukan setelah validasi Finance.
2. **Model zona WIP** dan kapan bahan dianggap terpakai. Pemutus: SPV Manufacture + Supervisor Quality.
3. **Satu Batch Record + keputusan rilis APJ**, dan **perlakuan batch berstatus Ditolak** (boleh masuk stok FG dengan catatan penyimpangan, atau ditahan). Pemutus: Supervisor Quality + APJ.
4. **Status bahan masuk** di sistem: karantina, Lulus, Reject, Ditolak.
5. **Cetak dokumen format BPOM** (kartu stok, Batch Record) sebagai syarat meninggalkan kertas.
6. **Pemilik HPP per batch**: PPIC vs Cost Accounting.
7. **Arah pembangunan** (usulan): dashboard dari spreadsheet sebagai jembatan, lalu pindahkan tab demi tab ke ERP mulai penerimaan bahan, hasil produksi, FG keluar, dengan form meniru kolom spreadsheet.
8. **Pihak belum terpetakan**: siapa APJ/PJT; SPV Manufacture tak punya SOP; departemen teknisi mesin.

## Dokumen Terkait

- [[Manufacture - Kesiapan Otomasi KPI (menunggu WMS)]] · [[Manufacture - Dashboard per Posisi]] · [[Manufacture - Dokumen Produksi Batch]] · [[Manufacture - Stock & Material Management]] · [[Manufacture - Material Order (SPK)]]
- [[Microservices - Manufacture Service]] · [[API - Manufacture Service]] · [[Microservices - Procurement Service]]
- SOP: [[Manufacture - SOP Posisi PPIC]] · [[Manufacture - SOP Posisi Admin Produksi]] · [[WH - SOP Posisi Staf Warehouse]] · [[WH - SOP Posisi Admin Warehouse]] · [[QA - SOP Posisi Quality Control]] · [[GA - SOP Posisi Procurement]] · [[GA - SOP Procurement]] · [[Finance - SOP Posisi Cost Control]] · [[REF - SOP Bharata 2026 per Posisi]]
- KPI & kepemilikan: [[HRIS - Matriks KPI per Departemen]] · [[REF - Kepemilikan Data]] · [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]]
