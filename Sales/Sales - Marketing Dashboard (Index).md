# Marketing Dashboard Analysis

- **Status**: 🟡 **Arsip desain (Juni–Juli 2026) — bukan peta arsitektur yang berlaku.** Rencana di sini **sudah dieksekusi**, tetapi pada arsitektur yang berbeda dari yang ditulisnya. Untuk keadaan sekarang baca [[Microservices - Marketing Analytics Service]] & [[API - Marketing Analytics Service]] lebih dulu. Keputusan: [[ADR - 0008 Profit Engine Join via item_group_id]] & [[ADR - 0009 Affiliate via Search Seller Affiliate Orders API]].

> ⛔ **Jangan memakai dokumen ini untuk memutuskan di mana kode ditaruh.** Ia menulis "service `integration` + `erp-frontend`" dan "progress ≈ 45–50%"; dua-duanya sudah tidak benar sejak Agustus 2026:
>
> - **Lapisan marketing & ads jadi service tersendiri**, `marketing-analytics` (Go + Fiber, database `marketing_analytics_db`, koleksi `mart_*`), bukan bagian `integration`. 40 route, live di PROD. Lihat [[Microservices - Marketing Analytics Service]].
> - **Profit engine + HPP memang mendarat di `integration`**, sebagai layar `/integration/gross-profit` ([[APP - Web ERP]], backend [[API - Integration Service]] rute `/profit/*`). Jadi rencana ini **pecah dua**, tidak batal.
> - Frontend-nya `/marketing-analytics/*` (16 halaman), bukan satu halaman `10_DASH_MARKETING_ADS.html`.
>
> Yang **masih berguna** dari berkas ini: audit sumber data lima sisi, strategi join, dan aturan affiliate TikTok — semuanya tervalidasi ke data produksi saat itu dan tak digantikan oleh dokumen mana pun. Yang **sudah usang**: peta service, persentase progres, dan daftar "gap inti".

Analisis + spec untuk membangun dashboard **Marketing & Ads Command Center** (mockup `10_DASH_MARKETING_ADS.html`) di service `integration` + `erp-frontend`. Semua temuan tervalidasi **data produksi nyata** (mongosh read-only) / **dok resmi TikTok**.

> Dok teknis (spec/plan) — copy dari `docs/superpowers/` repo bip-erp. Keputusan arsitektur diringkas di [[ADR - 0008 Profit Engine Join via item_group_id]] & [[ADR - 0009 Affiliate via Search Seller Affiliate Orders API]] (folder Decisions).

## Isi

- [[Sales - Marketing Dashboard (Analisis Rekap)]] — **INDEX, baca dulu** (9 poin + scope + blocker)
- [[Sales - Marketing Dashboard (Master Roadmap)]] — roadmap 8 scope + 9 engine + strategi join + affiliate
- [[Sales - Profit Engine (Design)]] — spec profit engine + HPP master
- [[Sales - HPP Master (Plan)]] — plan implementasi HPP (field cost + upload xlsx)
- [[Sales - Affiliate Seller Sync (Design)]] — spec affiliate auto-sync (API, bukan CSV)
- [[Sales - Affiliate Seller Sync (Plan)]] — plan implementasi affiliate (7 task; token via GetOrRefreshToken)
- [[Sales - Affiliate Integration (TikTok Docs)]] — dok resmi TikTok (endpoint + onboarding)
- [[Sales - TikTok Affiliate Rules (Docs)]] — dok resmi TikTok (aturan onboarding)

## Terkait

**Keadaan sekarang (baca ini lebih dulu):** [[Microservices - Marketing Analytics Service]] · [[API - Marketing Analytics Service]] · [[Sales - Marketing Analytics (Audit Ketersediaan Data)]] · [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]]

**Konteks asal:** [[Microservices - Integration Service]] · [[Sales - GMV Creative]] · [[ADR - 0008 Profit Engine Join via item_group_id]] · [[ADR - 0009 Affiliate via Search Seller Affiliate Orders API]]
