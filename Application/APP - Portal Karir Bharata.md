> Status: ⚠️ **Implemented (ada catatan)** — portal berjalan penuh terhadap BE dev (browse → detail → lamar + upload berkas; **E2E terverifikasi live 2026-07-16**). ⛔ **Fitur "cek status lamaran" SUDAH DIHAPUS** (BE `a298ba70`, 2026-07-24; portal tak punya rute `/status` — diverifikasi 2026-09-10). BE penopang **semua sudah deployed**. **SUDAH GO-LIVE**: repo GitHub ada, domain `career.bharatainternasional.com` aktif, dan portal **ter-deploy di prod VPS Biznet sejak 2026-08-02** (balas `200`). Yang masih tersisa: halaman legal masih draf (dan per perusahaan grup masih **TBD**, lihat [[HRIS - Recruitment]] §Rekrutmen Lintas Perusahaan), dan **production 0 lowongan** — `GET /public/recruitment/postings` balas `200 []`, jadi portalnya hidup tapi kosong sampai HR menerbitkan lowongan (lihat *Belum Diimplementasikan / Catatan*). ✅ **Nama perusahaan perekrut di daftar & detail lowongan: live prod sejak 2026-09-12 08:45 WIB** ([#12](https://github.com/bip-itteam-internal/career-bharata/pull/12); diukur 09:44 WIB: checkout prod `6032152`, `company_name` di bundel 3 berkas, sebelumnya 0). Deploy yang sama ikut membawa psikotes berpaket #10 dan #11.

## Deskripsi

*Portal karir publik **grup Bharata**, situs tanpa login tempat pelamar melihat lowongan, mengirim lamaran (satu berkas PDF gabungan), dan **mengerjakan psikotes lewat magic link** (Kraepelin, dan sejak 2026-09-11 tes berpaket CFIT, DISC, Kraepelin; merged lewat #10, live prod 2026-09-12). **Satu portal melayani lowongan SELURUH perusahaan grup** (bukan cuma PT Bharata Internasional Pharmaceutical/BIP): sejak rekrutmen lintas perusahaan (live prod 2026-09-12, lihat [[HRIS - Recruitment]] §Rekrutmen Lintas Perusahaan), lowongan bisa dibuka atas nama perusahaan grup mana pun, dan nama perusahaan perekrutnya (`company_name`) tampil di daftar maupun detail lowongan supaya pelamar tahu ia melamar ke perusahaan yang mana. Menggantikan alur **Google Form** lama HRD: lamaran langsung masuk pipeline [[Microservices - Recruitment Service]] sehingga HR tak perlu memindahkan data manual. Target domain: **`career.bharatainternasional.com`**.*

- **Repo**: `career-bharata` — **repo Git terpisah** (sibling di bawah `erp/`), **bukan** bagian dari `bip-erp`. Remote: `github.com/bip-itteam-internal/career-bharata`, branch utama **`master`** (bukan `main` — `origin/HEAD` menunjuk ke sana).
- **Package manager**: **pnpm** (`pnpm@10.25.0`). Bukan npm/yarn.
- **Stack**: Next.js **16.2.10** (App Router) + React **19.2.4** + TypeScript strict + **Tailwind v4**; form `react-hook-form` + `zod`; HTML rich-text disanitasi `isomorphic-dompurify`.
- **Backend**: **tidak punya BE sendiri** — sepenuhnya mengonsumsi `/public/recruitment/*` bip-erp lewat [[CORE - API Master Gateway]] (**tanpa JWT/SSO**). Base URL dari env `NEXT_PUBLIC_RECRUITMENT_API`.
- Pengguna: **pelamar/publik** (tanpa akun). Sisi HR memakai [[APP - Web ERP]]; konsep/keputusan HRD di [[HRIS - Recruitment]].

> **Bedakan dari [[APP - Website Bharata Internasional]]** — situs korporat itu punya halaman karir sendiri (`/api/lowongan`, BE Go + PostgreSQL sendiri, konten diinput admin). Portal ini **terpisah**, sumber datanya **pipeline ATS bip-erp** (requisition → posting → candidate). 🟡 TBD: apakah halaman karir situs korporat nanti diarahkan ke portal ini (hindari dua sumber lowongan).

## Arsitektur

- **Server Components** untuk fetch data (list/detail, `cache: "no-store"`); **Client Components** hanya untuk interaksi (form lamar, filter, modal WASPADA).
- Semua akses BE disentralkan di `src/lib/recruitment-api.ts` (tipe `PostingListItem`/`PostingView`/`ApplyDTO` + fungsi `listPostings`/`getPosting`/`apply`, native `fetch`). Detail → `null` bila 404 → `notFound()`. *(`TrackView`/`track` sudah tidak ada — ikut terhapus bersama fitur tracking.)*
- **Deploy: Docker standalone** (`output: "standalone"` + `Dockerfile` 2-stage + `docker-compose.yml` + `.dockerignore`) — **pola disamakan dengan `erp-frontend`** (2026-07-16): `.env` **ikut masuk image** (bukan `--build-arg`) karena `NEXT_PUBLIC_*` di-inline saat `next build`; compose punya healthcheck/restart/logging. **Guard**: build **digagalkan** bila `.env` tak ada (tanpa itu kode jatuh ke fallback URL **dev** → portal production salah alamat senyap). ✅ image **sudah divalidasi di produksi** (build + jalan, 2026-08-02). **Base API production = `https://api.bharatainternasional.com/public/recruitment`** (gateway di VPS Biznet, terverifikasi 200) — **bukan** `10.10.10.121` internal.

> [!warning] Compose di server SENGAJA berbeda satu baris dari repo
> Repo memetakan `3011:3011`, sedangkan prod sudah memakai **port host 3005** dan yang merutekan domain publik menunjuk ke sana. Compose di server karena itu dipatok **`3005:3011`** — port host mengikuti prod, port container mengikuti `ENV PORT=3011` di Dockerfile. Memakai compose lama apa adanya (`3005:3000`) akan menghasilkan container hidup tapi **tak ada yang mendengarkan di sisi dalam**.
>
> Sekalian dua jebakan saat deploy pertama ke prod: (1) `docker-compose.yml` kini **ter-track di repo** sedangkan server memegang versi lokal, jadi `git pull` berhenti dengan sendirinya — file lama harus disingkirkan lebih dulu, **jangan** dipaksa dengan reset/clean karena isinya konfigurasi prod; (2) nama service berubah `career` → `career-portal` sementara `container_name` tetap, sehingga compose menganggap container lama **orphan** dan bentrok nama. Container lama harus dihapus dulu, dan itu berarti ada jeda singkat.

## Halaman / Fitur (Sudah Diimplementasikan)

Sumber: `career-bharata/src/app/`.

- **`/` — Landing**: hero (background `/hero/pixel.jpg` + overlay gradien gelap, teks putih) **disatukan dengan daftar lowongan** (anchor `#lowongan`, komponen `careers/jobs-browser.tsx`: pencarian + filter klien). Muncul **modal "WASPADA"** anti-penipuan rekrutmen saat pertama membuka landing (pola serupa portal karir Pertamina) — implementasi `useSyncExternalStore` agar aman SSR. ✅ **Sub-judul tiap baris kini diawali nama perusahaan perekrut** (live prod 2026-09-12 lewat #12): `[job.company_name, job.job_type, jumlah posisi].filter(Boolean)` di `jobs-browser.tsx`, perusahaan paling depan karena satu portal kini memuat lowongan beberapa perusahaan grup sekaligus.
- **`/lowongan/[slug]` — Detail lowongan**: satu baris **judul + tombol "Lamar Sekarang"** (tombol tidak terkubur di bawah), sub-judul = **jenis pekerjaan** (dari master `job_types`) + jumlah posisi; di bawah tombol: keterangan **"Sebelum tanggal {deadline}"** (bulan disingkat, `timeZone: "UTC"` agar tanggal deadline tak bergeser ke H+1). Isi: deskripsi/persyaratan/benefit (HTML disanitasi) + section **Penempatan** di paling bawah. **Tanpa** badge status, badge skill, atau departemen (keputusan UI: bukan info yang dicari pelamar). 🟡 Sub-judul juga diawali `posting.company_name` sejak branch di atas, dengan alasan sama.
- **`/lowongan/[slug]/lamar` — Form lamaran** (halaman sendiri, bukan modal): field **native model `candidate`** (nama_lengkap, email, no_hp, jenis_kelamin, tanggal_lahir, alamat, pendidikan, ipk, pengalaman, expected_salary, dll) — **bukan** form-builder `custom_question`; + **upload satu berkas PDF gabungan (maks 10 MB)** → dikirim `multipart/form-data`. Sukses → redirect ke **`/lowongan/[slug]/lamar/sukses`**.
- **`/lowongan/[slug]/lamar/sukses` — Konfirmasi terkirim**: menyebut posisi yang dilamar, memberi tahu konfirmasi sudah dikirim ke email, satu tombol "Lihat Lowongan Lain", plus peringatan rekrutmen **tidak dipungut biaya**. **Tanpa token, tanpa nomor lamaran** — pelamar tak punya cara memeriksa kemajuan lamarannya sendiri; satu-satunya kontak balik adalah tim rekrutmen menghubunginya.
- **`/psikotes/[token]`: mengerjakan psikotes** (`components/psikotes/`: `mesin-tes.tsx`, `ledger-kolom.tsx`, `sapaan.tsx`, `tes-sudah-selesai.tsx`; `lib/psikotes/mesin.ts`). Dibuka kandidat **tanpa login**, dijaga token di URL. Rincian Kraepelin: **[[HRIS - Psikotes Kraepelin]]**.
	- **Tes berpaket (2026-09-11, career-bharata #10 merged `15240242`, belum prod)**: sesi ber-`jenis: "paket"` masuk `alur-paket.tsx` (ringkasan, petunjuk per bagian, kerja, jeda) dengan rel perjalanan `rel-paket.tsx`. Bagian pilihan ganda lewat `mesin-subtes.tsx` + `kerja-pilihan-ganda.tsx` (gambar `gambar-soal.tsx` ber-`key` per gambar, pintasan A sampai F dan Enter, preload gambar soal ini dan dua berikutnya), DISC lewat `kerja-disc.tsx` (radio asli), Kraepelin memakai `MesinTes` yang sama dengan fungsi kirim per bagian. Hitung mundur mengikuti batas mutlak dari sisa detik server (`lib/psikotes/use-hitung-mundur.ts`); jawaban dikirim berurutan di latar dengan retry (`AntreanJawab` di `lib/psikotes/paket.ts`). Muat ulang melanjutkan dari posisi yang dicatat server. Rincian: [[HRIS - Bank Soal dan Paket Psikotes]].
	- **Revisi layar kandidat (2026-09-11, branch `feat/psikotes-revisi-kandidat`, belum merged)**: `sapaan.tsx` menampilkan lowongan, telepon, dan email yang **sudah disamarkan server**. Semua label tahap lewat `labelTahap`/`labelBagian` (`lib/psikotes/paket.ts`), tanpa nama tes. Soal contoh sebelum soal asli: `contoh-pilihan-ganda.tsx` (dari `POST .../subtes/:s/contoh`), `contoh-disc.tsx` dan `contoh-kraepelin.tsx` (bawaan portal); opsi dan grup kata dipakai bersama contoh dan soal asli (`grid-opsi.tsx`, `grid-disc.tsx`). `kerja-pilihan-ganda.tsx` punya nomor soal, Sebelumnya/Berikutnya, Ragu-ragu (localStorage per token), dan konfirmasi Selesaikan bagian; `kerja-disc.tsx` punya Sebelumnya; pintasan huruf dan Enter di `lib/psikotes/use-pintasan-opsi.ts`. `AntreanJawab` tetap mengirim berurutan, kini supaya jawaban **terakhir** yang tersimpan saat soal dijawab ulang, dan memberi tahu pemanggil saat kiriman menyerah (`onMenyerah`) supaya jawaban itu dikirim ulang. Kapan contoh dilewati (subtes atau tahap yang sudah berjalan) diputuskan fungsi murni `keContohSubtes`, `contohBawaan`, dan `contohSubtesTunggal` beserta test. Kolom angka tetap maju saja.
	- ⚠️ **Inilah halaman yang dibuka kandidat di prod.** `ERP_FRONTEND_URL` di container `Recruitment-Service` prod berisi `https://career.bharatainternasional.com` (dibaca 2026-09-10), jadi magic link di email mengarah ke portal ini walau nama variabelnya menyebut erp-frontend. Implementasi kedua di `erp-frontend` (`src/app/psikotes/[token]` + `src/features/psikotes/`) masih ada dan kemungkinan besar tidak disentuh kandidat prod; keputusan resmi mana yang dipertahankan belum ada.
	- **Halaman tersembunyi = tes berakhir.** `mesin-tes.tsx` memanggil `/abandon` lewat `sendBeacon` **seketika** saat `visibilitychange → hidden` (pindah tab, peramban diminimalkan, layar ponsel terkunci, telepon masuk) atau `pagehide`. Disengaja, karena Kraepelin mengukur ketahanan di bawah tekanan waktu tak terputus. Harganya jatuh paling berat pada pengerja di ponsel, sementara satu-satunya peringatan soal ponsel ada di email (anjuran memakai komputer); layar petunjuk tidak menyebut aturan ini. Beacon ini juga bisa berbalapan dengan `/finish` selama layar "menyimpan", karena penanda selesai baru dipasang sesudah `/finish` sukses; **(T0, bip-erp #1828)** hanya penutup yang memenangkan balapan yang menulis Hasil Tes.
	- ⚠️ **Tautan yang tidak berlaku.** Sebelum T0, `recruitment-api.ts` hanya membaca `message` dari badan galat psikotes (BE mengirim `error`), sehingga kandidat melihat "Permintaan gagal (404)" dengan tombol Coba Lagi yang tak akan berhasil. **(T0, career-bharata #9, merged 2026-09-10 `77bfafc5`; portal ini tidak ada di VM dev; layarnya naik di prod 2026-09-11 08.44 WIB dan terbukti di Chrome hari itu (token acak menampilkan "Tautan tes ini sudah tidak berlaku." tanpa Coba Lagi). Kontrak yang dipetakannya sudah terbukti di gateway dev hari itu: token acak → `404 {"error": "sesi tes tidak ditemukan"}`, sesi selesai → `410 {"error": "sesi tes sudah selesai"}`)** Galat dipetakan di satu fungsi murni `galatPsikotes`: 404 → layar "Tautan tes ini sudah tidak berlaku" **tanpa** Coba Lagi (`components/psikotes/tautan-tidak-berlaku.tsx`), 410 → layar tes sudah selesai (tidak berubah, kalimatnya netral untuk sesi tuntas maupun terputus), 4xx lain → pesan `error` lalu `message`, jaringan putus/5xx → kalimat umum + Coba Lagi. Pemetaannya dijaga `pnpm check` dan verifikasi manual. **Sejak 2026-09-11 (#10)** repo punya vitest untuk fungsi murni di `src/lib` (`lib/psikotes/paket.test.ts`), dan `pnpm check` = lint + typecheck + test + build; komponen tetap diverifikasi lewat build dan uji di peramban.
- ⛔ **`/status` & `/status/[token]` SUDAH TIDAK ADA.** Rute itu pernah didokumentasikan di sini, tapi `career-bharata/src/app/` sekarang memuat `/`, `/lowongan/[slug]`, `/lowongan/[slug]/lamar`, `/lowongan/[slug]/lamar/sukses`, `/psikotes/[token]`, `/syarat-penggunaan`, `/kebijakan-privasi` (diverifikasi ke `origin/master` 2026-09-10). BE-nya juga sudah dihapus — lihat [[API - Recruitment Service]] §Publik.
- **`/syarat-penggunaan` & `/kebijakan-privasi`** — halaman legal (komponen bersama `legal-page.tsx`), ditautkan di footer.
- **Shared**: `Header` (**sticky**, logo `/logo/logo.png` "Winning Team Bharata") · `SiteFooter` · `SectionShell` (Container) · `components/form/fields.tsx` — field reusable (`TextField`/`TextareaField`/`SelectField`/`DateField`/`FileField`, RHF-compatible, wajib ditandai **asterisk merah**).

## Kontrak BE yang Dipakai

Detail: [[API - Recruitment Service]] §Publik.

| Endpoint | Dipakai di |
|---|---|
| `GET /public/recruitment/postings` | landing (`#lowongan`) |
| `GET /public/recruitment/postings/:slug` | `/lowongan/[slug]` (`:id` menerima **slug** ATAU ObjectID) |
| `POST /public/recruitment/apply` (**multipart**: `data` JSON + `berkas` PDF) | `/lowongan/[slug]/lamar` |
| `GET /public/recruitment/psikotes/:token` + `POST .../start`, `.../columns/:index`, `.../finish`, `.../abandon`; tes berpaket (2026-09-11): `POST .../bagian/:b/{mulai,kolom/:index,selesai}`, `POST .../bagian/:b/subtes/:s/{mulai,jawab,selesai}`, `GET .../gambar/:nama`; *(revisi, branch belum merged)* `POST .../bagian/:b/subtes/:s/contoh` | `/psikotes/[token]` |

`GET /public/recruitment/track/:token` **tidak lagi dipakai dan tidak lagi ada di BE**. Rutenya dibuang dari gateway di bip-erp #1824 (merged 2026-09-10): sudah hilang dari gateway dev dan prod (prod sejak 2026-09-11).

**Gotcha kontrak:** `posisi_dilamar` **wajib** dikirim (server tidak mengisinya dari `posting_id`; divalidasi lebih dulu, `services/recruitment/models_candidate.go:131`); `tanggal_lahir` **RFC3339**; nilai enum casing **persis** BE (mis. `jenis_kelamin` "Laki-laki"/"Perempuan"). Lamaran sukses → kandidat menerima **email otomatis** "Lamaran Anda Telah Kami Terima" (✅ terverifikasi live) via [[Microservices - Notification Service]].

⚠️ **`posting_id` sendiri kini JUGA wajib** (backend live prod 2026-09-12 lewat bip-erp #1853,
diverifikasi `services/recruitment/public_handlers.go`: `POST /apply` membalas `400 {"error":
"posting_id wajib diisi"}` bila kosong, `400 {"error": "posting_id tidak valid"}` bila bukan
ObjectID). Sebelum branch ini `posting_id` opsional (lamaran tanpa `posting_id` sah, kandidatnya
tanpa perusahaan tujuan yang jelas); sesudahnya WAJIB karena **perusahaan kandidat diturunkan
dari lowongannya, tak pernah dari header/body** (rute `/public` tak lewat `ValidateJWT`, jadi
header `BIP-*` di sini bisa dikarang siapa pun). `career-bharata` sudah mengikuti: tipe
`ApplyDTO.posting_id` di `src/lib/recruitment-api.ts` berubah dari opsional jadi wajib, dan portal
selalu mengirimnya (form lamaran selalu dibuka dari halaman detail satu lowongan). Ini **dua**
field wajib yang berbeda perannya: `posisi_dilamar` teks bebas untuk keperluan HR/MPP,
`posting_id` yang menentukan perusahaan tujuan.

## Belum Diimplementasikan / Catatan

- ✅ **Sudah live di prod** (terukur 2026-09-11): container `career-bharata` di VPS Biznet (`~/apps/career-bharata`, remote `bip-itteam-internal/career-bharata`, branch `master`), port host `3005`, dan `career.bharatainternasional.com` melayani halaman psikotes. Catatan lama "belum go-live, belum ada remote/domain/deploy" sudah tidak berlaku.
- **BE penopang: ✅ semua deployed & terverifikasi live di dev (2026-07-16)** — slug, job_type dari master, upload berkas (E2E multipart → `cv_object` → HR preview PDF valid), email kandidat (nama pengirim via `RECRUITMENT_EMAIL_FROM`, env sudah diset user). Tak ada lagi yang menunggu deploy BE.
- **Production 0 lowongan** — 5 lowongan hanya di **dev** (seed). Requisition → approve → posting harus dibuat dari nol di production sebelum portal menampilkan apa pun.
- **Halaman legal masih draf** — perlu review pihak berwenang sebelum publish. 🟡 **Legal per perusahaan grup: TBD.** `/syarat-penggunaan` dan `/kebijakan-privasi` (`legal-page.tsx`) SATU untuk seluruh portal, tak dibedakan per perusahaan perekrut walau satu portal kini melayani lowongan beberapa perusahaan grup; keputusan user "satu portal" tidak menjawab siapa pengendali data pelamar per perusahaan. Belum ada rencana kode untuk ini; dicatat sebagai TBD di [[HRIS - Recruitment]] §Rekrutmen Lintas Perusahaan, bukan diimplementasikan.
- 🟡 **Filter perusahaan di landing: belum ada.** `jobs-browser.tsx` menampilkan nama perusahaan per baris (lihat di atas) tapi tak menawarkan filter berdasarkan perusahaan; belum diminta.
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

- [[HRIS - Recruitment]] — konsep/bisnis & keputusan HRD, termasuk §Rekrutmen Lintas Perusahaan
- [[API - Recruitment Service]] · [[Microservices - Recruitment Service]]
- [[APP - Website Bharata Internasional]] — situs korporat (halaman karir terpisah, sumber data berbeda)
- [[ADR - 0092 Rekrutmen Lintas Perusahaan lewat Paket Izin]] (live prod 2026-09-12)
