---
description: Tutup task — gerbang kelengkapan + checklist akhir + commit project
---

Tutup task.

## 1. Gerbang kelengkapan rencana

Baca `architecture-draft/.agent-kit/rules/wrap-completion-gate.md` dan jalankan
prosedurnya: temukan artefak rencana (`.task-plans/`), ekstrak itemnya, tentukan mode
verifikasi (DIFF · LINTAS-REPO · KEADAAN-LUAR), klasifikasi tiap item, lalu terapkan
logika gerbangnya.

Yang tidak boleh dilewat, walau semua item rencana terlihat selesai:

- Fitur backend baru wajib sekali benar-benar dipanggil **lewat gateway**, bukan cuma
  unit test.
- Angka nol yang mencurigakan (0 dokumen, 0 notifikasi terkirim) diperlakukan sebagai
  pertanyaan, bukan kabar baik.
- Konsekuensi deploy yang menuntut lebih dari satu container ikut tercatat.

Bila gerbangnya tak bisa jalan (tak ada artefak rencana, berkas tak terbaca), **katakan
eksplisit**. Jangan lolos diam-diam.

Bila gerbangnya menyimpulkan BERHENTI, berhenti di sini. Jangan commit.

## 2. Checklist akhir

Konfirmasi tiap poin ke user:

- [ ] Test hijau (atau dicatat kenapa belum ada test). Untuk erp-frontend, bandingkan
      kegagalan dengan baseline `origin/main` sebelum menyalahkan perubahan sendiri.
- [ ] `/review` sudah dijalankan; temuan kritis ditangani.
- [ ] `/sync-docs` sudah dijalankan; dok architecture-draft sinkron, 0 broken wikilink.
- [ ] Perubahan sesuai lingkup task (bandingkan dengan `## Di Luar Lingkup` di artefak
      rencana).

## 3. Commit

1. Tampilkan ringkasan perubahan project (diff terkompres).
2. Commit sesuai konvensi repo tersebut (ikuti gaya pesan commit yang sudah ada).
   **Stage per-nama berkas**, jangan `git add -A`. Tanpa trailer `Co-Authored-By`.
3. Jangan push kecuali user minta. Repo KODE wajib lewat branch + PR; jangan commit
   langsung ke `main`.

## 4. Ringkas

Sebutkan: apa yang berubah di kode, apa yang berubah di dok, dan apa yang **ditunda**
dari gerbang kelengkapan (item BELUM yang user pilih untuk di-follow-up, dan item
TAK TERVERIFIKASI yang masih perlu dicek manual).
