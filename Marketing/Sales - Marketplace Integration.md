## Deskripsi

*Konsep (sisi Marketing) integrasi **marketplace** ke ERP — menghubungkan **TikTok Shop & Shopee** (juga TikTok Business/Ads) untuk menyinkronkan order/penjualan & performa iklan, lalu menjembatani ke akuntansi. Implementasi back-end-nya sudah ada di [[Microservices - Integration Service]].*

- **Status**: ✅ Implemented (backend) — dok ini melengkapi sisi konsep/bisnis yang sebelumnya belum ada
- **Implementasi**: [[Microservices - Integration Service]] (Go) + modul Integration di [[APP - Web Application]]

## Latar Belakang

- Tim marketing berjualan di banyak marketplace dengan banyak akun/toko → data order, penjualan, dan iklan tersebar di tiap platform.
- Dibutuhkan satu integrasi yang menarik & menormalkan data ke ERP, lalu meneruskannya ke finance.

## Cakupan / Fitur (business view)

- **Koneksi akun/toko marketplace** — OAuth TikTok Shop, Shopee, TikTok Business/Ads; kelola kredensial per toko
- **Sinkronisasi order/penjualan** → model **transaksi terpadu** (unified) lintas marketplace
- **Performa iklan/GMV** — laporan GMV Max (TikTok), GMS (Shopee); berkaitan dengan [[Sales - Dashboard]] (ads/omnichannel) & [[Sales - GMV Creative]]
- **Bridge ke akuntansi** — ringkasan transaksi → **Accurate** (Sales Invoice/Return); lihat [[Finance - Bridging App]] & [[External - Accurate]]
- **Webhook event order** — ingest via middleware [[External - Desty]]
- **Marketing team + shop ACL** — kontrol akses toko per tim marketing
- **Automasi** auto-ship/auto-approve (sadar hari libur)
- **Master & item catalog** marketplace (mapping produk ke Accurate)

## Konsumen Data

- [[Microservices - Insentive Service]] — menarik data iklan (TikTok GMV-Max, Shopee GMS) untuk perhitungan insentif marketing ([[Sales - Incentive]])
- [[Sales - Dashboard]] — visualisasi ads/omset per toko

## Catatan

- **Lazada** baru placeholder di kode (belum ada client) — lihat catatan di [[Microservices - Integration Service]]
- Pembeda: integrasi ini untuk **order/penjualan & akuntansi marketplace**, berbeda dari [[Sales - TikTok Sentiment Pipeline]] (sentimen komentar kompetitor) dan [[Sales - Veo (Gemini) Implementation]] (produksi konten)
## Kendala

- **Rate limit Shopee Ads API** — sync harian jam **02:00 WIB** menumpuk semua call di **burst ~2–4 detik** (paralel lintas toko: maks 3 toko × 5 request), sehingga **daily call limit kepukul** sebelum semua toko ter-sync. Observasi 2026-06-20…22: **~50% call gagal `429 error_limit`** (item GMS 50%, campaign GMS ~57% sukses) → data performa (GMS item/campaign) tidak lengkap. Diperparah token **shop-scoped** (1 call/toko) dan jumlah toko terus bertambah (8 toko saat ini). Detail metrik + surat permintaan kenaikan limit: [[LOG - Shopee API Rate Limit Request]].

## Dokumen Terkait

- [[Microservices - Integration Service]] (implementasi)
- [[Microservices - TikTok Shop Service]] (penerima callback/webhook TikTok)
- [[Finance - Bridging App]] · [[External - Accurate]]
- [[Sales - Dashboard]] · [[Sales - GMV Creative]] · [[Sales - Incentive]]
- [Referensi API Integration Service — docs-api-greget](https://docs-api-greget.vercel.app/)
