> **Status:** ⚠️ Implemented (langkah agent-kit init terverifikasi ke `init.ps1`/`init.sh`; bagian stack lokal & alur masih ringkas — perluas dari pengalaman onboarding nyata)

## Tujuan

Membawa developer baru dari nol sampai bisa menjalankan & berkontribusi ke bip-erp.

## Kapan dipakai

Hari pertama developer baru, atau saat setup ulang environment dari awal.

## Prasyarat

- Akses repo (vault + bip-erp + FE). Git, Go, pnpm, Docker terpasang.

## Langkah

1. Clone vault + repo kode sebagai folder bersebelahan (sibling) di dalam `erp/` — lihat [[CLAUDE]] §0 & [[DEVELOPER GUIDE]]. `architecture-draft` **wajib** ada.
2. **Pasang agent-kit** (sumber slash-command flow Claude Code). Dari folder `erp/`, jalankan **sekali**:
   - Windows: `powershell -ExecutionPolicy Bypass -File architecture-draft\.agent-kit\init.ps1`
   - mac/linux: `bash architecture-draft/.agent-kit/init.sh`

   Hasil: `erp/.claude/` (commands + hooks + skills) & `erp/CLAUDE.md` ter-generate. **Tanpa langkah ini tak ada command apa pun** — termasuk `/start-task … /sync-docs … /wrap`. Update standar: `git -C architecture-draft pull` lalu jalankan ulang init (otomatis prune command lama).
3. Pahami alur request: baca [[HOMEPAGE]] → [[CORE - API Master Gateway]] → [[CORE - SSO Flow]].
4. Jalankan stack lokal sesuai [[DEVELOPER GUIDE]].
5. Untuk bikin service baru: ikuti langkah di [[HOMEPAGE]] (bagian "Dari mana saya mulai").
6. Kerjakan task dengan flow wajib: `/start-task` → `/plan` → `/implement` → `/review` → `/sync-docs` → `/wrap`.

## Multi-project (memegang beberapa repo)

Satu workspace `erp/` menampung **banyak project sekaligus** — vault & `erp/.claude/` cukup **satu**.

- Clone **semua** project yang dipegang sebagai sibling di `erp/` (di samping `architecture-draft`), mis. `bip-erp`, `erp-frontend`, `mybharata-app`.
- Saat init, kit **mendeteksi semua** sibling ber-`.git` lalu meminta pilih **satu project aktif** — atau lewati prompt dengan `-ActiveProject <nama>` (PS) / `--active-project <nama>` (bash).
- **Project aktif** = fokus flow saat ini (ke mana `/start-task` membaca dok, ke mana `/wrap` commit). Tertulis di `erp/CLAUDE.md`.
- **Pindah fokus** = jalankan ulang init dengan project lain (beberapa detik; hanya menulis ulang baris "Project aktif", tak menyentuh repo project):
  ```
  powershell -ExecutionPolicy Bypass -File architecture-draft\.agent-kit\init.ps1 -ActiveProject erp-frontend
  ```
- Vault mendokumentasikan **semua** project ([[CLAUDE]] §7 memetakan repo→dok), jadi `/sync-docs` & `/start-task` otomatis mengarah ke dok project yang aktif. "Project aktif" **satu pada satu waktu** (tak ada multi-active).

## Verifikasi

- Di Claude Code ketik `/` → command flow muncul (`/start-task`, `/sync-docs`, dll.); cek `erp/.claude/commands/` berisi 7 file.
- `erp/CLAUDE.md` ter-generate (memuat "Project aktif" & versi kit).
- Login lokal berhasil & bisa hit `/health` salah satu service (lihat [[DEVELOPER GUIDE]]).

## Bila gagal / Rollback

- **Tak ada `/sync-docs` (atau command flow lain)** → belum jalankan init (Langkah 2), atau `architecture-draft` belum di-clone sebagai sibling. init menyalin **semua** command sekaligus, jadi bila satu hilang biasanya **seluruh flow** belum terpasang — bukan `/sync-docs` yang dihapus sendirian.
- `architecture-draft tidak ditemukan sebagai sibling` / `Tidak ada project sibling ber-.git` → perbaiki struktur folder (Langkah 1), ulangi init.
- Cek [[IT - Helpdesk]] / [[IT - Monitoring System]]; tanya di channel tim.

## Dokumen Terkait

- [[DEVELOPER GUIDE]] · [[HOMEPAGE]] · [[CLAUDE]] · [[CORE - API Master Gateway]] · [[CORE - SSO Flow]]
