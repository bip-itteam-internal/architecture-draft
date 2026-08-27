## Deskripsi

*Rekaman **11 SOP Procurement resmi** PT Bharata Internasional Pharmaceutical (disusun Leader Procurement, disetujui Direktur) berikut **peta kepatuhannya terhadap sistem ERP yang berjalan**. Tujuannya: pengembangan procurement/manufacture ke depan **terarah dan patuh SOP** — tiap fitur baru diukur terhadap tahap SOP yang relevan, dan gerbang `/plan`/`/review` bisa merujuk ke sini. Bagian "standar" bersumber dari dokumen SOP (`C:\Work\SOP-Procurement`, di luar repo — **sumber kebenaran proses bisnis**); bagian "status" grounded ke kode `bip-erp` dan diverifikasi penelusuran, bukan asumsi.*

- **Status**: ⚠️ **Standar SOP lengkap; implementasi ERP baru sebagian.** Tulang punggung transaksional (Permintaan → Pesanan → Penerimaan) ada; beberapa kontrol inti SOP (RFQ/3-vendor, evaluasi vendor, matriks approval nominal, dokumen/AVL vendor, pelaporan) **belum dibangun**. Diaudit 2026-08-26.
- **Sumber SOP (otoritatif)**: `C:\Work\SOP-Procurement` — 001–009 (per proses) + 010 (alur end-to-end & Work Instruction). **Tidak di-commit ke repo mana pun**; dokumen inilah yang menang bila perilaku sistem berbeda darinya.
- **Path implementasi**: `bip-erp/services/procurement` (PR/PO/Penerimaan ERP + cermin Accurate), `bip-erp/services/employee` (kontrak & cost-saving register), `bip-erp/services/manufacture` (perencanaan kebutuhan/MaterialOrder). FE `erp-frontend/src/features/procurement` & `.../manufacture`.
- **Peta lintas-modul terkait**: [[REF - Rantai Pengajuan Lintas Modul]] (§1 = kesenjangan SOP 001).

## Alur End-to-End (SOP 010) vs Implementasi

Legenda status: ✅ terpenuhi · ⚠️ sebagian · ❌ belum ada · 🔵 di luar ERP (Accurate).

| # | Tahap SOP | Wajib per SOP | Implementasi ERP | Status |
|---|---|---|---|---|
| 1 | Pengajuan PR | User buat PR: spesifikasi, qty, timeline, estimasi budget; verifikasi atasan | `permintaan_erp` (create) + FE Permintaan Barang; rincian + harga estimasi ada | ✅ |
| 2 | Verifikasi PR | Cek kelengkapan+budget+urgensi; **TTD PPIC + SPV Manufacture + Leader Procurement → Direktur**; SLA 1 hari | Persetujuan **atasan langsung** departemen (1 tahap); tanpa rantai TTD berlapis, cek budget, timer SLA | ⚠️ |
| 3 | Sourcing & RFQ | Kirim RFQ ke **min. 2–3 vendor**, terima quotation | **Nihil** — tak ada modul RFQ/quotation | ❌ |
| 4 | Analisa & Negosiasi | Bid comparison (harga/lead time/kualitas/terms) + negosiasi | **Nihil** — tak ada lembar perbandingan/rekam negosiasi | ❌ |
| 5 | Approval Pembelian | Limit berjenjang: Staff→Leader; Leader→Management bila **> Rp 50 juta** | PO disetujui by jabatan (setara Direktur), 1 tahap; **tanpa matriks nominal** | ⚠️ |
| 6 | Penerbitan PO | Buat PO, kirim vendor, konfirmasi; SLA 1–2 hari | `pesanan_erp` (create + Ambil Permintaan + persetujuan + penomoran `PO.YYYY.MM.NNNNN`) | ✅ |
| 7 | Monitoring Delivery | Track ETA, follow up, PO tracker, tutup PO | Cermin penerimaan hitung `selisih_hari`/`terlambat` (6 bln); status PO `sebagian_diproses`/`terproses` **tak pernah bergerak** | ⚠️ |
| 8 | Penerimaan + QC | Warehouse terima + QC inspection; output BA/GR | `penerimaan_erp` (GR) + tandai "barang tidak sesuai"; QC/BA formal terbatas | ⚠️ |
| 9 | Verifikasi Invoice | 3-way match: invoice vs PO vs BA | Faktur = cermin Accurate; match di Accurate/finance | 🔵 |
| 10 | Pembayaran Vendor | Finance bayar per term; procurement monitor | Pembayaran di Accurate; KPI tren AP (`/faktur/pembayaran-tren`) masih PR belum merge | 🔵 |
| 11 | Evaluasi Vendor | Scorecard bulanan (harga/OTD/quality/service), klasifikasi, blacklist | **Nihil** — tak ada scorecard/OTD/blacklist vendor | ❌ |

> ⚠️ Vonis "✅ terpenuhi" = mekanismenya ADA di sistem, **bukan** jaminan dipakai sesuai SOP secara operasional.

## Ringkas per Dokumen SOP (001–009)

- **001 Perencanaan Kebutuhan** — ⚠️ MaterialOrder hitung kebutuhan dari formula + `min_stok` (safety stock). Belum ada Procurement Plan formal, verifikasi anggaran, dan **rantai PPIC → pengadaan masih putus** (lihat [[REF - Rantai Pengajuan Lintas Modul]] §1). Detail perencanaan: [[Manufacture - Material Order (SPK)]].
- **002 Purchase Requisition** — ⚠️ `permintaan_erp` lengkap (create + persetujuan); approval 1 tahap, tanpa matriks/budget/SLA.
- **003 Seleksi & Registrasi Vendor** — ⚠️ Master Pemasok CRUD + sync Accurate. Belum ada status **AVL**, penyimpanan dokumen legalitas (NIB/NPWP/COA/MSDS/Sertifikat Halal), assessment/scoring, rekam site visit/audit.
- **004 Permintaan Penawaran Harga (RFQ)** — ❌ Nihil (kontrol wajib "3 vendor comparison" tak terpenuhi).
- **005 Penerbitan PO** — ✅ `pesanan_erp` native + cermin Accurate. Detail: [[Microservices - Procurement Service]].
- **006 Monitoring Pengiriman** — ⚠️ Cermin hitung keterlambatan (6 bln); belum ada PO tracker terpadu / penutupan outstanding PO.
- **007 Evaluasi Kinerja Vendor** — ❌ Nihil (scorecard/OTD/klasifikasi/corrective action).
- **008 Cost Saving** — ⚠️ Register Penghematan ada (`services/employee/procurement_saving.go`: item/vendor/kategori/`saving_value`). Belum ada baseline formal, tautan RFQ, laporan % saving terstruktur.
- **009 Laporan Procurement** — ⚠️ KPI Procurement + KPI AP ada; dari 8 laporan wajib (Outstanding PO, Vendor Performance, Realisasi PO, Cost Saving, bulanan/tahunan) sebagian besar belum jadi laporan formal.

## Prioritas Kesenjangan

1. **RFQ + komparasi 3 vendor** — kontrol internal wajib SOP; nol modul.
2. **Evaluasi kinerja vendor (scorecard/OTD/blacklist)** — SOP 007 & tahap 11; nihil.
3. **Matriks approval berbasis nominal** — jenjang Staff→Leader→Management (>Rp 50 jt); approval kini single-stage.
4. **Manajemen vendor: AVL + dokumen legalitas + assessment** — SOP 003; master pemasok baru data dasar.
5. **Perencanaan kebutuhan PPIC → pengadaan** — SOP 001; rantai §1 putus, sedang direncanakan (Phase 1 dalam manufacture).
6. **Pelaporan procurement formal + SLA PR→PO** — SOP 009 + kontrol SLA; belum terstruktur.

## Konteks yang Wajib Dibaca Bersama

- **Pembelian & pembayaran NYATA saat ini di Accurate.** `services/procurement` sebagian besar cermin baca-saja; entitas ERP-native (Permintaan/Pesanan/Penerimaan) = lapisan transisi keluar dari Accurate, belum menggantikan penuh. Latar: [[ADR - 0001 Akuntansi via Accurate]].
- **[[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]] (🟡 diusulkan, belum berkode)** akan mengubah alur pengadaan bahan baku — sebagian kesenjangan approval/rantai berpotensi tertutup dari arah berbeda. Rencana procurement baru **wajib** dicek terhadap ADR ini agar tak lahir jalur ketiga.
- **Kesenjangan SOP 001 = rantai §1** ([[REF - Rantai Pengajuan Lintas Modul]]) yang sedang diperbaiki; menyentuh perencanaan kebutuhan, bukan kontrol RFQ/vendor.

## Cara Memakai Dokumen Ini

- Sebelum merancang fitur procurement/manufacture baru, **cek tahap SOP mana** yang disentuh dan status implementasinya di tabel di atas.
- Penyimpangan sadar dari SOP **wajib jadi ADR** (bukan komentar kode) — pola sama dengan aturan bisnis payroll di `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md`.
- Dok ini disegarkan lewat `/sync-docs` bila implementasi bergerak (mis. modul RFQ atau evaluasi vendor dibangun).

## Dokumen Terkait

- [[Microservices - Procurement Service]] · [[Microservices - Manufacture Service]] — implementasi
- [[GA - Procurement System]] · [[GA - Form Pengadaan dan Pengajuan Dana]] — konsep pengadaan GA
- [[REF - Rantai Pengajuan Lintas Modul]] — §1 = kesenjangan SOP 001
- [[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]] — arah pengadaan bahan baku
- [[Manufacture - Material Order (SPK)]] — perencanaan kebutuhan (hulu)
