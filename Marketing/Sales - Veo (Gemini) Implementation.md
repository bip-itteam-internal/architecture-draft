
## Latar Belakang

saat ini kebutuhan konten iklan di adv sangat besar dan sangat mengandalkan editor (Designer dan Video/Photo Editor). Alangkah indahnya jika pembuatan konten dibantu AI dari sisi editing. Bisa hanya sebatas IDE hingga editing. Upaya serupa sudah pernah dijalankan namun hasil masih jauh dari harapan. 

## Isu yang Diketahui
1. Hasil generate masih sangat terlihat terbuat dari AI dan belum natural
2. Aspek didalam konten yang secara spesifik ingin dirubah belum akurat
3. Implementasi AI pada konten iklan belum ada yang bisa dijadikan acuan. karena konten iklan yang ada diplatform biasanya masih konvensional. Masih tingginya persepsi negatif soal konten AI. Hal ini bisa diatasi apabila implementasi AI hanya di sisipkan dalam sebuah konten, bukan sebuah pokok dari konten. 
4. Ide yang kreatif masih menjadi pokok utama dalam pembuatan konten

## Implementasi: Ideamills (Veo / Gemini)

*Konsep di atas kini diwujudkan oleh **Ideamills** — platform AI internal untuk membuat video iklan pendek (TikTok/Instagram) dari foto produk → ide kreatif → prompt → image → video. Engine video memakai **Veo 3.1 (Google/Gemini)**, bukan Sora.*

- **Stack**: Next.js 15 (App Router) + TypeScript + Tailwind/shadcn; MongoDB (raw driver + GridFS); 3 worker proses (tsx, polling MongoDB sebagai queue); automation pakai LangGraph (+ checkpoint MongoDB)
- **Path**: `ideamiils` (package `ideamills`), branch `automation-layer`
- **Auth**: terintegrasi **SSO bip-erp** (verifikasi/refresh JWT ke `api.bharatainternasional.com`) — lihat [[CORE - SSO Flow]]; bukan standalone
- **Status**: ✅ Implemented (manual app matang; automation layer WIP)

**Engine AI (sudah ter-wire)**
- **Video: Veo 3.1 (Google Flow via useapi.net)** — image-to-video, extend (sambung dari frame terakhir klip sebelumnya), concatenate, upscale
- **Image: Imagen 4 / Nano Banana** (via useapi.net)
- **LLM: OpenRouter** (Gemini 2.5, Claude Sonnet 4.6, GPT-5, DeepSeek) untuk vision, ideasi, expand prompt, enhance Veo prompt, analisis pola
- **TikTok scraping: Apify** (trend/competitor/audience)

**Mode pemakaian**
- **Dari Nol**: upload foto produk + brief → analisis vision → 3–5 ide → pilih → expand prompt → preview image → video Veo
- **Quick Generate**: foto + pilih script dari Script Bank → langsung Veo (paling cepat/murah untuk produksi massal)
- **Automation campaign** (baru, WIP): pipeline otomatis berbasis LangGraph

**Pipeline Automation (LangGraph)**
`discoverTrends` (scrape TikTok) → `analyzeATM` (Amati-Tiru-Modifikasi pola tren) → `ideate` (ide + N `clipPrompts`) → `produce` (enqueue + tunggu render Veo) → `assemble` (concat klip jadi 1 video) → `reviewStep` (approval manusia / HITL) → `publish` (deliver). Default `clipsPerVideo` = 3 (~24 detik).

**UI / Halaman**: `/studio` (Dari Nol + Quick, upload foto/Word doc), `/scripts` (Script Bank), `/assets` (galeri), `/history` + `/generations/[id]`, `/monitoring` (worker/queue/health), `/studio/concat` (gabung klip manual), `/chat`, `/automation` (campaign + review). *Catatan: `/automation` belum masuk menu sidebar.*

**Belum Diimplementasikan / Roadmap**
- **Fase 1B**: batch fan-out banyak produk + budget cap per campaign (`automation/scheduler.ts` belum ada)
- **Fase 1C**: cron scheduler untuk campaign jatuh tempo (`node-cron`)
- **Fase 2**: auto-publish ke YouTube Shorts + notifikasi Telegram (node `publish` sekarang masih *deliver-only stub*)
- Publish langsung ke TikTok/Instagram tidak direncanakan (butuh app review platform)
- Pipeline lama (tech-spec L0–L5, 50-angle) sudah dihapus; worker hanya menerima payload v2 Studio

## Referensi
* Form Requirement : https://docs.google.com/spreadsheets/d/1GleSHDjYmOSL6BNrgNZ6M_A9DktdzCGZTqgo-qGZgkI/edit?usp=drive_link
* Result : https://drive.google.com/drive/folders/1euadg8k0A7rI2wryTtVxjSZIS9DkhpBp?usp=sharing

## Dokumen Terkait
- [[Sales - GMV Creative]]
- [[Microservices - Integration Service]]
- [[CORE - SSO Flow]]
- [[CORE - API Master Gateway]]