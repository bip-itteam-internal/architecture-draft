> **Status:** 🟡 Benchmark / Konsep — research dari ERPGo SaaS, **belum** keputusan Bharata. Sumber: User Manual ERPGo (demo login-gated). Hub: [[ERPGo - Overview & Gap Matrix]].

## Apa yang ERPGo lakukan

Modul **Goal Management** (gaya OKR/goal-tracking):
- **Manage Goals** — tetapkan goal (judul, target, periode, owner, kategori).
- **Manage Milestones** — pecah goal jadi milestone terukur.
- **Manage Contributions** — catat kontribusi/progress terhadap goal.
- **Manage Tracking** — pantau pencapaian (%) over time.
- **Manage Categories** — master kategori goal.

## Yang sudah ada di Bharata ERP

- [[HRIS - Key Performance Index]] — **KPI** karyawan (skor periodik) + [[Microservices - Insentive Service]] (`master_kpis`, `kpi_score`). Ini **penilaian kinerja**, bukan goal-setting top-down/cascading.
- [[HRIS - Work Review]] — review kerja. Tidak ada entitas "goal" dengan milestone & contribution.
- 🔴 Tidak ada **OKR/goal cascading** (company → divisi → individu) dengan tracking progres.

## Gap / Peluang

- KPI menjawab "seberapa baik kinerjanya"; **Goal/OKR** menjawab "apa yang ingin dicapai & progресnya". Keduanya komplementer.
- Peluang: goal level perusahaan/divisi yang **terhubung** ke KPI individu sebagai ukuran.

## Rekomendasi

- **Adopsi — prioritas sedang/rendah.** Bernilai untuk manajemen, tapi bukan blocker operasional.
- **Penempatan usulan** (bila jadi): dok konsep `HRIS - Goal & OKR` di domain HRIS, **ditaut** ke [[HRIS - Key Performance Index]] (KPI sebagai key-result) dan [[HRIS - Work Review]].
- **MVP minimal**: Goal (owner, periode, target) + Milestone + progress tracking; kategori = master kecil. Hindari over-engineering contribution log di awal.

## Risiko & catatan jaga sistem berjalan

- Jangan tumpang-tindih dengan KPI yang sudah jalan; definisikan batas: **Goal = arah**, **KPI = ukuran**. Reuse data KPI dari [[Microservices - Insentive Service]] bila perlu (read-only via gateway).

## Dokumen Terkait

- [[ERPGo - Overview & Gap Matrix]]
- [[HRIS - Key Performance Index]] · [[HRIS - Work Review]] · [[Microservices - Insentive Service]]
