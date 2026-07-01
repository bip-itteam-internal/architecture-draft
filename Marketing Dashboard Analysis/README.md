# Marketing Dashboard Analysis

Analisis + spec untuk membangun dashboard **Marketing & Ads Command Center** (mockup `10_DASH_MARKETING_ADS.html`) di service `integration` + `erp-frontend`. Semua temuan tervalidasi **data produksi nyata** (mongosh read-only) / **dok resmi TikTok**.

> Dok teknis (spec/plan) — copy dari `docs/superpowers/` repo bip-erp. Keputusan arsitektur diringkas di [[ADR - 0008 Profit Engine Join via item_group_id]] & [[ADR - 0009 Affiliate via Search Seller Affiliate Orders API]] (folder Decisions).

## Isi

- [[2026-07-01-marketing-dashboard-ANALISIS-REKAP]] — **INDEX, baca dulu** (9 poin + scope + blocker)
- [[2026-06-30-marketing-dashboard-MASTER]] — roadmap 8 scope + 9 engine + strategi join + affiliate
- [[2026-06-30-profit-engine-design]] — spec profit engine + HPP master
- [[2026-06-30-hpp-master-plan]] — plan implementasi HPP (field cost + upload xlsx)
- [[2026-06-30-affiliate-seller-sync-design]] — spec affiliate auto-sync (API, bukan CSV)
- [[2026-07-01-affiliate-seller-sync-plan]] — plan implementasi affiliate (7 task; token via GetOrRefreshToken)
- [[Affiliate integration]] — dok resmi TikTok (endpoint + onboarding)
- [[TikTok Shop Affiliate(Creator Collaboration)Developer onboarding & termination Rules]] — dok resmi TikTok (aturan onboarding)

## Terkait
[[Microservices - Integration Service]] · [[Sales - GMV Creative]] · [[ADR - 0008 Profit Engine Join via item_group_id]] · [[ADR - 0009 Affiliate via Search Seller Affiliate Orders API]]
