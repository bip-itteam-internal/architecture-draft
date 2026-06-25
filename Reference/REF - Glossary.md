## Deskripsi

*Glosarium istilah & singkatan yang dipakai lintas vault + kode bip-erp Bharata International Pharmaceutical. Tujuan: agar agent/manusia membaca istilah dengan arti yang sama. Doc **Reference** (area non-domain) — grounded, terus ditambah seiring istilah baru muncul.*

- **Status**: 🟡 Seed (akan terus dilengkapi)
- **Aturan isi**: hanya istilah yang **benar-benar dipakai** di vault/kode atau standar regulasi yang berlaku. Arti Bharata-spesifik yang belum pasti → tandai (TBD).

## Umum / Teknis

| Istilah | Kepanjangan | Arti singkat | Konteks |
|---|---|---|---|
| ERP | Enterprise Resource Planning | Sistem terpadu proses bisnis | [[HOMEPAGE]] |
| bip-erp | Bharata International Pharmaceutical ERP | Backend mono-repo microservices Go | [[HOMEPAGE]] |
| SSO | Single Sign-On | Login sekali untuk semua aplikasi internal | [[CORE - SSO Flow]] |
| JWT | JSON Web Token | Token auth yang ditandatangani gateway | [[CORE - API Master Gateway]] |
| RBAC | Role-Based Access Control | Otorisasi berbasis peran (`system_roles`) | [[CORE - API Master Gateway]] |
| FCM | Firebase Cloud Messaging | Push notification ke HP | [[Microservices - Notification Service]] |
| MinIO | — | Object storage bersama (S3-compatible) | [[DB - Overview and Notes]] |
| BPMN | Business Process Model and Notation | Notasi diagram alur proses | [[HRIS - Big Pictures]] |
| UTC | Coordinated Universal Time | Semua server simpan waktu dalam UTC | [[DB - Overview and Notes]] |

## Bisnis / ERP

| Istilah | Kepanjangan | Arti singkat | Konteks |
|---|---|---|---|
| SKU | Stock Keeping Unit | Kode unik item/produk | [[Microservices - Inventory Service]] |
| PO | Purchase Order | Pesanan pembelian ke vendor | [[GA - Procurement System]] |
| WMS | Warehouse Management System | Sistem kelola gudang | [[WH - Management System]] |
| SO | Stock Opname | Penghitungan fisik stok | [[Manufacture - Issue ED Material after Stock Opname]] |
| GMV | Gross Merchandise Value | Nilai total transaksi marketplace | [[Sales - GMV Creative]] |
| KPI | Key Performance Index | Ukuran kinerja karyawan | [[HRIS - Key Performance Index]] |
| SP | Surat Peringatan | Sanksi disiplin karyawan | [[HRIS - Disciplinary (Surat Peringatan)]] |
| PKWT | Perjanjian Kerja Waktu Tertentu | Kontrak kerja kontrak (Indonesia) | (TBD penggunaan internal) |

## Farmasi / Regulasi

> Definisi mengikuti standar regulasi farmasi Indonesia (publik). Penerapan **spesifik Bharata** (sertifikat mana yang dimiliki, nomor, lingkup) = (TBD), diisi tim QA/RA — lihat [[QA - Big Pictures]].

| Istilah | Kepanjangan | Arti singkat | Konteks |
|---|---|---|---|
| CPOB | Cara Pembuatan Obat yang Baik | Standar GMP versi Indonesia (BPOM) | [[QA - CPOB (GMP)]] |
| GMP | Good Manufacturing Practice | Standar mutu pembuatan obat | [[QA - CPOB (GMP)]] |
| BPOM | Badan Pengawas Obat dan Makanan | Otoritas regulasi obat & makanan RI | [[QA - BPOM & Izin Edar (NIE)]] |
| NIE | Nomor Izin Edar | Nomor registrasi produk yang sah beredar | [[QA - BPOM & Izin Edar (NIE)]] |
| CDOB | Cara Distribusi Obat yang Baik | Standar distribusi obat | [[QA - Big Pictures]] |
| PBF | Pedagang Besar Farmasi | Entitas berizin distribusi obat | (TBD relevansi) |
| CoA | Certificate of Analysis | Sertifikat hasil uji mutu batch | [[QA - Batch Record & Traceability]] |
| CAPA | Corrective And Preventive Action | Tindakan korektif & preventif atas masalah mutu | [[QA - Deviation & CAPA]] |
| QA | Quality Assurance | Penjaminan mutu | [[QA - Big Pictures]] |
| QC | Quality Control | Pengendalian/pengujian mutu | [[QA - Big Pictures]] |
| RA | Regulatory Affairs | Urusan kepatuhan regulasi | [[QA - Big Pictures]] |
| ED | Expired Date | Tanggal kedaluwarsa produk/material | [[QA - Expired (ED) & Recall]] |
| Batch / Bets | — | Satu lot produksi dengan identitas tunggal | [[QA - Batch Record & Traceability]] |

## Pihak Ketiga / Kanal

| Istilah | Arti singkat | Konteks |
|---|---|---|
| Accurate | Software akuntansi (sumber kebenaran finance) | [[External - Accurate]] |
| Desty | Tool integrasi marketplace | [[External - Desty]] |
| TikTok Shop / Shopee | Marketplace tempat berjualan | [[Sales - Marketplace Integration]] |
| Glints / TapLoker | Portal lowongan/ATS untuk rekrutmen | [[HRIS - Recruitment]] |

## Dokumen Terkait

- [[HOMEPAGE]] · [[QA - Big Pictures]] · [[DB - Overview and Notes]]
