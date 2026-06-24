> **Status:** 🟡 Benchmark / Konsep — research dari ERPGo SaaS, **belum** keputusan Bharata. Sumber: User Manual ERPGo (demo login-gated). Hub: [[ERPGo - Overview & Gap Matrix]].

## Apa yang ERPGo lakukan

Modul **CRM** berbasis pipeline:
- **Manage Leads** — lead masuk (sumber, kontak, owner), follow-up, **konversi lead → deal**.
- **Manage Deals** — deal dengan **stages/pipeline** (Kanban), nilai, probabilitas, produk terkait, **calendar view per deal**, tasks, notes, files, **360° deal detail**.
- **CRM System Setup** — master pipeline/stage/sumber/label.
- **Reports** — corong & performa per owner/stage.

## Yang sudah ada di Bharata ERP

- ⚠️ **CRM ditangani sistem/vendor eksternal**: [[Sales - CRM management tool]] (dashboard `monitoring.hubcrm...`, data customer TikTok dari vendor Semarang) dan [[Vendor - CRM]].
- Masalah terdokumentasi: data tersensor dari vendor + isu WA blasting (suspend). Tidak ada **pipeline lead→deal** internal yang kita kontrol.

## Gap / Peluang

- Yang ada = **manajemen kontak/blasting** customer marketplace, **bukan** pipeline sales B2B.
- Peluang: **CRM internal** yang kita miliki datanya (mengurangi ketergantungan vendor + masalah data tersensor), khususnya bila ada jalur penjualan non-marketplace.

## Rekomendasi

- **Adopsi bersyarat — prioritas sedang.** Bergantung pada keberadaan proses sales pipeline internal (lihat TBD di [[ERPGo - Quotation & Proposal]]).
- **Penempatan usulan** (bila jadi): perluas [[Sales - CRM management tool]] menjadi konsep CRM internal, atau dok baru `Sales - Internal CRM Pipeline`. Pertimbangkan service baru hanya bila volume besar.
- **MVP minimal**: Lead → Deal + stage Kanban + owner + activity log. Integrasi blasting WA = pisahkan (sudah jadi isu sendiri di [[Sales - CRM management tool]]).

## Risiko & catatan jaga sistem berjalan

- Jangan putus integrasi vendor yang masih dipakai mendadak; rancang sebagai **paralel/komplemen** dulu.
- Data customer sensitif — hormati [[IT - Security]] dan jalur SSO ([[CORE - SSO Flow]]).

## Dokumen Terkait

- [[ERPGo - Overview & Gap Matrix]]
- [[Sales - CRM management tool]] · [[Vendor - CRM]] · [[ERPGo - Quotation & Proposal]]
- [[IT - Security]] · [[CORE - SSO Flow]]
