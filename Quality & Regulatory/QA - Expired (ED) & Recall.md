## Deskripsi

*Manajemen produk/material **kedaluwarsa (ED)** & prosedur **penarikan (recall)**. Satu-satunya area QA yang **sudah punya sinyal operasional** di vault → di sini diberi rumah & dikaitkan. **Scaffold** — alur recall formal spesifik Bharata = (TBD).*

- **Status**: 🟡 Konsep — ada sinyal operasional ED; alur recall (TBD)
- **Induk**: [[QA - Big Pictures]]

## Latar Belakang

- Material/produk lewat **ED** tidak boleh dipakai/dijual. Vault sudah mencatat penanganan material ED yang ketahuan saat stock opname: [[Manufacture - Issue ED Material after Stock Opname]] (operasional, point-in-time).
- **Recall** = penarikan produk yang sudah beredar bila ada masalah mutu/keamanan; wajib tertelusur per bets ([[QA - Batch Record & Traceability]]).

## Ruang Lingkup / Cakupan (business view)

- Monitoring ED material & produk (alert mendekati ED) — (TBD; potensi [[Microservices - Notification Service]])
- Penanganan stok ED: karantina → disposisi (retur/musnah) — sebagian terlihat di [[Manufacture - Issue ED Material after Stock Opname]]
- Prosedur recall (kelas, notifikasi, telusur per bets, pelaporan BPOM) — (TBD)

## Konsumen Data

- [[Manufacture - Stock & Material Management]] · [[WH - Management System]] — lokasi & status stok ED
- [[Microservices - Inventory Service]] — flag ED per bets (TBD)

## Belum Diputuskan (TBD)

- Apakah perlu alert ED otomatis (threshold hari) di sistem.
- Alur recall formal + pelaporan ke [[QA - BPOM & Izin Edar (NIE)]].
- Disposisi stok ED (retur vendor / pemusnahan) — dampak ke [[Finance]] (nilai stok).

## Dokumen Terkait

- [[QA - Big Pictures]] · [[QA - Batch Record & Traceability]] · [[QA - BPOM & Izin Edar (NIE)]]
- [[Manufacture - Issue ED Material after Stock Opname]] · [[Manufacture - Stock & Material Management]] · [[REF - Glossary]]
