## ADR 0007 — Reimbursement / Settlement Perjalanan Dinas

- **Status**: 🟡 Proposed (belum diputuskan — placeholder arah; menunggu Finance System & konfirmasi HRD/Finance)
- **Tanggal**: 2026-06-29 (diusulkan)
- **Konteks dok**: [[HRIS - Perjalanan Dinas]] · [[ADR - 0001 Akuntansi via Accurate]] · [[GA - Procurement System]] · [[HRIS - Payroll]]

## Context

Fitur [[HRIS - Perjalanan Dinas]] (collection `business_trip_request`, BE selesai PR #174) saat ini menyimpan **anggaran sebagai estimasi datar** — `BusinessTripBudget{transport_pp, accommodation, allowance}` (rupiah `int64`) yang diisi pemohon dan ditampilkan ke reviewer **Atasan Langsung → HRD**. **Tidak ada** jalur uang: tak ada uang muka (cash advance), realisasi/aktual, bukti/kwitansi, rekonsiliasi, maupun pencairan/reimbursement. Ini **sengaja** (lihat keputusan scope di [[HRIS - Perjalanan Dinas]]) — form fisik HRD pun hanya bertanda tangan Atasan + HRD, tanpa Finance.

HRD menanyakan: **bila ke depan ingin terhubung ke Finance / payroll / reimbursement, apakah bisa?** ADR ini merekam jawabannya dan **decision point** yang harus diputuskan saat itu — supaya tidak ada field uang setengah-jadi dibangun spekulatif sekarang.

Batasan yang sudah ada (jangan dilanggar):
- [[ADR - 0001 Akuntansi via Accurate]]: bip-erp **tidak** membangun akuntansi/GL internal; pembukuan = **Accurate**, dijembatani via [[Finance - Bridging App]] / [[Microservices - Integration Service]].
- **Finance System masih 🟡 konsep** ([[GA - Procurement System]]) — target integrasi belum ada.

Kelayakan teknis (read-only, grounded): desain sekarang **tidak menghalangi** — `business_trip_request` adalah collection terpisah (bisa tumbuh field & workflow sendiri), `budget` sudah sub-dokumen (extensible), dan framework review bersama ([[HRIS - Employee Request & Approval]]) memudahkan menambah tahap reviewer (mis. Finance) dengan pola yang sama.

## Decision

> Belum diputuskan. ADR ini mengunci **prinsip** + memetakan **opsi**; angka & mekanisme final menyusul saat Finance System siap.

**Prinsip (diusulkan, selaras [[ADR - 0001 Akuntansi via Accurate]]):**
1. bip-erp **tidak** membangun mesin reimbursement/akuntansi sendiri. `business_trip_request` berperan sebagai **sumber data + workflow persetujuan**; pencairan & pembukuan = domain Finance/Accurate.
2. Penambahan ke depan bersifat **additive** ke `business_trip_request` (tambah field/sub-state), **bukan** rewrite.
3. **Jangan** tambahkan field uang spekulatif sekarang — tunggu keputusan di bawah.

**Decision point yang harus diputuskan (saat hendak go-Finance):**

| # | Pertanyaan | Opsi |
|---|---|---|
| D1 | **Ke mana uang mengalir?** | (A) via **Payroll** — uang saku jadi komponen gaji (hook ke `payroll-supplement` / lihat [[HRIS - Payroll]]) · (B) via **Finance/kas + Accurate** (jembatani lewat [[Microservices - Integration Service]]) · (C) **hybrid** (uang saku→payroll, transport/akomodasi→Finance) |
| D2 | **Uang muka?** | (A) reimburse-after (klaim setelah perjalanan) · (B) cash advance (uang muka cair dulu, lalu settle selisih) |
| D3 | **Realisasi & bukti** | perlukah input biaya **aktual** + unggah kwitansi + rekonsiliasi estimasi↔aktual sebelum pencairan? |
| D4 | **Finance sebagai reviewer?** | (A) tambah tahap `finance_status` (reviewer biaya, pola sama review berjenjang) · (B) Finance hanya **konsumen pasca-approval** (tanpa veto) |

**Rekomendasi awal** (untuk didiskusikan, bukan final): **D1=C/hybrid**, **D2=B (cash advance)** karena perjalanan dinas lazim butuh dana di muka, **D3=ya** (realisasi+bukti wajib untuk audit/CPOB), **D4=A** (Finance review bila ada uang muka). Implementasi **ditunda** sampai Finance System ada.

## Consequences

- ➕ Arah terekam; tim FE/BE tahu `business_trip_request` adalah fondasi yang **boleh tumbuh**, bukan jalan buntu.
- ➕ Menjaga [[ADR - 0001 Akuntansi via Accurate]]: tak ada duplikasi mesin akuntansi; reimbursement = jembatan ke Accurate / komponen payroll, bukan GL internal.
- ➖ Sampai ADR ini di-*Accept*, **anggaran tetap estimasi** — tidak ada pencairan otomatis; uang saku/akomodasi diproses **manual** di luar sistem (kondisi sekarang).
- ⚠️ **Blocker utama bukan model perjalanan dinas**, melainkan **Finance System belum ada** ([[GA - Procurement System]] 🟡) — keputusan D1–D4 baru bisa final setelah itu.
- ⚠️ Bila kelak realisasi (D3) diaktifkan, perlu pikirkan **konsistensi periode gaji (26–25)** seperti gap yang sudah dicatat di [[HRIS - Employee Request & Approval]] (cutoff/payroll-lock).
- 🔗 Saat di-*Accept*, perbarui status `business_trip_request.budget` di [[HRIS - Perjalanan Dinas]] dari "estimasi" → lifecycle, dan kemungkinan buat dok `Finance - Reimbursement` baru.

## Dokumen Terkait

- [[HRIS - Perjalanan Dinas]] · [[HRIS - Employee Request & Approval]] · [[Microservices - Attendance Service]]
- [[ADR - 0001 Akuntansi via Accurate]] · [[GA - Procurement System]] · [[HRIS - Payroll]]
- [[Finance - Big Pictures]] · [[Finance - Bridging App]] · [[Microservices - Integration Service]] · [[External - Accurate]]
