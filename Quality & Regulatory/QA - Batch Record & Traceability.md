## Deskripsi

*Catatan bets (**batch record**) & **ketertelusuran** produk farmasi: dari material masuk → produksi → produk jadi → distribusi. **Scaffold** — kerangka; skema penomoran bets & format record spesifik Bharata = (TBD).*

- **Status**: 🔴 Stub — kerangka
- **Induk**: [[QA - Big Pictures]]
- **Implementasi digital (WMS)**: [[Manufacture - Dokumen Produksi Batch]] — dossier batch 7 lembar + workflow rilis (✅ Implemented)

## Latar Belakang

- CPOB ([[QA - CPOB (GMP)]]) mewajibkan tiap bets punya identitas tunggal + record lengkap (material, proses, hasil uji/**CoA**) agar bisa ditelusuri & ditarik bila perlu ([[QA - Expired (ED) & Recall]]).

## Ruang Lingkup / Cakupan (business view)

- Penomoran bets + atribut (tanggal produksi, **ED**, qty) — (TBD)
- Batch record: material→produk + hasil **CoA** (Certificate of Analysis) — (TBD)
- Traceability hulu-hilir (material lot ↔ bets ↔ pengiriman) — (TBD)

## Konsumen Data

- [[Manufacture - Stock & Material Management]] — material per lot/bets
- [[Microservices - Inventory Service]] — stok per bets/ED (TBD apakah inventory simpan batch/ED)
- [[QA - Expired (ED) & Recall]] — dasar penarikan per bets

## Belum Diputuskan (TBD)

- Apakah bets/ED sudah disimpan di [[Microservices - Inventory Service]] (`inventory`/`data_master`) atau hanya manual.
- Format & lokasi master batch record (kertas/sistem).

## Dokumen Terkait

- [[QA - Big Pictures]] · [[QA - CPOB (GMP)]] · [[QA - Expired (ED) & Recall]]
- [[Manufacture - Stock & Material Management]] · [[Microservices - Inventory Service]] · [[REF - Glossary]]
