**Status**: ⚠️ **Implemented (ada catatan)**. Peta domain Finance System. Rencana awal membangun ulang sistem finance di dalam ERP sudah sebagian terwujud (diukur 2026-09-12, lihat bagian "Peta sistem finance di ERP"); dua paragraf Deskripsi di bawah adalah latar belakang rencana itu, bukan keadaan hari ini.

## Deskripsi

*Sistem finance saat ini mengelola data masuk dari Vendor - CRM, membersihkan dan menyinkronkan informasi tersebut untuk [[External - Accurate]] guna membuat ikhtisar mengenai seluruh aspek dalam finance*

*Karena sistem ini sudah terenkapsulasi dan memiliki ekosistemnya sendiri, tidak disarankan untuk menautkan sistem yang ada ini ke dalam arsitektur, sehingga finance akan mendapatkan sistem baru yang dibangun dari awal dan seluruh ekosistem terenkapsulasi sebelumnya akan diimplementasikan ulang dengan benar pada sistem baru tersebut*

## Peta sistem finance di ERP (diukur 2026-09-12)

| Ranah | Tempat di kode | Dokumen |
|---|---|---|
| Pajak (Tax Control), rekomendasi cost control, biaya variabel produksi, backend audit internal | `bip-erp/services/finance` | [[API - Finance Service]] · [[Finance - Rancangan Finance Service]] · [[Finance - Audit Internal]] |
| Kas kecil, pengajuan budget, pengajuan barang lima tipe, utang pemasok (tagihan, pembayaran, bukti transfer) | `bip-erp/services/procurement` | [[Finance - Kas Kecil dan Pengajuan Budget]] · [[Microservices - Procurement Service]] · [[API - Procurement Service]] |
| Bridging ke Accurate (faktur, retur, penerimaan), laporan keuangan, jurnal, piutang marketplace, rekonsiliasi | `bip-erp/services/integration` | [[Microservices - Integration Service]] · [[API - Integration Service]] |
| Insentif berbasis profit | `bip-erp/services/insentive` bersama integration-service | [[Finance - Incentive]] · [[Microservices - Insentive Service]] |
| Menu Finance dan dashboard per posisi | `erp-frontend/src/features/finance` | [[Finance - Dashboard per Posisi (FAT)]] |
| Aplikasi audit internal | repo `audit-bharata`; container `Audit-App` berjalan di prod sejak 2026-09-11, backend-nya masih di finance-service | [[APP - Audit Internal]] |

Siapa memakai apa per posisi, akses nyatanya di prod, dan alur kerja antar posisi: [[Finance - FAT Persona]].

## Sistem akuntansi kedua yang berjalan di luar peta ini

⚠️ Sejak **5 Agustus 2026** ada buku besar double-entry + konsolidasi untuk **40 CV** grup yang berjalan sepenuhnya di luar ERP dan di luar [[External - Accurate]]: [[APP - Buku Besar Konsolidasi CV FINCON]]. Entitas yang dibukukannya **sama** dengan badan usaha di [[Microservices - Payroll Service]] dan rekening/proyek Accurate, sehingga laba per CV kini punya dua sumber yang tak direkonsiliasi. Ia sekaligus menutup satu celah asli — kertas kerja konsolidasi + jurnal eliminasi intercompany yang tidak dimiliki ERP maupun Accurate.

Arahnya belum diputuskan; pilihan dan konsekuensinya di [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]] (🟡 Proposed). Keputusan induk yang dilanggarnya: [[ADR - 0001 Akuntansi via Accurate]].

## Dokumen Terkait

- [[Finance - Bridging App]] — implementasi bridging
- [[Finance - Incentive]] — perhitungan insentif
- [[Finance - Dashboard per Posisi (FAT)]] — dashboard keuangan per posisi (kartu + grafik keputusan)
- [[Finance - FAT Persona]]: persona per posisi dan alur kerja antar posisi
- [[APP - Buku Besar Konsolidasi CV FINCON]] — buku besar & konsolidasi 40 CV **di luar ERP** · [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]]
- [[External - Accurate]] (akuntansi) · [[Vendor - CRM]] (sumber data purchase order)

