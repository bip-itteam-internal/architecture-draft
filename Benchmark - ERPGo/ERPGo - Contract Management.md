> **Status:** 🟡 Benchmark / Konsep — research dari ERPGo SaaS, **belum** keputusan Bharata. Sumber: User Manual ERPGo (demo login-gated). Hub: [[ERPGo - Overview & Gap Matrix]].

## Apa yang ERPGo lakukan

Modul **Contract Management** mengelola kontrak end-to-end:
- **Manage Contracts** — buat kontrak (subjek, nilai, pihak/customer/vendor, tanggal mulai–akhir, tipe), status, attachment.
- **Contract Types** — master kategori kontrak (mis. NDA, supplier, sewa, kerja).
- Per kontrak: deskripsi, **notes/comments**, lampiran file, dan (di modul aslinya) penandatanganan/approval serta penautan ke customer/vendor yang sama dengan modul Accounting/CRM.

## Yang sudah ada di Bharata ERP

- 🔴 **Tidak ada modul kontrak khusus.** Tidak ada collection/service yang memiliki entitas "contract".
- Singgungan terdekat: [[GA - Procurement System]] (hubungan ke vendor/PO) dan [[Vendor - CRM]] (data vendor), tapi keduanya tidak menyimpan dokumen kontrak + masa berlaku + reminder.
- File/dokumen umum diurus [[Microservices - File Service]] (MinIO), tapi tanpa metadata kontrak.

## Gap / Peluang

- Tidak ada **single source** untuk kontrak vendor, customer, sewa gedung, atau kontrak kerja karyawan beserta **tanggal kedaluwarsa + reminder**.
- Risiko nyata: kontrak/PKWT/sewa lewat tanpa renewal. Ini fit dengan kebutuhan [[GA - Procurement System]] dan HRIS (kontrak kerja → [[HRIS - Personalia]]).

## Rekomendasi

- **Adopsi — prioritas sedang.** Mulai dari yang berdampak: **kontrak vendor (GA)** dan **kontrak kerja/PKWT (HRIS)**.
- **Penempatan usulan** (bila jadi): dok konsep `GA - Contract Management` di domain General Affairs (atau `HRIS - Employment Contract` untuk sisi kepegawaian), bukan service baru dulu — bisa ditempel ke service GA/employee yang ada.
- **MVP minimal**: entitas Contract (pihak, tipe, nilai, periode, file, status) + **reminder kedaluwarsa** via [[Microservices - Notification Service]]. Contract Types = master kecil.

## Risiko & catatan jaga sistem berjalan

- Jangan duplikasi data vendor — referensikan sumber yang ada ([[Vendor - CRM]] / data procurement), jangan bikin master vendor baru.
- Hormati **database-per-service** ([[DB - Overview and Notes]]): kontrak GA milik service GA, kontrak kerja milik employee-service — jangan saling query DB langsung.

## Dokumen Terkait

- [[ERPGo - Overview & Gap Matrix]]
- [[GA - Procurement System]] · [[Vendor - CRM]] · [[HRIS - Personalia]]
- [[Microservices - File Service]] · [[Microservices - Notification Service]]
