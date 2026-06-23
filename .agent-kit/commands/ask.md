---
description: Tanya-jawab grounded atas vault + kode (read-only, sebut sumber)
argument-hint: <pertanyaan>
---

Jawab pertanyaan user secara grounded. READ-ONLY: JANGAN menulis/ubah dok atau kode apa
pun — tugasmu hanya menjawab + menyebut sumber.

Pertanyaan: $ARGUMENTS

Langkah:
1. Tentukan area pertanyaan. Buka `architecture-draft/CLAUDE.md` §7 (pemetaan repo→dokumen)
   untuk menemukan dok arsitektur relevan.
2. Baca dok vault terkait di `architecture-draft/`. Perhatikan status marker
   (§5: ✅ Implemented / ⚠️ ada catatan / 🟡 Konsep / 🔴 Stub).
3. Bila vault mencakup pertanyaan & konsisten dengan kode → jawab dari vault.
4. Bila vault diam ATAU terlihat usang vs kode → baca kode terkait di project aktif
   (lihat .claude/CLAUDE.md baris "Project aktif") untuk tetap menjawab.
5. Sajikan jawaban dengan format:
   - **Jawaban**: ringkas dan langsung.
   - **Sumber**: wikilink dok yang dibaca + `file:line` kode yang dipakai.
   - **Status**: ✅ terdokumentasi & cocok kode / ⚠️ dok ada tapi usang (sebut gap-nya) /
     🟡 hanya konsep/TBD / 🔴 tak terdokumentasi (dijawab dari kode).
   - **Saran**: bila ada gap dok, sarankan "jalankan /sync-docs untuk update dok <X>".
     JANGAN jalankan /sync-docs otomatis.
6. Bila tak ada di vault maupun kode → katakan jujur "tidak ditemukan", JANGAN mengarang
   (grounded-in-code §1).
