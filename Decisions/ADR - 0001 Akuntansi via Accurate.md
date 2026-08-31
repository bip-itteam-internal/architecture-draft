## ADR 0001 — Akuntansi didelegasikan ke Accurate (bukan dibangun internal)

- **Status**: ✅ Accepted (mencerminkan kondisi saat ini)
- **Tanggal**: TBD (keputusan historis; dikodifikasi 2026-06-24)
- **Konteks dok**: [[Finance - Big Pictures]] · [[External - Accurate]] · [[Finance - Bridging App]]

## Context

Sistem finance Bharata sudah terenkapsulasi dengan ekosistemnya sendiri dan menyinkronkan data ke **Accurate** (software akuntansi) sebagai sumber kebenaran pembukuan. Lihat catatan di [[Finance - Big Pictures]]: tidak disarankan menautkan sistem finance lama langsung ke arsitektur baru; finance akan dibangun ulang dengan benar, namun **akuntansi inti tetap di Accurate**.

## Decision

ERP internal (bip-erp) **tidak membangun akuntansi double-entry / general ledger sendiri**. Chart of Accounts, journal, ledger, balance sheet, P&L = domain **Accurate**. bip-erp hanya **menyiapkan & menjembatani data** (orders, purchase) ke Accurate via [[Finance - Bridging App]] / [[Microservices - Integration Service]].

## Consequences

- ➕ Tidak ada duplikasi mesin akuntansi; risiko ke pembukuan yang sudah jalan diminimalkan.
- ➕ Konsumsi data actual untuk kebutuhan lain (mis. Budget Planner) cukup **read-only** dari jalur bridging.
- ➖ Fitur ERP yang mengasumsikan akuntansi internal (mis. modul Accounting/Double-Entry penuh) **out-of-scope**.
- ⚠️ Perubahan integrasi harus menjaga kontrak ke Accurate; jangan menulis balik sembarangan.

## Ditantang keadaan (2026-08-31, belum diputuskan)

⚠️ Sejak 5 Agustus 2026 berjalan sebuah general ledger + konsolidasi untuk 40 CV grup di luar ERP dan di luar Accurate — persis yang dinyatakan out-of-scope di atas. Keputusan ini **belum dicabut maupun diamandemen**; pilihan arahnya dikumpulkan di [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]] (🟡 Proposed), sistemnya di [[APP - Buku Besar Konsolidasi CV FINCON]]. Jangan menyimpulkan ADR ini sudah gugur — sampai ADR 0068 diputuskan, yang berlaku tetap yang tertulis di sini.

## Dokumen Terkait

- [[Finance - Big Pictures]] · [[External - Accurate]] · [[Finance - Bridging App]]
- [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]] · [[APP - Buku Besar Konsolidasi CV FINCON]]
