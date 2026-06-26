## Deskripsi

*Konsep (sisi Marketing) **intelijen kompetitor** berbasis komentar TikTok: mendengarkan suara pelanggan/penonton di konten kompetitor untuk menemukan **tema keluhan** dan **ide produk** sebagai bahan riset konten & R&D. Implementasi teknisnya (FastAPI + dashboard Next.js) ada di [[APP - Tiktok Insight Analyzer]].*

- **Status**: ✅ Implemented — berjalan otomatis tiap awal pekan
- **Implementasi**: [[APP - Tiktok Insight Analyzer]] (folder `scraping`, Python/FastAPI + Next.js)

## Latar Belakang

- Tim R&D/marketing butuh sinyal pasar yang murah & cepat dari kompetitor — apa yang dikeluhkan & diinginkan penonton di konten mereka.
- Mengumpulkan komentar manual lambat dan tidak terukur → dibutuhkan pipeline otomatis yang merangkum sentimen + tema jadi insight yang bisa ditindaklanjuti.

## Nilai / Insight (business view)

- **Distribusi sentimen** per target (akun/video/hashtag kompetitor) + tren dari waktu ke waktu.
- **Aspek pujian & keluhan teratas** — apa yang disukai/dikeluhkan penonton.
- **Tema keluhan per produk** (judul, frekuensi %, kutipan asli) + **saran ide produk** sebagai input R&D.
- Dipakai untuk arah konten & pengembangan produk; **keputusan tetap di manusia** (AI memberi rangkuman, bukan eksekutor).

## Posisi vs Dokumen Lain

- **Berbeda** dari scraping TikTok di [[Microservices - Integration Service]] — yang itu untuk **order/iklan marketplace** (Accurate bridging); ini untuk **sentimen komentar kompetitor**.
- **Beririsan** secara fungsi dengan riset tren konten di [[Sales - Veo (Gemini) Implementation]] (Ideamills) yang juga memakai Apify untuk discovery tren TikTok.

## Dokumen Terkait

- [[APP - Tiktok Insight Analyzer]] — implementasi (pipeline, API, dashboard)
- [[Sales - GMV Creative]]
- [[Sales - Veo (Gemini) Implementation]]
- [[Sales - Dashboard]]
- [[Sales - Big Pictures]]
