---
description: Tanya-jawab grounded atas vault + kode (read-only, sebut sumber)
argument-hint: <pertanyaan>
---

Jawab pertanyaan user secara grounded. READ-ONLY: JANGAN menulis/ubah dok atau kode apa
pun — tugasmu hanya menjawab + menyebut sumber.

Pertanyaan: $ARGUMENTS

Langkah:
1. Baca `architecture-draft/VAULT-INDEX.json` (manifest ~218 dokumen: judul, area,
   jenis, status, tautan, ringkasan, kata kunci). Pilih **3 sampai 5 dokumen** paling
   relevan dengan mencocokkan pertanyaan ke `ringkasan` dan `kata_kunci`.
   Bila index tidak ada, rusak, atau `versi_skema` tak dikenal → pakai cara lama
   (`architecture-draft/CLAUDE.md` §7 + grep) dan **beri tahu user** bahwa index tidak
   tersedia; sarankan `/index-vault`.
2. Baca dokumen terpilih **secara utuh** di `architecture-draft/`. Perhatikan
   `status_emoji` + `status_teks` di entri index dan marker di dokumennya
   (✅ Implemented / ⚠️ ada catatan / 🟡 Konsep / 🔴 Stub / 🔜 Direncanakan /
   ⛔ Superseded). Sekitar sepertiga dokumen **tidak punya status** — seluruh dok meta
   root dan seluruh `API - *`. Itu normal, bukan gap.
   Bila pertanyaannya berangkat dari kode, `CLAUDE.md` §7 tetap dipakai: §7 memetakan
   **repo → dokumen**, index memetakan **pertanyaan → dokumen**. Sumbu berbeda,
   keduanya berguna.
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
