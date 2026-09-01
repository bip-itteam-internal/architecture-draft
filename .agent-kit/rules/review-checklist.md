# Checklist Review — bip-erp

> Dipakai oleh `/review`. **Jangan** di-import ke `CLAUDE.md` (akan membakar konteks tiap
> sesi); dibaca **on-demand** saat `/review` dijalankan.
>
> Sumber: diadaptasi dari checklist review [gstack](https://github.com/garrytan/gstack)
> (MIT) + gotcha yang sudah terbukti menggigit di bip-erp (lihat `team-memory.md`).
> Kategori Rails/Python/SQL asli dibuang, diganti padanan Go/Fiber/MongoDB/Next.js.

Update file ini cukup `git pull architecture-draft` (tak perlu re-run `init`).

---

## Cara pakai

Baca diff, cari **masalah nyata**. Lewati yang sudah benar. Tiap temuan wajib
`file:line` + saran fix konkret. Jangan menulis ringkasan "secara umum sudah bagus".

**Dua pass:**
- **Pass 1 (KRITIS)** — jalankan lebih dulu. Kelas bug yang sudah pernah lolos ke dev/prod.
- **Pass 2 (INFORMASIONAL)** — severity lebih rendah, tetap ditindak.

**Format keluaran:**

```
Review: N temuan (X kritis, Y informasional)

**SUDAH DIPERBAIKI:**
- [file:line] Masalah -> fix yang diterapkan

**BUTUH KEPUTUSAN:**
- [file:line] Deskripsi masalah
  Saran fix: ...
```

Bila bersih: `Review: tidak ada temuan.`

---

## Gerbang verifikasi SEBELUM melapor (wajib)

Kelas false-positive paling sering adalah "field/fungsi ini tidak ada" padahal ada,
atau "tidak ditangani" padahal ditangani di berkas lain. Diff saja tidak cukup.

Sebelum menulis satu pun temuan:

1. **Baca berkasnya utuh**, bukan cuma potongan diff. Perubahan di baris 40 bisa sudah
   ditangani di baris 12 yang tidak muncul di diff.
2. **Bila temuan menyebut sesuatu "tidak ada"** (field, handler, konstanta, key locale),
   buktikan dengan Grep dulu. Tidak ketemu di diff bukan berarti tidak ada di repo.
3. **Bila temuan menyebut consumer "tidak menangani" nilai baru**, buka berkas consumer-nya
   dan baca. Jangan menyimpulkan dari nama berkas.
4. **Bila ragu, turunkan jadi pertanyaan**, bukan pernyataan. Review yang sering salah
   akan diabaikan, dan itu lebih buruk daripada review yang melewatkan satu hal.

---

## Pass 1 — KRITIS

### A. Lapisan glue: rute, binding, gateway

Kelas bug paling mahal di bip-erp: kodenya benar, tapi tak pernah terpanggil.

- **Rute akar modul didaftarkan di `app.Get("/<module>")`.** Gateway MEMBUANG prefix
  `/api/<module>` sebelum meneruskan (`routes.Reroute` -> `strings.TrimPrefix`), jadi
  rute akar harus `app.Get("/")`. Salah taruh = 404 untuk SEMUA permintaan lewat jalur
  normal, sementara unit test tetap hijau karena memanggil path lokal langsung ke Fiber.
  (calendar-service 2026-08-06, PR #1041)
- **Struct request tidak ikut diperbarui saat menambah field fitur.** Fitur bisa MERGED,
  DEPLOYED, dan tetap mustahil dipakai karena `<x>Request` tak punya field-nya. Telusuri
  field baru dari body JSON -> struct binding -> service -> repository. Putus di mana pun =
  fitur mati senyap. (form-builder `recurrence`, PR terkait #1018)
- **`c.JSON()` dipakai sebagai nilai galat.** `c.JSON()` mengembalikan `nil` saat sukses,
  jadi `return nil, c.Status(400).JSON(x)` sebenarnya `return nil, nil`; penjaga
  `if err != nil` tak pernah menyala, lalu memanik dengan pointer nil dan gateway membalas
  502. Pola aman: kembalikan `(*T, bool)`, pemanggil `return nil` saat `ok` false.
  Mengembalikan error non-nil juga salah (Fiber menulis respons kedua). (PR #1018)
- **`mongodb.GetCollection` dipanggil tanpa penjaga `mongodb.DB == nil`.** Panic-nya tak
  terlihat sebagai panic: fasthttp memutus koneksi, gateway membalas 502, respons tanpa
  petunjuk.

### B. Hak akses & visibilitas

- **Rute `/internal/` tanpa gerbang identitas sendiri.** `/internal/` **bukan** privat:
  gateway tetap meneruskannya dari internet. Tiap rute internal wajib memeriksa identitas
  pemanggil sendiri.
- **RBAC: key `system_roles` dipakai sebagai nama departemen.** Key = **kode MODUL**
  (`it`, `hris`, `finance`, `ga`), bukan nama departemen. `system_roles` = hak akses
  modul/menu, **bukan hierarki org**; atasan/supervisor ada di `work_data`
  (`is_supervisor:true` + `department`).
- **Feed kalender menyaring pakai RBAC modul asalnya.** "Boleh diakses" bukan "layak muncul
  di kalender". Prinsip tiga lapis: kalender memuat data DIRI SENDIRI, PEKERJAAN sendiri,
  dan AGENDA PERUSAHAAN. Data pribadi orang lain tak boleh masuk sekalipun pemanggilnya
  supervisor. (PR #1047)
- **Fallback yang meloloskan semua orang.** Bila resolver hak akses gagal/kosong lalu
  jatuh ke "izinkan", itu bug keamanan, bukan ketahanan. Cek arah fallback-nya.

### C. Kelengkapan enum & nilai baru

Kelas bug berulang nomor satu. Bila diff memperkenalkan nilai enum, status, tipe, atau
kategori baru:

- **Telusuri ke SEMUA consumer, dengan MEMBACA berkasnya, bukan grep saja.** Grep nilai
  saudaranya (mis. nilai lama di enum yang sama) untuk menemukan tiap `switch`, filter,
  daftar-izin, dan tampilan. Kesalahan lazim: nilai ditambah di dropdown frontend tapi
  model/compute backend tak menyimpannya.
- **Kategori inbox notifikasi**: `notification.InboxCategories` di `shared-library` adalah
  **daftar-izin**. Kategori di luar daftar ditolak 400 dan pengiriman best-effort, jadi
  gagalnya **senyap**. Kategori terdaftar-tapi-KELIRU lebih sering dan lebih senyap lagi
  (MyBharata memilih label/warna/ikon dari kategori). **Jangan andalkan `default`** pada
  pemetaan kategori; petakan tiap tipe eksplisit dan uji kategori yang BENAR, bukan sekadar
  terdaftar. (PR #1050)
- **Rantai `if-else` / `switch`**: apakah nilai baru jatuh ke default yang salah?

### D. Konkurensi & keutuhan data (MongoDB)

- **Read-check-write tanpa unique index.** `FindOne` lalu `InsertOne` tanpa indeks unik =
  duplikat saat permintaan paralel. Tangani duplicate-key error dan retry.
- ⛔ **Field KUNCI di `$set` DAN `$setOnInsert` sekaligus → upsert SELALU gagal.** MongoDB
  menolak field yang sama di dua operator update: *"Updating the path '<f>' would create a
  conflict at '<f>'"*, jadi **setiap** tulis balas 500 — bukan kasus tepi, melainkan jalur
  utamanya. Gejalanya menipu: kompilasi hijau, unit test hijau, karena tak satu pun test
  melewati `UpdateOne` (jalur galat validasi berhenti sebelum menyentuh Mongo). Yang
  mengekspos hanya **simpan sungguhan lewat gateway** (gerbang `/wrap` 5a). Field kunci
  taruh **HANYA di `$setOnInsert` (+ filter)**, bukan `$set` — pada insert di-seed sekali,
  pada update tak boleh berubah. Ujilah tanpa Mongo: **ekstrak penyusun dokumen update ke
  fungsi murni**, lalu pastikan **`$set` ∩ `$setOnInsert` = ∅**. Terjadi 2026-09-01 di
  opname perlengkapan (`periode` ada di keduanya; fix `opnameUpsert` + test overlap).
- ⛔ **Koleksi bersama dengan diskriminator: konsumen BARU yang lupa menyaring mencemari
  UANG/KPI, senyap.** Bila satu koleksi memuat dua jenis baris yang dibedakan sebuah field
  (mis. `inventory` berisi FASS **dan** perlengkapan via `sifat`, ADR-0069; atau soft-delete
  via `deleted_at`), aturan "jenis X dikecualikan dari konsumen Y" hidup di **setiap**
  konsumen — dan yang paling mahal adalah `GetPenyusutan → opex` (uang) & KPI yang menarik
  `/items`. Kelas ini kritis karena gagalnya tak terlihat di diff konsumen yang **tak
  disentuh**: menambah baris jenis baru diam-diam menyusup ke setiap query lama yang tak
  menyaringnya. **Yang dicek**: tiap query ke koleksi itu menyaring diskriminatornya
  (default ke jenis lama, mis. `sifat != perlengkapan`, agar baris lama tanpa field tetap
  ikut); dan ada **test regresi** yang membuktikan baris jenis baru **tak menggeser** angka
  jenis lama (jumlah, biaya, skor). Denormalisasi diskriminator ke baris (bila immutable)
  menghindari `$lookup` di tiap penyaring. Terbukti dua kali di `inventory`: filter
  `deleted_at` yang harus diulang di "jalur penyusutan KEDUA", lalu `sifat` di ADR-0069.
- ⛔ **Indeks unik atas field ber-`omitempty` WAJIB parsial.** Field bertanda `omitempty`
  tidak disimpan sama sekali ketika bernilai kosong, dan MongoDB memperlakukan seluruh
  dokumen yang kehilangan field itu sebagai **satu nilai null yang sama**. Indeks unik
  polos karena itu tidak membatasi segelintir dokumen yang mengisi field itu — ia
  membatasi **semua dokumen yang tidak mengisinya**, sehingga dokumen kedua yang wajar
  ditolak dan fitur yang tak ada hubungannya ikut lumpuh. Arah kerusakannya terbalik dari
  yang diniatkan: makin jarang field itu dipakai, makin luas yang rusak.

  Contoh nyata: `(company_id, owner_department, metric_key)` di form-builder. `metric_key`
  hanya diisi segelintir form, jadi indeks unik polos akan membuat **dua form biasa** di
  satu departemen saling menolak dan penerbitan form mati untuk semua orang. Yang benar
  `partialFilterExpression` (`{metric_key: {$exists: true}, status: "published"}`).

  Dua hal yang menyertainya: `mongodb.CreateIndex` di `shared-library` **tidak** menerima
  filter parsial (hanya flag unik), jadi kasus ini harus lewat
  `GetCollection(...).Indexes().CreateOne(...)` langsung dengan penjaga `mongodb.DB == nil`;
  dan pembuatan indeksnya sebaiknya **tidak fatal** saat boot — service yang menolak hidup
  gara-gara satu indeks memadamkan seluruh modul demi aturan yang cuma mengatur sebagian
  kecil dokumen. Verifikasinya bukan "indeksnya terbentuk", melainkan **dokumen yang TIDAK
  punya field itu masih bisa disisipkan berdampingan**.
- **Transisi status tidak atomik.** Pakai `UpdateOne` dengan filter menyertakan status LAMA,
  bukan baca-lalu-tulis. Tanpa itu, dua permintaan bisa melewati atau menggandakan transisi.
  (kelas bug pengajuan ganda, PR #494)
- **`PATCH` yang sebenarnya menimpa penuh.** Permintaan tanpa sebuah field menghapus isinya
  tanpa pesan. Pola aman: struct patch **seluruhnya pointer** (nil = jangan sentuh) supaya
  nilai kosong bisa dibedakan dari tak-disebut, lalu validasi **HASIL GABUNGAN**, bukan
  perubahannya saja. (PR #1067)
- **N+1**: memanggil service/koleksi lain di dalam loop. Kumpulkan id lalu satu query
  `$in`.
- **Menulis ulang resolusi milik modul lain.** Panggil resolver aslinya; urutan menangnya
  sering berlapis dan menyalinnya melahirkan sumber kebenaran kedua yang pasti menyimpang.

### E. Batas kepercayaan input eksternal

Berlaku untuk keluaran LLM (scraping, sentiment, Veo), webhook marketplace, dan upload.

- Nilai dari LLM/pihak ketiga ditulis ke DB atau diteruskan ke mailer tanpa validasi bentuk.
- Keluaran terstruktur (array/objek) diterima tanpa cek tipe sebelum ditulis ke DB.
- URL dari sumber luar di-fetch tanpa allowlist (risiko SSRF ke jaringan internal).
- Nilai user-controlled dirender tanpa escape (`dangerouslySetInnerHTML`).
- Upload: file-service dibatasi **4 MB** dan prefix per access key. Cek batas ditegakkan
  di sisi pemanggil, jangan mengandalkan pesan galat service.

### F. Alur pengguna terputus

Kelas cacat yang selama ini tak dicari sama sekali, dan yang paling sering dikeluhkan
pengguna. Semuanya lolos setiap gerbang teknis: kodenya benar, test hijau, tak ada galat.
Yang rusak adalah **orangnya tidak bisa menyelesaikan pekerjaannya**.

Berlaku untuk tiap diff yang menyentuh UI, menu, atau navigasi.

- **Langkah berikutnya hidup di modul lain tanpa tautan.** Layar menampilkan masalah, tetapi
  tempat membetulkannya ada di layar lain dan tak ada apa pun yang mengantar ke sana.
  Contoh nyata: kolom Pemegang bernilai "belum ditugaskan" di Marketing Analytics →
  Affiliate; jawabannya di ICC Management → tab Akun Affiliate, tanpa tautan.
- **Aksi ditolak sementara cara membetulkannya ada di modul lain.** Pesannya benar dan
  jelas, tetapi jalan keluarnya menuntut pengguna pergi ke tempat lain lalu mencari jalan
  kembali sendiri. Contoh: assign toko ditolak karena karyawan belum punya atasan langsung
  di HRIS. Minimal beri tautan langsung ke layar tujuan.
- **Pilihan yang hilang tanpa penjelasan.** Item yang tak muncul di dropdown karena sudah
  dipakai orang lain terlihat sebagai "tidak ada", bukan "sudah dipegang X". Pengguna
  menebak atau mencari di tabel lain.
- **Keadaan yang menunggu orang lain tanpa pemberitahuan.** Pengguna harus membuka halaman
  berulang kali untuk tahu hasilnya. Loop yang tak pernah tertutup.
- **Urutan wajib yang hanya dijelaskan lewat teks.** Bila layar butuh paragraf panduan
  untuk menerangkan urutan kerjanya (mis. rotasi = nonaktifkan dulu, baru buat baru), itu
  gejala alurnya belum mengantar sendiri. Tanyakan apakah alurnya yang perlu diperbaiki,
  bukan panduannya yang perlu diperpanjang.

Bila rencana punya bagian `## Alur Pengguna`, bandingkan diff dengannya: titik putus yang
sudah ditandai di rencana tetapi tak ditutup di diff adalah temuan, bukan catatan.

### G. Satu fakta hidup di dua tempat

Pertanyaannya bukan "apakah kodenya mirip" melainkan **"kalau fakta ini berubah, berapa
berkas harus disunting?"**. Lebih dari satu = temuan. Yang dimaksud *fakta*: ambang, rumus,
daftar-izin, urutan menang, label, nama rute. Kelas ini kritis karena gagalnya **senyap dan
tertunda**: kedua salinan benar saat ditulis, lalu satu diperbaiki dan satunya tidak.

- **Ambang/konstanta ditulis ulang** alih-alih diimpor. Kartu "Tercapai" memakai `75`
  sementara donut tepat di bawahnya memakai `AMBANG_BAIK` = 80, jadi orang berskor 77
  tercapai di satu kartu dan "perlu dijaga" di kartu sebelahnya. Tak ada galat, tak ada
  test merah, dan angkanya sama-sama masuk akal.
- **Satu field ditulis dari dua layar** lewat endpoint yang sama. `weight` disunting di
  editor template DAN di tab Atur Target; yang belakangan menyimpan menang tanpa ada yang
  tahu. Bila memang disengaja, wajib jadi catatan eksplisit di dok, bukan dibiarkan diam.
- **Daftar/aturan disalin lintas lapisan**: daftar-izin kategori inbox, daftar sumber, peta
  formula, urutan menang resolver. Salinan berhenti menerima perbaikan lalu menyimpang.
  ⚠️ Salinan lewat **biner** (`shared-library` di service yang tak ikut naik) **tidak
  terlihat sama sekali di diff**; lihat §L.
- **Format/normalisasi diulang** di lapisan fetch dan di render. Yang di fetch menang diam
  diam dan mengunci kolomnya dari bahasa aktif.

⚠️ **Menyatukan dua penulis satu field mengubah perilaku yang terlihat user** → masuk
TANYAKAN DULU, bukan perbaiki langsung. Yang boleh langsung: mengganti ambang yang ditulis
ulang dengan impor konstanta yang sudah ada.

---

### G2. Kolom yang tampak komponen tapi bukan (hitung ganda)

Pertanyaannya: **"kalau kolom ini dijumlahkan ke total di sebelahnya, apakah ada rupiah yang
terhitung dua kali?"** Kelas ini kritis karena gagalnya bukan error melainkan **angka yang
salah dan masuk akal**; tak ada test yang menangkapnya, dan keluhannya datang sebagai "laba
lebih kecil dari yang saya hitung sendiri" berhari-hari kemudian.

Pemicunya selalu sama: kolom yang **namanya terdengar seperti kerugian atau komponen biaya**,
padahal ia cuma memotret ulang sesuatu yang **sudah** terpotong di jalur utama. Yang membuatnya
berbahaya, aturan pemakaiannya hampir selalu hanya hidup sebagai komentar di berkas Go-nya,
sehingga siapa pun yang merancang layar dari dokumentasi tak punya cara mengetahuinya.

- **Kolom yang sudah terpotong di hulu, dipotong lagi di hilir.** `iklan_sia_sia` di
  `/returns/detail` adalah porsi `ads_cost` pada order retur — dan `ads_cost` tak pernah
  dialokasikan ulang saat retur, jadi angka itu **sudah** dikurangkan dari laba. Menjumlahkannya
  lagi menghitung belanja yang sama dua kali.
- **Dua kolom yang salah satunya himpunan bagian.** `orders_dikirim` adalah irisan dari
  `orders` di blok `pembatalan`, bukan kolom sejajar. Menjumlahkan keduanya menghitung order
  yang sama dua kali.
- **Kolom yang sama sekali bukan komponen laba.** `pembatalan` tak boleh mengurangi `revenue`
  atau `gross_profit`: yang batal sebelum kirim tak pernah masuk revenue, yang kembali sudah
  masuk `retur`.
- **Dua metrik dijumlah jadi satu "total" karangan.** `iklan_sia_sia` + beban packing jadi
  "total kerugian retur" menghasilkan angka dobel — yang satu belanja yang sudah terbayar,
  yang satu uang fisik tambahan.
- **Level agregasi berbeda dijumlah silang.** `/profit/products` (kode master, bundel dipecah),
  `/profit/items` (judul listing), `/profit/skus` (SKU master) menjawab pertanyaan berbeda atas
  koleksi yang sama. Hasil penjumlahannya tak berarti apa-apa tetapi tampak wajar.

**Yang dicari saat review:**

1. Kolom baru yang namanya memuat *rugi*, *sia-sia*, *terbuang*, *beban*, *batal* — telusuri
   apakah nilainya sudah tercermin di kolom lain pada baris yang sama.
2. Penamaan yang mengundang salah pakai. `iklan_sia_sia` sengaja **tidak** bernama
   `kerugian_iklan`; me-rename-nya di lapisan mana pun (BE, FE, ekspor Excel) menghidupkan
   kembali seluruh kelas ini. Nama di sini bukan kosmetik, ia satu-satunya pengaman.
3. Aturan pemakaian yang **cuma ada di komentar kode**. Bila sebuah kolom butuh kalimat
   "jangan dijumlahkan ke X", kalimat itu wajib naik ke dok vault — komentar Go tak terbaca
   oleh yang merancang layar. Ini temuan, bukan catatan gaya.
4. Test penjaganya. Pola yang benar sudah ada: `TestPembatalanTidakMengubahAngkaLaba` mengunci
   bahwa blok tambahan **tidak** menggeser angka laba.

⚠️ **Mengubah nama kolom atau menghapus salah satunya mengubah perilaku yang terlihat user**
→ masuk TANYAKAN DULU. Yang boleh langsung: menambah test penjaga, dan menaikkan aturan
pemakaian dari komentar ke dok.

---

## Pass 2 — INFORMASIONAL

### H. Nama field & tag bson/json

- **Tag `bson` tidak cocok dengan nama field di koleksi.** Gejalanya senyap: field terbaca
  sebagai nilai nol, bukan error. Cocokkan dengan dokumen nyata atau Data Dictionary di vault.
- **Fixture rakitan tangan tak pernah melewati decode BSON**, jadi ketidakcocokan tipe
  (mis. `primitive.A`) lolos di test tapi jatuh di runtime.
- **Pemeriksa request yang cuma mengecek string** meloloskan field `time.Time`/`int` sebagai
  nilai nol. Cek eksplisit per tipe.

### I. Kontrak API & kompatibilitas mundur

- Field dihapus/berganti tipe di respons, atau parameter wajib baru di endpoint lama.
- Status code atau method berubah tanpa alias path lama.
- **MyBharata tidak bisa dipaksa update.** Perubahan kontrak wajib aman untuk versi app
  lama yang masih beredar. **Deploy BE sebelum FE** untuk perubahan kontrak (FE fallback
  aman bila field baru belum ada).
- Dok `API - <Service>.md` di vault tidak ikut diperbarui saat rute berubah.

### J. Frontend (erp-frontend / mybharata)

- **Teks user-facing baru di-hardcode.** Wajib lewat `t("domain.key")`, key ditaruh di
  **dua** berkas `src/i18n/locales/id.ts` **dan** `en.ts`. Istilah teknis lazim English
  biarkan English di kedua locale. (ADR 0010)
- **Variabel interpolasi bernama `count` menyalakan pluralisasi i18next** (`key_one`/
  `key_other` dicari lebih dulu). Uji halaman memakai `t` tiruan sehingga BUTA terhadap ini.
- **Format tanggal/uang di lapisan fetch.** `toLocaleDateString("id-ID")` di dalam fungsi
  transform membuat kolomnya mustahil ikut bahasa aktif. Format di `render` kolom pakai
  `intlLocale(lang)`.
- **`FilterTable` hanya mengenal `select` dan `date`.** Tidak ada filter angka. Ambang
  numerik jadi preset select atau kontrol sendiri di slot `actions`.
- **Aturan saling-kunci antar filter tidak menggabungkan `{...sebelum, ...sesudah}`.**
  Draft `FilterTable` disemai SEKALI saat panel dibuka; key yang hilang berarti "tak
  berubah", bukan "dikosongkan". Objek kosong `{}` ditangani lebih dulu = kosongkan semua.
- **Halaman daftar tidak memakai struktur tabel HRIS**: satu kartu, `Banner bare` di dalam
  prop `toolbar` milik `MainTable`, seluruh keadaan di `useTableState`. Jangan merakit
  tabel/filter/paginasi sendiri.
- **Loading pakai spinner** alih-alih kerangka. ⚠️ Komponennya BEDA per repo:
  `Skeleton` (`@/components/ui/skeleton`) di **erp-frontend**, `ShimmerBox` di
  **mybharata** (Flutter). `ShimmerBox` TIDAK ADA di erp-frontend; menyuruhnya di sana
  berarti menyuruh membuat komponen baru, bukan memakai ulang yang sudah dipakai 155 berkas.
- **Komponen tiruan look-alike** alih-alih reuse komponen shared via adapter.
- Error validasi form tidak lewat `showFormErrorsToast`.

### K. Celah test

- Jalur galat/guard baru tanpa test negatif sama sekali.
- **Test fungsi murni tidak menangkap cacat glue handler.** Tambahkan minimal satu
  `app.Test(httptest.NewRequest(...))` untuk jalur galat tiap handler; tak butuh database
  bila kasusnya gagal di penguraian ID.
- Cek auth/authz yang ada di kode tapi tak pernah diuji untuk kasus "ditolak".
- **Uji Radix Tabs memakai `click`.** Harus `fireEvent.mouseDown`, kalau tidak tabnya tak
  berpindah dan testnya lolos-diam.
- ⛔ **Radix Select ber-`position="item-aligned"` MEMBUNUH worker vitest di jsdom.** Bukan
  test yang gagal, melainkan proses yang mati: `SyntaxError: Invalid regular expression:
  /file:\/\/\/(\w:)?/: Stack overflow` dari `vite-node/source-map`, diikuti
  `Error: Worker exited unexpectedly`, dan satu berkas test menghabiskan ~7 menit sebelum
  tumbang. Sebabnya varian itu mengukur dan menggulir isinya sendiri, dan jsdom tak punya
  layout sehingga jalurnya berulang tanpa henti. **Kedua idiom yang sudah terbukti jalan
  untuk Select biasa tetap gagal di sini**: `fireEvent.pointerDown(trigger, {button: 0,
  ctrlKey: false, pointerType: "mouse"})` (`form-editor.test.tsx`) maupun
  `fireEvent.keyDown(..., {key: "ArrowDown"})` lalu `findByRole("option")`
  (`create-task-form.test.tsx`). Select `position` bawaan (popper) TIDAK kena.
  **Yang harus dilakukan**: jangan menggerakkan Select-nya. Angkat logikanya ke fungsi
  murni dan uji di situ, kunci anti-polanya lewat keadaan `disabled`/kelas, lalu **tulis
  batasnya terang-terangan di berkas test** — sama seperti catatan jsdom-tak-punya-layout.
  Test yang berpura-pura membuktikan interaksi yang tak pernah terjadi lebih buruk
  daripada gap yang diakui. Terjadi 2026-08-22 di form rotasi shift (erp-frontend #1144).
- Test bergantung jam sistem, timezone, atau urutan eksekusi.
- Uji i18n memakai `t` tiruan sehingga buta terhadap key yang hilang; uji terpisah dengan
  instance i18next asli + kontrol negatif bahwa `en` bukan hasil fallback ke `id`.

### L. Deploy & konfigurasi

- **Menambah env tanpa mencatat bahwa container harus `--force-recreate`.** Env dibaca saat
  container DIBUAT, `restart` saja tidak cukup.
- **Menambah kategori inbox tanpa menaikkan DUA container.** Service pengirim memegang
  salinan `shared-library` lama meski dipakai lewat `replace` lokal. Naikkan
  `<pengirim>` + `notification-service` bersama.
- **URL provider dimasukkan ke map yang divalidasi `ValidateInternalURL`.** Panic bila
  kosong = seluruh fitur padam hanya karena satu service belum di-deploy. Dependensi
  opsional taruh di luar map (URL kosong = dilewati diam-diam).
- **Seed master data** berhenti bila koleksi tak kosong, jadi data baru tak masuk ke
  environment yang sudah terisi. Sediakan migrasi terpisah.

### M. Kode mati & konsistensi

- Variabel/fungsi/import yang tak terpakai setelah perubahan.
- Komentar yang bertentangan dengan kode setelah diubah.
- Angka ajaib yang muncul di lebih dari satu tempat.
- Perubahan yang menyimpang dari dok di `architecture-draft/` (endpoint, kontrak,
  ownership data) tanpa dok-nya ikut diperbarui. Bila menyimpang dari ADR, sebutkan
  ADR-nya dan katakan apakah ini penyimpangan sadar atau kelalaian.

### N. Abstraksi yang kelewat dini

Arah kesalahan yang **berlawanan** dengan §G, dan sengaja dipisah darinya. Jangan
memperlakukan keduanya sama: review yang menuntut abstraksi untuk tiap kemiripan akan
diabaikan seluruhnya, beserta bagiannya yang benar. Kalau ragu antara §G dan §N, tanyakan
apakah yang berulang itu sebuah **fakta** (§G) atau cuma **bentuk** (§N).

- **Menambah prop, tipe, atau generic ke komponen/fungsi yang dipakai banyak tempat demi
  SATU pemanggil baru.** Sebutkan berapa pemanggil lain ikut terdampak. `FilterTable`
  dirender puluhan halaman; menambah tipe filter ke sana demi satu modul memindahkan
  risikonya ke semuanya sementara manfaatnya tinggal di satu (§J).
- **Mengangkat abstraksi pada pemakai KEDUA.** Tunggu yang ketiga; dua yang mirip sering
  kebetulan, dan bentuk yang dikunci terlalu awal biasanya salah. Yang benar-benar terjadi:
  pemakai kedua `department` datang sebagai label grup `HRGA` yang tak dimiliki `work_data`
  siapa pun, jadi "persiapan" apa pun tetap patah.
- **Generalisasi untuk pemakai yang belum ada sama sekali.** Parameter, flag, atau lapisan
  yang tak punya pemanggil hari ini. Kode yang dirakit tapi tak dibaca siapa pun tak
  menghasilkan satu pun test merah saat ia salah.
- **Ekstraksi tanpa test sendiri, atau jalur lama tak dihapus.** Fungsi murni yang diangkat
  tapi hanya teruji lewat komponennya cuma berpindah tempat, belum jadi sumber kebenaran.
  Dan jalur lama yang dibiarkan hidup **adalah** duplikasi fakta yang baru saja dibuat, jadi
  temuannya naik ke §G.

---

## Klasifikasi severity

```
KRITIS                              INFORMASIONAL
├─ Lapisan glue (rute/binding)      ├─ Nama field & tag bson
├─ Hak akses & visibilitas          ├─ Kontrak API & kompatibilitas mundur
├─ Kelengkapan enum & nilai baru    ├─ Frontend (i18n, filter, format, komponen)
├─ Konkurensi & keutuhan data       ├─ Celah test
├─ Batas kepercayaan input          ├─ Deploy & konfigurasi
├─ Alur pengguna terputus           ├─ Kode mati & konsistensi
└─ Satu fakta dua tempat (§G)       └─ Abstraksi kelewat dini (§N)
```

---

## Heuristik Fix-First

```
PERBAIKI LANGSUNG                    TANYAKAN DULU
├─ Kode mati / variabel tak terpakai ├─ Keamanan (auth, escape, injection)
├─ N+1 yang jelas                    ├─ Konkurensi / atomisitas
├─ Komentar basi                     ├─ Keputusan desain
├─ Angka ajaib -> konstanta bernama  ├─ Fix > 20 baris
├─ Ambang ditulis ulang -> impor     ├─ Kelengkapan enum
│  konstanta yang sudah ada          ├─ Menghapus fungsionalitas
├─ Key i18n hilang di salah satu     ├─ Menyatukan dua penulis satu
│  locale                            │  field (mis. `weight`)
├─ Format tanggal pindah ke render   ├─ Mengangkat abstraksi baru
└─ Ketidakcocokan versi/path         └─ Apa pun yang mengubah perilaku
                                        yang terlihat user
```

Patokan: bila fix-nya mekanis dan senior engineer akan menerapkannya tanpa diskusi,
perbaiki langsung. Bila engineer yang wajar bisa berbeda pendapat, tanyakan.
Temuan kritis condong ke TANYAKAN (risikonya lebih besar), informasional condong ke
PERBAIKI LANGSUNG.

---

## JANGAN dilaporkan

- **Plaintext credentials di dok IT vault** (`IT - Server, VMs and Databases`,
  `IT - Monitoring System`) **DISENGAJA** sebagai referensi akses internal tim IT. Jangan
  diflag sebagai isu keamanan, jangan usulkan rotasi atau scrub.
- **Status CI erp-frontend — jangan disinggung sama sekali.** Jangan membacanya sebagai
  sinyal, jangan menyimpulkan kode aman darinya, dan jangan menyuruh siapa pun
  memperbaikinya. Aturannya sempat ditulis dua kali dalam satu hari dan salah dua-duanya,
  karena yang sedang dikodekan bukan sifat repo ini melainkan keadaan yang berubah-ubah.
  Aturan yang berulang kali meleset akan diabaikan seluruhnya, termasuk bagiannya yang
  benar.
- **`pnpm test` erp-frontend tidak pernah hijau penuh di `main`.** Bandingkan kegagalan
  dengan baseline `origin/main` sebelum menyalahkan perubahan sendiri. **Verifikasi lokal
  satu-satunya yang dipercaya**, terlepas dari apa pun yang tampil di CI.
- Redundansi yang tidak berbahaya dan justru menolong keterbacaan.
- "Tambahkan komentar yang menjelaskan ambang ini" (ambang berubah saat tuning, komentar
  membusuk).
- Saran konsistensi murni tanpa dampak perilaku.
- "Regex tidak menangani kasus X" ketika input-nya terbatas dan X tak pernah terjadi.
- **Apa pun yang SUDAH ditangani di diff yang sedang direview.** Baca diff utuh dulu.
