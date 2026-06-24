> **Status:** 🟡 Benchmark / Konsep — research dari ERPGo SaaS, **belum** keputusan Bharata. Sumber: User Manual ERPGo (demo login-gated). Hub: [[ERPGo - Overview & Gap Matrix]].

## Apa yang ERPGo lakukan

Modul **Budget Planner** = perencanaan & monitoring anggaran:
- **Budget Periods** — definisikan periode anggaran (bulanan/kuartal/tahunan).
- **Manage Budget** — buat anggaran per periode (per akun/kategori).
- **Budget Allocations** — alokasikan nominal ke pos/departemen.
- **Budget Monitoring** — bandingkan **anggaran vs realisasi** (actual dari modul Accounting) → variance.

## Yang sudah ada di Bharata ERP

- 🔴 **Tidak ada modul budgeting.** [[Finance]] fokus pada bridging data ke **Accurate** (akuntansi), bukan perencanaan anggaran ke depan.
- [[Finance - Incentive]] / [[Sales - Incentive]] menghitung insentif, bukan budget plan.
- Realisasi biaya/pendapatan tersimpan di **Accurate** ([[External - Accurate]]).

## Gap / Peluang

- Tidak ada tempat menetapkan **plan** anggaran per departemen dan memantau **budget vs actual**.
- Karena actual sudah ada di Accurate, peluangnya: **layer planning ringan** yang menarik actual dari Accurate (via [[Finance - Bridging App]]) untuk monitoring variance — tanpa membangun akuntansi penuh.

## Rekomendasi

- **Adopsi — prioritas sedang**, tapi **hati-hati ruang lingkup**: ambil hanya **planning + monitoring**, jangan akuntansinya (itu tetap Accurate).
- **Penempatan usulan** (bila jadi): dok konsep `Finance - Budget Planner` di domain Finance System, sebagai pelengkap [[Finance]].
- **MVP minimal**: Budget Period + Budget per departemen/kategori + tarik actual read-only dari bridging → tampilkan variance di [[Sales - Dashboard]]/dashboard finance.

## Risiko & catatan jaga sistem berjalan

- **Jangan** menarik double-entry/CoA ke internal — sumber kebenaran akuntansi tetap [[External - Accurate]] (lihat catatan [[Finance]]).
- Konsumsi actual harus **read-only** lewat jalur bridging yang sudah ada; jangan tulis balik ke Accurate dari modul budget.

## Dokumen Terkait

- [[ERPGo - Overview & Gap Matrix]]
- [[Finance]] · [[Finance - Bridging App]] · [[External - Accurate]]
- [[Sales - Dashboard]]
