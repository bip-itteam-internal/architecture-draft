# ANALISA - Audit Internal Terpisah

Papan kerja untuk [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]].
Dok aplikasi [[APP - Audit Internal]], dok domain [[Finance - Audit Internal]].

Disusun 2026-09-03.
**Status: belum ada satu baris kode pun.** Modul audit hari ini masih di dalam `services/finance` dan layarnya masih di `erp-frontend`.

⛔ **URUTANNYA MENGIKAT.** Fase 1 sebelum Fase 3. Membalik urutannya menerbitkan penampakan independensi di atas penyimpanan yang belum terpisah, dan itu lebih berbahaya daripada tidak memisahkan sama sekali — orang berhenti bertanya.

---

## Fase 0 — Prasyarat, dan ini yang menahan segalanya

- [ ] ⛔ **Tambahkan blok service `finance-service` + `finance-mongo-db` ke `docker-compose.dev.yml`.** Sekarang berkas itu hanya punya `FINANCE_MODULE_URL: "http://finance-service:9999"` sebagai placeholder, **tanpa definisi service-nya**, jadi `/api/finance/*` membalas 502 dan modul audit **belum pernah memuat satu baris data pun**.
  ⚠️ **Port di placeholder itu ditulis mati `9999`, bukan `${FINANCE_SERVICE_PORT}` (=6989).** Menambahkan service tanpa membetulkan baris itu membuat gateway tetap menembak 9999 sementara service mendengar di 6989 — **tetap 502, dengan container yang hidup dan sehat.**
  ⚠️ Cek dulu `.env` VM dev memuat `FINANCE_SERVICE_PORT`, `MONGO_FINANCE_DB`, `INTEGRATION_SERVICE_KEY`. Runbook mencatat kejadian nyata: port di `.env.example` tidak pernah tersalin ke `.env` dev, dan itu sebabnya gateway tak pernah bisa di-rebuild berbulan-bulan.
  ⚠️ Host port 32799 sudah dicek bebas di dev. Preseden payroll harus pindah 32792→32795 karena tabrakan, jadi jangan asumsikan.
  **Selesai bila**: satu panggilan sungguhan ke `/api/finance/audit/uji` lewat gateway dev membalas 36 uji.

- [ ] **Pasang paket izin `Audit: *` ke minimal dua akun uji** (satu auditor, satu direksi). Tanpa ini kategori sidebarnya tak muncul untuk siapa pun kecuali pemegang super-akses menu, dan pemisahan tugas antar-paket tak pernah benar-benar teruji.

- [ ] **Jalankan alur pengguna utuh sekali sebagai orang** di layar yang sudah ada. `curl` tidak menggantikannya.
  **Kenapa ini tetap dikerjakan padahal layarnya akan dipindah**: memindahkan layar yang belum pernah dilihat siapa pun berarti memindahkan asumsi, bukan fitur. Semua yang ditemukan di sini ikut pindah gratis; yang tidak ditemukan akan muncul di tempat baru dan lebih mahal.

---

## Fase 1 — Pisahkan backend dan DATABASE-nya

⛔ **Yang memberi independensi DATABASE-nya, bukan prosesnya.** Bila di tengah jalan muncul usul "cukup pisahkan service-nya, DB-nya biarkan bersama demi hemat container", usul itu membatalkan seluruh alasan ADR 0074.

- [ ] **T1.1 — `services/audit` sebagai service baru.** Pindahkan 11 berkas produksi (2.380 baris) + 8 test (1.138). Salin 3 helper (±27 baris): `koleksi` (`db.go`), `lokasiWIB` + `normalPeriode`/`polaPeriode` (`rekomendasi.go`). Salin helper test `kirim` + `izinJSON`.
  Kerangkanya dari `services/.template/`. Dua preseden bisa dipakai sebagai checklist harfiah: commit `ec184c71` (finance, 12 berkas / 475 sisipan) dan `93486b63` (calendar, 12 berkas / 417).

- [ ] **T1.2 — ⛔ Pindahkan `DaftarkanRuteAudit` dari `app.Group("/audit")` ke akar `/`.** Gateway sudah membuang `/api/audit`, jadi grup `/audit` membuat rutenya hanya terjangkau lewat `/api/audit/audit/uji`. Bawa **kedua** guard-test prefix dari `services/finance/routes_test.go` ke service baru. Kelas ini menggigit calendar-service 2026-08-06.

- [ ] **T1.3 — `audit_db` + kredensial sendiri.** Blok `audit-mongo-db` di compose dengan cap `--wiredTigerCacheSizeGB`. **Kredensialnya tidak boleh sama dengan `finance_db`** — kalau sama, seluruh keputusan ini tidak menghasilkan apa pun.

- [ ] **T1.4 — Migrasi 6 koleksi** `audit_kertas_kerja`, `audit_baris`, `audit_temuan`, `audit_jejak`, `audit_setelan_sampel`, `audit_sampel` dari `finance_db` ke `audit_db`. Indeks tak perlu dimigrasi; `siapkanIndexAudit` membuatnya ulang saat boot.
  ⚠️ **Tulis skripnya, jalankan MANUSIA.** Dry run wajib, `mongodump` dulu.

- [ ] **T1.5 — Gateway & env.** `AuditModuleURL` di `shared-library/common/env.go`, satu baris di `InternalURL` (`api-gateway/main.go`), dan **wajib** satu baris `AUDIT_MODULE_URL` di blok api-gateway `docker-compose.yml`.
  ⛔ Lupa yang terakhir membuat `ValidateInternalURL` **memanik saat boot** dan **seluruh ERP padam** — bukan satu modul mati. Dijaga `api-gateway/internal_url_compose_test.go`.
  - [ ] Putuskan apakah `"audit"` masuk `noCacheModules` (`api-gateway/redis.go`). Kertas kerja yang di-cache setelah tarik ulang = angka basi.

- [ ] **T1.6 — `deploy.yml`: enam titik sisipan**, diperiksa satu per satu. Service baru punya riwayat lolos dari berkas ini dengan kegagalan senyap.

- [ ] **T1.7 — Bersihkan `finance-service`.** Hapus blok bootstrap di `main.go` dan `routes.go` (±35 baris kontigu), buang `PROCUREMENT_MODULE_URL`, `EMPLOYEE_MODULE_URL`, `INTEGRATION_SERVICE_KEY` beserta komentarnya dari blok `finance-service` di compose.

- [ ] **T1.8 — Frontend menunjuk alamat baru**: `/api/finance/audit/*` → `/api/audit/*` di `erp-frontend`, sementara layarnya masih di sana.

---

## Fase 2 — Tutup celah akses yang tersisa

- [ ] **T2.1 — Daftarkan keempat izin `audit.*` ke `TANPA_BYPASS_SEMUA_MENU`** (`erp-frontend/src/utils/menu-permission.ts`).
  ⚠️ **Ini membalik keputusan 2026-09-02** yang memilih mengikuti konvensi modul ber-tier-default kosong. Konvensi itu benar untuk modul tanpa tuntutan kerahasiaan; tuntutan "yang diaudit tidak boleh melihat sebelum terbit" membuatnya tidak berlaku.
  **Selesai bila**: ada test yang membuktikan pemegang `system_roles.it: supervisor` **tanpa** paket audit tidak melihat menunya, dan kontrol negatifnya membuktikan yang berpaket tetap melihat.

- [ ] **T2.2 — Bangun `GET /internal/audit/pemasok`** di procurement-service. Bergerbang sendiri — `/internal/` bukan batas keamanan.
- [ ] **T2.3 — Bangun `GET /internal/audit/karyawan`** di employee-service. Bergerbang sendiri.
  Sampai keduanya ada, uji silang pemasok berkeadaan `gagal_tarik` dengan sebab terbaca — bukan bersih.

---

## Fase 3 — Aplikasi di subdomain sendiri

- [ ] **T3.1 — Putuskan nama dan alamatnya.** Wadahnya untuk seluruh audit internal, jadi namanya wajib membedakan diri dari [[GA - Audit Internal System]]. Dua hal bernama sama tanpa pembeda sudah terbukti membingungkan permanen.

- [ ] **T3.2 — Repo baru**, Next.js + shadcn/ui. `npx shadcn@latest init` lalu `add` 15 komponen yang dipakai.
  ⚠️ Konvensi repo ini: **pnpm**, branch `main` (Portal Karir memakai `master` dan itu jebakan CI).
  ⚠️ Tambah varian `success` dan `warning` ke `badge` — shadcn stok tak punya, dan `tampilan.ts` menuntutnya.

- [ ] **T3.3 — Keputusan tabel: fork atau bangun ulang.** `MainTable` dipakai 124 halaman lain, `Banner` 106. Halaman audit hanya memakai 13 dari 19 prop. Putuskan sadar, jangan mengalir.

- [ ] **T3.4 — Pindahkan modul audit** (1.924 baris + 524 test). Import relatifnya sudah tertutup.
  - [ ] Tulis ulang `bolehAksiAudit` (~8 baris, perilakunya sudah terkunci `izin.test.ts`) alih-alih membawa 1.476 baris `menu-permission`.
  - [ ] Inline `isSelisihNyata` alih-alih membawa 285 baris `reconciliation-view`.
  - [ ] Ukir blok `audit.*` + `common` dari locale (281 baris).

- [ ] **T3.5 — SSO**: halaman `/auth/callback` dikecualikan dari guard, penjaga anti-loop logout, penanganan 401 setelah 72 jam.
  ⛔ **ERP JWT dipakai sekali lalu dibuang**, pola `services/vault-mcp/erp.go`. Jangan menyimpannya sebagai token sesi.
  - [ ] ⛔ **PR CORS ke `api-gateway/main.go` + deploy gateway.** Daftar origin hardcode di Go. Dok [[CORE - SSO Flow]] bilang "tidak butuh perubahan backend" dan itu salah.
  - [ ] Perbaiki allowlist redirect ERP supaya memeriksa **skema**, bukan hostname saja — `http://` di subdomain lolos hari ini dan token dikirim plaintext.

- [ ] **T3.6 — Pasang `form-errors-modal` di layout.** Tanpa itu validasi lima unsur temuan **gagal tanpa satu pun galat**.

- [ ] **T3.7 — Guard build**: gagalkan build bila `.env` tak ada, supaya situs produksi tidak menunjuk alamat dev secara senyap.

- [ ] **T3.8 — Cabut rute `/audit*` dari `erp-frontend`** setelah situsnya hidup dan terverifikasi. Jangan sebelumnya.

---

## Fase 4 — Dokumentasi yang menyusul

- [ ] Buat `Microservices - Audit Service` setelah service-nya benar-benar ada (jangan sebelum, grounded-in-code).
- [ ] Buat `API - Audit Service` + daftarkan di `API - Index`.
- [ ] Buat `RUN - Deploy Aplikasi Audit Internal` — preseden Portal Karir menunjukkan jebakan deploy tidak muat di dok `APP -`.
- [ ] Perbarui `CLAUDE.md` §7 vault: baris repo→dok, tandai "repo terpisah".
- [ ] ⛔ **Perbaiki tiga klaim usang di [[CORE - SSO Flow]]** SEBELUM ada yang memakainya sebagai panduan: `use-task-manager-sso.ts` tidak ada, "tidak butuh perubahan backend" salah, dan allowlist `localhost` lolos tanpa cek port.
- [ ] Perbarui [[CORE - API Master Gateway]] dan [[CORE - RBAC dan Permission Set]].

---

## Yang sengaja TIDAK ada di daftar ini

- **Auditor dari luar perusahaan (KAP)** — SSO tidak melayani orang tanpa akun ERP. Kebutuhan itu menuntut jalur identitas sendiri dan ADR-nya sendiri.
- **Layar audit kepatuhan GA** — registry 36 uji berbentuk pembanding dua sisi berangka, checklist kepatuhan berbentuk lain, dan belum diperiksa apakah keduanya muat dalam satu bentuk. Yang sudah diputuskan hanya satu: **koleksi temuannya terpisah**.
- **Memisahkan modul pajak dan cost control** dari finance-service — tidak ada tuntutan yang menghendakinya.
- **Menyatukan `ssoStore` gateway ke Redis** — kebutuhannya nyata (gateway tak boleh di-scale horizontal) tapi bukan bagian dari pemisahan ini.

---

## Task pertama

```
/start-task Tambahkan blok service finance-service + finance-mongo-db ke
docker-compose.dev.yml di bip-erp, dan betulkan FINANCE_MODULE_URL yang
port-nya masih ditulis mati 9999 alih-alih ${FINANCE_SERVICE_PORT}
```
