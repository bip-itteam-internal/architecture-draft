---
description: Mulai task baru — muat konteks arsitektur + kode relevan sebelum menulis kode
argument-hint: <deskripsi task>
---

Kamu memulai task baru di workspace ERP. WAJIB arch-first: JANGAN menulis kode apa pun
sampai konteks dipahami dan user mengonfirmasi.

Task dari user: $ARGUMENTS

## 0. Triase — keputusannya sudah ada, atau belum?

Sebelum memuat apa pun, tentukan task ini mestinya lewat jalur mana. Memuat arsitektur untuk task
yang mestinya jadi brief adalah pekerjaan yang dibuang.

Muat jadi brief bila SELURUHNYA benar:

1. Keputusannya sudah tertulis dan bisa **ditunjuk**: ADR, dok domain vault, atau
   `Workspace/ANALISA - *.md`. "Sudah jelas" tidak cukup.
2. Apa yang harus benar bisa dinyatakan tanpa memilih pendekatan.
3. Ada kriteria yang bisa dibuktikan mesin DAN satu yang terlihat di layar.
4. Ukuran S per brief. Lintas repo dipecah, BE dulu — lintas repo BUKAN diskualifikasi.
5. Tidak menyentuh uang, sanksi, jatah cuti, atau ambang disiplin tanpa mengutip
   `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md`.

Tetap manual bila salah satu benar: keputusannya belum ada dan yang diminta justru memutuskan;
program yang menghasilkan beberapa PR berurutan; deploy prod; audit atau riset tanpa kriteria
lolos-gagal.

Lalu tentukan tingkatnya. ⛔ **Resolusikan sumbernya dengan perintah, jangan dari ingatan.**
Prosedur pencariannya `architecture-draft/.agent-kit/rules/vault-retrieval.md` §1b (pencocokan
`VAULT-INDEX.json`) — dipakai di sini juga, bukan hanya di Langkah 2, karena task yang dialihkan
ke brief tidak pernah sampai ke Langkah 2.

| Tingkat | Syarat | Yang kamu lakukan |
|---|---|---|
| `yakin` | Seluruh syarat di atas terpenuhi **dan** berkas sumber keputusan berhasil dibuka | `/brief`, lalu `/kerjakan` langsung. Cetak `Triase: yakin · dasar <sumber>` |
| `ragu` | Syarat terpenuhi tapi sumber tak bisa ditunjuk, atau repo/domain `(ditebak)` | `/brief`, lalu **TAMPILKAN** briefnya dan tunggu persetujuan sebelum `/kerjakan` |
| `tidak` | Ada satu syarat yang gagal | Lanjut ke Langkah 1 di bawah |

Ragu antara `yakin` dan `ragu` berarti **`ragu`**. Gagal-tertutup, sama seperti `pre-commit-gate`.

Bila dialihkan ke brief, `/start-task` **BERHENTI di sini**. Jangan memuat arsitektur.

Langkah:
1. Baca `.claude/CLAUDE.md`, ambil baris "Project aktif".
2. Pilih dan baca dokumen arsitektur yang relevan dengan task ini. Ikuti
   `architecture-draft/.agent-kit/rules/vault-retrieval.md`.
3. Baca kode terkait di project aktif (modul/handler/service yang tersentuh).
4. Ringkas:
   - **Task**: <ringkasan>
   - **Landasan arsitektur**: dok yang dibaca + poin penting + status marker
   - **Kode relevan**: file/fungsi + perannya
   - **Gap/risiko**: di mana rencana arsitektur ≠ implementasi saat ini
   - **Pertanyaan terbuka**: yang perlu diklarifikasi sebelum lanjut
5. BERHENTI. Tunggu konfirmasi user sebelum `/plan`. Jangan menulis kode di tahap ini.
