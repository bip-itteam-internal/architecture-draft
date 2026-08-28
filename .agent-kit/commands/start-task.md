---
description: Mulai task baru — muat konteks arsitektur + kode relevan sebelum menulis kode
argument-hint: <deskripsi task>
---

Kamu memulai task baru di workspace ERP. WAJIB arch-first: JANGAN menulis kode apa pun
sampai konteks dipahami dan user mengonfirmasi.

Task dari user: $ARGUMENTS

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
