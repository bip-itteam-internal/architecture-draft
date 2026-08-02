## ADR 0010 — Internasionalisasi (i18n): dukungan dua bahasa (Indonesia + English)

- **Status**: ✅ Accepted (tahap awal Implemented di `erp-frontend`)
- **Tanggal**: 2026-07-04
- **Konteks dok**: [[APP - Web ERP]]

## Context

Sistem dipakai karyawan Indonesia, namun sebagian pengguna/istilah lebih pas dalam English. Sebelumnya string UI **hardcoded** dan campur ID/English tanpa aturan, sehingga tidak bisa diganti pengguna dan tidak konsisten. Dibutuhkan dukungan **dua bahasa (Indonesia & English)** yang bisa dipilih user, konsisten, dan bisa diterapkan **bertahap** tanpa merombak semua service sekaligus.

## Decision

**`erp-frontend` (Next.js) memakai `react-i18next`.** Aturan wajib:

1. **Default Bahasa Indonesia (`id`)**, opsi English (`en`). Pemilihan lewat **switcher di header** (bersebelahan dengan toggle tema); pilihan disimpan di **cookie `lang`** dan dibaca **server-side** di root layout (`<html lang>`, anti-flash/SSR konsisten). **Pengecualian:** halaman **login** belum punya header, jadi menyediakan **switcher mini di kartu login** (reuse komponen `LanguageSettings`) — tetap tulis cookie `lang` yang sama.
2. **Semua teks user-facing BARU WAJIB lewat i18n** — `const { t } = useTranslation(); t("domain.key")`. **Dilarang hardcode string** yang tampil ke user.
3. **Kamus** di `erp-frontend/src/i18n/locales/id.ts` (sumber tipe) & `en.ts`, objek **bertingkat per domain** (`common`, `hris`, …). Tambah key saat menerjemahkan; fallback: locale aktif → `id` → key.
4. **Istilah teknis yang lazim English TETAP English** di kedua locale (mis. Dashboard, Export, Refresh, KPI, Score, Template, External URL, Space). **Jangan dipaksa** diterjemahkan ke Indonesia.
   - **Batasnya: kata, bukan nama modul.** Aturan ini untuk istilah yang memang dipakai sehari-hari dalam English. **Nama modul/menu diterjemahkan bila padanannya lazim** dan isi modulnya sudah berbahasa Indonesia — nama yang tetap English di modul yang isinya Indonesia justru jadi satu-satunya yang menyimpang.
   - Contoh yang ditinjau ulang **2026-08-02**: modul **Task Management** semula dibiarkan English atas dasar butir ini, kini jadi **"Manajemen Tugas"** di locale `id` (en tetap "Task Management"), selaras dengan isinya yang sudah memakai "Tugas" (Ajukan Tugas, Tugas Saya, Tugas Tim). Berlaku di **erp-frontend dan MyBharata** supaya satu menu tak bernama berbeda antar platform.
   - ⚠️ **Gotcha**: di `erp-frontend`, judul grup menu sidebar punya **pengenal internal** (`JUDUL_MENU_TASK_MANAGEMENT`) yang dipakai mencocokkan menu dengan penyaring RBAC-nya. Yang diterjemahkan **hanya label tampilan** lewat `tr(item.title)`; mengubah pengenalnya mematikan gating sub-menu tanpa satu pun test gagal.
5. **Tanggal/bulan/angka** dilokalkan via `toLocaleDateString(intlLocale(lang))` — **bukan** hardcode `"id-ID"`.
6. **Rollout bertahap** (per service/halaman), bukan sekaligus. Infrastruktur (`src/i18n/*`, provider, switcher) sudah terpasang; konversi jalan per area.

Infrastruktur teknis: instance i18next dibuat via `createInstance()` (bukan singleton global → aman SSR). Detail pola & progres: lihat memori proyek / `src/i18n/`.

## Consequences

- ➕ UI dwibahasa konsisten; user memilih sendiri; pilihan tahan reload.
- ➕ Pola seragam untuk semua fitur baru; mengurangi string liar/campur.
- ➖ Setiap fitur baru **wajib** menyediakan key di **dua** file locale (`id` + `en`) — sedikit overhead.
- ⚠️ **Bertahap**: sebagian halaman/komponen belum dikonversi. Komponen **shared** (mis. Banner/MainTable) dikonversi terjadwal karena menyentuh chrome **semua** service sekaligus — sampai itu, sebuah halaman bisa **campur sementara** (mis. banner English + konten Indonesia).
- 🔗 **Aturan AI agent**: workspace CLAUDE.md (agent-kit) mewajibkan setiap string user-facing baru di `erp-frontend` lewat i18n dengan key `id`+`en`.

## Status Rollout (per 2026-07-06)

- ✅ Infra i18n + **switcher header** + default Indonesia.
- ✅ HRIS: **Ulang Tahun**, **KPI** (Scoring & Templates), **Announcements** (list + create).
- ✅ **Login / Entrance** ([[BASE - Enterance Point]]): halaman login di-i18n penuh (namespace `auth.login.*`, key di `id.ts`+`en.ts`) + **switcher bahasa di kartu login**; pesan error login dilokalkan & dibedakan (kredensial vs server vs jaringan).
- 🟡 Menyusul: sisa halaman HRIS, komponen **shared** (Banner, MainTable), lalu service lain.

## Dokumen Terkait

- [[APP - Web ERP]]
- [[ADR - 0003 SSO-only Gateway]]
