> **Status:** 🟡 Draft (seed — perluas dari pengalaman onboarding nyata)

## Tujuan

Membawa developer baru dari nol sampai bisa menjalankan & berkontribusi ke bip-erp.

## Kapan dipakai

Hari pertama developer baru, atau saat setup ulang environment dari awal.

## Prasyarat

- Akses repo (vault + bip-erp + FE). Git, Go, pnpm, Docker terpasang.

## Langkah

1. Clone vault + repo kode sebagai folder bersebelahan (sibling) — lihat [[CLAUDE]] §0 & [[DEVELOPER GUIDE]].
2. Pahami alur request: baca [[HOMEPAGE]] → [[CORE - API Master Gateway]] → [[CORE - SSO Flow]].
3. Jalankan stack lokal sesuai [[DEVELOPER GUIDE]].
4. Untuk bikin service baru: ikuti langkah di [[HOMEPAGE]] (bagian "Dari mana saya mulai").

## Verifikasi

Login lokal berhasil & bisa hit `/health` salah satu service (lihat [[DEVELOPER GUIDE]]).

## Bila gagal / Rollback

Cek [[IT - Helpdesk]] / [[IT - Monitoring System]]; tanya di channel tim.

## Dokumen Terkait

- [[DEVELOPER GUIDE]] · [[HOMEPAGE]] · [[CLAUDE]] · [[CORE - API Master Gateway]] · [[CORE - SSO Flow]]
