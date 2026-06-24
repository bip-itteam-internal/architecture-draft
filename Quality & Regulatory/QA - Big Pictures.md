## Deskripsi

*Peta fungsi **Quality Assurance / Regulatory Affairs (QA/RA)** untuk Bharata International Pharmaceutical — domain yang menjamin produk farmasi dibuat & diedarkan sesuai regulasi. Doc induk domain `Quality & Regulatory`; sub-dok detail per area. **Kerangka (scaffold)** — isi spesifik Bharata diisi tim QA/RA dari SOP/sertifikat nyata, jangan dikarang.*

- **Status**: 🟡 Konsep / Kerangka — scaffold; mayoritas isi (TBD)
- **Sumber kebenaran**: SOP & sertifikat QA/RA Bharata (bukan kode). Lihat [[CLAUDE]] §7 (area non-kode).

## Latar Belakang

- Perusahaan farmasi wajib patuh standar **CPOB (GMP)** dan registrasi **BPOM**; mutu & ketertelusuran (traceability) bersifat regulatif, bukan opsional.
- Saat ini sinyal mutu di vault baru muncul **operasional & tersebar** (mis. penanganan material **ED** setelah stock opname di [[Manufacture - Issue ED Material after Stock Opname]]). Domain ini memberi rumah terpusat untuk QA/RA.
- Tujuan second-brain: agent paham batasan regulasi sebelum mengusulkan perubahan proses produksi/distribusi.

## Ruang Lingkup / Cakupan (business view)

- [[QA - CPOB (GMP)]] — kepatuhan Cara Pembuatan Obat yang Baik
- [[QA - BPOM & Izin Edar (NIE)]] — registrasi & izin edar produk
- [[QA - Batch Record & Traceability]] — catatan bets + telusur hulu-hilir
- [[QA - Deviation & CAPA]] — penyimpangan mutu + tindakan korektif/preventif
- [[QA - Expired (ED) & Recall]] — manajemen kedaluwarsa + penarikan produk
- CDOB (distribusi) — (TBD: apakah Bharata memegang fungsi distribusi/PBF?)

## Konsumen Data

- [[Manufacture - Stock & Material Management]] — status mutu/karantina material & produk
- [[WH - Management System]] — pemisahan stok released/quarantine/rejected (TBD)
- [[Finance]] / [[External - Accurate]] — nilai stok terdampak ED/recall (TBD)

## Kendala

- Konten regulatif tak boleh dikarang (rulebook §1) → butuh input QA/RA.

## Belum Diputuskan (TBD)

- Struktur tim QA/RA & pemilik proses (lihat rencana `REF - Ownership & RACI`).
- Sertifikat CPOB & nomor izin edar yang dimiliki Bharata (lingkup produk).
- Apakah Bharata melakukan **distribusi** (CDOB/PBF) atau hanya produksi + jual via marketplace.
- Integrasi status mutu (released/quarantine/reject) ke [[Microservices - Inventory Service]].

## Dokumen Terkait

- [[REF - Glossary]] (istilah farmasi) · [[HOMEPAGE]]
- [[Manufacture - Issue ED Material after Stock Opname]] · [[Manufacture - Stock & Material Management]]
