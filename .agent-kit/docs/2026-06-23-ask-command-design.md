# Design — `/ask` command (recall grounded) · agent-kit v1.1.0

> Status: Disetujui (brainstorming) · Tanggal: 2026-06-23 · Bagian dari ERP agent-kit

## Latar Belakang

Agent-kit (`architecture-draft/.agent-kit/`) sudah menutup pilar capture/organize/operate
(6 command flow + hooks + init). Pilar **recall** belum punya jalur khusus — menanyakan
sesuatu ke "otak" arsitektur masih ad-hoc. `/ask` menutup itu: tanya-jawab **read-only**
yang grounded ke vault + kode, selalu menyebut sumber.

## Tujuan & Non-Tujuan

**Tujuan**
- Jawab pertanyaan arsitektur/kode dengan jawaban + sitasi sumber + status keandalan.
- Read-only: tidak pernah menulis/ubah dok atau kode.
- Menutup loop maintenance: bila menemukan gap dok, **sarankan** `/sync-docs` (tidak auto-jalan).

**Non-Tujuan**
- Tidak menulis/memperbarui dokumentasi (itu tugas `/sync-docs`).
- Tidak memulai task koding (itu `/start-task`).
- Tidak menjalankan `/sync-docs` otomatis.

## Keputusan Desain (hasil brainstorming)

| Topik | Keputusan |
|---|---|
| Grounding posture | **Vault-first + verifikasi kode + lapor gap** |
| Mutasi | **READ-ONLY** total |
| Saat ada gap dok | **Sarankan** `/sync-docs`, jangan jalankan otomatis |
| Versi kit | minor bump → **1.1.0** (fitur baru) |

## Perilaku Command (`commands/ask.md`)

Argumen: pertanyaan user (`$ARGUMENTS`).

Langkah:
1. Tentukan area pertanyaan → pakai `architecture-draft/CLAUDE.md §7` (pemetaan repo→dokumen)
   untuk menemukan dok arsitektur relevan.
2. Baca dok vault terkait; perhatikan status marker (§5: ✅/⚠️/🟡/🔴).
3. Bila vault mencakup & konsisten dengan kode → jawab dari vault.
4. Bila vault diam ATAU terlihat usang vs kode → baca kode terkait di project aktif untuk
   tetap menjawab.
5. Susun jawaban dengan format:
   - **Jawaban** — ringkas, langsung.
   - **Sumber** — wikilink dok + `file:line` kode yang dipakai.
   - **Status** — ✅ terdokumentasi & cocok kode / ⚠️ dok ada tapi usang (sebut gap) /
     🟡 hanya konsep/TBD / 🔴 tak terdokumentasi (dijawab dari kode).
   - **Saran** — bila ada gap dok: "jalankan `/sync-docs` untuk update dok X" (disarankan,
     tidak dijalankan otomatis).
6. Bila tak ada di vault maupun kode → katakan jujur "tidak ditemukan"; **jangan mengarang**
   (§1 grounded-in-code).

## Distinctness vs command lain

- `/start-task`: mulai task lalu berhenti untuk konfirmasi menuju koding. `/ask`: tanya-jawab
  murni, tidak menuju koding, fokus recall + sitasi.
- `/sync-docs`: menulis dok. `/ask`: membaca + menyarankan sync. Komplementer.

## Perubahan kit

- Tambah `commands/ask.md` (frontmatter `description` + `argument-hint`, body instruksi di atas).
- `VERSION` → `1.1.0`.
- `README.md`: tambah `/ask` ke daftar isi kit + entri changelog 1.1.0.
- `tests/test-init.ps1`: tambah assert jumlah file `commands/*.md` = 7 (deteksi command hilang).
- Re-install ke `erp/` (regenerate `erp/.claude`).

## Risiko & Mitigasi

- **`/ask` tergoda menulis dok** → instruksi command tegaskan READ-ONLY; saran `/sync-docs`
  hanya teks.
- **Jawaban mengarang saat sumber tipis** → langkah 6 wajib "tidak ditemukan", selaras §1.
- **Bingung dgn `/start-task`** → bagian Distinctness + deskripsi frontmatter dibedakan jelas.

## Pertanyaan Terbuka (TBD)

- Tidak ada. Scope terkunci untuk satu command.
