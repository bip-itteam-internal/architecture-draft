# Design — ERP Agent Kit (gaya kerja koding ber-AI yang seragam)

> Status: Disetujui (brainstorming) · Tanggal: 2026-06-23 · Tool agen: Claude Code (semua dev)

## Latar Belakang

Tim ingin **gaya kerja koding dengan AI agent yang seragam** untuk semua developer,
dengan **arsitektur draf (`architecture-draft`, Obsidian vault) sebagai landasan**.
Tiap dev bekerja di satu folder induk `erp/` yang berisi project yang digarap +
vault `architecture-draft` sebagai sibling. Yang dibutuhkan: sebuah **"inisiasi"**
sehingga setup dan flow kerja tiap dev identik dan mudah di-update saat standar berubah.

Sisi **dokumentasi** sudah punya rulebook: `architecture-draft/CLAUDE.md`
(grounded-in-code, konvensi nama, repo→doc mapping, alur sync). Design ini menambah
sisi **koding** tanpa menduplikasi aturan dokumentasi tersebut — sisi-koding
**mendelegasi** ke rulebook itu lewat command `/sync-docs`.

## Tujuan & Non-Tujuan

**Tujuan**
- Flow koding per-task yang seragam: arch-first → plan → implement → review → sync-docs → wrap.
- Distribusi & update standar lewat satu sumber kebenaran (git pull).
- Onboarding dev baru ≤ 3 langkah.

**Non-Tujuan**
- Tidak mengganti/menulis-ulang aturan dokumentasi vault (tetap di `architecture-draft/CLAUDE.md`).
- Tidak memaksa CI/PR pipeline baru (di luar lingkup; bisa menyusul).
- Tidak mendukung tool agen selain Claude Code untuk rilis pertama.

## Keputusan Desain (hasil brainstorming)

| Topik | Keputusan |
|---|---|
| Tool agen | **Claude Code** untuk semua dev |
| Isi flow | **Arch-first lengkap** (6 command) |
| Lokasi kit | **Numpang di vault**: `architecture-draft/.agent-kit/` (dot-folder → Obsidian abaikan, git lacak) |
| Target install | **Project-level** `erp/.claude/` (bukan user-level), supaya tidak bocor ke project lain |
| TDD di `/implement` | **Default tapi adaptif** (test-first bila ada test infra; jangan paksa berhenti bila belum ada) |
| Pre-commit hook | **Reminder saja** (non-blocking, bisa dimatikan) |

## Arsitektur & Layout

```
erp/                              ← working directory agen (buka folder ini di Claude Code)
├── architecture-draft/          ← vault (sudah ada) — SUMBER KEBENARAN arsitektur
│   ├── CLAUDE.md                ← rulebook dokumentasi (sudah ada, dipakai oleh /sync-docs)
│   └── .agent-kit/              ← BARU (dot-folder; Obsidian ignore; git track)
│       ├── commands/           ← start-task, plan, implement, review, sync-docs, wrap (.md)
│       ├── skills/             ← skill pendukung (mis. arch-context loader) [opsional rilis-1]
│       ├── hooks/              ← script hook (session-start, pre-commit-reminder)
│       ├── templates/
│       │   ├── workspace-CLAUDE.md
│       │   └── settings.json   ← template settings (daftar hooks)
│       ├── docs/               ← design ini + catatan kit
│       ├── VERSION             ← versi kit (semver sederhana, mis. 1.0.0)
│       ├── README.md           ← onboarding 3 langkah
│       ├── init.ps1            ← inisiasi (Windows, utama)
│       └── init.sh             ← inisiasi (mac/linux)
├── bip-erp/                     ← contoh project digarap
└── .claude/                    ← DIHASILKAN init (tidak di-commit ke repo manapun)
    ├── commands/  skills/  hooks/   ← salinan dari .agent-kit
    ├── settings.json
    ├── .kit-version             ← versi kit yang terpasang (untuk cek update)
    └── CLAUDE.md                ← dari workspace-CLAUDE.md, berisi project aktif
```

Catatan: `erp/` bukan git repo (per environment). Isi `erp/.claude/` adalah artefak
hasil-generate, bukan untuk di-commit; sumber kebenarannya `.agent-kit/` di dalam vault.

## Flow 6 Command

File markdown di `commands/`, terpasang ke `erp/.claude/commands/`. Tiap command =
instruksi untuk agen (bukan kode).

| Command | Fungsi | Input | Output |
|---|---|---|---|
| `/start-task` | Baca dok arsitektur + kode relevan (pakai repo→doc mapping `architecture-draft/CLAUDE.md §7`); ringkas konteks & batasan sebelum menulis apa pun. | arch-draft, kode project aktif | Ringkasan konteks, daftar file/dok relevan, pertanyaan terbuka |
| `/plan` | Susun rencana implementasi grounded ke arsitektur; tandai gap rencana≠arsitektur. | output `/start-task` | Rencana bertahap, file terdampak, risiko |
| `/implement` | Eksekusi rencana. **TDD default-adaptif**: test-first bila ada test infra; bila belum ada, lanjut + sarankan test. | rencana | Kode + test |
| `/review` | Cek bug + konsistensi vs arsitektur (deteksi penyimpangan dari draf). | diff + arch-draft | Temuan + saran fix |
| `/sync-docs` | Update `architecture-draft` agar dok sinkron. **Mendelegasi** ke `architecture-draft/CLAUDE.md` (grounded, wikilink, status marker, konvensi nama). | diff kode + CLAUDE.md vault | Dok ter-update, 0 broken wikilink |
| `/wrap` | Tutup task: commit per-konvensi + checklist (test hijau? dok sinkron? wikilink resolve?). | status repo | Commit rapi + ringkasan |

Prinsip: `/sync-docs` **tidak menulis ulang** aturan dokumentasi — hanya memanggil
rulebook yang sudah ada, sehingga tidak ada aturan tabrakan.

## Hooks (`erp/.claude/settings.json`)

1. **SessionStart** — tiap sesi tampil identik untuk semua dev:
   - Ringkasan flow wajib (6 command).
   - Versi kit + cek apakah `architecture-draft` ketinggalan dari remote
     (`git -C architecture-draft fetch` lalu bandingkan) → saran `git pull` + re-init.
2. **Pre-commit reminder** (non-blocking, dapat dimatikan) — sebelum `git commit` di
   project: ingatkan "sudah `/sync-docs`? wikilink resolve? test hijau?".

## Init Script

`init.ps1` (Windows utama) / `init.sh` (mac/linux), dijalankan dari `erp/`:

1. Validasi `architecture-draft/` ada sebagai sibling; bila tidak, stop + instruksi clone.
2. `git -C architecture-draft fetch`; cek kit ketinggalan → saran pull.
3. Deteksi sibling project (folder dengan `.git`), tampilkan, tanya **project aktif**.
4. Salin `commands/ skills/ hooks/` dari `.agent-kit/` → `erp/.claude/` (salin, bukan
   symlink — aman lintas-OS & lintas-drive Windows).
5. Tulis `erp/.claude/settings.json` dari template (daftar hooks).
6. Generate `erp/CLAUDE.md` dari `workspace-CLAUDE.md` (isi nama project aktif).
7. Tulis `erp/.claude/.kit-version` dari `VERSION`.
8. Cetak ringkasan: versi kit, project aktif, flow wajib, cara update.

Idempoten: aman dijalankan ulang (overwrite artefak generate, tidak menyentuh `.agent-kit`).

## Template `workspace-CLAUDE.md` (jadi `erp/CLAUDE.md`)

- **Landasan**: `architecture-draft/` = sumber kebenaran arsitektur; baca dulu sebelum koding.
- **Project aktif**: `<diisi init>`.
- **Flow wajib**: `/start-task → /plan → /implement → /review → /sync-docs → /wrap`.
- **Aturan turunan**: pakai pnpm (bukan npm); grounded-in-code; dok di-sync via `/sync-docs`.
- Pointer ke `architecture-draft/CLAUDE.md` untuk aturan dokumentasi detail.

## Versioning & Update

- `.agent-kit/VERSION` (semver sederhana).
- SessionStart bandingkan `erp/.claude/.kit-version` vs `VERSION`; bila beda → "ada
  update kit, jalankan ulang init".
- Perubahan standar menyebar lewat `git pull` (vault) + re-init.

## Onboarding (`.agent-kit/README.md`) — 3 langkah

1. Clone `architecture-draft` + project yang digarap sebagai **sibling** di dalam `erp/`.
2. Buka folder `erp/` di Claude Code; jalankan `architecture-draft/.agent-kit/init.ps1`.
3. Mulai task dengan `/start-task`.

## Risiko & Mitigasi

- **Obsidian meng-index file kit** → ditaruh di dot-folder `.agent-kit/` (Obsidian
  mengabaikan dot-folder). Verifikasi saat implementasi.
- **Drift kit terpasang vs sumber** → SessionStart cek versi; init idempoten untuk refresh.
- **TDD memberatkan service legacy** → mode adaptif (tidak memaksa berhenti).
- **Reminder hook mengganggu** → non-blocking + dapat dimatikan per dev.

## Pertanyaan Terbuka (TBD)

- Apakah `skills/` perlu di rilis-1 atau cukup commands? (rencana: opsional, bisa menyusul)
- Konvensi commit/branch detail di `/wrap` (ikuti yang sudah ada di tiap repo).
```
