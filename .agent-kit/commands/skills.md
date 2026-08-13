---
description: Cek skill/plugin Claude Code rekomendasi tim; tawarkan install yang belum ada (user konfirmasi)
---

Cek skill/plugin Claude Code yang **direkomendasikan tim**, bandingkan dengan yang sudah terpasang,
lalu tawarkan install yang belum ada. **User cukup konfirmasi — kamu yang menjalankan install.**

## Daftar rekomendasi tim
| Skill/plugin | Kegunaan | Install (marketplace resmi) |
|---|---|---|
| **superpowers** ⭐ **WAJIB** | brainstorming · TDD · systematic-debugging · writing-plans · verification | `claude plugin install superpowers@claude-plugins-official` |
| **code-review** | review diff (bug) + `/simplify` (cleanup kualitas) | `claude plugin install code-review@claude-plugins-official` |
| **dataviz** | chart/visualisasi data konsisten | `claude plugin install dataviz@claude-plugins-official` |
| **frontend-design** | arah desain UI (erp-frontend, mybharata) | `claude plugin install frontend-design@claude-plugins-official` |
| **deep-research** | riset multi-sumber terverifikasi | `claude plugin install deep-research@claude-plugins-official` |

## Langkah
1. **Cek terpasang**: tentukan skill mana yang SUDAH ada — bandingkan daftar di atas dengan skill
   yang tersedia di sesi ini (lihat daftar skill di `<system-reminder>`) DAN/ATAU jalankan
   `claude plugin list`. Tandai tiap baris **✅ ada** / **⬜ belum**.
2. **Sajikan** ringkas: yang ✅ dan yang ⬜ (+ kegunaan). Bila SEMUA ✅ → selesai
   ("semua skill rekomendasi tim sudah terpasang").
3. Bila ada yang ⬜ → **tawarkan install** yang kurang (sebut command-nya). **BERHENTI, tunggu
   konfirmasi user** (boleh pilih sebagian).
4. Setelah user konfirmasi → jalankan `claude plugin install <nama>@claude-plugins-official` untuk
   tiap yang dipilih. Bila nama marketplace beda / install gagal headless → arahkan user verifikasi
   via `/plugin` (tab Marketplaces) atau install manual lewat `/plugin` (tab Discover).
5. **Ingatkan**: skill baru umumnya baru aktif setelah **restart sesi** Claude Code.

## Catatan
- Ini **skill umum** (plugin per-mesin), BEDA dari command tim ERP (`/start-task`…`/wrap`, `/ask`)
  yang datang dari agent-kit via `init`.
- **`superpowers` WAJIB tim** (kit ≥ 1.11.0). `init` sudah menyalakannya lewat `enabledPlugins`
  di `.claude/settings.json` scope project, **tetapi menyalakan ≠ memasang**: bila plugin-nya
  belum pernah ter-install di mesin ini, skill-nya tetap tak muncul dan gagalnya **senyap**.
  Karena itu superpowers **tetap wajib dicek di langkah 1** — kalau ⬜, tawarkan install lebih
  dulu sebelum yang lain, dan tekankan restart sesi setelahnya.
- **JANGAN install tanpa konfirmasi user** (perubahan konfigurasi mesin). Berlaku juga untuk
  yang WAJIB: yang otomatis cuma penyalaannya, pemasangannya tetap keputusan pemilik mesin.
- Sesuaikan daftar rekomendasi dengan mengedit `architecture-draft/.agent-kit/commands/skills.md`.
  Untuk mengubah yang **wajib**, sunting `enabledPlugins` di `init.ps1` **dan** `init.sh`
  (dua-duanya, kalau tidak Windows dan Linux akan menyimpang), lalu bump `VERSION`.
