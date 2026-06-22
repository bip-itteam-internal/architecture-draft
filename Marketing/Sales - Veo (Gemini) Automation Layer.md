## Deskripsi

*Automation Layer dari **Ideamills** — pipeline **otomatis** yang membuat video iklan dari penemuan tren TikTok sampai siap-kirim, dengan satu titik **persetujuan manusia (HITL)**. Ini kelanjutan dari alur manual di [[Sales - Veo (Gemini) Implementation]]; engine video tetap **Veo 3.1 (Google/Gemini)**.*

- **Stack**: Next.js 15 + TypeScript (UI/API) + **LangGraph.js** (`@langchain/langgraph` + checkpoint MongoDB) untuk orkestrasi; worker `worker/automation` (polling MongoDB)
- **Path**: `ideamiils/automation` (+ `worker/automation`, `app/automation`, `app/api/automation`)
- **Branch**: **`automation-layer`** — **belum di-merge ke `main`** (±31 commit di depan main; folder `automation/` hanya ada di branch ini)
- **Status**: ⚠️ WIP — Fase 0 & 1A selesai; Fase 1B/1C/2 belum

## Pipeline Automation (LangGraph)

```
START → discoverTrends → analyzeATM → ideate → produce → assemble → reviewStep
        reviewStep --approve--> publish → END
        reviewStep --revise--> ideate (loop)
        reviewStep --reject--> END
```

- **discoverTrends** — scrape tren TikTok (via Apify) untuk niche/hashtag/kompetitor
- **analyzeATM** — *Amati-Tiru-Modifikasi*: analisis pola tren (hook, struktur, format, tone) via LLM (OpenRouter)
- **ideate** — buat ide + N `clipPrompts` (Veo prompt yang sudah di-enhance) + caption
- **produce** — enqueue render ke worker Veo yang sama dengan alur manual, lalu tunggu hasil (tidak memanggil Veo langsung; idempotent agar aman di-resume)
- **assemble** — concat klip jadi 1 video (`finalVideoUrl`); default `clipsPerVideo` = 3 (~24 detik)
- **reviewStep** — `interrupt()` untuk approval manusia → approve / revise / reject
- **publish** — "deliver": tandai siap untuk diunggah manual (belum auto-publish)

Checkpoint state disimpan via LangGraph `MongoDBSaver`; `CampaignRuns` jadi proyeksi untuk UI.

## API & UI

**API** (`app/api/automation`): `campaigns`, `runs`, `runs/[id]`, `runs/[id]/approve`
**UI** (`/automation`): form campaign (niche/hashtags/kompetitor + produk), daftar runs (auto-refresh), review (preview video + Approve/Revise/Reject)
> Catatan: `/automation` **belum masuk menu sidebar** (hanya via URL langsung) — konsisten dgn status WIP/unmerged.

## Status Fase

- ✅ **Fase 0** — graph + semua node, runner, worker automation, API, UI, store campaigns/runs (lengkap dgn unit test)
- ✅ **Fase 1A** — multi-clip (`clipsPerVideo`, `clipPrompts`) + node `assemble` (concatenation)
- ⏳ **Fase 1B** — batch fan-out banyak produk + budget cap per campaign (`automation/scheduler.ts` belum ada)
- ⏳ **Fase 1C** — cron scheduler campaign jatuh tempo (`node-cron`)
- ⏳ **Fase 2** — auto-publish ke YouTube Shorts + notif Telegram (node `publish` masih *deliver-only stub*); publish langsung TikTok/Instagram tidak direncanakan (butuh app review)

## Dependencies & Integrasi

- **Engine & worker Veo** dari alur manual — lihat [[Sales - Veo (Gemini) Implementation]] (produce node enqueue ke worker render yang sama)
- **Apify** — sumber discovery tren TikTok (mirip namun terpisah dari [[Sales - TikTok Sentiment Pipeline]])
- **OpenRouter** (LLM) untuk analyzeATM & ideate
- **Auth**: SSO bip-erp ([[CORE - SSO Flow]]); per-user isolation via `employee_id`

## Dokumen Terkait

- [[Sales - Veo (Gemini) Implementation]]
- [[Sales - GMV Creative]]
- [[Sales - TikTok Sentiment Pipeline]]
- [[CORE - SSO Flow]]
