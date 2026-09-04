# ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri

## Untuk Manajemen

- **Yang berubah di layar**: audit internal pindah dari menu di dalam sistem ERP ke **alamat webnya sendiri**, dengan halaman masuk terpisah. Masuknya tetap memakai akun ERP yang sama — tidak ada kata sandi baru untuk dihafal. Isinya sama seperti yang sudah dirancang: kertas kerja bulanan, register temuan, dan pengaturan ukuran sampel milik Direksi.
- **Siapa terdampak**: auditor internal sebagai pemakai utama, Direksi sebagai penerima laporan sekaligus satu-satunya yang menyetel ukuran sampel, dan pembaca yang hanya boleh melihat. Divisi yang diperiksa **tidak** mendapat akses ke sini; mereka tetap pihak yang dimintai klarifikasi.
- **Tidak dijanjikan**: alamat terpisah **tidak** membuat pemeriksaannya lebih akurat, dan **tidak** membuka akses bagi auditor dari luar perusahaan — jalur masuknya menuntut akun karyawan. Pemindahan ini juga **tidak** menambah satu pun pengujian baru; dari 36 pengujian, yang sudah berjalan otomatis tetap enam. Yang benar-benar dijamin hanya satu hal, dan itu memang inti keputusannya: **catatan pemeriksaan disimpan dengan kunci yang tidak dipegang divisi yang diperiksa.**
- **Besaran kerja**: tiga tahap. Memindahkan mesinnya beserta penyimpanannya, menutup satu celah akses, dan membangun situsnya. ⚠️ **Situsnya dikerjakan lebih dulu (2026-09-03), berlawanan dengan urutan yang dianjurkan ADR ini sendiri** — keputusan sadar pemilik pekerjaan setelah diberi tahu akibatnya. Yang perlu diketahui manajemen: **situsnya sudah jadi, tetapi janji "catatan pemeriksaan disimpan dengan kunci yang tidak dipegang divisi yang diperiksa" BELUM berlaku** dan baru berlaku setelah tahap pertama dikerjakan. Sampai saat itu, yang berubah baru alamatnya.

## Deskripsi

*Audit internal dikeluarkan dari `finance-service` menjadi service sendiri dengan database dan kredensial sendiri, lalu layarnya dikeluarkan dari `erp-frontend` menjadi aplikasi di subdomain sendiri yang masuk lewat SSO ERP. Keputusan ini **membalik ADR 0073 §1** dan berdiri di atas dua tuntutan yang saat itu belum dinyatakan: pihak yang diperiksa tidak boleh dapat mengubah bukti pemeriksaan tentang dirinya, dan modul ini akan menjadi wadah bagi seluruh audit internal, bukan audit pembukuan saja.*

- **Status**: ⚠️ **Implemented sebagian** — **§2 (aplikasi terpisah) SUDAH DIKERJAKAN**: repo [`bip-itteam-internal/audit-bharata`](https://github.com/bip-itteam-internal/audit-bharata) **PRIVATE** dibuat 2026-09-03 dan 15 commit sudah naik — sebelumnya aplikasinya HANYA ada di satu laptop tanpa remote sama sekali, jadi "repo ada" sempat berarti sesuatu yang jauh lebih rapuh daripada yang terbaca. Tiga layar jalan, 64 test hijau, build sukses; PR CORS bip-erp [#1690](https://github.com/bip-itteam-internal/bip-erp/pull/1690) OPEN. **§1 (pemisahan service + database) BELUM dimulai.** §5 (bypass super-akses) belum dikerjakan.
- **Path di repo**: `bip-erp/services/audit/*` (baru) · `bip-erp/shared-library/common/env.go` · `bip-erp/api-gateway/main.go` · `bip-erp/docker-compose.yml` · `bip-erp/.github/workflows/deploy.yml` · `erp-frontend/src/utils/menu-permission.ts` · repo aplikasi baru (baru)
- **Tanggal**: 2026-09-03

## Context

⚠️ **ADR ini berdiri di atas dokumen berstatus ✅, bukan 🟡.** [[Finance - Audit Internal]] dan [[ADR - 0073 Modul Audit Internal di finance-service dan Kertas Kerja yang Dipegang Sendiri]] keduanya menggambarkan kode yang **live di produksi per 2026-09-03**, dengan 36 baris uji nyata. ⚠️ Yang belum pernah terjadi bukan penjalanannya melainkan **pemakaiannya**: paket izin `Audit: *` belum ditugaskan ke satu akun pun, jadi belum ada orang yang membukanya.

ADR 0073 memutuskan audit sebagai **modul di dalam `finance-service`, bukan service tersendiri**, dengan tiga alasan operasional: container baru mahal di VM dev yang punya riwayat OOM, service baru berulang kali lolos dari `deploy.yml` dengan kegagalan senyap, dan jebakan urutan rute sudah dijinakkan di service lama. Ketiganya **masih berlaku dan tidak dibantah ADR ini**.

Yang berubah bukan ongkosnya, melainkan **apa yang dituntut**. Dua tuntutan berikut dinyatakan 2026-09-03 dan tidak ada dalam pertimbangan ADR 0073:

1. **Pihak yang diperiksa tidak boleh dapat mengubah bukti pemeriksaan tentang dirinya.** Hari ini `finance_db` menampung `pajak_*`, `cost_*`, dan `audit_jejak`/`audit_temuan` dalam satu instans dengan satu kredensial root, terpapar di `127.0.0.1:32799`. `finance-service` — service yang mengelola domain yang diauditnya — memegang kredensial itu. ADR 0073 §11 sudah mencatat konsekuensinya apa adanya: *"Pemisahnya RBAC, bukan batas proses."* Selama itu benar, tuntutan ini **tidak terpenuhi**, dan tidak ada jumlah gerbang di lapisan HTTP yang menutupnya.

2. **Modul ini akan menjadi wadah bagi seluruh audit internal.** [[GA - Audit Internal System]] (🟡, audit kepatuhan ISO 22000 / K3 / SOP GA) direncanakan menyusul ke tempat yang sama. ADR 0073 memutuskan lingkupnya saat masih audit pembukuan saja.

Tuntutan kedua ini yang paling menentukan, dan ia **lebih kuat daripada tuntutan pertama**: modul audit kepatuhan pangan dan K3 yang tinggal di dalam service keuangan bukan trade-off yang bisa ditimbang, melainkan salah kategori. Tak ada susunan alasan yang membuatnya masuk akal.

**Pengukuran yang membuat keputusan ini murah, dan tanpanya ADR ini tidak akan ditulis.** Modul audit berukuran 3.518 baris, 42% dari seluruh `services/finance`, dan yang dipinjamnya dari finance non-audit hanya **27 baris kode produksi** — tiga fungsi murni tanpa state (`koleksi`, `lokasiWIB`, `normalPeriode`). Nol tipe bersama, nol koleksi bersama, nol klien Accurate bersama, nol query silang. Arah sebaliknya enam pemanggilan, seluruhnya di `main.go` dan `routes.go`, satu blok kontigu ±35 baris. Rasio koplingnya **1,1%**.

Modul ini sudah berbentuk service mandiri; ia kebetulan di-*link* ke binary lain. Dengan 3.518 baris ia bahkan lebih besar daripada service terkecil yang hidup di repo ini.

Sisi frontend punya bentuk yang sama: seluruh import relatif `features/audit/*` tertutup di dalam modulnya, tak satu pun menembus keluar. 1.924 baris kode dan 524 baris test pindah apa adanya.

## Decision

### 1. `audit-service` dengan database dan kredensial SENDIRI

Modul dipindah ke `services/audit`, dengan `audit_db` dan kredensial terpisah dari `finance_db`.

⛔ **Yang memberi independensi adalah DATABASE-nya, bukan prosesnya.** Memisahkan proses tanpa memisahkan penyimpanan tidak mengubah apa pun — kredensial root yang sama tetap membuka `audit_jejak`. Pemisahan proses di sini adalah **konsekuensi teknis** dari pemisahan kredensial, bukan tujuannya. Bila kelak ada yang mengusulkan "cukup pisahkan service-nya, database-nya biarkan bersama demi hemat container", usul itu membatalkan seluruh alasan ADR ini.

Prefiks izin sudah `audit` sejak awal (`catalog_audit.go`), `AuditTierDefault` sudah mengembalikan kosong, dan paket bawaannya sudah disemai employee-service. **Bagian ini sudah dikerjakan seolah pemisahan memang akan terjadi**, jadi tidak ada perubahan katalog izin sama sekali.

### 2. Layar pindah ke aplikasi sendiri di subdomain, masuk lewat SSO ERP

Aplikasi Next.js + shadcn/ui di repo terpisah. Autentikasi memakai jalur yang sudah ada: `POST /auth/sso/ticket` lalu `POST /auth/sso/redeem` ([[CORE - SSO Flow]]).

⛔ **DILARANG punya auth sendiri.** [[ADR - 0003 SSO-only Gateway]] mengikat: aplikasi internal memakai akun karyawan yang sama, bukan tabel pengguna sendiri. Preseden pelanggarnya sudah ada dan ongkosnya tercatat di [[APP - Buku Besar Konsolidasi CV FINCON]].

⚠️ **ERP JWT DIPEGANG aplikasi ini, dan anjuran "pakai sekali lalu buang" TIDAK berlaku di sini.** Versi pertama ADR ini menuliskan anjuran itu mengikuti [[CORE - SSO Flow]] dan pola `services/vault-mcp/erp.go` — dan itu **keliru untuk kasus ini**. Pola tersebut menuntut konsumen punya backend sendiri untuk menerbitkan tokennya; aplikasi audit adalah SPA yang memanggil gateway langsung dari peramban, jadi ia tak punya tempat menerbitkan apa pun. Menganjurkannya di sini berarti menuliskan saran yang tak dapat dijalankan, dan saran semacam itu akan diabaikan seluruhnya beserta bagiannya yang benar.

Yang diterima sebagai konsekuensi, ditulis terbuka di `src/lib/sesi.ts` aplikasinya: token berlaku **penuh di seluruh `/api/*`** karena ERP JWT tak punya `aud` dan tak diperiksa audience-nya, dan **berumur 72 jam tanpa refresh** karena jalur SSO tak menerbitkan refresh token. Disimpan di `sessionStorage`, bukan `localStorage`, supaya umurnya seumur tab.

⛔ **Yang tetap DILARANG**: menyimpan ERP JWT di konsumen yang memapar permukaan sendiri ke luar. Larangan itu berlaku penuh untuk konsumen server-to-server, dan `vault-mcp` tetap contoh yang benar untuk bentuk itu.

### 3. Situs ini wadah SELURUH audit internal, dan namanya harus menyatakan itu

Lingkupnya audit pembukuan sekarang, kepatuhan GA menyusul. Konsekuensi penamaan mengikat: dua hal berbeda **tidak boleh** sama-sama bernama "Audit Internal" tanpa pembeda. Kelas kebingungan itu sudah menggigit — portal ticketing ERP dan aplikasi terpisah sama-sama bernama "Task Management", dan sampai hari ini orang harus bertanya yang mana yang dimaksud ([[APP - Dynamic Task Tracker]]).

### 4. ⛔ Register temuan kepatuhan GA TIDAK menumpang koleksi temuan pembukuan

Keputusan diambil **sekarang**, sebelum GA dibangun, karena setelahnya menuntut migrasi.

`audit_temuan` menyimpan temuan pembukuan lima unsur. Temuan kepatuhan GA mendapat koleksinya sendiri. Alasannya bukan kerapian melainkan kelas kegagalan yang sudah tercatat berulang di repo ini: **koleksi bersama ber-diskriminator mencemari angka secara senyap.** Konsumen berikutnya yang lupa menyaring tidak menghasilkan galat, ia menghasilkan angka yang masuk akal dan salah — dan temuan audit memberi makan metrik KPI.

Ini konsisten dengan ADR 0073 §5 yang sudah menolak menyatukan temuan audit ke `quality_capa` karena `CAPA_AREAS` terkunci `["Produksi","Gudang"]` dan memberi makan `temuan_capa_produksi`. Penolakan yang sama berlaku untuk penyatuan berikutnya.

### 5. Bypass super-akses menu DITUTUP untuk izin audit

Keempat izin `audit.*` didaftarkan ke `TANPA_BYPASS_SEMUA_MENU` di `erp-frontend/src/utils/menu-permission.ts`.

⚠️ **Ini membalik keputusan yang diambil 2026-09-02** saat review layar fase 2, yang waktu itu memilih mengikuti konvensi modul lain ber-tier-default kosong (`BudgetTierDefault`, `KasKecilTierDefault`) dan **tidak** mendaftarkannya. Konvensi itu benar untuk modul tanpa tuntutan kerahasiaan. Tuntutan "yang diaudit tidak boleh melihat sebelum terbit" membuatnya tidak lagi berlaku: `aksesSemuaMenu` meloloskan IT supervisor **atau** jabatan Direktur sebelum `perm` dinilai, dan pengukuran ke prod 20 Agustus 2026 menemukan tiga pemegang `system_roles.it: supervisor` **di luar Tech Development**.

Yang berhak tetap bisa ditunjuk seperti siapa pun: pasang paket `Audit: *` ke akunnya. Itu justru maksud katalognya.

### 6. Urutan WAJIB: penyimpanan dulu, situs belakangan

Pemisahan database dan service dikerjakan **sebelum** situsnya. Membalik urutannya menerbitkan penampakan independensi di atas penyimpanan yang belum terpisah — dan penampakan pemisahan pada modul audit lebih berbahaya daripada tidak ada pemisahan sama sekali, sebab orang berhenti bertanya.

### 7. Yang TIDAK diputuskan di sini

- **Auditor dari luar perusahaan (KAP).** Seluruh ADR ini mengandaikan pemakainya karyawan ber-akun ERP. SSO tidak melayani orang tanpa akun, jadi kebutuhan itu menuntut jalur identitas tersendiri dan ADR-nya sendiri.
- **Bentuk registry uji untuk audit kepatuhan GA.** Registry 36 uji hari ini berbentuk pembanding dua sisi berangka; checklist kepatuhan berbentuk lain. Belum diperiksa apakah keduanya muat dalam satu bentuk.
- **Nasib `GET /internal/audit/pemasok` dan `/internal/audit/karyawan`** — keduanya tetap harus dibangun, terlepas dari pindah atau tidak.

## Consequences

- ➕ Tuntutan "yang diaudit tidak boleh mengubah bukti" terpenuhi secara struktural, bukan lewat kesepakatan. Kredensial `audit_db` tidak dipegang service mana pun yang mengelola domain yang diperiksa.
- ➕ Audit kepatuhan GA punya rumah yang masuk akal. Menaruhnya di `finance-service` tidak akan pernah bisa dipertahankan.
- ➕ Ongkos kodenya kecil dan terukur: 27 baris kopling, ±420–475 baris pipa berdasarkan dua preseden nyata di repo ini, template `services/.template/` sudah ada, dan dua guard-test yang sudah menangkap kelas kegagalannya masih berlaku.
- ➖ **Dua container baru di VM dev** yang punya riwayat OOM. Alasan penolakan ADR 0073 ini tidak hilang, ia hanya kalah oleh tuntutan yang lebih kuat. Cap `--wiredTigerCacheSizeGB` wajib ikut.
- ➖ **Service baru punya riwayat lolos dari `deploy.yml` dengan kegagalan senyap.** Enam titik sisipan wajib diperiksa satu per satu, bukan diasumsikan.
- ➖ Aplikasi terpisah membawa ongkos yang tercatat di dua preseden: deploy adalah bagian termahal, bukan kodenya, dan aplikasi bisa "selesai" berbulan-bulan sebelum ada yang memakainya.
- ⚠️ **`AUDIT_MODULE_URL` wajib ada di blok `api-gateway` compose.** `ValidateInternalURL` memanik bila ada nilai kosong, dan panik itu berarti **seluruh ERP padam**, bukan satu modul mati. Dijaga `api-gateway/internal_url_compose_test.go`.
- ⚠️ **`DaftarkanRuteAudit` harus pindah dari `app.Group("/audit")` ke akar `/`.** Gateway sudah membuang `/api/audit`, jadi grup `/audit` membuat rutenya hanya terjangkau lewat `/api/audit/audit/uji`. Kelas ini menggigit calendar-service 2026-08-06 dan sudah dikunci `services/finance/routes_test.go`.
- ⚠️ **Konsumen berbasis browser menuntut PR CORS ke `api-gateway/main.go` dan deploy gateway.** [[CORE - SSO Flow]] menyatakan menambah konsumen "tidak butuh perubahan backend" — itu **salah**, dan sudah dikonfirmasi ke kode dua kali: Portal Karir (PR #460) dan aplikasi ini (bip-erp [#1690](https://github.com/bip-itteam-internal/bip-erp/pull/1690)). Daftarnya dikompilasi ke dalam biner Go, jadi entri baru tidak aktif sampai gateway dibangun ulang.
- ⚠️ **Migrasi 6 koleksi** `audit_*` dari `finance_db` ke `audit_db`. Indeksnya tidak perlu dimigrasi; `siapkanIndexAudit` membuatnya ulang saat boot.
- ⚠️ **Urutan deploy**: integration-service, lalu audit-service, lalu gateway (`--force-recreate` karena env baru), baru aplikasinya.
- ⚠️ `ssoStore` di gateway masih `map` in-memory, jadi gateway **tidak boleh di-scale horizontal** selama jalur SSO dipakai.
- ⚠️ Pemakai utamanya tetap belum ada. Posisi auditor internal belum terisi di master data.

## Dokumen Terkait

- [[ADR - 0073 Modul Audit Internal di finance-service dan Kertas Kerja yang Dipegang Sendiri]] — **diamandemen oleh ADR ini pada §1** (modul di finance-service). Keputusan lainnya tetap berlaku.
- [[ADR - 0003 SSO-only Gateway]] · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]
- [[Finance - Audit Internal]] — dok domain 36 uji dan aturan layarnya
- [[GA - Audit Internal System]] — audit kepatuhan yang akan menyusul ke wadah yang sama
- [[CORE - SSO Flow]] · [[CORE - API Master Gateway]] · [[CORE - RBAC dan Permission Set]]
- [[APP - Dynamic Task Tracker]] · [[APP - Portal Karir Bharata]] · [[APP - Buku Besar Konsolidasi CV FINCON]] — tiga preseden aplikasi terpisah beserta ongkosnya
- [[RUN - Deploy Microservices bip-erp]]
