## Latar Belakang

saat ini kebutuhan konten iklan di adv sangat besar dan sangat mengandalkan editor (Designer dan Video/Photo Editor). Alangkah indahnya jika pembuatan konten dibantu AI dari sisi editing. Bisa hanya sebatas IDE hingga editing. Upaya serupa sudah pernah dijalankan namun hasil masih jauh dari harapan. 

## Isu yang Diketahui
1. Hasil generate masih sangat terlihat terbuat dari AI dan belum natural
2. Aspek didalam konten yang secara spesifik ingin dirubah belum akurat
3. Implementasi AI pada konten iklan belum ada yang bisa dijadikan acuan. karena konten iklan yang ada diplatform biasanya masih konvensional. Masih tingginya persepsi negatif soal konten AI. Hal ini bisa diatasi apabila implementasi AI hanya di sisipkan dalam sebuah konten, bukan sebuah pokok dari konten. 
4. Ide yang kreatif masih menjadi pokok utama dalam pembuatan konten

## Konsep: Ideamills — Pembuatan Video Manual

*Konsep di atas diwujudkan oleh **Ideamills** — platform AI internal untuk membuat video iklan pendek (TikTok/Instagram) dari foto produk → ide kreatif → prompt → image → video. Dokumen ini mencakup alur **manual** (operator menyetir tiap langkah); alur otomatis ada di [[Sales - Veo (Gemini) Automation Layer]]. Implementasi teknis (stack, engine, mode, UI) ada di [[APP - Ideamills]].*

- **Status**: ✅ Implemented (matang)
- **Nilai**: mempercepat produksi konten iklan & mengurangi beban editor; **AI membantu, ide kreatif tetap pokok** (AI disisipkan dalam konten, bukan pengganti konsep)
- **Engine video**: **Veo 3.1 (Google/Gemini)**, bukan Sora

## Referensi
* Form Requirement : https://docs.google.com/spreadsheets/d/1GleSHDjYmOSL6BNrgNZ6M_A9DktdzCGZTqgo-qGZgkI/edit?usp=drive_link
* Result : https://drive.google.com/drive/folders/1euadg8k0A7rI2wryTtVxjSZIS9DkhpBp?usp=sharing

## Dokumen Terkait
- [[APP - Ideamills]] — implementasi (stack, engine, mode manual, UI)
- [[Sales - Veo (Gemini) Automation Layer]] — alur otomatis (branch `automation-layer`)
- [[Sales - GMV Creative]]
- [[CORE - SSO Flow]]
- [[CORE - API Master Gateway]]
