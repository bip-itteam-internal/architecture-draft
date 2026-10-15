> Detail ingatan tim, dibaca **ON-DEMAND** dari indeks `../team-memory.md`. Jangan di-import ke `CLAUDE.md`; update cukup `git pull architecture-draft`. Induk: `## Konvensi FE / UI (erp-frontend · mybharata)`.

### Verifikasi erp-frontend: LOKAL, jangan lewat CI
**Status CI erp-frontend sengaja TIDAK diatur di sini, dan jangan ditambahkan lagi.** Aturannya sempat ditulis dan ditulis ulang beberapa kali, dan tiap versinya usang dalam hitungan hari karena yang dikodekan bukan sifat repo ini melainkan keadaan yang berubah-ubah. Aturan yang berulang kali meleset akan diabaikan seluruhnya, termasuk bagiannya yang benar.

Yang berlaku dan stabil:

- **Verifikasi WAJIB lokal**: `pnpm tsc --noEmit`, `pnpm lint`, `pnpm test`, dan `pnpm build` sebelum merge.
- **`pnpm test` tak pernah hijau penuh di `main`** — bandingkan kegagalan dengan baseline `origin/main` sebelum menyalahkan perubahan sendiri.
- **Merged bukan berarti tergerbang.** PR #1030 di-merge 2026-08-13 saat gerbangnya belum selesai, tanpa ada yang menahan. Jangan menyimpulkan sebuah perubahan sudah teruji hanya karena sudah masuk `main`.

