**Status**: ✅ Implemented — live sejak 2026-08-04, terisi 3 bulan data (5.629 commit kerja, 1.719 PR).

## Deskripsi

*Papan peringkat aktivitas developer se-organisasi GitHub `bip-itteam-internal`, diperbarui seketika lewat webhook. Dibuat sebagai cermin bersama untuk evaluasi diri, bukan alat pengawasan.*

- **Stack**: TypeScript · Cloudflare Workers · D1 (SQLite) · Durable Object
- **Repo**: `bip-itteam-internal/dev-activity-board` (repo terpisah, **bukan** bagian bip-erp)
- **Path dok internal**: `docs/spec/` (desain) · `docs/plan/` (rencana) · `docs/pasang-webhook.md`
- **URL**: `https://dev-activity-board.bharataitteam.workers.dev/<DASHBOARD_SLUG>`
- **Akun**: Cloudflare `bharataitteam@gmail.com` (akun bersama tim, bukan pribadi)
- **Status**: ✅ Implemented

Penyimpangan arsitekturnya disengaja dan dicatat di [[ADR - 0034 Papan Aktivitas Developer di Luar Arsitektur ERP]].

## Fitur (Sudah Diimplementasikan)

**Tabel**
- **Per developer** — commit, pemisahan kode vs dokumentasi, baris +/−, PR merged, review diberikan, lead time (median), hari aktif, tren, repo utama. Kolom bisa diurutkan.
- **Per repo** — commit, porsi, baris, PR merged, kontributor, aktivitas terakhir. Repo dokumentasi ditandai terpisah.
- **Per service di bip-erp** — kepemilikan komponen: pemegang, porsinya, jumlah kontributor. Komponen yang hanya disentuh satu orang ditandai.

**Grafik**
- Sebaran jam (WIB) dengan pita jam kerja 08.00–16.00
- Sebaran hari, akhir pekan dibedakan

**Periode**: Hari ini · 7 hari · 30 hari · 90 hari. Semuanya bergulir dan berakhir hari ini, bukan minggu/bulan kalender. Tiap baris menampilkan selisih terhadap periode sepanjang itu tepat sebelumnya.

**Realtime**: webhook organisasi (`push`, `pull_request`, `pull_request_review`) → verifikasi HMAC → simpan → Durable Object menyiarkan ke semua tab lewat WebSocket. Perpindahan peringkat dianimasikan.

**Cron tiap 15 menit**: melengkapi angka baris dan komponen commit, lalu menyapu ulang 24 jam terakhir untuk menambal webhook yang tidak sampai.

## Aturan Perhitungan (penting saat membaca angkanya)

- **Hanya branch integrasi** (`main`, `master`, `dev`, `develop`, `development`, `staging`) yang dicatat. Commit di branch fitur sengaja tidak dihitung; kalau ikut dihitung lalu PR-nya di-squash saat merge, kerja yang sama terhitung dua kali.
- **Merge commit tidak dihitung** sebagai commit kerja maupun baris.
- **Review ke PR sendiri tidak dihitung** sebagai kolaborasi.
- **Semua tanggal dan jam dalam WIB** (UTC+7), bukan UTC.
- **Rollup selalu dihitung ulang dari data mentah**, tidak pernah ditambah-nambahkan, supaya satu peristiwa yang terproses dua kali tidak menggelembungkan angka permanen.
- **Judul commit tidak pernah disimpan**, karena halamannya dibuka lewat tautan publik.

## Temuan dari Data (per 2026-08-04)

Angka-angka ini yang memicu pembuatan sistemnya, dan tetap relevan sebagai catatan kondisi:

- **Review kode praktis tidak berjalan**: 38 dari 1.702 PR (2,2%) pernah di-review orang lain; 22 PR punya komentar.
- **90% PR di-merge oleh penulisnya sendiri**, median 2,2 menit dari dibuka sampai merged. PR di sini berfungsi sebagai catatan perubahan, bukan gerbang mutu.
- **Keluaran terpusat**: dua orang menyumbang 72,4% seluruh commit.
- **39,5% commit di luar jam kerja** 08.00–16.00, dan **23,3% di akhir pekan**. Sabtu hampir setiap minggu ada yang bekerja.
- **10 dari 28 komponen bip-erp hanya disentuh satu orang** dalam 30 hari, termasuk `procurement` (125 commit) dan `marketing-analytics` (93 commit).
- **Lima repo dipegang satu orang saja**, termasuk `my-bharata` (382 commit) yang merupakan aplikasi presensi seluruh karyawan.

## Loop otonom (ingest dari mesin developer, 2026-09-07)

Kode ada di `main` sejak 2026-09-07 (PR #1 `feat/loop-ingest`, di-merge manusia). Ia menambah `POST /loop/ingest` dan bagian **Loop otonom** di papan: sesi Claude Code yang berjalan (aktif / basi lebih dari 24 jam / selesai), brief 30 hari dengan verdict judge terakhir dan nomor PR. Sumbernya hook agent-kit ≥ 1.17.0 di tiap mesin developer, **opt-in** lewat `~/.agent-kit/loop-ingest.json`.

- **Auth menulis**: HMAC-SHA256 (`X-Loop-Signature-256`) dengan rahasia `LOOP_INGEST_SECRET`; rahasia belum dipasang = 503 mati tertutup. **Membaca tetap lewat tautan** (ADR 0034 §3); yang berubah hanya sisi tulis. Ini jawaban atas TBD ADR 0034 "perlu autentikasi bila data lebih sensitif".
- **Privasi**: mengikuti §4 (judul commit tidak disimpan), judul brief, teks task, dan judul PR **tidak pernah dikirim maupun disimpan**; yang tampil hanya id hash slug, tahap, status, repo, domain, nomor PR, dan nama orang hasil pemetaan `identity_alias` (email tak terpetakan dipotong di `@`).
- **Best-effort**: timeout 3 detik, gagal senyap dengan jeda 10 menit setelah 3 kegagalan, lalu satu baris peringatan di konteks sesi. Papan yang sepi bisa berarti ingest belum dinyalakan, bukan tidak ada yang bekerja; dashboard lokal `/dashboard` tetap sumber yang tidak butuh jaringan.
- **Menghidupkan** (pemegang akun Cloudflare): `pnpm db:remote` → `wrangler secret put LOOP_INGEST_SECRET` (atau `wrangler secret bulk <berkas.json>`, bebas jebakan newline) → **`pnpm run deploy`** → bagikan `url` + `secret` ke tiap dev. Urutan tercatat di README repo. ⚠️ Harus **`pnpm run deploy`**: `pnpm deploy` telanjang adalah perintah bawaan pnpm untuk workspace dan gagal `ERR_PNPM_CANNOT_DEPLOY` (terjadi 2026-09-07, dua langkah sebelumnya sudah sukses). Merge **bukan** deploy: worker hanya berubah lewat perintah itu dari mesin yang login ke akun Cloudflare tim.
- **Mengukur sudah hidup atau belum** (jangan disimpulkan dari tanggal merge): `GET /loop/ingest` membalas **405** bila kode baru sudah naik dan **404** bila worker masih versi lama; `POST` tanpa tanda tangan membalas **503** bila rahasia belum dipasang dan **401** bila sudah. Dihidupkan 2026-09-07 (versi worker `ff35af77`): sebelum deploy 404, sesudahnya 405 dan 401.

## Belum Diimplementasikan / Catatan

- **Tanpa autentikasi.** Akses lewat tautan berpotongan URL acak panjang; itu bukan autentikasi, hanya membuat alamatnya tidak gampang ditemukan. Keputusan sadar, lihat ADR.
- **Tanpa panel admin.** Pemetaan alias identitas diubah lewat `wrangler d1 execute`.
- **Force-push atau rebase** yang menghapus commit lebih dari 24 jam lalu meninggalkan baris yatim; penyapuan hanya berwenang atas 24 jam terakhir.
- **Repo yang diganti nama** tercatat sebagai dua repo sampai aliasnya dibetulkan manual.
- **Daftar berkas per commit dibatasi GitHub pada 300**; commit yang menyentuh lebih dari itu kehilangan sebagian komponennya.
- **Kepemilikan komponen hanya untuk `bip-erp`.** Repo lain tidak dipetakan ke komponen.
- **TBD**: peringatan otomatis (mis. saat sebuah komponen jatuh ke satu penyentuh) belum ada; sekarang hanya ditampilkan di halaman.

## Batasan yang Wajib Disebut Saat Memakai Angkanya

Jumlah commit dan baris mengukur **volume**, bukan dampak, kesulitan, atau mutu. Perancangan, pendampingan rekan, penanganan insiden, review lisan, dan dukungan pengguna tidak meninggalkan jejak di Git sama sekali. Beberapa peran akan tampak kecil di papan ini padahal tidak.

Waktu commit diambil dari `committedDate`, dan rebase atau squash saat merge **menulis ulang waktu itu**. Bacalah sebaran jam sebagai pola kasar, bukan absensi.

**Jangan dipakai sebagai dasar tunggal penilaian karyawan.**

## Dependensi & Integrasi

- **GitHub organisasi `bip-itteam-internal`** — sumber seluruh data, lewat webhook organisasi + REST/GraphQL API. Webhook dipasang oleh akun `BIP-ITTeam`, satu-satunya pemilik organisasi.
- **Cloudflare** — Workers, D1, Durable Object. Di luar infrastruktur perusahaan; lihat ADR.
- Tidak menyentuh [[CORE - API Master Gateway]], tidak memakai SSO, tidak menyentuh database ERP mana pun.

## Dokumen Terkait

- [[ADR - 0034 Papan Aktivitas Developer di Luar Arsitektur ERP]] — alasan penyimpangan arsitekturnya
- [[IT - Development Apps and Tools]] — daftar tool internal
- [[IT - Big Pictures]] — peta domain IT
- [[IT - CI-CD]] — alur deploy repo lain (papan ini deploy-nya terpisah, lewat `wrangler`)
- [[DEVELOPER GUIDE]] — cara kerja dev
