---
description: Sinkronkan architecture-draft dengan kode (delegasi ke rulebook vault)
---

Sinkronkan dokumentasi `architecture-draft` dengan perubahan kode.

PENTING: Aturan dokumentasi LENGKAP ada di `architecture-draft/CLAUDE.md`. Command ini
hanya orkestrasi — IKUTI rulebook itu, JANGAN buat aturan dokumentasi sendiri.

Langkah:
1. Baca `architecture-draft/CLAUDE.md` (grounded-in-code §1, konvensi nama §3, wikilink §4,
   status marker §5, template §6, repo→doc §7, alur sync §8, aturan git §9).
2. `git -C architecture-draft pull` (vault dikerjakan paralel banyak orang).
3. Tentukan dok terdampak dari diff kode (pakai §7).
4. Update/buat dok sesuai template & konvensi; perbarui status marker.
5. Verifikasi 0 broken wikilink (§4).
6. Segarkan index pencarian, dari akar `erp/`:
   `architecture-draft/Tools/.venv/Scripts/python.exe architecture-draft/Tools/build-vault-index.py --check --root architecture-draft`
   Exit 1 berarti `VAULT-INDEX.json` basi → jalankan `/index-vault` sebelum commit.
   Index basi lebih berbahaya daripada tidak ada index, karena `/ask` akan memakai
   ringkasan yang salah.
7. Commit per-file (`git add -- "Folder/Nama.md"`, JANGAN `git add -A`), pesan `docs: ...`.
   Sertakan `VAULT-INDEX.json` bila ikut berubah. Jangan push otomatis kecuali user minta.
