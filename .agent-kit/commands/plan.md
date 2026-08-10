---
description: Susun rencana implementasi grounded ke arsitektur
---

Lanjutan dari /start-task. Susun rencana implementasi yang grounded ke arsitektur.

Langkah:
1. Pastikan ada konteks dari /start-task. Bila belum, minta user jalankan /start-task dulu.
   Lalu baca `architecture-draft/.agent-kit/rules/plan-checklist.md` — di situ ada cara
   mencari kode yang sudah ada, analisis mode kegagalan, matriks pilih jenis test, dan
   aturan regresi.
2. Susun rencana bertahap:
   - Perubahan per file (path eksak) + alasan. Sebut **repo mana** untuk tiap berkas;
     satu fitur biasanya menyentuh lebih dari satu repo sibling.
   - Langkah-langkah kecil yang masing-masing bisa diuji.
   - Test yang akan ditulis (lihat TDD adaptif di /implement).
   - Risiko & dependensi antar-service (rujuk dok arsitektur).
   - Konsekuensi deploy bila ada: env baru (butuh `--force-recreate`), kategori inbox baru
     (butuh dua container naik bersama), perubahan kontrak (BE sebelum FE).
3. Tandai EKSPLISIT bila rencana menyimpang dari arsitektur draf (sebut dok mana & gap-nya).
4. Sajikan rencana, minta persetujuan user sebelum /implement.
5. **Setelah user setuju**, tulis artefak rencana ke
   `.task-plans/<YYYY-MM-DD>-<slug-task>.md` di akar workspace `erp/` (buat foldernya bila
   belum ada). Ini yang dipakai `/wrap` untuk mengaudit kelengkapan; tanpa artefak,
   gerbangnya tidak punya pembanding. Sebutkan path-nya ke user.

Bentuk artefak (judul persis, `/wrap` mencarinya):

```markdown
# <Judul task>

- Branch: <nama branch>
- Tanggal: <YYYY-MM-DD>

## Konteks
<1 sampai 2 paragraf: kenapa, dan dok arsitektur apa yang jadi landasan>

## Apa yang Sudah Ada
- <kode/komponen/master data/resolver yang sudah menyelesaikan sebagian masalah ini>
  — dipakai ulang / dibangun tandingannya karena <alasan>

## Ruang Lingkup
- [ ] <repo> `<path/eksak>` — <apa yang berubah>
- [ ] <repo> `<path/eksak>` — <apa yang berubah>

## Test
- [ ] <test yang akan ditulis>

## Migrasi / Konfig / Deploy
- [ ] <env, indeks, seed, urutan deploy; kosongkan bila tidak ada>

## Mode Kegagalan
- <jalur kode baru> — gagal karena <sebab realistis>; ada test? ada penanganan galat?
  user lihat pesan atau senyap? <tandai CELAH KRITIS bila tidak, tidak, dan senyap>

## Cara Verifikasi
- [ ] <langkah konkret yang membuktikan fiturnya JALAN, bukan cuma test hijau.
      Untuk backend: sebut panggilan lewat gateway `/api/<module>/...`>

## Di Luar Lingkup
- <hal yang sengaja tidak dikerjakan> — <satu baris alasan, wajib>
```

Isi `## Cara Verifikasi` jangan dikosongkan. Test hijau bukan bukti fitur bisa dipakai:
fitur pernah merged, deployed, dan tetap mustahil dipakai selama 3 hari karena lapisan
binding tak ikut diperbarui.
