> **Status:** 🟡 Benchmark / Konsep — research dari ERPGo SaaS, **belum** keputusan Bharata. Sumber: User Manual ERPGo (demo login-gated). Hub: [[ERPGo - Overview & Gap Matrix]].

## Apa yang ERPGo lakukan

Dua modul pra-penjualan yang berurutan:
- **Proposal Management** — buat **Sales Proposal** (penawaran naratif/itemized) dari template, kirim ke prospek, lacak status (sent/accept/decline), konversi → invoice.
- **Quotations Management** — **Quotation** itemized (produk/jasa, qty, harga, pajak, diskon), **Quotation Actions** (duplicate, convert ke invoice/sales order, kirim PDF).

Keduanya terhubung ke modul CRM (deal), Product/Service (item), dan Accounting (invoice).

## Yang sudah ada di Bharata ERP

- 🔴 Tidak ada entitas quotation/proposal. Penjualan Bharata mayoritas **marketplace** (TikTok Shop/Shopee) → order masuk sebagai `transaction_orders` di [[Microservices - Integration Service]], invoicing di [[External - Accurate]].
- Tidak ada alur **B2B penawaran → nego → deal** yang terdokumentasi.

## Gap / Peluang

- Relevan **hanya bila** ada jalur penjualan **B2B/proyek/wholesale** (di luar marketplace) yang butuh penawaran resmi. **TBD**: apakah Bharata punya kanal ini?
- Bila ada, quotation/proposal melengkapi [[ERPGo - Internal CRM (Leads & Deals)]] (deal → quotation → invoice).

## Rekomendasi

- **Adopsi bersyarat — prioritas rendah.** Tunggu konfirmasi adanya kanal B2B/wholesale.
- **Penempatan usulan** (bila jadi): dok konsep `Sales - Quotation & Proposal` di domain Marketing, ditaut ke CRM internal.
- Jika tidak ada kanal B2B → **skip**; jangan bangun fitur tanpa pemakai.

## Risiko & catatan jaga sistem berjalan

- Jangan tumpang-tindih dengan alur order marketplace yang sudah jalan ([[Sales - Marketplace Integration]], [[Microservices - Integration Service]]).
- Konversi ke invoice tetap lewat [[External - Accurate]], bukan akuntansi internal baru.

## Belum Diputuskan (TBD)

- Apakah ada kanal penjualan B2B/wholesale/proyek di luar marketplace? (penentu utama relevansi modul ini)

## Dokumen Terkait

- [[ERPGo - Overview & Gap Matrix]]
- [[ERPGo - Internal CRM (Leads & Deals)]]
- [[Microservices - Integration Service]] · [[Sales - Marketplace Integration]] · [[External - Accurate]]
