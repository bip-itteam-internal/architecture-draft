> Status: ⚠️ **Implemented (ada catatan)** — situs publik + dashboard admin sudah berjalan; beranda modern & refresh visual sitewide SELESAI. Catatan: konten masih data demo, foto masih placeholder, dan `next build` masih terganjal typecheck file test (lihat *Belum Diimplementasikan / Catatan*).

## Deskripsi

*Website korporat **PT Bharata Internasional Pharmaceutical** — rebuild dari situs lama berbasis WordPress (`bharatainternasional.com`) menjadi aplikasi web custom. Tujuannya **bukan** transaksi/checkout, melainkan katalog/perkenalan produk, membangun kepercayaan (legalitas), dan — prioritas v1 — menjaring calon mitra/reseller/distributor termasuk ekspor. Pembelian konsumen diarahkan ke marketplace resmi.*

- **Repo**: `website-bharata` — **repo Git terpisah** (sibling di bawah `erp/`), **bukan** bagian dari `bip-erp`. Remote: `github.com/irfanarfianto/bharata-internasional`.
- **Package manager**: **pnpm** (workspaces). Bukan npm/yarn.
- Acuan bisnis: `website-bharata/PRD-Website-Bharata-Internasional.md` (v1.2).
- Pengguna: pengunjung/calon pelanggan, **calon mitra/reseller (prioritas)**, calon karyawan, admin konten, admin sistem.

## Tech Stack

- **Frontend**: Next.js 16 (App Router) + TypeScript + **Tailwind v4** (`@theme` design tokens) + **next-intl** (bilingual **ID/EN**, `localePrefix: as-needed`).
- **Dua app**: `apps/web` (publik, SSR/ISR → `bharata.co.id`) & `apps/admin` (dashboard di balik auth → `admin.bharata.co.id`). Tipe & API client bersama di `packages/shared`.
- **Backend**: Go + chi (router) + sqlc + pgx + goose (migrasi); berlapis handler → service → query. Target `api.bharata.co.id`.
- **Database**: PostgreSQL (dev via Docker Compose).
- **Test**: Vitest + Testing Library (frontend), Go `testing`/`httptest` (backend).
- **Identitas visual**: hijau-alami + aksen emas, font **Plus Jakarta Sans** (token brand di `apps/web/app/globals.css`).

## Arsitektur

- **Monorepo pnpm workspaces**: `apps/web`, `apps/admin`, `packages/shared`, `backend/`.
- Frontend mengonsumsi Go API yang sama lewat `@bharata/shared` (base URL dari `NEXT_PUBLIC_API_URL`). Auth admin pakai cookie JWT httpOnly lintas-subdomain (`Domain=.bharata.co.id`) + CORS `Allow-Credentials`.
- **Tidak terhubung** ke [[CORE - API Master Gateway]] / SSO bip-erp — sistem ini berdiri sendiri (backend & DB sendiri).

## Endpoint / Fitur (Sudah Diimplementasikan)

**Publik (tanpa auth)** — sumber: `backend/internal/http/router.go`:
- `GET /api/products` (`?kategori=&brand=`), `GET /api/products/{slug}`
- `GET /api/brands`, `GET /api/brands/{slug}`
- `GET /api/berita`, `GET /api/berita/{slug}`
- `GET /api/pages/{slug}` (halaman statis: Tentang, Kebijakan Privasi, dll.)
- `GET /api/lowongan`, `GET /api/lowongan/{slug}` (karir)
- `GET /api/settings` (kontak global, sosial, link marketplace footer)
- `POST /api/mitra`, `POST /api/kontak` (form + captcha Turnstile + notifikasi email)

**Auth & Admin** (cookie JWT): login/logout/forgot/reset; CRUD produk, brand, berita, pages, lowongan; kelola pendaftar mitra & pesan kontak (+ export CSV); pengaturan situs; manajemen pengguna (role admin/editor); upload foto (`/uploads/*`).

**Frontend `apps/web` (publik)** — halaman: beranda, produk + detail, merek, berita + detail, karir + detail, kemitraan (form mitra), kontak (form), tentang, kebijakan privasi.

**Modernisasi UI (SELESAI, sesi 2026-06-29):** beranda baru 7 section (Hero CTA "Jadi Mitra" → Tentang → Keunggulan/budaya → Produk → Legalitas → Berita → Kontak), Header (sticky + CTA + menu mobile) & Footer multi-kolom, sistem desain token (`components/ui/*`), bilingual ID/EN, placeholder gambar.

## Belum Diimplementasikan / Catatan

- **Konten masih demo** — produk/berita/settings belum diisi data final (`data-template/*.csv` masih `[CONTOH]`); teks manfaat & no. BPOM menunggu persetujuan regulatori (gerbang anti-klaim ilegal).
- **Foto masih placeholder** SVG ber-brand di `apps/web/public/images/` — diganti aset final.
- **`next build` typecheck** gagal pada file `*.test.tsx` (matcher jest-dom tak ter-type saat tsc berjalan); perlu exclude test dari typecheck build. (Vitest sendiri hijau.)
- Roadmap PRD P1/P2: pencarian produk, lokasi reseller, testimoni, alur approval konten regulatori, audit log, retargeting/live chat.

## Dependensi & Integrasi

- **Backend Go + PostgreSQL** (in-repo) — sumber data utama.
- **Cloudflare Turnstile** (anti-spam form), **email transaksional** (notifikasi lead), **Google Analytics 4** (statistik).
- Berbeda & terpisah dari sistem bip-erp; **tidak** memakai [[CORE - SSO Flow]] maupun [[CORE - API Master Gateway]].

## Dokumen Terkait

- [[Sales - Landing page]] — *konsep berbeda* (landing konversi penjualan ala Nike / WhatsApp-CS), **bukan** project website korporat ini.
- [[Sales - Big Pictures]]
