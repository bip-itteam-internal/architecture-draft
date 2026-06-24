## ADR 0004 — Modul ERPGo yang sengaja TIDAK diadopsi

- **Status**: ✅ Accepted
- **Tanggal**: 2026-06-24
- **Konteks dok**: [[ERPGo - Overview & Gap Matrix]]

## Context

Benchmark fitur ERPGo SaaS vs bip-erp ([[ERPGo - Overview & Gap Matrix]]) memunculkan beberapa modul yang **tidak selaras** dengan model bisnis Bharata (farmasi + manufaktur + seller marketplace, single-tenant internal). Tanpa keputusan eksplisit, ada risiko ada yang mengira modul-modul ini harus dibangun.

## Decision

Modul ERPGo berikut **out-of-scope** (tidak dibangun internal):
1. **Accounting penuh & Double-Entry** → didelegasikan ke Accurate ([[ADR - 0001 Akuntansi via Accurate]]).
2. **POS (retail)** → model = seller marketplace + manufaktur, bukan toko fisik → **deferred** ([[ERPGo - POS (Point of Sale)]]).
3. **SaaS layer** (subscription, coupon, plan, multi-tenant, CMS landing builder) → bip-erp **single-tenant internal**; hanya landing marketing yang relevan ([[Sales - Landing page]]).

## Consequences

- ➕ Tim tidak menghabiskan effort pada fitur tanpa pemakai.
- ➕ Agent/manusia tahu menolak usulan yang sudah ditolak (mencegah scope creep).
- ➖ Bila model bisnis berubah (mis. buka outlet ritel), POS perlu **re-evaluasi** — pemicu dicatat di [[ERPGo - POS (Point of Sale)]].
- 🔗 Kandidat yang **layak** diadopsi tetap di [[ERPGo - Overview & Gap Matrix]] (Form Builder, Contract, Budget Planner, dll).

## Dokumen Terkait

- [[ERPGo - Overview & Gap Matrix]] · [[ADR - 0001 Akuntansi via Accurate]] · [[ERPGo - POS (Point of Sale)]] · [[Sales - Landing page]]
