**Status**: 🟡 **Konsep / Overview** — peta domain Finance System: sistem lama terenkapsulasi (sinkron ke Accurate), direncanakan dibangun ulang dari awal.

## Deskripsi

*Sistem finance saat ini mengelola data masuk dari Vendor - CRM, membersihkan dan menyinkronkan informasi tersebut untuk [[External - Accurate]] guna membuat ikhtisar mengenai seluruh aspek dalam finance*

*Karena sistem ini sudah terenkapsulasi dan memiliki ekosistemnya sendiri, tidak disarankan untuk menautkan sistem yang ada ini ke dalam arsitektur, sehingga finance akan mendapatkan sistem baru yang dibangun dari awal dan seluruh ekosistem terenkapsulasi sebelumnya akan diimplementasikan ulang dengan benar pada sistem baru tersebut*

## Sistem akuntansi kedua yang berjalan di luar peta ini

⚠️ Sejak **5 Agustus 2026** ada buku besar double-entry + konsolidasi untuk **40 CV** grup yang berjalan sepenuhnya di luar ERP dan di luar [[External - Accurate]]: [[APP - Buku Besar Konsolidasi CV FINCON]]. Entitas yang dibukukannya **sama** dengan badan usaha di [[Microservices - Payroll Service]] dan rekening/proyek Accurate, sehingga laba per CV kini punya dua sumber yang tak direkonsiliasi. Ia sekaligus menutup satu celah asli — kertas kerja konsolidasi + jurnal eliminasi intercompany yang tidak dimiliki ERP maupun Accurate.

Arahnya belum diputuskan; pilihan dan konsekuensinya di [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]] (🟡 Proposed). Keputusan induk yang dilanggarnya: [[ADR - 0001 Akuntansi via Accurate]].

## Dokumen Terkait

- [[Finance - Bridging App]] — implementasi bridging
- [[Finance - Incentive]] — perhitungan insentif
- [[Finance - Dashboard per Posisi (FAT)]] — dashboard keuangan per posisi (kartu + grafik keputusan)
- [[APP - Buku Besar Konsolidasi CV FINCON]] — buku besar & konsolidasi 40 CV **di luar ERP** · [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]]
- [[External - Accurate]] (akuntansi) · [[Vendor - CRM]] (sumber data purchase order)

