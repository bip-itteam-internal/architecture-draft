## Deskripsi

*TikTok Sentiment Pipeline (folder `scraping`) adalah tool intelijen kompetitor: **scrape komentar TikTok kompetitor → analisis sentimen + klasifikasi tema dengan Claude AI → simpan ke MongoDB**, lalu menyajikan dashboard insight (tema keluhan + ide produk). Berjalan otomatis tiap Senin pagi. Dipakai untuk riset konten/produk (kebutuhan R&D/marketing).*

- **Stack**: Python 3.11+ (FastAPI), Apify (scraping), Anthropic **Claude** (sentimen + sintesis insight), MongoDB; frontend Next.js 16 + React 19 + Tailwind v4 + Recharts
- **Path**: `scraping` (repo terpisah), branch `master`
- **Sifat**: **standalone/lokal** — MongoDB lokal (`localhost:27017`), API bind `127.0.0.1:8000` (tidak terekspos), **bukan** bagian dari bip-erp gateway
- **Status**: ✅ Implemented (Fase 1, 1.5, 1.6, 2a, 2b selesai)

## Cara Kerja / Pipeline

1. **Target** didefinisikan di `config/targets.yaml`: `accounts`, `videos`, `hashtags` + batas (`max_videos_per_account`, `max_videos_per_hashtag`, `max_comments_per_video`)
2. **Resolver** (`src/resolver.py` `VideoResolver`): akun → ambil N video terbaru; hashtag → ambil N video via Apify hashtag search (lebih luas & lebih mahal kredit)
3. **Scraper** (`src/scraper.py`): ambil komentar tiap video
4. **Sentiment Analyzer**: analisis sentimen + aspek per komentar via Claude
5. **Simpan** ke MongoDB + ekspor file
6. **Insight**: sintesis tema keluhan per produk + saran ide produk

Jadwal otomatis: **tiap Senin 08:00** via Windows Task Scheduler (`scripts/register_task.ps1`).

## Engine & Sumber Data

- **Apify actors**: `clockworks/tiktok-comments-scraper` (komentar), `clockworks/tiktok-scraper` (profil/video)
- **Model Claude**: `claude-haiku-4-5` untuk analisis sentimen; `claude-sonnet-4-6` untuk sintesis insight/ide produk
- **Klasifikasi tema** memakai *prompt repetition* (ulang prompt 2× untuk akurasi pengelompokan lebih baik, +13.7pp eval-driven; `docs/prompt-repetition.md`)

## Dashboard API (Fase 2a — FastAPI)

| Endpoint | Keterangan |
|---|---|
| `GET/PUT /api/targets` | Baca/tulis `config/targets.yaml` |
| `POST /api/scrape` | Jalankan scraping (tanpa analisis) |
| `POST /api/analyze` | Analisis sentimen pada komentar yang belum dianalisis |
| `GET /api/run/status`, `/api/runs` | Status job berjalan + riwayat run |
| `GET /api/comments` | Daftar komentar (filter target/sentimen, paginasi) |
| `GET /api/stats` | Distribusi sentimen, aspek teratas, tren per tanggal |
| `POST/GET /api/insights`, `/api/insights/products` | Sintesis & baca tema keluhan + ide produk per produk |
| `GET /api/export/raw.csv`, `/api/export/comments.csv` | Ekspor CSV |
| `GET /api/health` | Cek koneksi MongoDB |

## Dashboard Web (Fase 2b — Next.js)

- **Dashboard**: kartu ringkasan, distribusi sentimen per target, tren harian, aspek pujian/keluhan teratas, export CSV
- **StatusBar**: tombol Jalankan Scrape & Jalankan Analisis (dengan konfirmasi biaya), indikator status job (polling)
- **Target**: kelola akun/video/hashtag + batas → simpan ke `targets.yaml`
- **Komentar**: tabel + filter target/sentimen + paginasi + export
- **Insight & Ide Produk**: tema keluhan per produk (judul, frekuensi %, kutipan asli, saran ide produk) + export PDF

## Output & Penyimpanan

- `output/komentar_<run_id>.csv` — komentar + hasil analisis
- `output/ringkasan_<run_id>.md` — ringkasan per video/target
- MongoDB `tiktok_sentiment.comments` (komentar + analisis) & `tiktok_sentiment.runs` (log run)

## Catatan

- **Scrape & analyze sengaja dipisah** untuk kontrol biaya (kredit Apify + API Anthropic); **satu job dalam satu waktu**
- Tool ini **berbeda** dari scraping TikTok di [[Microservices - Integration Service]] — yang itu untuk **order/iklan marketplace** (Accurate bridging), sedangkan ini untuk **sentimen komentar kompetitor**
- Beririsan secara fungsi dengan riset tren konten di [[Sales - Veo (Gemini) Implementation]] (Ideamills) yang juga memakai Apify untuk discovery tren TikTok

## Dokumen Terkait

- [[Sales - GMV Creative]]
- [[Sales - Veo (Gemini) Implementation]]
- [[Sales - Dashboard]]
- [[Sales - Big Pictures]]
