## Deskripsi

*Form Builder Service adalah pembuat form dinamis tanpa coding: sebuah departemen menyusun form sendiri (9 tipe pertanyaan), menerbitkannya ke sasaran tertentu, membaca rekap jawabannya, dan mengekspornya ke CSV — tanpa rilis kode untuk tiap form baru. Service ini juga menyediakan satu endpoint kepatuhan yang dipakai [[Microservices - Attendance Service]] untuk menahan clock-in mobile bila ada form wajib yang belum diisi.*

- **Stack:** Go + Fiber v2 + MongoDB (database sendiri `form_builder_db`)
- **Path:** `services/form-builder`
- **Port:** 6986 (internal, `expose`; tidak dipublish ke host)
- **Status**: ⚠️ **Implemented & LIVE di dev** (PR [#849](https://github.com/bip-itteam-internal/bip-erp/pull/849) + perbaikan [#855](https://github.com/bip-itteam-internal/bip-erp/pull/855)); terverifikasi end-to-end lewat gateway dev 2026-08-01. **PROD belum jalan** — container-nya belum pernah dibuat. FE web di [[APP - Web ERP]] sudah lengkap (kelola, builder, **analisa jawaban**), dan pengisian di [[APP - MyBharata]] sudah ada (section Survei di beranda + halaman isi 9 tipe). **Kepemilikan per departemen** menunggu merge PR [#869](https://github.com/bip-itteam-internal/bip-erp/pull/869).

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| Staf/SPV IT | Tech Development | Peran staff/supervisor/admin + departemen `Tech Development` aktif | Web |
| Staf/SPV HRGA | Human Resource · General Affair | Idem; SPV HRGA membawahi keduanya lewat `supervised_by` | Web |
| Karyawan | Semua divisi | Terautentikasi (tanpa syarat peran) | Mobile (MyBharata), Web |

- **Tujuan** — pemilik form: membuat form ad-hoc (survei, deklarasi, pendataan) tanpa menunggu rilis kode, lalu membaca hasilnya. Karyawan: mengisi form yang ditujukan kepadanya.
- **Pain point** — sebelum ini setiap form baru berarti satu siklus development; permintaan pendataan mendadak tak terlayani.
- **Aksi utama** — pemilik form: susun pertanyaan → tentukan sasaran → terbitkan → baca analisa/export. Karyawan: buka daftar form → isi → kirim.

> Peran `security` milik GA (satpam) **sengaja dikecualikan** dari pengelola form: tingkat perannya bukan staff/supervisor/admin, jadi tak pernah lolos gerbang.

## Endpoint / Fitur (Sudah Diimplementasikan)

Prefix gateway `/api/form-builder/*`. Kontrak lengkap: [[API - Form Builder Service]].

**Kelola form** (gerbang `requireFormManager`: tingkat peran pengelola + departemen aktif)
- `POST /forms` · `GET /forms` — buat & daftar form. Daftar **hanya menampilkan form milik departemen dalam cakupan pemanggil**, jadi tim GA tak melihat form IT.
- `GET /forms/:id` · `PATCH /forms/:id` · `DELETE /forms/:id` — detail, sunting, hapus lunak (`deleted_at`).
- `PATCH /forms/:id/status` — `draft` → `published` → `closed`. Form terbit **tidak bisa mundur** ke draft.
- `owner_department` tak bisa dipindah setelah dibuat (memindahkannya akan membuat form lenyap dari daftar pemiliknya sendiri).
- `GET /me/capability` — `{can_manage, departments[]}` untuk klien, supaya daftar departemen aktif tak perlu disalin ke FE.
- **Susunan pertanyaan terkunci begitu ada jawaban masuk** (balas `409`). Menyunting field setelah orang menjawab membuat jawaban lama menunjuk pertanyaan yang sudah berubah arti, dan analisanya diam-diam jadi salah.

**Tipe pertanyaan (9)** — `short_text`, `long_text`, `number`, `date`, `time`, `dropdown`, `radio`, `checkbox`, `scale`. Validasi struktur (key unik, options wajib untuk tipe pilihan, rentang scale maksimal 10 langkah, `min ≤ max`) dan validasi jawaban (tipe cocok, nilai ∈ options, batas angka & panjang teks, format `YYYY-MM-DD` dan `HH:MM`) keduanya **fungsi murni** — teruji tanpa Mongo.

**Bagian (`section`)** — penanda pemisah halaman, bukan pertanyaan. Lihat bagian tersendiri di bawah.

**Sasaran form (audience)** — `all`, `departments`, atau `employees`. Diresolusi dari **header identitas yang sudah dibawa gateway** (`BIP-Employee-ID`, `BIP-Department`), sehingga service ini **tak memanggil satu service pun**. Tipe sasaran yang tak dikenal **gagal-tertutup** (tidak cocok), supaya salah ketik tak pernah menahan presensi sekantor.

**Pengisian** (cukup karyawan terautentikasi)
- `GET /me/forms` — form terbit yang ditujukan ke pemanggil, lengkap dengan penanda `submitted` dan `blocks_attendance`.
- `POST /me/forms/:id/responses` — kirim jawaban. Form non-`published` ditolak, dan bukan-sasaran ditolak `403`.
- `GET /me/responses` — riwayat jawaban sendiri.
- **Idempoten**: pengiriman identik dalam 2 menit dianggap retry dan dibalas sukses tanpa insert baru. Sidiknya di-hash dari jawaban yang **kuncinya diurutkan lebih dulu**, jadi klien yang menyusun ulang payload saat retry tetap terdeteksi. Pola sejenis dipakai leave request di [[Microservices - Attendance Service]].
- `settings.single_response` membatasi satu jawaban per karyawan (balas `409`).

**Analisa & export**
- `GET /forms/:id/analytics` — hitungan per opsi (**termasuk opsi ber-nol, urut sesuai definisi form** supaya grafik tak berganti susunan tiap data bertambah), rata-rata/min/maks untuk `number` & `scale`, cuplikan 5 jawaban teks terbaru, `answered`/`skipped` per pertanyaan, tren harian, dan tingkat pengisian.
- `GET /forms/:id/responses` — daftar jawaban berhalaman.
- `GET /forms/:id/export` — CSV; satu pertanyaan = satu kolom secara konsisten, checkbox digabung `"; "` dalam satu sel, angka tanpa nol berlebih.

**Kepatuhan presensi**
- `GET /internal/compliance` — dipakai attendance-service saat clock-in. Membalas `blocking` (mode `block`) dan `warning` (mode `warn`).

## Kepemilikan form: departemen, bukan modul

Sampai PR #869, pemilik form adalah key `system_roles` (`it`/`ga`). Itu **salah sumbu**: `system_roles` adalah hak akses modul/menu, bukan hierarki organisasi (lihat [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]). Akibatnya orang yang kebetulan punya peran di dua modul melihat form dua tim sekaligus — SPV HRD sempat melihat form IT di daftarnya.

Sekarang:

- **Pemilik** = `owner_department`, nilai `master_department` (mis. `"General Affair"`).
- **Cakupan** = `common.SupervisedDepartments` (departemen sendiri + yang dibawahi lewat `master_department.supervised_by`) **diiris** daftar departemen aktif. Pola yang sama sudah dipakai `services/recruitment/rbac.go`.
- **Departemen aktif** = env `FORM_BUILDER_DEPARTMENTS` (dipisah koma). Bila kosong dipakai bawaan `Human Resource, General Affair, Tech Development`. Defaultnya sengaja ada: daftar kosong berarti tak seorang pun bisa membuka Form Builder, jadi env yang lupa diisi akan mematikan fitur tanpa pesan galat yang menjelaskan sebabnya.
- **Tingkat peran** tetap `staff`/`supervisor`/`admin` di modul mana pun. Key `group` **dikecualikan** — itu penanda jangkauan lintas-perusahaan (`common.IsCentralAdmin`), bukan modul; tanpa pengecualian ini setiap admin grup jadi pengelola Form Builder.

Hasilnya "HRGA" tak pernah jadi nilai tersimpan di mana pun: ia gabungan dua departemen yang muncul sendiri dari master data, persis seperti di [[HRIS - Organization Structure]].

> [!warning] Dua jebakan yang sudah ditutup, keduanya diam-diam
> **Kanonikalisasi ejaan.** Penyaringan daftar memakai `$in` Mongo yang PEKA HURUF. Kiriman `"tech development"` lolos pemeriksaan akses (yang tak sensitif huruf) lalu tersimpan apa adanya — formnya berhasil dibuat dan **langsung lenyap dari daftar pembuatnya sendiri**. Karena itu `owner_department` dikanonikkan ke ejaan daftar aktif saat menulis.
>
> **Backfill saat boot, bukan skrip manual.** Begitu versi ini naik, form yang masih menyimpan `owner_module` tak cocok filter mana pun: hilang dari daftar dan menolak dibuka dengan `403`. Dev deploy-nya otomatis dari `main`, jadi jedanya tak bisa dijadwalkan. Pemindahan dijalankan idempoten saat boot (`it`→`Tech Development`, `ga`→`General Affair`), bersama pembuatan index.

**Siapa yang berubah aksesnya**: staf HR (`hris:staff`) yang dulu terkunci kini bisa membangun form; pemegang peran `it`/`ga` yang departemennya di luar daftar aktif kehilangan akses; karyawan tanpa `department` di `work_data` kini tertutup (fail-closed, disengaja untuk perubahan kontrol akses). Token berlaku 72 jam, jadi SPV HRGA yang belum login ulang sementara hanya melihat departemennya sendiri — fallback `SupervisedDepartments` menanganinya tanpa error.

## Bagian (section): penanda di daftar datar, bukan struktur bersarang

Form panjang bisa dipecah jadi beberapa halaman saat diisi. Bagian disimpan sebagai **item bertipe `section` di dalam `fields` yang tetap datar** — `label` jadi judulnya, `description` jadi keterangannya, jadi tak ada penambahan skema.

Tiga bentuk dipertimbangkan; yang dipilih paling murah justru karena bentuk datanya tak berubah:

| Bentuk | Konsekuensi |
|---|---|
| `Form.Sections[]` bersarang berisi `fields[]` | Paling rapi secara konsep, tapi SEMUA pengulang `form.Fields` ikut berubah: validasi, analitik, export, renderer web, renderer mobile. Plus migrasi seluruh form lama |
| `section_index` di tiap field + daftar judul terpisah | Dua sumber kebenaran yang bisa tak sinkron; menggeser urutan jadi rawan |
| **Penanda di daftar datar** ✅ | Reorder, validasi, analitik, dan export cukup MELEWATI penanda. **Tak ada migrasi** |

Penjagaan yang dipasang:

- **Bagian tak bisa diwajibkan.** Kontradiksi: tak ada yang bisa diisi di sana, jadi form-nya jadi mustahil dikirim.
- **Bagian menolak `options`, rentang scale, batas panjang, dan batas angka.** Atribut yang menempel padanya pasti sisa perpindahan tipe, dan membiarkannya lolos berarti menyimpan aturan yang tak pernah dijalankan siapa pun.
- **Jawaban yang menunjuk key bagian ditolak** (`400`). Nilainya tak akan pernah muncul di analisa maupun export, jadi diam-diam hilang.
- **Analisa dan export memakai `questionFields()`**, supaya bagian tak jadi kolom CSV yang selalu kosong maupun kartu analisa hampa.

Bagian tetap wajib punya key unik dan judul, mengikuti aturan field lain. Form yang sudah punya jawaban tetap terkunci (`409`), jadi bagian tak bisa ditambahkan ke form berjalan.

**Pemecahan halamannya terjadi di klien**, bukan di bentuk datanya: [[APP - MyBharata]] memakai `splitSurveyPages()` untuk memecah daftar datar jadi halaman. Form tanpa bagian menghasilkan tepat satu halaman, sehingga perilaku lamanya tak berubah.

## Keputusan yang menjaga presensi tetap hidup

Fitur ini menyentuh jalur clock-in, jadi beberapa keputusan sengaja konservatif:

- **Gerbang gagal-tertutup pada data cacat.** Gerbang tanpa jendela tanggal lengkap dianggap **tidak aktif** (gerbang tanpa tanggal berakhir berarti presensi tertahan selamanya bila form-nya dilupakan). Mode enum yang tak dikenal **turun kelas jadi peringatan**, bukan penahan.
- **`mode` default `warn`** saat form dibuat. Menahan presensi harus jadi pilihan yang ditulis eksplisit.
- **Jendela tanggal wajib** saat gerbang menyala.
- **Identitas `/internal/compliance` terkunci ke header.** Query param hanya dihormati bila **tak ada** identitas header sama sekali (ciri panggilan service-to-service). Tanpa aturan ini, karyawan mana pun bisa mengirim `?employee_id=<orang-lain>&company_id=<perusahaan-lain>` dan mengintip form tertunda milik orang lain menembus batas tenant — persis kelas bug di [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]. Header aman dijadikan sandaran karena gateway membuang seluruh namespace `BIP-*` kiriman klien lalu mengisinya dari klaim JWT.

## Multi-perusahaan (tenant)

Ter-scope `company_id` **sejak awal**, bukan ditambal belakangan: stempel `common.CompanyID` saat menulis, `common.EffectiveCompanyID` saat membaca (override `?company=` hanya untuk admin pusat). Lihat [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]].

## Belum Diimplementasikan / Catatan

- ✅ **LIVE di dev sejak 2026-08-01.** `form-builder-service` + `form-builder-mongo-db` dijalankan dan `api-gateway` dibangun ulang; `GET /health?check=form-builder` balas `200`. Terverifikasi end-to-end lewat gateway: buat → terbit → isi → analisa → export → hapus.
- ⚠️ **PROD belum**: repo & `.env` sudah siap, gateway prod bahkan sudah mengenal `form-builder` (balas `503`, bukan `400`), tapi **container `form-builder-service` belum pernah dibuat**. Untuk menyelesaikannya: `docker compose build form-builder-service` lalu `docker compose up -d form-builder-mongo-db form-builder-service` (mongo disebut eksplisit karena statusnya masih `created`).
- ⚠️ **attendance-service masih pra-merge di dev dan prod**, jadi gerbang presensi belum aktif di mana pun. Itu aman selama belum ada form ber-mode `block`.
- ✅ **`.env` dev dan prod SUDAH diisi (2026-08-01)**: `FORM_BUILDER_SERVICE_PORT=6986` + `MONGO_FORM_BUILDER_DB=form_builder_db`. Diverifikasi lewat `docker compose config` di kedua server — `FORM_BUILDER_MODULE_URL` merender `http://form-builder-service:6986` di blok gateway maupun attendance. Backup disimpan (`~/apps/bip-erp/.env.bak-*`). Port 6986 bebas di keduanya.
- ⚠️ **Kenapa dua variabel itu wajib ada SEBELUM gateway di-redeploy.** Berbeda dari attendance (yang sengaja menaruh URL form-builder DI LUAR map tervalidasi), gateway memasukkan `form-builder` ke `InternalURL` dan menjalankan `validation.ValidateInternalURL` — nilai kosong berarti **gateway panic saat boot dan SELURUH ERP ikut mati**. `docker-compose.yml` meredam ini karena nilainya dirakit dari string literal (`http://form-builder-service:${...}`) sehingga tak pernah benar-benar kosong, tapi variabel port yang hilang tetap menghasilkan URL rusak dan semua `/api/form-builder/*` gagal. Deploy gateway HARUS memakai compose yang ikut ter-merge, bukan env lama.
- **Konsumen**: [[APP - Web ERP]] memakai seluruh rute `/forms*` **termasuk** `analytics`, `responses`, dan `export` (halaman analisa, erp-frontend PR #683).
- ✅ **Pengisian (`/me/*`) sudah punya konsumen**: [[APP - MyBharata]] (my-bharata PR #93, merged) — section Survei di beranda + halaman isi 9 tipe. Web sengaja tetap tak menyediakan halaman isi form.
- ⚠️ **Gerbang mode `block` tetap belum boleh dinyalakan di produksi**: `form-builder-service` belum jalan di prod DAN attendance-service masih pra-merge. Lihat [[IT - Form Builder]].
- ⚠️ **`FORM_BUILDER_DEPARTMENTS` belum diisi di `.env` mana pun** — tak masalah, bawaannya sudah benar. Isi hanya bila daftarnya mau berbeda.

> [!warning] Gotcha yang sudah menggigit: BSON tak sama dengan JSON
> **PR #855, ditemukan di dev 2026-08-01.** Pertanyaan checkbox melaporkan SEMUA opsi bernilai nol dan kolom CSV-nya keluar sebagai `[Tidak ada]` lengkap dengan kurung siku, padahal datanya tersimpan benar di Mongo.
>
> Sebabnya driver Mongo men-decode array BSON menjadi **`primitive.A`**, yaitu tipe **BERNAMA** (`type A []interface{}`). Type switch `case []interface{}:` **tidak cocok dengan tipe bernama**, jadi setiap nilai yang dibaca **kembali** dari database gagal dikenali sebagai daftar lalu jatuh ke `fmt.Sprintf("%v")`. Jalur TULIS aman karena nilainya masih dari JSON — itulah kenapa validasi saat submit tak pernah menolak apa pun dan bug ini lolos sampai dev.
>
> Perbaikannya memakai **reflection** (`reflect.Kind() == Slice`), bukan mendaftar tipe satu per satu, supaya bentuk lain ikut tertangani.
>
> **Pelajaran yang berlaku untuk service mana pun di repo ini:** 122 unit test service ini semuanya hijau saat bug ini hidup, karena setiap fixture dirakit tangan sebagai `[]interface{}` dan tak satu pun melewati BSON. Uji dengan data buatan sendiri **tidak** menguji lapisan decode database. Regresinya dikunci di `bson_values_test.go` memakai `primitive.A` asli.
- **Upload file** belum didukung (menyusul via [[Microservices - File Service]], cap 4 MB).
- **Logika percabangan** (lompat seksi berdasarkan jawaban) belum ada.
- **Jumlah sasaran tidak dihitung otomatis.** Untuk sasaran `all`/`departments`, penyebut tingkat pengisian memakai `audience.estimated_size` yang diisi manual pembuat form — service ini sengaja tak memanggil employee-service. Bila kosong, tingkat pengisian **tidak dilaporkan** (menampilkan 0% lebih menyesatkan daripada tak menampilkan apa pun).
- **Agregasi dibatasi 20.000 jawaban.** Bila terlampaui, total sebenarnya tetap dilaporkan dan hasil ditandai `truncated` + `sample_size`, sedangkan tingkat pengisian disembunyikan. Export menandai lewat header `X-Export-Truncated`.
- **`attendance_gate.start_date`/`end_date` hanya menerima RFC3339** (mis. `2026-08-01T00:00:00Z`); kiriman `"2026-08-01"` akan ditolak dengan pesan parse JSON yang tidak informatif. Perlu dibereskan saat FE dibangun.
- **RBAC belum berkatalog permission-set** per [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]. Pindah ke sumbu departemen **mendekatkan** ke ADR itu (hak menempel pada tempat orang bekerja, bukan pada key modul) tapi belum memenuhinya: tingkat perannya masih tier lama `staff`/`supervisor`/`admin`, bukan permission-set granular.
- ✅ **Section/multi-halaman sudah ada** (PR [#870](https://github.com/bip-itteam-internal/bip-erp/pull/870), belum merged).
- **Upload file, percabangan, grid, dan opsi "Lainnya" belum ada** — jarak yang tersisa terhadap Google Forms. Urutan yang disarankan: opsi "Lainnya" (murah) → upload file → percabangan. Percabangan menuju bagian, jadi kini sudah punya landasannya.
- **Analisa belum mengelompokkan hasil per bagian.** Yang dijamin sekarang hanya bagian tak muncul sebagai kartu kosong; pengelompokan visualnya polesan yang belum dikerjakan.
- **Form approval yang sudah matang JANGAN dimigrasikan ke sini** (leave/overtime/koreksi presensi) — semuanya punya workflow & rantai approval sendiri. Form Builder untuk kasus baru/ad-hoc.

## Dependensi & Integrasi

- **MongoDB** `form_builder_db` — koleksi `forms`, `form_responses`. Index dibuat idempoten saat boot. Lihat [[DB - Overview and Notes]].
- [[CORE - API Master Gateway]] — satu-satunya pintu masuk; modul `form-builder` di map `InternalURL`.
- [[Microservices - Attendance Service]] — **konsumen** `GET /internal/compliance` pada jalur clock-in mobile.
- Auth mengikuti [[CORE - SSO Flow]]; identitas datang sebagai header `BIP-*`.
- **Tidak memanggil service lain.** Ini disengaja: sasaran form diresolusi dari header, sehingga tak ada entri di `InternalURL` milik service ini dan tak ada service yang bisa membuatnya gagal boot.

## Dokumen Terkait

- [[IT - Form Builder]] — konsep & latar belakang
- [[API - Form Builder Service]] — daftar endpoint
- [[Microservices - Attendance Service]] · [[CORE - API Master Gateway]] · [[DB - Overview and Notes]]
- [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]] · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]
- [[APP - Web ERP]] · [[APP - MyBharata]] — klien yang belum dibangun
