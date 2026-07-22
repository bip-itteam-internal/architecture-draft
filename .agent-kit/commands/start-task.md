---
description: Mulai task baru — muat konteks arsitektur + kode relevan sebelum menulis kode
argument-hint: <deskripsi task>
---

Kamu memulai task baru di workspace ERP. WAJIB arch-first: JANGAN menulis kode apa pun
sampai konteks dipahami dan user mengonfirmasi.

Task dari user: $ARGUMENTS

Langkah:
1. Baca `.claude/CLAUDE.md`, ambil baris "Project aktif".
2. Tentukan dokumen relevan dari **dua arah**, lalu gabungkan:
   a. `architecture-draft/CLAUDE.md` §7 — pemetaan **repo kode → dokumen**.
   b. `architecture-draft/VAULT-INDEX.json` — cocokkan deskripsi task ke `ringkasan`
      dan `kata_kunci`, ambil 3 sampai 5 kandidat.
   Bila index tidak tersedia atau rusak, pakai (a) saja dan beri tahu user; sarankan
   `/index-vault`.
3. Baca dokumen terpilih secara utuh di `architecture-draft/`. Perhatikan status marker
   (✅ Implemented / ⚠️ ada catatan / 🟡 Konsep / 🔴 Stub / 🔜 Direncanakan /
   ⛔ Superseded) untuk menilai mana yang nyata dan mana yang masih rencana.
   Dokumen tanpa status (dok meta root, `API - *`) itu normal.
4. Baca kode terkait di project aktif (modul/handler/service yang tersentuh).
5. Ringkas:
   - **Task**: <ringkasan>
   - **Landasan arsitektur**: dok yang dibaca + poin penting + status marker
   - **Kode relevan**: file/fungsi + perannya
   - **Gap/risiko**: di mana rencana arsitektur ≠ implementasi saat ini
   - **Pertanyaan terbuka**: yang perlu diklarifikasi sebelum lanjut
6. BERHENTI. Tunggu konfirmasi user sebelum `/plan`. Jangan menulis kode di tahap ini.
