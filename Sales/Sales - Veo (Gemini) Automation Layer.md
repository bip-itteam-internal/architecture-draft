## Deskripsi

*Konsep **Automation Layer** dari [[Sales - Veo (Gemini) Implementation|Ideamills]] — alih-alih operator menyetir tiap langkah (alur manual), pipeline **otomatis** membuat video iklan dari **penemuan tren TikTok** sampai **siap-kirim**, dengan satu titik **persetujuan manusia (HITL)**. Engine video tetap **Veo 3.1 (Google/Gemini)**. Implementasi teknis (pipeline LangGraph, fase, API/UI) ada di [[APP - Ideamills]].*

- **Status**: ⚠️ WIP — sebagian alur sudah jalan, sebagian belum (rincian fase di [[APP - Ideamills]])

## Konsep & Nilai

- **Dari tren → konten otomatis**: sistem menemukan tren TikTok yang relevan (niche/hashtag/kompetitor), lalu mengubahnya jadi ide + video — mengurangi kerja manual ideasi & produksi.
- **Pendekatan ATM (Amati-Tiru-Modifikasi)**: pola tren yang menang (hook, struktur, format, tone) dianalisis lalu dimodifikasi untuk produk sendiri — bukan menyalin mentah.
- **Human-in-the-loop (HITL)**: ada satu titik **review manusia** (approve / revise / reject) sebelum konten dianggap siap — kualitas & brand-safety tetap dijaga manusia.
- **Siap-kirim, belum auto-publish**: hasil ditandai siap untuk diunggah; publikasi langsung ke platform belum termasuk (lihat fase di [[APP - Ideamills]]).

## Dokumen Terkait

- [[APP - Ideamills]] — implementasi (pipeline LangGraph, status fase, API/UI)
- [[Sales - Veo (Gemini) Implementation]] — konsep alur manual (fondasi)
- [[Sales - GMV Creative]]
- [[Sales - TikTok Sentiment Pipeline]] — sama-sama discovery tren TikTok via Apify (terpisah)
- [[CORE - SSO Flow]]
