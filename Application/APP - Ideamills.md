## Deskripsi

*Implementasi teknis **Ideamills** — platform AI internal (satu app Next.js) untuk membuat video iklan pendek (TikTok/Instagram) dari foto produk → ide → prompt → image → video, dengan engine **Veo 3.1 (Google/Gemini)**. Satu repo, **dua alur**: **manual** (branch `main`, matang) dan **automation layer** (branch `automation-layer`, WIP). Konsep/bisnis tiap alur ada di [[Sales - Veo (Gemini) Implementation]] (manual) & [[Sales - Veo (Gemini) Automation Layer]] (automation).*

- **Stack**: Next.js 15 (App Router) + TypeScript + Tailwind/shadcn; MongoDB (raw driver + GridFS); worker proses (tsx, polling MongoDB sebagai queue) untuk render Veo. Automation: **LangGraph.js** (`@langchain/langgraph` + checkpoint MongoDB).
- **Path**: `ideamiils` (package `ideamills`)
- **Branch**: `main` (alur manual) · `automation-layer` (automation, **belum di-merge**, ±31 commit di depan `main`; folder `automation/` hanya ada di branch ini)
- **Auth**: terintegrasi **SSO bip-erp** (verifikasi/refresh JWT ke `api.bharatainternasional.com`) — lihat [[CORE - SSO Flow]]; per-user isolation via `employee_id`; bukan standalone
- **Status**: alur manual ✅ Implemented (matang); automation layer ⚠️ WIP (Fase 0 & 1A selesai; 1B/1C/2 belum)

## Engine AI (shared kedua alur)

- **Video: Veo 3.1 (Google Flow via useapi.net)** — image-to-video, extend (sambung dari frame terakhir klip sebelumnya), concatenate, upscale
- **Image: Imagen 4 / Nano Banana** (via useapi.net)
- **LLM: OpenRouter** (Gemini 2.5, Claude Sonnet 4.6, GPT-5, DeepSeek) — vision, ideasi, expand prompt, enhance Veo prompt
- **TikTok scraping: Apify** — riset referensi konten / discovery tren
- **Worker render Veo** — proses tsx polling MongoDB sebagai queue; dipakai bersama oleh alur manual & automation (automation `produce` enqueue ke worker yang sama)

## Alur Manual (branch `main`)

**Mode pembuatan**
- **Dari Nol**: upload foto produk + brief → analisis vision → 3–5 ide → pilih → expand prompt → preview image → video Veo
- **Quick Generate**: foto + pilih script dari Script Bank → langsung Veo (paling cepat/murah untuk produksi massal)

**UI / Halaman**
- `/studio` (Dari Nol + Quick, upload foto/Word doc), `/scripts` (Script Bank), `/assets` (galeri), `/history` + `/generations/[id]`, `/monitoring` (worker/queue/health), `/studio/concat` (gabung klip manual), `/chat`, `/scrape` (riset TikTok)

## Automation Layer (branch `automation-layer`)

Pipeline **otomatis** dari discovery tren sampai siap-kirim, dengan satu titik **persetujuan manusia (HITL)**. Path: `ideamiils/automation` (+ `worker/automation`, `app/automation`, `app/api/automation`). Orkestrasi via LangGraph:

```
START → discoverTrends → analyzeATM → ideate → produce → assemble → reviewStep
        reviewStep --approve--> publish → END
        reviewStep --revise--> ideate (loop)
        reviewStep --reject--> END
```

- **discoverTrends** — scrape tren TikTok (Apify) untuk niche/hashtag/kompetitor
- **analyzeATM** — *Amati-Tiru-Modifikasi*: analisis pola tren (hook, struktur, format, tone) via LLM (OpenRouter)
- **ideate** — buat ide + N `clipPrompts` (Veo prompt ter-enhance) + caption
- **produce** — enqueue render ke worker Veo (shared); idempotent agar aman di-resume
- **assemble** — concat klip jadi 1 video (`finalVideoUrl`); default `clipsPerVideo` = 3 (~24 detik)
- **reviewStep** — `interrupt()` untuk approval manusia → approve / revise / reject
- **publish** — "deliver": tandai siap diunggah manual (belum auto-publish)

Checkpoint state via LangGraph `MongoDBSaver`; `CampaignRuns` jadi proyeksi untuk UI.

**API** (`app/api/automation`): `campaigns`, `runs`, `runs/[id]`, `runs/[id]/approve`
**UI** (`/automation`): form campaign (niche/hashtags/kompetitor + produk), daftar runs (auto-refresh), review (preview video + Approve/Revise/Reject)
> `/automation` **belum masuk menu sidebar** (hanya via URL langsung) — konsisten dgn status WIP/unmerged.

**Status Fase**
- ✅ **Fase 0** — graph + semua node, runner, worker automation, API, UI, store campaigns/runs (lengkap dgn unit test)
- ✅ **Fase 1A** — multi-clip (`clipsPerVideo`, `clipPrompts`) + node `assemble` (concatenation)
- ⏳ **Fase 1B** — batch fan-out banyak produk + budget cap per campaign (`automation/scheduler.ts` belum ada)
- ⏳ **Fase 1C** — cron scheduler campaign jatuh tempo (`node-cron`)
- ⏳ **Fase 2** — auto-publish ke YouTube Shorts + notif Telegram (node `publish` masih *deliver-only stub*); publish langsung TikTok/Instagram tidak direncanakan (butuh app review)

## Penyimpanan

- MongoDB (raw driver) + **GridFS** untuk aset/video; checkpoint LangGraph (automation) di MongoDB

## Dokumen Terkait

- [[Sales - Veo (Gemini) Implementation]] — konsep/bisnis alur **manual**
- [[Sales - Veo (Gemini) Automation Layer]] — konsep/bisnis alur **automation**
- [[Sales - TikTok Sentiment Pipeline]] — sama-sama pakai Apify untuk discovery tren TikTok (terpisah)
- [[Sales - GMV Creative]]
- [[CORE - SSO Flow]] · [[CORE - API Master Gateway]]
