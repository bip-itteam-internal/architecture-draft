> **Status:** 🟡 Benchmark / Konsep — research dari ERPGo SaaS, **belum** keputusan Bharata. Sumber: User Manual ERPGo (demo login-gated). Hub: [[ERPGo - Overview & Gap Matrix]].

## Apa yang ERPGo lakukan

Modul **Performance Management**:
- **Performance Indicators** — definisikan indikator penilaian (kompetensi/perilaku/teknis) per role.
- **Employee Goals** — goal yang dinilai dalam review.
- **Review Cycles** — **periode review terjadwal** (mis. kuartalan) yang membungkus penilaian.
- **Employee Reviews** — atasan menilai indikator per karyawan dalam suatu cycle, hasil tersimpan & dibandingkan antar-periode.

## Yang sudah ada di Bharata ERP

- [[HRIS - Key Performance Index]] + [[Microservices - Insentive Service]] (`master_kpis`, `kpi_score`) — **skor KPI** yang menggerakkan insentif. Sudah ada indikator + skor.
- [[HRIS - Work Review]] — konsep review kerja.
- 🟡 Yang **kurang**: konsep **Review Cycle** eksplisit (periode formal yang mengikat sekumpulan review + status open/closed + perbandingan antar-cycle).

## Gap / Peluang

- Bharata sudah punya **indikator + skor**; gap-nya adalah **orkestrasi siklus**: jadwal review, status pengisian, agregasi per cycle, histori.
- Ini **enrichment**, bukan modul baru — paling pas digraft ke [[HRIS - Work Review]] / [[HRIS - Key Performance Index]].

## Rekomendasi

- **Adopsi sebagai enrichment — prioritas sedang.** Tambahkan entitas **Review Cycle** + status + histori ke alur KPI/Work Review yang ada.
- **Penempatan usulan**: perkaya [[HRIS - Work Review]] (definisi proses) dan [[Microservices - Insentive Service]] (penyimpanan skor per cycle) — **bukan** dok/area baru.
- **MVP minimal**: entity ReviewCycle (periode, status open/closed) yang menaungi `kpi_score` existing + tampilan tren antar-cycle.

## Risiko & catatan jaga sistem berjalan

- KPI sudah memengaruhi **insentif** — perubahan skema skor berisiko ke perhitungan insentif ([[Finance - Incentive]]). Tambah cycle sebagai **lapisan di atas** skor, jangan ubah formula yang sudah jalan.

## Dokumen Terkait

- [[ERPGo - Overview & Gap Matrix]]
- [[HRIS - Work Review]] · [[HRIS - Key Performance Index]] · [[Microservices - Insentive Service]] · [[Finance - Incentive]]
