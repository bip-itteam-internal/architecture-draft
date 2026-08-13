## Deskripsi

*Register Perizinan & Sertifikasi adalah workspace ERP pertama untuk posisi **Staf Legal**: satu daftar terpusat izin & sertifikat perusahaan (izin edar BPOM, sertifikat Halal, izin usaha, sertifikasi lain) berikut masa berlakunya, dengan penanda **alert H-90** sebelum kedaluwarsa. Dibangun sebagai bagian dari inisiatif "satu workspace per posisi" (branch `feature/workspace-position`) — memberi jejak kerja di ERP bagi posisi yang sebelumnya bekerja di luar sistem, sehingga KPI-nya kelak bisa dihitung otomatis. Fitur unggah PDF sertifikat dan register Kontrak/Dispute menyusul.*

- **Stack**: Go (Fiber, di-host di employee-service) + MongoDB (`legal_license`) + JWT/`system_roles` sebagai pembawa peran; frontend Next.js (App Router, TanStack Query).
- **Path di repo**:
  - Backend: `bip-erp/services/employee/{legal_perizinan.go,legal_kontrak.go,legal_dispute.go}` (routes+handler CRUD) · gerbang izin `services/employee/secretary_gate.go` (`gateSecretary`) · katalog `shared-library/common/catalog_secretary.go` · model `LegalLicense`/`LegalContract`/`LegalDispute` di `bip-erp/shared-library/models/employee/models.go` · collection `legal_license`/`legal_contract`/`legal_dispute` · gerbang tier lama `RequireLegalStaff`/`RequireLegalSupervisor` di `bip-erp/shared-library/common/roles.go` (kini dipakai sebagai fallback kill-switch). Unggah PDF memakai endpoint generik `POST /upload` yang sudah ada (`minio.UploadSingleHandler`).
  - Frontend: `erp-frontend/src/app/(main)/legal/{perizinan,kontrak,dispute}/page.tsx` · `erp-frontend/src/features/legal/{perizinan,kontrak,dispute}/*` (types, hooks fetch/upsert/delete, form modal) · helper unggah `features/legal/shared/upload.ts` · helper daftar `features/legal/shared/daftar.ts` (pencarian + param penyaring) · tiga entri menu di blok **`secretary`** pada `src/components/layout/sidebar-menus.tsx` (**bukan** `sidebar.tsx`) · alias kategori `src/components/layout/modul-aktif.ts` · gating rute di `src/proxy.ts`.
- **Status**: ⚠️ Implemented (ada catatan). Ketiga register (Perizinan, Kontrak & SLA, Dispute & Advis) + **unggah PDF** **live di kode**, dan sejak **2026-08-13 modulnya bukan `legal` lagi melainkan `secretary`** (Kesekretariatan) bersama R&D — lihat blok di bawah. Rute `/legal/*` **tidak berubah**. **Backend terverifikasi live di dev 2026-08-13** lewat gateway: katalog `secretary` muncul dengan 6 izin, kelima rute baca membalas 200 untuk pemegang peran, 403 untuk yang tidak, dan satu izin benar-benar dibuat lalu dihapus lewat `/api/employee/legal/licenses`. **Frontend-nya belum di-deploy** ke dev, jadi ketiga pemeriksaan sidebar masih menunggu. Pemisahan ke service `legal` tersendiri **belum** (dan kini kecil kemungkinannya).

> [!warning] Merge TIDAK men-deploy, dan itu bukan soal modul ini
> Saat PR mendarat 2026-08-13 10:12 WIB, dev masih menjalankan container yang dibuat **17 jam sebelumnya** dan repo servernya tertinggal **9 commit**. Frontend sama. Delegate Harness `Up`, tapi tak satu pun merge sejak sore sebelumnya pernah naik. Backend ini akhirnya di-deploy manual (`docker compose up -d --build employee-service --no-deps`, build 89 detik).
>
> Pelajarannya untuk dok mana pun: **"merged" bukan "live"**. Buktikan dengan probe API yang hanya dikenali kode baru, bukan dengan umur container dan bukan dengan status PR.

> [!info] Modul `legal` DILEBUR ke `secretary` (2026-08-13)
> Register ini tak lagi berdiri sebagai modul sendiri. Ia kini satu dari dua **area** di
> dalam modul **`secretary`** (Kesekretariatan), bersama [[QA - R&D Regulatory (Registrasi & Pipeline Produk)]].
>
> | | Sebelum | Sesudah |
> |---|---|---|
> | Kunci modul | `legal` | `secretary` |
> | Izin | `legal.view/work/manage` | `secretary.legal.view/work/manage` |
> | Paket | `legal_lihat`/`legal_pelaksana`/`legal_admin` | `secretary_legal_lihat`/`_pelaksana`/`_admin` |
> | Gerbang | `gateLegal` | `gateSecretary` |
> | Kill-switch | `LEGAL_PERMISSION_ENFORCEMENT` | `SECRETARY_PERMISSION_ENFORCEMENT` (nama lama tetap dibaca sebagai alias) |
> | Kategori sidebar | `LEGAL` | `SEKRETARIAT` |
> | Rute halaman | `/legal/*` | **`/legal/*`, tidak berubah** |
>
> **Rutenya sengaja tidak ikut pindah.** `menu_hidden` menyimpan URL dan mencocokkannya
> persis, jadi memindahkannya ke `/sekre/*` akan membatalkan setelan Tampilan Menu tiap
> jabatan secara senyap.
>
> **Peran `system_roles.legal` tetap hidup** sebagai tier fallback dan sebagai sumbu yang
> menentukan menu serta lolosnya `proxy.ts` — lihat catatan tiga lapis di
> [[CORE - RBAC dan Permission Set]]. Yang berubah pemiliknya, bukan jalurnya.
>
> Alasan penggabungan ada di sensus produksi di bagian **Belum Diimplementasikan** di bawah,
> dan keputusannya adalah pilihan kedua yang ditawarkan sensus itu.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| Staf Legal | jabatan **`Legal`** di department **`secretary`** (Kesekretariatan) | peran `legal:staff` diturunkan dari jabatan (`peran_dari_jabatan.go`), atau paket **Sekretariat: Legal Pelaksana** — buat/edit/lihat izin | Web ERP |
| Legal Supervisor | department `secretary` | peran `legal:supervisor` atau paket **Sekretariat: Legal Admin** — termasuk hapus izin | Web ERP |
| Supervisor / admin IT | Tech Development | super-akses ke seluruh 25 rute, bertahan juga di fase dua | Web ERP |

⚠️ Baris pertama BERUBAH 2026-08-13. Sebelumnya persona ini digantungkan pada department
`legal` yang **tak pernah ada di produksi**; kini ia jabatan di dalam Kesekretariatan, yang
memang tempat orangnya duduk.

- **Tujuan**: satu layar yang menjawab "izin apa yang segera habis" tanpa menyusuri folder/berkas fisik.
- **Pain point**: pemantauan masa berlaku izin hari ini manual (spreadsheet), sehingga perpanjangan sering baru disadari mepet tenggat.
- **Aksi utama**: catat izin baru, perbarui status perpanjangan, pantau alert H-90.

## Fitur (Sudah Diimplementasikan)

**Register Perizinan & Sertifikasi** — di-host di employee-service, dipanggil FE lewat prefix gateway `/api/employee/legal/...`:
- `GET /legal/licenses` — daftar izin (filter opsional `?license_type=` & `?status=`). Gate `RequireLegalStaff`.
- `GET /legal/licenses/:id` — detail satu izin (`_id` ObjectID). Gate `RequireLegalStaff`.
- `POST /legal/licenses` — buat izin (`name` + `license_type` wajib). Gate `RequireLegalStaff`.
- `PUT /legal/licenses/:id` — perbarui izin (metadata `created_*` dipertahankan). Gate `RequireLegalStaff`.
- `DELETE /legal/licenses/:id` — hapus izin. Gate `RequireLegalSupervisor`.
- Model `LegalLicense`: `name`, `license_type` (BPOM/Halal/Izin Usaha/Sertifikasi/Lainnya), `number`, `issuer`, `pic`, `status` (Aktif/Dalam Perpanjangan/Kedaluwarsa/Tidak Perlu), `issued_at` & `expires_at` (ISO `YYYY-MM-DD`, string agar bebas dari friksi parse `time.Time`), `notes`, `file_object`+`file_name` (PDF sertifikat), `metadata`.
- **Alert H-90 dihitung di sisi UI** dari `expires_at`: badge `H-{n}` (≤90 hari) / `Kedaluwarsa` (lewat tenggat) di halaman `/legal/perizinan`.

**Register Kontrak & SLA Legal** (`legal_kontrak.go`, collection `legal_contract`):
- `GET/POST /legal/contracts`, `GET/PUT /legal/contracts/:id` (gate `RequireLegalStaff`), `DELETE` (gate `RequireLegalSupervisor`). Filter `?contract_type=`&`?review_status=`.
- Model `LegalContract`: `name`, `counterparty` (pihak), `contract_type`, `value` (Rp), `review_status` (Draft/Review/Aktif/Selesai/Berakhir), `start_date`/`end_date`, `pic`, `notes`, `file_object`+`file_name`. **Alert jatuh tempo H-60** dari `end_date` di UI.

**Register Dispute & Advis Hukum** (`legal_dispute.go`, collection `legal_dispute`):
- `GET/POST /legal/disputes`, `GET/PUT /legal/disputes/:id` (gate `RequireLegalStaff`), `DELETE` (gate `RequireLegalSupervisor`). Filter `?dispute_type=`&`?status=`.
- Model `LegalDispute`: `title`, `dispute_type` (Vendor/Karyawan/Pajak/Regulasi/Lainnya), `counterparty`, `risk_value` (Rp), `status` (Terbuka/Proses/Advis/Selesai), `chronology`, `advice`, `notes`, `file_object`+`file_name`.

**Unggah PDF** — reuse endpoint generik `POST /api/employee/upload` (field multipart `file`, `minio.UploadSingleHandler`) yang sudah ada; FE (`features/legal/shared/upload.ts`) unggah lebih dulu, simpan `full_url`→`file_object` di payload. Tiap halaman menautkan `file_object` (buka PDF di tab baru).

- **Frontend**: tiga halaman list (Perizinan/Kontrak/Dispute) + modal create/edit (react-hook-form + zod) + hapus (ActionDialog) + unggah PDF. Tiga menu muncul di sidebar untuk pemegang role `legal`; rute `/legal/*` digating di `proxy.ts`. Sejak branch `refactor/legal-struktur-halaman-hris` (⚠️ **belum merge**) ketiganya memakai **struktur halaman HRIS** berikut pencarian, penyaring, paginasi, export, dan i18n dua bahasa — rinciannya beserta alasan tiap keputusan di [[APP - Web ERP]] bagian **Legal**.
- **RBAC & seed**: sejak [#1117](https://github.com/bip-itteam-internal/bip-erp/pull/1117) (**merged 2026-08-09**) modul ini berkatalog penuh dengan tiga izin `legal.*` lewat `gateLegal`. Sejak **2026-08-13** katalognya dilebur ke modul `secretary`: ketiga izin jadi `secretary.legal.view|work|manage`, gerbangnya `gateSecretary`, dan paket bawaannya **Sekretariat: Legal Lihat / Pelaksana / Admin** (reach `all`). Isi Pelaksana & Admin persis mencerminkan `legal:staff` dan `legal:supervisor` hari ini, dikunci `TestPaketBawaanSecretaryCerminTierHariIni`; paket **Lihat** tetap kemampuan BARU yang tak punya padanan tier. Department `legal` **dicabut dari `DefaultDepartments`** (ia tak pernah lahir di lingkungan mana pun). Migrasi `migrasiPaketLegalKeSecretary` menulis ulang assignment paket lama, dan shim baca di `common.IzinSecretaryEfektifDari` menjaga yang lolos dari migrasi itu. Rincian keputusan: [[CORE - RBAC dan Permission Set]].

## Belum Diimplementasikan / Catatan

> [!warning] Sensus produksi 2026-08-09: modul ini **tidak dipakai siapa pun**, dan tak bisa dipakai
> Dihitung langsung ke `employee_db` produksi:
>
> | | |
> |---|---|
> | total akun (`system_authentication`) | 208 |
> | punya `system_roles.legal` | **0** |
> | supervisor IT (super-akses) | 12 |
>
> **Nol, bukan sedikit.** Sebabnya berantai dan tak satu pun ada di kode register ini:
>
> 1. **Departemen `legal` tak ada di produksi.** `master_department` berisi 12 dokumen — `hris`, `ga`, `it`, `secretary`, `finance`, `beauty_hacks`, `kyura`, `manufacture`, `quality`, `procurement`, plus **`marketing`** dan **`pct`** yang tak pernah ada di seed. Master data prod sudah lama dikelola manual.
> 2. **Deploy tak akan membuatnya.** `seedMasterDepartments` (`services/employee/master_data.go`) berhenti total begitu koleksinya tidak kosong — ia tidak menambahkan yang kurang, melainkan melewati semuanya. Prod punya 12, jadi seed tak pernah jalan lagi.
> 3. **Tanpa departemen `legal`, dropdown role di Master Data tak punya pilihan `legal`**, jadi HR tak bisa memberikannya kepada siapa pun.
>
> Praktisnya modul ini hanya bisa dibuka **12 supervisor IT** lewat super-akses. Itu sebabnya cabang super-akses IT di `catalog_legal.go` bukan pelengkap melainkan satu-satunya yang menahan modul ini tetap terbuka.
>
> Dan orangnya sebenarnya ada: **satu** karyawan berjabatan legal di produksi, `BIP-0184-08-25`, departemen **Kesekretariatan**, jabatan `Legal` — persis posisi yang jadi alasan register ini dibangun. Ia duduk di `secretary`, bukan di departemen `legal` yang di-seed, dan tak punya akses ke modulnya sendiri.
>
> **Yang perlu diputuskan orang, bukan kode**: buat departemen `legal` di Master Data prod lalu assign rolenya, ATAU akui Legal memang tinggal di Kesekretariatan dan sesuaikan `deptKeyToNames`.
>
> ✅ **DIPUTUSKAN 2026-08-13: pilihan KEDUA.** Modul `legal` dilebur ke `secretary`, dan
> jabatan `Legal` di Kesekretariatan kini menurunkan peran `legal: staff` lewat
> `peran_dari_jabatan.go`. `deptKeyToNames` tidak disentuh (entri `legal` dibiarkan sebagai
> pemetaan inert untuk akses KPI); yang berubah adalah modul mana yang memiliki register ini.

> [!note] Pengukuran ulang 2026-08-13: dev ternyata sama kosongnya dengan prod
> Diukur langsung ke `employee_db` dev sebelum perubahan dikerjakan:
>
> | | |
> |---|---|
> | departemen di `master_department` dev | **10** — `legal` dan `rnd` **tidak ada**, sama seperti prod |
> | akun ber-`system_roles.legal` atau `.rnd` | **0** |
> | assignment paket `legal_*` (akun maupun posisi) | **0** |
> | pemegang jabatan `Legal` / `QA RND` di Kesekretariatan (dev) | **0** |
>
> Dua akibatnya. Pertama, mencabut kedua departemen dari `DefaultDepartments` **nol dampak
> di mana pun** — seed-nya memang tak pernah jalan lagi sejak koleksinya terisi. Kedua,
> **dev tak punya akun untuk menguji fitur ini**: verifikasi lewat gateway menuntut akun uji
> berposisi `Legal` dibuat lebih dulu. Pengukuran yang sama di PROD belum dijalankan.

- **Unggah PDF pakai bucket `uploads/` generik**: berkas disimpan lewat `POST /upload` (prefix `uploads/`, bukan `legal/...` khusus) dan `file_object` menyimpan `full_url` publik langsung — belum ada preview presigned/akses berbasis-peran. Cukup untuk sekarang; perlu ditinjau bila dokumen legal harus dibatasi.
- **Hosting sementara di employee-service** (TBD): dipilih agar tidak menambah modul gateway/URL baru (menghindari panic `ValidateInternalURL`) dan bisa langsung boot. Bila beban Legal tumbuh, ekstrak ke service `legal` tersendiri (env `LEGAL_MODULE_URL` + entri `InternalURL` di [[CORE - API Master Gateway]] + service data-owning meniru [[Microservices - Recruitment Service]]).
- **Verifikasi runtime**: build Go & typecheck FE lolos; smoke-test end-to-end (login akun `legal`, CRUD terhadap employee-service berjalan) **belum dijalankan** — perlu redeploy `docker-compose.dev.yml`. Yang khususnya tak bisa ditutup test: apakah nilai enum penyaring (`Aktif`, `BPOM`, `Draft`, dst) benar-benar cocok dengan yang tersimpan di Mongo. Bila meleset, gejalanya tabel kosong **tanpa satu pun pesan galat**.
- ⚠️ **Tombol Hapus tampil untuk `legal:staff` yang tak berhak.** DELETE digerbangi `RequireLegalSupervisor` di backend, sementara frontend merender `ActionDialog` tanpa memeriksa peran — staf menekan Hapus, mengkonfirmasi dialognya, lalu dapat toast gagal. Ada sejak register ini lahir; **belum diperbaiki**.
- **Penyaring backend sempat dirakit tanpa pemanggil.** `license_type`, `status`, `contract_type`, `review_status`, dan `dispute_type` diterima handler sejak awal dan tak pernah dikirim frontend sampai `refactor/legal-struktur-halaman-hris`. Sekelas dengan `formRequest` yang tak punya field `recurrence` di form-builder: dirakit benar, tak dibaca siapa pun, nol test merah. **Pencarian teks masih tak ada di backend** dan dikerjakan di klien; sah selama register ini masih puluhan baris, perlu ditinjau ulang bila tumbuh.
- **Domain**: perizinan (BPOM/Halal/izin edar) masuk cakupan Quality & Regulatory; sebagian isi (izin usaha, kontrak) beririsan dengan fungsi Legal/GA. ✅ **Tiga representasi legal di master data kini tinggal dua** (2026-08-13): department `legal` dicabut dari `DefaultDepartments`, menyisakan posisi `Legal` di `secretary` (yang dipakai, dan yang haknya diturunkan) serta posisi `Legal Staff` di `ga` (yang tak dipetakan ke modul apa pun — lihat [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]]). Menyatukan dua sisa itu adalah keputusan master data, bukan kode. Lihat [[HRIS - Organization Structure]].

## Dependensi & Integrasi

- [[Microservices - Employee Service]] — host endpoint `/legal/*`, koneksi Mongo, seed department.
- [[CORE - API Master Gateway]] — meneruskan `/api/employee/legal/*` + header `BIP-*` (termasuk `BIP-System-Roles` yang dipakai `RequireLegal*`).
- [[CORE - RBAC dan Permission Set]] — modul `secretary`, izin `secretary.legal.*`, dan tier lama `system_roles.legal` yang tetap dipakai sebagai fallback.
- [[QA - R&D Regulatory (Registrasi & Pipeline Produk)]] — area kedua di modul yang sama; keduanya satu kategori sidebar tapi haknya tetap terpisah.
- [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]] — jabatan `Legal` di Kesekretariatan menurunkan peran `legal: staff`, yang menentukan menu dan lolosnya `proxy.ts`.
- [[APP - Web ERP]] — kategori sidebar SEKRETARIAT (gating, halaman Perizinan/Kontrak/Dispute, struktur halaman HRIS).
- [[HRIS - Organization Structure]] — posisi `Legal` di `secretary` dan `Legal Staff` di `ga` yang masih berdampingan.
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]] — namespace `legal.*` di kedua locale.

## Dokumen Terkait

- [[Microservices - Employee Service]]
- [[CORE - RBAC dan Permission Set]]
- [[APP - Web ERP]]
- [[HRIS - Organization Structure]]
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]
