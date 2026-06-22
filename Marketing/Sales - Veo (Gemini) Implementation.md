
## Latar Belakang

saat ini kebutuhan konten iklan di adv sangat besar dan sangat mengandalkan editor (Designer dan Video/Photo Editor). Alangkah indahnya jika pembuatan konten dibantu AI dari sisi editing. Bisa hanya sebatas IDE hingga editing. Upaya serupa sudah pernah dijalankan namun hasil masih jauh dari harapan. 

## Isu yang Diketahui
1. Hasil generate masih sangat terlihat terbuat dari AI dan belum natural
2. Aspek didalam konten yang secara spesifik ingin dirubah belum akurat
3. Implementasi AI pada konten iklan belum ada yang bisa dijadikan acuan. karena konten iklan yang ada diplatform biasanya masih konvensional. Masih tingginya persepsi negatif soal konten AI. Hal ini bisa diatasi apabila implementasi AI hanya di sisipkan dalam sebuah konten, bukan sebuah pokok dari konten. 
4. Ide yang kreatif masih menjadi pokok utama dalam pembuatan konten

## Implementasi: Ideamills — Pembuatan Video Manual (branch `main`)

*Konsep di atas diwujudkan oleh **Ideamills** — platform AI internal untuk membuat video iklan pendek (TikTok/Instagram) dari foto produk → ide kreatif → prompt → image → video. Engine video memakai **Veo 3.1 (Google/Gemini)**, bukan Sora. Dokumen ini mencakup alur **manual** (branch `main`); alur otomatis ada di [[Sales - Veo (Gemini) Automation Layer]].*

- **Stack**: Next.js 15 (App Router) + TypeScript + Tailwind/shadcn; MongoDB (raw driver + GridFS); worker proses (tsx, polling MongoDB sebagai queue) untuk render Veo
- **Path**: `ideamiils` (package `ideamills`), branch **`main`**
- **Auth**: terintegrasi **SSO bip-erp** (verifikasi/refresh JWT ke `api.bharatainternasional.com`) — lihat [[CORE - SSO Flow]]; bukan standalone
- **Status**: ✅ Implemented (matang)

**Engine AI (sudah ter-wire)**
- **Video: Veo 3.1 (Google Flow via useapi.net)** — image-to-video, extend (sambung dari frame terakhir klip sebelumnya), concatenate, upscale
- **Image: Imagen 4 / Nano Banana** (via useapi.net)
- **LLM: OpenRouter** (Gemini 2.5, Claude Sonnet 4.6, GPT-5, DeepSeek) untuk vision, ideasi, expand prompt, enhance Veo prompt
- **TikTok scraping: Apify** (riset referensi konten)

**Mode pembuatan (manual)**
- **Dari Nol**: upload foto produk + brief → analisis vision → 3–5 ide → pilih → expand prompt → preview image → video Veo
- **Quick Generate**: foto + pilih script dari Script Bank → langsung Veo (paling cepat/murah untuk produksi massal)

**UI / Halaman**
- `/studio` (Dari Nol + Quick, upload foto/Word doc), `/scripts` (Script Bank), `/assets` (galeri), `/history` + `/generations/[id]`, `/monitoring` (worker/queue/health), `/studio/concat` (gabung klip manual), `/chat`, `/scrape` (riset TikTok)

## Referensi
* Form Requirement : https://docs.google.com/spreadsheets/d/1GleSHDjYmOSL6BNrgNZ6M_A9DktdzCGZTqgo-qGZgkI/edit?usp=drive_link
* Result : https://drive.google.com/drive/folders/1euadg8k0A7rI2wryTtVxjSZIS9DkhpBp?usp=sharing

## Dokumen Terkait
- [[Sales - Veo (Gemini) Automation Layer]] — alur otomatis (branch `automation-layer`)
- [[Sales - GMV Creative]]
- [[CORE - SSO Flow]]
- [[CORE - API Master Gateway]]
