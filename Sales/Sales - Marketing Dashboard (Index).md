# Marketing Dashboard Analysis

- **Status**: 🟡 Konsep — indeks dok desain "Marketing & Ads Command Center"; keputusan di [[ADR - 0008 Profit Engine Join via item_group_id]] & [[ADR - 0009 Affiliate via Search Seller Affiliate Orders API]].

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
[[Microservices - Integration Service]] · [[Sales - GMV Creative]] · [[ADR - 0008 Profit Engine Join via item_group_id]] · [[ADR - 0009 Affiliate via Search Seller Affiliate Orders API]]
