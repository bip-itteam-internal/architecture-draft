---
description: Impact analysis sebelum mengubah fakta di vault — dok + kode terdampak, usul suntingan, terapkan setelah disetujui
---

Sebelum sebuah fakta di vault (ambang, rumus, daftar-izin, nama rute, field) diubah, temukan di mana
lagi fakta itu ditulis. Kelas bug termahal di sini adalah satu fakta di dua tempat yang menyimpang
diam-diam (`rules/team-memory.md` § SATU FAKTA SATU TEMPAT). Spec:
`.agent-kit/docs/2026-10-07-dampak-command-design.md`.

Pemakaian:
- `/dampak <judul-atau-path dok> "<perubahan yang dimaksud>"`
- `/dampak --diff [PATH ...]` — dok yang sudah disunting tapi belum di-commit. **Sebut PATH-nya**:
  pohon vault dipakai bersama sesi lain, tanpa PATH dok tak-ter-commit milik orang lain ikut terbaca.

Batas tegas: **tidak menyunting kode**, **tidak menyunting dok sumber** (itu tugas pemanggil),
**tidak membuat ADR**.

## 1. Siapkan

1. `git -c core.fsmonitor=false -C architecture-draft pull --ff-only`. Gagal → lanjut, tulis
   "⚠️ salinan vault lokal basi: <alasan>" di kepala laporan.
2. Dari akar `erp/`, jalankan dengan **`run_in_background: true`** dan simpan keluarannya ke scratchpad:
   `architecture-draft/Tools/.venv/Scripts/python.exe architecture-draft/Tools/dampak.py --root architecture-draft --sumber "<dok>" --teks "<perubahan>"`
   (atau `--diff <PATH ...>`; PATH boleh relatif `erp/`, relatif vault, atau absolut). Tiga repo kode
   di-grep per jalan; di mesin yang sibuk itu bisa melewati batas tool foreground, dan perintah yang
   terbunuh terbaca seperti galat skrip. Exit 2 = sumber/PATH tak ditemukan atau tak ada perubahan:
   laporkan pesannya, berhenti.
3. `index_segar: false` → catat di kepala laporan; jangan berhenti.
4. Kode dibaca dari ref remote (`origin/main`, `mybharata-app` `origin/dev`). Repo yang ref-nya basi
   menjawab tentang kode lama: bila ragu, `git -C <repo> fetch` dulu (membaca, bukan mengubah kerja siapa pun).

## 2. Nilai kandidat dok

Periksa **setiap** `kandidat_dok` di berkasnya sendiri (bukan ringkasan index). Kandidat yang alasannya
**hanya** `fakta:<angka>` cukup diperiksa di baris yang cocok (`Grep` angka itu di berkas tersebut,
dengan konteks beberapa baris); sisanya dibuka dengan `Read`. Angka mudah cocok kebetulan, dan diukur
2026-10-07 satu perubahan ambang bisa menghasilkan puluhan kandidat semacam itu. Beri satu vonis +
satu kalimat alasan:

| Vonis | Artinya |
|---|---|
| **Terdampak** | menyatakan fakta yang sama, atau bergantung pada keputusan yang berubah. **Wajib kutipan baris.** |
| **Hanya menyebut** | menautkan, tak memuat fakta yang berubah |
| **Tidak terkait** | kecocokan kebetulan (mis. `80` sebagai port) |

## 3. Nilai kandidat kode

Kelompokkan `kandidat_kode` per repo, buka `berkas:baris`-nya. **Tidak disunting.** Fakta yang sama di
≥ 2 berkas kode → tandai ⛔ **duplikasi fakta**, sebagai kandidat task/brief.

## 4. Sajikan laporan, lalu BERHENTI

```
Perubahan ini menyentuh N dok + M berkas kode.   [peringatan basi bila ada]

| Dok | Vonis | Kutipan | Usulan suntingan (diff singkat) |
Dibuang: vonis "hanya menyebut"/"tidak terkait" + seluruh `dilewati` beserta alasannya
Kode (tidak disunting): repo · berkas:baris · fakta · ⛔ bila duplikasi
```

Bila perubahannya **menyimpang dari ADR yang berlaku** (bukan sekadar menyelaraskan dok dengan ADR),
tulis **"butuh ADR"** dan berhenti di sini tanpa langkah 5-6.

## 5. Persetujuan per dok

`AskUserQuestion` multiSelect, satu opsi per dok berverdikt **Terdampak**. Yang tidak dipilih tidak disentuh.

## 6. Terapkan yang disetujui

1. Sunting dok terpilih; perbarui status marker bila berubah (rulebook vault §5).
2. Verifikasi 0 wikilink rusak (rulebook §4).

**Dipanggil dari command lain** (`/sync-docs`, `/analisa-kebutuhan`): berhenti di sini. Index, commit,
dan push ikut alur pemanggil, sekali untuk seluruh suntingan. `/sync-docs` melarang push otomatis, dan
`/analisa-kebutuhan` meregenerasi index sesudah merge; commit sendiri di tengah alur mereka
menghasilkan push sepotong dan index basi.

**Dipanggil langsung** (`/dampak`), lanjutkan:

3. `--check` index (`/sync-docs` langkah 7); basi → `/index-vault`.
4. Commit **per nama berkas**: `docs: selaraskan <fakta> (dampak dari <sumber>)`. Lalu merge
   `origin/main`, push `main` (konvensi vault: tanpa PR).
