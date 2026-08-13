# Gerbang Kelengkapan — bip-erp

> Dipakai oleh `/wrap`. **Jangan** di-import ke `CLAUDE.md`; dibaca **on-demand**.
>
> Sumber: diadaptasi dari `ship/sections/plan-completion.md` [gstack](https://github.com/garrytan/gstack)
> (MIT). Mekanisme subagent, PR body, `/qa-only`, dan learnings-nya dibuang; mode
> verifikasi lintas-repo dan keadaan-luar justru diperkuat karena di bip-erp itu
> keadaan normal, bukan pengecualian.

Update file ini cukup `git pull architecture-draft` (tak perlu re-run `init`).

---

## Kenapa gerbang ini ada

Kelas kegagalan paling mahal di sini bukan kode yang salah, tapi kode yang **benar dan
tak pernah terpanggil**. Form berulang di form-builder lengkap sampai cron dan teruji,
tapi `formRequest` tak punya field `recurrence` sehingga tak seorang pun bisa
menyalakannya; diam selama 3 hari dalam keadaan "live", ketahuan cuma karena uji
end-to-end. Test hijau tidak membuktikan fitur bisa dipakai.

Gerbang ini menutup jarak antara "diff-nya ada" dan "fiturnya jalan".

---

## 1. Temukan berkas rencana

Urutan:

1. **Konteks percakapan** (paling andal). Bila `/plan` sesi ini menulis artefak, pakai
   path itu langsung.
2. **`.task-plans/`** di akar workspace `erp/`: ambil berkas `.md` terbaru yang nama
   atau isinya cocok dengan branch/task saat ini.

Bila tak ada berkas rencana: **jangan diam-diam lolos**. Katakan
"Tidak ada berkas rencana, gerbang kelengkapan dilewati" dan lanjut ke checklist `/wrap`
biasa. User berhak tahu gerbangnya tidak jalan.

Bila berkas rencana ada tapi tak terbaca, laporkan itu sebagai kegagalan, bukan sebagai
lolos.

---

## 2. Ekstrak item

Baca berkas rencana. Ambil setiap item yang menggambarkan **pekerjaan**:

- checkbox `- [ ]` / `- [x]`
- langkah bernomor di bawah judul implementasi
- kalimat imperatif ("tambah X di Y", "ubah handler Z")
- spesifikasi tingkat berkas ("berkas baru: `path/ke/file.go`")
- kebutuhan test dan migrasi

**Abaikan**: bagian Konteks/Latar Belakang, pertanyaan terbuka dan TBD, dan apa pun di
bawah judul **Di Luar Lingkup**.

Untuk tiap item catat kategorinya: `KODE` · `TEST` · `MIGRASI` · `KONFIG/ENV` · `DOK` ·
`DEPLOY`.

Batas 50 item. Bila lebih, kerjakan 50 teratas dan katakan sisanya berapa.

---

## 3. Tentukan mode verifikasi

Diff tidak bisa membuktikan segalanya. Sebelum menilai, klasifikasi **bagaimana** tiap
item bisa dibuktikan.

| Mode | Artinya | Contoh di sini |
|---|---|---|
| **DIFF** | Perubahan ada di repo project aktif, terlihat di `git diff` | handler baru, field struct, test |
| **LINTAS-REPO** | Perubahannya di repo sibling | BE di `bip-erp`, FE di `erp-frontend`, app di `mybharata-app`, dok di `architecture-draft` |
| **KEADAAN-LUAR** | Keadaan di sistem lain; diff tak bisa membuktikan apa pun | env container, koleksi Mongo dev/prod, seed master data, deploy Harness, indeks unik yang dibuat manual |

**LINTAS-REPO adalah keadaan normal di sini, bukan pengecualian.** Hampir tiap fitur
menyentuh minimal dua repo, dan repo-repo itu **ada di disk sebagai sibling** di dalam
`erp/`. Jadi jangan buru-buru bilang tak terverifikasi: buka repo sibling-nya dan cek.

**Aturan path konkret.** Bila item menyebut path berkas yang konkret, item itu WAJIB
diputuskan SELESAI atau BELUM berdasarkan keberadaan berkasnya. "Tak terverifikasi" hanya
sah bila sasarannya memang abstrak (keadaan Mongo, env container yang sudah naik) atau
repo sibling-nya memang tidak ada di mesin ini. "Malas mengecek" bukan "tidak terjangkau".

---

## 4. Klasifikasi tiap item

- **SELESAI** — ada bukti jelas. Sebutkan berkas di diff, atau path yang terverifikasi ada
  di repo sibling.
- **SEBAGIAN** — sebagian jalan sudah ada tapi belum tuntas (model ada, handler belum;
  field ada di struct DB tapi belum di struct request).
- **BELUM** — verifikasi sudah dijalankan dan hasilnya negatif.
- **BERUBAH** — tujuannya tercapai dengan cara lain dari yang direncanakan. Sebutkan
  bedanya.
- **TAK TERVERIFIKASI** — diff dan pengecekan repo sibling tak bisa membuktikan maupun
  membantah. Sebutkan **pengecekan manual persis** yang harus user lakukan.

**Ketat untuk SELESAI.** Berkas tersentuh belum cukup; fungsionalitas yang disebut rencana
harus benar-benar ada.

**Longgar untuk BERUBAH.** Kalau tujuannya tercapai lewat jalan lain, itu terhitung
tertangani.

**Jujur untuk TAK TERVERIFIKASI.** Lebih baik memunculkan lima item yang perlu
dikonfirmasi manual daripada diam-diam menandainya SELESAI.

**Aturan kejujuran.** Jangan menandai SELESAI hanya karena kode yang berhubungan sudah
naik. **Kode yang MENANGANI sebuah deliverable bukan deliverable itu sendiri.** Mengirim
pustaka yang membaca berkas bukan sama dengan mengirim berkasnya.

---

## 5. Gerbang khusus bip-erp

Tiga pemeriksaan ini di luar checklist rencana, dan berlaku **selalu**, bahkan ketika
semua item rencana SELESAI.

### 5a. Fitur backend baru wajib sekali lewat gateway

Endpoint atau perilaku backend baru **tidak boleh diklaim selesai** sebelum sekali
benar-benar dipanggil lewat gateway (`/api/<module>/...`), bukan cuma lewat unit test.
Gateway MEMBUANG prefix `/api/<module>`, jadi rute yang salah taruh tetap hijau di unit
test dan 404 di jalur nyata. Bila belum pernah dipanggil lewat gateway, item itu
**TAK TERVERIFIKASI**, bukan SELESAI.

### 5b. Angka nol yang mencurigakan adalah pertanyaan, bukan kabar baik

Fitur sudah live tapi koleksinya 0 dokumen, notifikasi 0 terkirim, daftar 0 baris:
perlakukan sebagai indikasi ada rantai yang putus, dan tanyakan. Jangan laporkan sebagai
"aman, belum ada data".

### 5c. Deploy yang menuntut lebih dari satu container

Bila rencana menyentuh salah satu dari ini, pastikan konsekuensi deploy-nya ikut tercatat
sebagai item, dan tandai **KEADAAN-LUAR**:

- **Kategori inbox notifikasi baru** → `<service pengirim>` **dan** `notification-service`
  wajib naik bersama; service yang tak di-rebuild memegang salinan `shared-library` lama
  dan gagalnya senyap.
- **Env baru** → `docker compose up -d --force-recreate <svc>`, bukan `restart`; env dibaca
  saat container DIBUAT.
- **Perubahan kontrak** → deploy BE sebelum FE.

### 5d. Alur pengguna wajib ditempuh utuh, bukan endpoint-nya saja

Berlaku bila rencana menyentuh UI, menu, atau navigasi.

`5a` membuktikan **endpoint**-nya hidup. Itu tidak membuktikan **orangnya** bisa
menyelesaikan pekerjaannya. Keduanya berbeda, dan yang kedua yang dikeluhkan pengguna.

Bila artefak rencana punya bagian `## Alur Pengguna` (§1b plan-checklist), audit tiap
langkahnya sebagai item tersendiri. Tandai **BELUM** bila ada titik putus yang ditandai di
rencana tetapi tak ditutup di diff.

Bila rencana **tidak** punya bagian itu padahal menyentuh UI, katakan begitu secara
eksplisit dan tandai seluruh alurnya **TAK TERVERIFIKASI**. Jangan diam-diam melewatinya:
tak ada bagian rencana berarti tak ada yang pernah memikirkan perjalanannya, bukan berarti
perjalanannya baik.

Bukti yang diterima: **satu perjalanan utuh sebagai orang**, dari niat sampai selesai,
melewati semua modul yang terlibat. `curl` ke endpoint tidak menggantikannya, dan begitu
pula "sudah saya cek" tanpa keterangan langkahnya.

Tiga pertanyaan yang wajib terjawab untuk tiap alur:

1. Setelah tiap aksi, apakah langkah berikutnya terjangkau dari layar itu — atau pengguna
   harus sudah tahu sendiri ke mana?
2. Bila sebuah aksi ditolak, apakah cara membetulkannya terjangkau dari pesan itu?
3. Bila hasilnya menunggu orang lain, apakah pengguna diberi tahu — atau harus membuka
   halaman berulang kali?

---

## 6. Keluaran

```
AUDIT KELENGKAPAN RENCANA
═════════════════════════
Rencana: <path berkas>

## Kode
  [SELESAI]           Handler POST /promotions — services/employee/handlers/promotion.go
  [SEBAGIAN]          Validasi tanggal — ada di model, belum di struct request
  [BELUM]             Field recurrence di formRequest — tak ada di diff

## Test
  [SELESAI]           Test jalur galat handler — app.Test(httptest.NewRequest(...))

## Lintas-repo
  [SELESAI]           Kolom di halaman FE — erp-frontend/src/app/hris/promotion/page.tsx
  [BELUM]             Key i18n en.ts — hanya ada di id.ts

## Keadaan luar
  [TAK TERVERIFIKASI] Indeks unik promotions — cek langsung di Mongo dev
  [TAK TERVERIFIKASI] Endpoint dipanggil lewat gateway — belum pernah dicoba (lihat 5a)

─────────────────────────
KELENGKAPAN: 3/8 SELESAI, 1 SEBAGIAN, 2 BELUM, 0 BERUBAH, 2 TAK TERVERIFIKASI
─────────────────────────
```

---

## 7. Logika gerbang

Evaluasi berurutan.

**Prioritas 1 — ada item BELUM.** Tampilkan checklist di atas, lalu tanyakan satu kali
dengan tiga pilihan:

- **A. Berhenti** dan kerjakan yang kurang sebelum ditutup. Sarankan A bila yang hilang
  adalah fungsionalitas inti.
- **B. Tutup saja**, sisanya jadi follow-up. Sarankan B bila yang hilang cuma satu dua item
  kecil (dok, konfig). Bila B dipilih, tulis daftar yang ditunda di ringkasan penutup dan
  di badan commit.
- **C. Item ini memang dibatalkan** dan dikeluarkan dari lingkup.

Bila A: BERHENTI. Jangan commit. Daftarkan yang hilang.

**Prioritas 2 — ada item TAK TERVERIFIKASI.** Hanya berjalan setelah prioritas 1 beres.

**Konfirmasi wajib per item, bukan satu borongan.** Bertanya sekali untuk semua item
adalah bentuk kegagalannya sendiri: user menekan "sudah" tanpa membuka satu pun. Jadi:
tanyakan satu per satu, sebut pengecekan spesifiknya ("apakah endpoint sudah pernah
dipanggil lewat gateway dev?"), bukan pertanyaan umum. Tiap item tiga pilihan: sudah
diverifikasi (minta bukti singkat), belum (naik jadi BELUM dan kembali ke prioritas 1),
atau memang dibatalkan.

Bila lebih dari 5 item TAK TERVERIFIKASI, tampilkan dulu sebagai daftar bernomor dan
tanyakan apakah mau dikonfirmasi satu per satu (default dan yang disarankan), atau
lingkupnya dikecilkan.

**Prioritas 3 — hanya ada SEBAGIAN.** Tidak memblokir. Lanjut dengan catatan.

**Prioritas 4 — semua SELESAI atau BERUBAH.** Lolos.

---

## 8. Jangan

- **Jangan lolos diam-diam.** Bila gerbangnya tak bisa jalan (tak ada rencana, berkas tak
  terbaca, ekstraksi gagal), katakan begitu secara eksplisit. Gagal-diam adalah bentuk
  kegagalan yang gerbang ini justru dibuat untuk mencegah.
- **Status CI erp-frontend KINI sinyal sungguhan** (sejak 2026-08-12; `ci.yml` punya
  `on: pull_request` lagi). Aturan lama "abaikan saja" sudah dicabut — ia justru menyuruh
  mengabaikan gerbang yang bekerja. Yang tetap berlaku: periksa commit mana yang diuji versus
  waktu merge, dan verifikasi lokal wajib karena `pnpm test` tak pernah hijau penuh di `main`.
- **Jangan menandai SELESAI hanya karena CI hijau atau karena PR sudah merged.** PR
  erp-frontend #1030 di-merge 2026-08-13 saat `verify` masih `pending`; merged bukan berarti
  tergerbang, dan tergerbang bukan berarti pernah dilihat orang di layar (lihat 5d).
- **Jangan menjadikan "test hijau" sebagai bukti fitur bisa dipakai.** form-builder punya
  183 test hijau saat bug binding-nya hidup.
- Jangan commit atau push di dalam gerbang ini. Itu langkah `/wrap` sesudahnya.
