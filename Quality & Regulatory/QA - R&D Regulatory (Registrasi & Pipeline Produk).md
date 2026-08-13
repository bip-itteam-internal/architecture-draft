## Deskripsi

*Workspace ERP untuk posisi **R&D Regulatory** (branch `feature/workspace-position`). Dua register: **Register NIE / BPOM / Halal** (memantau proses registrasi izin edar produk baru sampai terbit, dengan alert bila lewat target) dan **Papan Pengembangan Produk Baru** (pipeline tahap ide → formulasi → trial → registrasi → siap launching). Memberi jejak kerja di ERP bagi divisi yang selama ini bekerja lewat spreadsheet. Simulasi HPP produk baru (ke Cost Control) dan Register CAPA audit eksternal (bersama Quality) belum termasuk.*

- **Stack**: Go (Fiber, di-host di employee-service) + MongoDB (`rnd_registration`, `rnd_product`) + JWT/`system_roles`; frontend Next.js (App Router, TanStack Query).
- **Path di repo**:
  - Backend: `bip-erp/services/employee/{rnd_regulatory.go,rnd_product.go}` (`RegisterRnDRoutes`) · gerbang izin `services/employee/secretary_gate.go` (`gateSecretary`) · katalog `shared-library/common/catalog_secretary.go` · model `RnDRegistration`/`RnDProduct` di `.../models/employee/models.go` · collection `rnd_registration`/`rnd_product` · gerbang tier lama `RequireRnDStaff`/`RequireRnDSupervisor` di `.../common/roles.go` (kini fallback kill-switch).
  - Frontend: `erp-frontend/src/app/(main)/rnd/{regulatory,product-development}/page.tsx` · `src/features/rnd/{regulatory,product,shared}/*` · dua entri menu di blok **`secretary`** pada `sidebar-menus.tsx` (**bukan** `sidebar.tsx`) · alias kategori `modul-aktif.ts` · gating di `proxy.ts`.
- **Status**: ⚠️ Implemented (ada catatan). Kedua register + unggah PDF **live di kode**, dan sejak **2026-08-13 modulnya bukan `rnd` lagi melainkan `secretary`** (Kesekretariatan) bersama Legal — lihat blok di bawah. Rute `/rnd/*` **tidak berubah**. Verifikasi lewat gateway **belum dijalankan**. Simulasi HPP & CAPA belum; Papan Pengembangan berupa **tabel bertahap** (belum kanban drag-drop).

> [!info] Modul `rnd` DILEBUR ke `secretary` (2026-08-13), dan inilah lapisan izin PERTAMANYA
> Kedua register ini sebelumnya hanya bertier `system_roles.rnd` — **tak punya katalog
> permission sama sekali**, dan tak satu pun dari sepuluh rutenya punya test izin. Keduanya
> kini jadi salah satu dari dua **area** di dalam modul `secretary`, bersama
> [[QA - Register Perizinan & Sertifikasi]].
>
> | | Sebelum | Sesudah |
> |---|---|---|
> | Kunci modul | `rnd` | `secretary` |
> | Izin | **tak ada** | `secretary.rnd.view/work/manage` |
> | Paket | **tak ada** | `secretary_rnd_lihat`/`_pelaksana`/`_admin` |
> | Gerbang | `RequireRnDStaff`/`RequireRnDSupervisor` langsung | `gateSecretary` + keduanya sebagai fallback |
> | Kategori sidebar | `RND` | `SEKRETARIAT` |
> | Rute halaman | `/rnd/*` | **`/rnd/*`, tidak berubah** |
>
> ⚠️ **Satu modul, tapi haknya TETAP DUA.** Peran atau paket Legal tak pernah membuka rute
> R&D dan sebaliknya, persis seperti sebelum penggabungan. Itu alasan izinnya dipecah per
> AREA alih-alih satu tangga `secretary.view/work/manage` untuk seluruh modul: Staf Legal
> dan R&D Regulatory dua pekerjaan berbeda dengan kedalaman yang sama. Dikunci uji di kedua
> lapisan (`TestSecretaryTierPerAreaTerpisah` dan `TestAreaSekretariatTidakSalingMembuka`).
>
> Alasan penggabungan, termasuk sensus produksi yang mendasarinya, ada di
> [[QA - Register Perizinan & Sertifikasi]].

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| R&D Regulatory | jabatan **`QA RND`** di department **`secretary`** (Kesekretariatan) | peran `rnd:staff` diturunkan dari jabatan, atau paket **Sekretariat: R&D Pelaksana** — kelola registrasi & pipeline | Web ERP |
| R&D Regulatory Supervisor | department `secretary` | peran `rnd:supervisor` atau paket **Sekretariat: R&D Admin** — termasuk hapus | Web ERP |
| Supervisor / admin IT | Tech Development | super-akses, bertahan juga di fase dua | Web ERP |

⚠️ **Pemetaan jabatan `QA RND` ke modul `rnd` BELUM dikonfirmasi pemilik produk** (2026-08-13).
Ia dipilih dari nama jabatannya: Kesekretariatan tak punya jabatan ber-R&D lain, dan fungsi
QA punya departemen `quality` sendiri. Tak bisa diperiksa ke data karena dev tak punya
pemegang jabatan itu. Bila keliru, yang terbuka dua register registrasi produk (bukan data
pribadi atau angka uang) dan pencabutannya satu baris di `peran_dari_jabatan.go`.

- **Tujuan**: satu layar untuk "izin apa yang sedang diproses & apakah lewat target", dan "produk apa di pipeline & tahap mana".
- **Pain point**: status registrasi & progres formulasi terpencar; keterlambatan target 14 hari kerja tak terlihat sampai ditanya.

## Fitur (Sudah Diimplementasikan)

**Register NIE / BPOM / Halal** (`rnd_regulatory.go`, collection `rnd_registration`), dipanggil FE lewat `/api/employee/rnd/*`:
- `GET/POST /rnd/registrations`, `GET/PUT /rnd/registrations/:id` (gate `RequireRnDStaff`), `DELETE` (gate `RequireRnDSupervisor`). Filter `?registration_type=`&`?status=`.
- Model `RnDRegistration`: `product`, `registration_type` (NIE/BPOM · Halal · SNI · Lainnya), `status` (Persiapan → Terdaftar → Review BPOM → Terbit/Ditolak), `number` (nomor NIE), `issuer`, `pic`, `register_date`, `target_date`, `expires_at` (ISO string), `notes`, `file_object`+`file_name`.
- **Alert target di UI**: badge `Telat {n}h`/`H-{n}` dari `target_date` selama status belum Terbit/Ditolak.

**Papan Pengembangan Produk Baru** (`rnd_product.go`, collection `rnd_product`):
- `GET/POST /rnd/products`, `GET/PUT /rnd/products/:id` (gate `RequireRnDStaff`), `DELETE` (gate `RequireRnDSupervisor`). Filter `?stage=`&`?status=`.
- Model `RnDProduct`: `product`, `stage` (Ide/Formulasi/Trial/Registrasi/Siap Launching), `status` (On Track/Telat/Selesai), `pic`, `start_date`, `target_date`, `notes`, `file_object`+`file_name` (hasil uji).

**Unggah PDF** — reuse endpoint generik `POST /api/employee/upload` (`minio.UploadSingleHandler`); FE `features/rnd/shared/upload.ts`. Pola identik dengan Legal — lihat [[QA - Register Perizinan & Sertifikasi]].

**RBAC & seed**: tier lama `system_roles.rnd` (`rnd:staff|supervisor`) tetap hidup sebagai fallback dan sebagai sumbu yang menentukan menu serta lolosnya `proxy.ts`. Sejak 2026-08-13 kesepuluh rute digerbang izin `secretary.rnd.view|work|manage` lewat `gateSecretary`, dengan tiga paket bawaan **Sekretariat: R&D Lihat / Pelaksana / Admin** (reach `all`). Department `rnd` **dicabut dari `DefaultDepartments`**: ia tak pernah lahir di dev maupun prod, sebab `seedMasterDepartments` berhenti begitu koleksinya terisi. Lihat [[CORE - RBAC dan Permission Set]].

## Belum Diimplementasikan / Catatan

- **Simulasi HPP Produk Baru** (P1, route `/finance/cost-control/hpp?mode=simulasi`) — butuh data BOM/harga dari Cost Control/Manufacture; **belum**.
- **Register CAPA Audit Eksternal** (P2) — kini **sudah tersedia** lewat modul Quality (`/quality/capa`, sumber `Audit Eksternal/BPOM/HACCP`); R&D memakai register yang sama. Lihat [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]].
- **Papan Pengembangan** masih **tabel** dengan kolom tahap + badge, bukan **kanban drag-drop**; lead time vs target 14 hari kerja belum dihitung otomatis (baru badge target_date manual).
- **Hosting di employee-service** (TBD) — sama seperti Legal; ekstrak ke service `rnd` bila beban tumbuh. Lihat [[CORE - API Master Gateway]].
- **Verifikasi runtime**: build/typecheck lolos; smoke-test E2E (akun `rnd`, CRUD ke employee-service) belum — perlu redeploy `docker-compose.dev.yml`.
- **Overlap dengan Legal**: registrasi BPOM/Halal produk (R&D) vs izin perusahaan (Legal) beririsan; dijaga terpisah — R&D memantau proses per-produk sampai terbit, Legal memantau izin aktif perusahaan. Sejak keduanya satu modul, pemisahan itu ditegakkan lewat izin per-area, bukan lagi lewat modul yang berbeda.
- **Belum ada paket yang terpasang ke jabatan mana pun** (dev maupun prod), sama seperti `formbuilder`. Selama begitu, katalognya benar tapi yang benar-benar membuka akses tetap peran yang diturunkan dari jabatan. Fase dua (`SECRETARY_TIER_FALLBACK=off`) karena itu **belum boleh dinyalakan**.

## Dependensi & Integrasi

- [[Microservices - Employee Service]] — host endpoint `/rnd/*`, Mongo, seed department.
- [[CORE - API Master Gateway]] — meneruskan `/api/employee/rnd/*` + header `BIP-*`.
- [[CORE - RBAC dan Permission Set]] — modul `secretary`, izin `secretary.rnd.*`, dan tier lama `system_roles.rnd`.
- [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]] — jabatan `QA RND` di Kesekretariatan menurunkan peran `rnd: staff`.
- [[APP - Web ERP]] — kategori sidebar SEKRETARIAT.

## Dokumen Terkait

- [[QA - Register Perizinan & Sertifikasi]]
- [[Microservices - Employee Service]]
- [[CORE - RBAC dan Permission Set]]
