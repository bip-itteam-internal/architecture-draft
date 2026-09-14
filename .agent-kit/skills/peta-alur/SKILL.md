---
name: peta-alur
description: Gunakan saat membuat, memperbarui, atau membagikan diagram Archify (arsitektur, workflow, sequence, dataflow, lifecycle) untuk bip-erp, erp-frontend, atau MyBharata; juga saat visual-check Archify gagal (overflow, teks di bawah 6px), legend workflow menampilkan "Agent logic" atau "Tool action", validate berulang gagal explicit-pin-conflict, atau muncul pilihan menyimpan diagram di vault architecture-draft.
---

# Peta Alur dengan Archify (tim ERP)

Lapisan keputusan khusus tim ERP di atas skill `archify`. Cara menulis spec, perintah
`validate`/`deliver`/`visual-check`, dan batas putaran perbaikan ada di skill archify.

**REQUIRED SUB-SKILL:** `archify`. Belum terpasang? Jalankan `/skills`, lalu restart sesi.

Soal cara memakai Archify, skill archify yang menang. Soal tempat simpan, cara berbagi, dan
kapan peta boleh dibagikan di tim ini, skill ini yang menang.

## 1. Simpan dan bagikan: Artifact privat, bukan vault

Hasil akhir dibagikan sebagai **satu Artifact privat multi-berkas**:

1. Halaman induk (register peta): pertanyaan yang dijawab tiap peta, snapshot SHA dan tanggal,
   hasil pemeriksaan, apa yang tidak ditunjukkan, dan pernyataan "bukan sumber kebenaran".
2. `<peta>.html` hasil `deliver`.
3. `sumber/<peta>.json`, spec yang lolos, supaya sesi lain bisa memperbaruinya lewat
   Artifact `read_file`.
4. Pratinjau PNG terang dan gelap dari sidecar `visual-check`.

Kandidat dan sidecar kerja tetap di scratchpad. Memperbarui peta berarti publish ulang ke
URL Artifact yang sama.

**Vault `architecture-draft` bukan tempat peta dan bukan opsi yang ditawarkan.** Repo-nya
PUBLIC, sementara peta memuat endpoint, izin, path kode, dan tautan ke repo privat. Tiap HTML
juga sekitar 800 KB.

| Pikiran | Kenyataan |
|---|---|
| "Rulebook vault tidak mengatur lampiran, jadi boleh" | Tidak diatur bukan izin. Vault PUBLIC. |
| "Saya minta konfirmasi dulu sebelum push ke vault" | Jangan tawarkan vault sama sekali. Tawarkan Artifact privat. |
| "Dok domain di vault perlu menautkan petanya" | Dok vault tetap sumber kebenaran; peta salinan yang bisa basi. |

## 2. Anggaran tata letak untuk layar 1440×900

Ukuran teks dan tinggi halaman diturunkan dari viewBox, jadi rencanakan ukurannya sebelum
menulis spec.

| Ukuran | Batas yang terbukti |
|---|---|
| Tinggi dibagi lebar viewBox | Paling besar 0,45. Workflow 4 lane (1001×660) meluap 326px; workflow 2 lane (1181×404) dan architecture 1330×592 muat |
| Lebar viewBox workflow | Paling besar 1240, supaya sublabel 8px tetap minimal 6px |
| Lebar viewBox architecture | Paling besar 1390, untuk sublabel 9px |
| Node workflow selebar 140 | Label paling panjang 17 karakter, sublabel 24 |

- Workflow 3 lane belum pernah diukur. Sebelum menambah lane, baca `viewBox` dari
  `validate <type> <spec> --layout-json`.
- Nyatakan "muat di layar" hanya sesudah `visual-check` pass, dan sebut ukuran layar yang lolos
  (1440×900, 1600×1000, 1920×1080, 2048×1320). Layar 1366×768 tidak diuji Archify.

## 3. Workflow: label legend wajib diganti

Renderer workflow melabeli type dengan istilah agent AI: "User UI", "Agent logic",
"Tool action", "Context / trace", "External system". Untuk `diagram_type: "workflow"`, isi
`meta.legend.entries` untuk setiap `type` yang dipakai node:

```json
"legend": { "entries": {
  "frontend":   { "label": "Layar aplikasi" },
  "backend":    { "label": "Service / proses" },
  "messagebus": { "label": "Notifikasi" },
  "database":   { "label": "Penyimpanan" },
  "external":   { "label": "Di luar sistem" }
} }
```

## 4. Kapan peta boleh dibagikan

- `visual-check` berstatus `fail` (overflow atau teks di bawah 6px) berarti peta **belum boleh
  dibagikan**, termasuk saat dikejar rapat. Lolos `validate` dan `deliver` tidak membuktikan
  peta muat di layar.
- Dikejar waktu: bagikan versi terakhir yang **lolos `visual-check`**, atau sampaikan terus
  terang berapa lama perbaikannya. Versi yang gagal tidak dikirim, dengan catatan sekalipun.
- `explicit-pin-conflict` muncul di edge berbeda dua putaran berturut-turut: hapus **semua**
  `fromSide`/`toSide` yang kamu tulis sekaligus, lalu validasi ulang. Memperbaiki satu edge per
  putaran hanya memindahkan konfliknya.
- `validate --repo-root` yang lolos hanya membuktikan berkas dan rentang baris **ada** di revision
  yang dikunci. Itu tidak membuktikan isi baris cocok dengan label, dan tidak mendeteksi kode yang
  sudah berubah di `main`. Baca isi baris di revision itu sebelum menulis labelnya.

## 5. Catatan teknis mesin Windows tim

- Jalankan `node "<base directory skill archify>\bin\archify.mjs"` lewat tool PowerShell. Untuk
  `--repo-root`, set dulu `$env:GIT_CONFIG_COUNT='1'; $env:GIT_CONFIG_KEY_0='core.fsmonitor';
  $env:GIT_CONFIG_VALUE_0='false'`, karena Archify memanggil git di path berspasi.
- Aturan Artifact mewajibkan HTML dibaca utuh sebelum publish. `Read` menolak potongan yang
  memuat font base64 di `<style id="archify-fonts">` dan JSON `archify-i18n-data` karena melebihi
  25 ribu token: baca per potongan kecil, dan cek baris font lewat PowerShell (hasil decode
  base64 diawali magic `wOF2`). Viewer antar peta hampir identik: baca satu HTML penuh, lalu
  HTML lain cukup baris yang berbeda.

## Tanda bahaya

- Menulis path `architecture-draft/...` sebagai lokasi peta.
- "Sudah lolos deliver, kirim saja."
- Rencana workflow 4 lane atau lebih untuk layar laptop.
- Legend workflow masih "Agent logic".
- Memperbaiki konflik pin satu edge per putaran.
- "Lolos `--repo-root`, jadi labelnya pasti benar."
