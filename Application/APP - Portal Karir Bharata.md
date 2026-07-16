> Status: ⚠️ **Implemented (ada catatan)** — portal berjalan penuh terhadap BE dev (browse → detail → lamar + upload berkas → cek status; **E2E terverifikasi live 2026-07-16**). BE penopang **semua sudah deployed**. **Belum go-live**: belum ada remote Git, domain, maupun deploy portal; halaman legal masih draf; production 0 lowongan (lihat *Belum Diimplementasikan / Catatan*).

## Deskripsi

*Portal karir publik **PT Bharata Internasional Pharmaceutical** — situs tanpa login tempat pelamar melihat lowongan, mengirim lamaran (satu berkas PDF gabungan), dan mengecek status lamarannya. Menggantikan alur **Google Form** lama HRD: lamaran langsung masuk pipeline [[Microservices - Recruitment Service]] sehingga HR tak perlu memindahkan data manual. Target domain: **`career.bharatainternasional.com`**.*

- **Repo**: `career-bharata` — **repo Git terpisah** (sibling di bawah `erp/`), **bukan** bagian dari `bip-erp`. **Belum ada remote** — commit lokal di branch `master` (🟡 TBD: buat repo GitHub).
- **Package manager**: **pnpm** (`pnpm@10.25.0`). Bukan npm/yarn.
- **Stack**: Next.js **16.2.10** (App Router) + React **19.2.4** + TypeScript strict + **Tailwind v4**; form `react-hook-form` + `zod`; HTML rich-text disanitasi `isomorphic-dompurify`.
- **Backend**: **tidak punya BE sendiri** — sepenuhnya mengonsumsi `/public/recruitment/*` bip-erp lewat [[CORE - API Master Gateway]] (**tanpa JWT/SSO**). Base URL dari env `NEXT_PUBLIC_RECRUITMENT_API`.
- Pengguna: **pelamar/publik** (tanpa akun). Sisi HR memakai [[APP - Web ERP]]; konsep/keputusan HRD di [[HRIS - Recruitment]].

> **Bedakan dari [[APP - Website Bharata Internasional]]** — situs korporat itu punya halaman karir sendiri (`/api/lowongan`, BE Go + PostgreSQL sendiri, konten diinput admin). Portal ini **terpisah**, sumber datanya **pipeline ATS bip-erp** (requisition → posting → candidate). 🟡 TBD: apakah halaman karir situs korporat nanti diarahkan ke portal ini (hindari dua sumber lowongan).

## Arsitektur

- **Server Components** untuk fetch data (list/detail/track, `cache: "no-store"`); **Client Components** hanya untuk interaksi (form lamar, filter, modal WASPADA, input token).
- Semua akses BE disentralkan di `src/lib/recruitment-api.ts` (tipe `PostingListItem`/`PostingView`/`ApplyDTO`/`TrackView` + fungsi `listPostings`/`getPosting`/`apply`/`track`, native `fetch`). Detail/track → `null` bila 404 → `notFound()`.
- **Deploy: Docker standalone** (`output: "standalone"` + `Dockerfile` 2-stage + `docker-compose.yml` + `.dockerignore`) — **pola disamakan dengan `erp-frontend`** (2026-07-16): `.env` **ikut masuk image** (bukan `--build-arg`) karena `NEXT_PUBLIC_*` di-inline saat `next build`; compose punya healthcheck/restart/logging. **Guard**: build **digagalkan** bila `.env` tak ada (tanpa itu kode jatuh ke fallback URL **dev** → portal production salah alamat senyap). ⚠️ image masih **belum divalidasi** (Docker daemon mati saat uji). **Base API production = `https://api.bharatainternasional.com/public/recruitment`** (gateway di VPS Biznet, terverifikasi 200) — **bukan** `10.10.10.121` internal.

## Halaman / Fitur (Sudah Diimplementasikan)

Sumber: `career-bharata/src/app/`.

- **`/` — Landing**: hero (background `/hero/pixel.jpg` + overlay gradien gelap, teks putih) **disatukan dengan daftar lowongan** (anchor `#lowongan`, komponen `careers/jobs-browser.tsx`: pencarian + filter klien). Muncul **modal "WASPADA"** anti-penipuan rekrutmen saat pertama membuka landing (pola serupa portal karir Pertamina) — implementasi `useSyncExternalStore` agar aman SSR.
- **`/lowongan/[slug]` — Detail lowongan**: satu baris **judul + tombol "Lamar Sekarang"** (tombol tidak terkubur di bawah), sub-judul = **jenis pekerjaan** (dari master `job_types`) + jumlah posisi; di bawah tombol: keterangan **"Sebelum tanggal {deadline}"** (bulan disingkat, `timeZone: "UTC"` agar tanggal deadline tak bergeser ke H+1). Isi: deskripsi/persyaratan/benefit (HTML disanitasi) + section **Penempatan** di paling bawah. **Tanpa** badge status, badge skill, atau departemen (keputusan UI: bukan info yang dicari pelamar).
- **`/lowongan/[slug]/lamar` — Form lamaran** (halaman sendiri, bukan modal): field **native model `candidate`** (nama_lengkap, email, no_hp, jenis_kelamin, tanggal_lahir, alamat, pendidikan, ipk, pengalaman, expected_salary, dll) — **bukan** form-builder `custom_question`; + **upload satu berkas PDF gabungan (maks 10 MB)** → dikirim `multipart/form-data`. Sukses → tampil `tracking_token` + tautan ke `/status/[token]`.
- **`/status` & `/status/[token]` — Cek status lamaran**: input token → tampilan curated (progress/status label + stepper) dari `GET /public/recruitment/track/:token`.
- **`/syarat-penggunaan` & `/kebijakan-privasi`** — halaman legal (komponen bersama `legal-page.tsx`), ditautkan di footer.
- **Shared**: `Header` (**sticky**, logo `/logo/logo.png` "Winning Team Bharata") · `SiteFooter` · `SectionShell` (Container) · `components/form/fields.tsx` — field reusable (`TextField`/`TextareaField`/`SelectField`/`DateField`/`FileField`, RHF-compatible, wajib ditandai **asterisk merah**).

## Kontrak BE yang Dipakai

Detail: [[API - Recruitment Service]] §Publik.

| Endpoint | Dipakai di |
|---|---|
| `GET /public/recruitment/postings` | landing (`#lowongan`) |
| `GET /public/recruitment/postings/:slug` | `/lowongan/[slug]` (`:id` menerima **slug** ATAU ObjectID) |
| `POST /public/recruitment/apply` (**multipart**: `data` JSON + `berkas` PDF) | `/lowongan/[slug]/lamar` |
| `GET /public/recruitment/track/:token` | `/status/[token]` |

**Gotcha kontrak:** `posisi_dilamar` **wajib** dikirim (server tidak mengisinya dari `posting_id`); `tanggal_lahir` **RFC3339**; nilai enum casing **persis** BE (mis. `jenis_kelamin` "Laki-laki"/"Perempuan"). Lamaran sukses → kandidat menerima **email otomatis** "Lamaran Anda Telah Kami Terima" (✅ terverifikasi live) via [[Microservices - Notification Service]].

## Belum Diimplementasikan / Catatan

- **Belum go-live**: belum ada **remote Git**, domain, maupun deploy portal. Image Docker **belum divalidasi** (Docker daemon mati saat pengujian). Production gateway juga perlu deploy agar CORS origin portal (PR #460) aktif di sana.
- **BE penopang: ✅ semua deployed & terverifikasi live di dev (2026-07-16)** — slug, job_type dari master, upload berkas (E2E multipart → `cv_object` → HR preview PDF valid), email kandidat (nama pengirim via `RECRUITMENT_EMAIL_FROM`, env sudah diset user). Tak ada lagi yang menunggu deploy BE.
- **Production 0 lowongan** — 5 lowongan hanya di **dev** (seed). Requisition → approve → posting harus dibuat dari nol di production sebelum portal menampilkan apa pun.
- **Halaman legal masih draf** — perlu review pihak berwenang sebelum publish.
- **`pnpm dev` rusak di path ber-spasi** (`c:\Data utama\...`): Turbopack panic "Next.js package not found"; `next dev --webpack` → `ENOENT .next/browser/default-stylesheet.css` (500 di route dinamis). **Preview andal = `pnpm build` lalu `pnpm start`**. Bukan bug kode portal.
- `public/hero/pixel.jpg` **±2,9 MB** — perlu dioptimasi sebelum go-live.
- **Tanpa captcha/anti-spam** dan tanpa rate-limit sisi portal (gateway `/public` sudah rate-limited) — pertimbangkan Turnstile sebelum publik.
- **Nol konten Herbalife**: portal ini dibangun **bersih** dari nol; scaffold clone lama (`ai-website-cloner-template`) **ditinggalkan**, hanya pola/token yang diadopsi ulang.
- Lowongan **pra-PR #448 tidak punya `slug`** → tak muncul dengan URL slug; posting baru aman.

## Dependensi & Integrasi

- [[Microservices - Recruitment Service]] — sumber data lowongan & muara lamaran (`/public/recruitment/*`).
- [[CORE - API Master Gateway]] — jalur akses publik (grup `/public`, rate-limited, **tanpa** [[CORE - SSO Flow]]).
- [[Microservices - Notification Service]] — email otomatis ke kandidat (Resend).
- **MinIO** — berkas lamaran PDF disimpan BE di `recruitment/cv/<candidate_id>/berkas.pdf` (portal hanya mengunggah).
- [[APP - Web ERP]] — sisi HR (kelola requisition/posting/kandidat) atas data yang sama.

## Dokumen Terkait

- [[HRIS - Recruitment]] — konsep/bisnis & keputusan HRD
- [[API - Recruitment Service]] · [[Microservices - Recruitment Service]]
- [[APP - Website Bharata Internasional]] — situs korporat (halaman karir terpisah, sumber data berbeda)
