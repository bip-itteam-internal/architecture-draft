# Checklist Perencanaan — bip-erp

> Dipakai oleh `/plan`. **Jangan** di-import ke `CLAUDE.md`; dibaca **on-demand**.
>
> Sumber: diadaptasi dari `plan-eng-review/sections/review-sections.md`
> [gstack](https://github.com/garrytan/gstack) (MIT). Outside Voice/Codex, worktree
> parallelization, TODOS.md, dan pola "satu temuan satu pertanyaan" dibuang; matriks jenis
> test diganti padanan Go/Fiber dan analisis mode kegagalan diperluas karena kegagalan
> senyap adalah kelas bug paling mahal di sini.

Update file ini cukup `git pull architecture-draft` (tak perlu re-run `init`).

---

## Kenapa checklist ini ada

Gerbang di `/wrap` hanya sebaik artefak rencananya. Rencana yang itemnya kabur
menghasilkan audit yang kabur. Tiga bagian di bawah ini yang paling sering hilang dari
rencana dan paling mahal akibatnya: **apa yang sudah ada** (kita membangun ulang sesuatu
yang sudah dipunya), **mode kegagalan** (fiturnya gagal tanpa ada yang tahu), dan **cara
verifikasi** (test hijau disangka bukti fitur jalan).

---

## 1. Apa yang sudah ada

Sebelum menulis satu langkah pun, cari kode/alur yang **sudah** menyelesaikan sebagian
masalah ini. Untuk tiap yang ditemukan, putuskan eksplisit: rencana ini **memakainya
ulang** atau **membangun tandingannya**. Kalau membangun tandingan, sebutkan kenapa.

Yang wajib dicek di sini:

- **Komponen shared frontend.** Reuse yang asli lewat adapter, jangan bikin tiruan
  look-alike. Halaman daftar sudah punya `MainTable` + `useTableState` + `FilterTable`;
  jangan merakit tabel, filter, atau paginasi sendiri.
- **Master data yang sudah ada.** Cek dulu sebelum menambah field baru; sering yang
  dibutuhkan sudah ada dengan nama lain.
- **Resolver milik modul lain.** Panggil aslinya, jangan menyalin logikanya. Urutan
  menangnya sering berlapis, dan salinan itu pasti menyimpang.
- **Kalender terpusat.** Fitur bertanggal WAJIB mendaftarkan feed ke `calendar-service`;
  dilarang bikin halaman kalender sendiri.
- **Dok arsitektur di vault.** Apakah sudah ada dok/ADR yang mengatur ini? Rencana yang
  menyimpang wajib menyebut dok mana dan apakah penyimpangannya disengaja.

Bagian ini masuk ke artefak rencana sebagai `## Apa yang Sudah Ada`.

---

## 2. Mode kegagalan

Untuk **tiap jalur kode baru** di rencana, tulis satu cara realistis fitur itu gagal di
produksi, lalu jawab tiga pertanyaan:

1. Apakah ada test yang menutupi kegagalan itu?
2. Apakah ada penanganan galat untuk itu?
3. Apakah user melihat pesan yang jelas, atau **gagalnya senyap**?

**Bila jawabannya tidak, tidak, dan senyap: tandai sebagai celah kritis** dan tangani di
rencana, bukan di follow-up.

Bentuk kegagalan yang sudah terbukti terjadi di sini, pakai sebagai daftar pancingan:

| Bentuk | Gejalanya | Contoh nyata |
|---|---|---|
| **Senyap total** | Fitur tampak jalan penuh, akibatnya tak pernah tiba | Kategori inbox salah/absen, notifikasi tak pernah sampai. Provider kalender dilewati karena URL kosong. Seed master data berhenti karena koleksi tak kosong |
| **502 tanpa petunjuk** | Gateway balas 502, respons tak menjelaskan apa pun | `c.JSON()` dipakai sebagai nilai galat lalu memanik. `mongodb.GetCollection` memanik karena DB nil |
| **Hijau di test, 404 di jalur nyata** | Unit test lolos, permintaan lewat gateway gagal | Rute akar didaftarkan di `app.Get("/<module>")` padahal gateway sudah membuang prefiksnya |
| **Ada tapi tak bisa dinyalakan** | Merged, deployed, mustahil dipakai | Struct request tak punya field fiturnya |
| **Data hilang tanpa pesan** | Tak ada galat, isinya lenyap | `PATCH` yang sebenarnya menimpa penuh. Transisi status tidak atomik |
| **Terlihat oleh yang tak berhak** | Sah menurut RBAC, salah menurut fiturnya | Feed kalender menyaring pakai RBAC modul asalnya |

Bagian ini masuk ke artefak rencana sebagai `## Mode Kegagalan`.

---

## 3. Pilih jenis test yang benar

Test fungsi murni **tidak** menangkap cacat lapisan glue. form-builder punya 183 test
hijau saat bug binding-nya hidup, karena tak satu pun melewati Fiber.

| Pilih | Kapan |
|---|---|
| **Unit test** | Fungsi murni, input dan output jelas, helper tanpa efek samping, kasus tepi satu fungsi |
| **Test handler lewat Fiber** (`app.Test(httptest.NewRequest(...))`) | Ada handler baru atau jalur galat handler berubah. **Minimal satu per handler.** Tak butuh database bila kasusnya gagal di penguraian ID |
| **Panggilan manual lewat gateway** | Rute baru, perubahan kontrak, atau apa pun yang menyentuh prefiks `/api/<module>`. Ini bukan test otomatis, ini langkah verifikasi; tulis di `## Cara Verifikasi` |
| **Test integrasi lintas service** | Alur melewati 3+ service, atau titik integrasi yang kalau di-mock justru menyembunyikan kegagalan aslinya (mis. kirim notifikasi lintas container) |

Untuk frontend: uji halaman yang memakai `t` tiruan **buta** terhadap key i18n yang hilang
dan terhadap pluralisasi yang tak sengaja menyala. Bila rencana menyentuh teks
user-facing, sebutkan test terpisah dengan instance i18next asli plus kontrol negatif
bahwa `en` bukan hasil fallback ke `id`.

### Rubrik mutu test

Saat menilai test yang sudah ada, jangan hitung jumlahnya saja:

- ★★★ menguji perilaku, kasus tepi, **dan** jalur galat
- ★★ menguji perilaku benar, jalur bahagia saja
- ★ sekadar asap: "tidak melempar", "ter-render"

Test ★ untuk jalur yang penting sama saja dengan tidak ada test.

---

## 4. Aturan regresi (mutlak)

Bila rencana **mengubah perilaku yang sudah ada** dan suite test yang ada tidak menutupi
jalur yang berubah, test regresi masuk ke rencana sebagai kebutuhan **kritis**. Tidak
ditanyakan, tidak dilewati.

Ragu apakah sesuatu terhitung regresi? Tulis test-nya.

---

## 5. Diagram

Rencana yang punya alur data non-trivial, mesin status, atau pipeline bertahap wajib
menyertakan diagram ASCII. Sebutkan juga berkas mana yang sebaiknya diberi komentar
diagram inline: model dengan transisi status berlapis, service dengan pipeline
multi-langkah.

---

## 6. Jangan

- **Jangan menutup pilihan desain diam-diam.** Bila ada dua jalan yang wajar, sajikan
  keduanya dengan biaya dan risikonya, lalu minta user memutuskan. Rencana bukan tempat
  menyembunyikan keputusan.
- **Jangan menulis "Di Luar Lingkup" tanpa alasan.** Satu baris alasan per item, kalau
  tidak bagian itu cuma jadi tempat pembuangan.
- **Jangan menunda kelengkapan yang murah.** Bila versi lengkapnya cuma sedikit lebih
  mahal dari jalan pintas, rencanakan yang lengkap.
- **Jangan menjadikan "test hijau" sebagai target.** Targetnya fitur terbukti jalan.
