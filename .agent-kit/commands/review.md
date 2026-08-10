---
description: Review diff — bug + konsistensi vs arsitektur
---

Review pekerjaan sebelum `/sync-docs` & `/wrap`.

## 0. Ambil diff

Branch per service dari `main`, jadi lingkup review = diff branch terhadap base-nya.

```
git -c core.fsmonitor=false fetch origin --quiet
git -c core.fsmonitor=false diff origin/main...HEAD
```

Di Windows jalankan lewat **PowerShell**, dan selalu sertakan `-c core.fsmonitor=false`
(git menggantung di path ber-spasi tanpa itu). Bila belum ada commit, review working tree.

Sebutkan di awal: branch apa, berapa berkas, berapa baris. Bila diff kosong, berhenti dan
katakan begitu, jangan mengarang temuan.

## 1. Baca checklist

Baca `architecture-draft/.agent-kit/rules/review-checklist.md` **sekarang**, sebelum
membaca diff. Isinya kategori Pass 1 (kritis) dan Pass 2 (informasional), heuristik
fix-first, dan daftar hal yang JANGAN dilaporkan.

## 2. Pass kritis, lalu informasional

Jalankan Pass 1 dulu, baru Pass 2. Untuk tiap kandidat temuan, lewati **gerbang
verifikasi** di checklist sebelum menuliskannya:

- Baca berkasnya utuh, bukan cuma potongan diff.
- Klaim "tidak ada" (field, handler, key locale) wajib dibuktikan dengan Grep.
- Klaim "consumer tidak menangani" wajib dibuktikan dengan membaca berkas consumer-nya.
- Ragu = tulis sebagai pertanyaan, bukan pernyataan.

Review yang sering salah akan diabaikan orang. Lebih baik lima temuan yang benar
daripada dua belas yang setengahnya meleset.

## 3. Konsistensi arsitektur

Dimensi kedua, di luar checklist: apakah implementasi menyimpang dari dok di
`architecture-draft/`? Rujuk dok yang sudah dimuat saat `/start-task`. Cek endpoint,
kontrak, ownership data, dan ADR terkait. Bila menyimpang, sebutkan dok/ADR mana dan
apakah ini penyimpangan sadar (perlu dok diperbarui di `/sync-docs`) atau kelalaian.

## 4. Fix-first

Klasifikasi tiap temuan pakai heuristik di checklist:

- **Perbaiki langsung** yang mekanis. Terapkan fix-nya, lalu laporkan sebagai sudah
  diperbaiki.
- **Tanyakan** yang butuh keputusan. Kumpulkan jadi **satu** pertanyaan berisi semua item,
  jangan menanyakan satu per satu.

Jangan memperbaiki hal di luar lingkup diff. Temuan di luar lingkup dicatat sebagai
catatan, bukan dikerjakan.

## 5. Laporkan

```
Review: N temuan (X kritis, Y informasional)

**SUDAH DIPERBAIKI:**
- [file:line] Masalah -> fix yang diterapkan

**BUTUH KEPUTUSAN:**
- [file:line] Deskripsi masalah
  Saran fix: ...
```

Lalu satu kalimat penutup: bila ada temuan kritis yang belum tuntas, sarankan kembali ke
`/implement`; bila bersih, lanjut ke `/sync-docs`.

## Opsi: review dalam

Bila user meminta "review dalam" / "review menyeluruh", atau diff > 300 baris dan
menyentuh lebih dari satu service, pecah Pass 2 ke beberapa subagent paralel per dimensi
(keamanan, konkurensi & data, kontrak API, frontend/i18n, celah test), lalu gabungkan dan
buang duplikat sebelum melapor. **Jangan** lakukan ini secara default: mahal, dan untuk
diff kecil hasilnya sama saja.

## Yang tidak dilakukan di sini

- Jangan commit, push, atau buka PR. Itu tugas `/wrap`.
- Jangan menyimpulkan apa pun dari status CI erp-frontend (gerbangnya mati sejak
  2026-07-29; merah di Actions = startup failure). Verifikasi wajib lokal.
