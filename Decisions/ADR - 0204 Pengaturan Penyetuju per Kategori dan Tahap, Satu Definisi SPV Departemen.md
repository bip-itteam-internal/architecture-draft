> **Status**: 🟡 Diusulkan, 2026-10-24. Dari `/analisa-kebutuhan`. Pemutus: irfanarfianto. Kode belum ada. Pecahan kerja: [[ANALISA - Pengaturan Penyetuju per Kategori dan Tahap]]. Mengubah sebagian [[ADR - 0194 Peta Penyetuju per Orang Lintas Modul sebagai Tahap Pertama Persetujuan Terpusat]] §4.

## Untuk Manajemen

**Yang berubah di layar.** Tiga menu di Pengaturan → Organisasi (Penyetuju Pengajuan, Penyetuju Booking Ruang, Peta Penyetuju) digabung jadi satu menu **Pengaturan Penyetuju**. Kategorinya sama dengan kategori di Portal Persetujuan. Untuk tiap kategori terlihat tahapnya berurutan, siapa saja yang bisa memutus di tiap tahap, dan dari mana wewenangnya. Tahap yang **tidak punya pemegang** ditandai merah (pengajuan akan mentok). Tahap yang **hanya dipegang satu orang** ditandai kuning (mentok saat orangnya cuti). Tab kedua menampilkan per orang: semua yang bisa disetujui seseorang. Penyetuju departemen, Manager, penyetuju booking ruang, dan admin ruang kerja tiket bisa diubah langsung dari halaman ini.

Sekaligus diperbaiki satu celah: penyetuju departemen yang dipilih HR dari departemen lain hari ini tidak ikut memegang tahap persetujuan atasan di Pengajuan Barang, Permintaan GA, Realisasi PM, dan triase tiket. Sesudah keputusan ini, siapa "atasan departemen" ditentukan satu aturan yang sama di seluruh ERP.

**Siapa yang terdampak.** Supervisor HRIS dan IT, yang mengelola penyetuju. Pemohon tidak terdampak. Penyetuju departemen pilihan HR lintas departemen mulai menerima tahap atasan di empat modul tadi.

**Yang TIDAK dijanjikan.**
- Mengubah wewenang yang berasal dari **izin akun** (paket per posisi/akun, mis. tahap SPV Finance pengajuan barang, tahap payroll) dari halaman ini. Itu tetap di Hak Akses (IT) sampai [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]] diputuskan; halaman ini menautkan ke sana dan menyebut tahap lain yang ikut terbuka oleh izin yang sama.
- Delegasi saat penyetuju cuti dan rangkap jabatan (pertanyaan terbuka ADR 0137).
- Mengubah urutan tahap. Urutan tetap milik tiap modul.

**Besaran kerja.** Besar: empat bagian backend dan dua bagian web.

## Deskripsi

*Satu halaman pengaturan penyetuju bersumbu kategori Portal Persetujuan × tahap, dibangun di atas agregator di employee-service yang menanyai tiap service sumber "tahapmu apa" dan mengisi pemegangnya lewat resolver yang sudah ada; tahap kosong dan tahap satu orang ditandai. Seluruh tahap "atasan departemen" di modul mana pun memakai satu resolver penyetuju departemen, bukan cakupan token. Edit langsung hanya untuk wewenang berbasis penetapan; wewenang berbasis izin akun menunggu ADR 0137.*

- **Status**: 🟡 Diusulkan, kode belum ada (lihat baris status di atas).
- **Path di repo**: `bip-erp/services/employee/pengaturan_penyetuju.go` (baru) · `bip-erp/services/employee/department_approver.go` · `bip-erp/services/employee/peta_penyetuju.go` · `bip-erp/services/employee/department_approver_lookup.go` · `bip-erp/services/procurement/pengajuan_barang_gate.go` · `bip-erp/services/procurement/pengajuan_barang_handler.go` · `bip-erp/services/inventory/permintaan_daftar.go` · `bip-erp/services/inventory/permintaan_gate.go` · `bip-erp/services/inventory/pm_realisasi.go` · `bip-erp/services/task-management/space_admin.go` · `bip-erp/services/task-management/task_filter.go` · `/internal/tahap-penyetuju` di attendance, learning, marketing-analytics, procurement, payroll, inventory, task-management, recruitment (baru) · `erp-frontend/src/app/(main)/pengaturan/organisasi/` (halaman baru) · `erp-frontend/src/features/hris/pengaturan/lib/sections.ts` · `erp-frontend/src/features/panduan/isi/hrga.ts`
- **Tanggal**: 2026-10-24
- **Desain**: Figma "Pengaturan Penyetuju Terpusat" (file privat tim, disetujui user 2026-10-23).

## Context

Kebutuhan dari HR/IT: tidak ada satu tempat untuk menjawab "tahap X dipegang siapa, dan apakah ada pengajuan yang bakal mentok". Jawabannya tersebar di tiga menu, Hak Akses, dan aturan di kode tiap modul. [[ADR - 0194 Peta Penyetuju per Orang Lintas Modul sebagai Tahap Pertama Persetujuan Terpusat]] menjawab sumbu **orang**; sumbu **tahap** belum ada (`git grep` pola `tahap-penyetuju|pemegang-tahap|stage-holders` di `bip-erp` origin/main, 2026-10-23: nihil).

**Diukur di prod 2026-10-23 (baca saja, `employee_db`):**
- 13 departemen; **0** punya penyetuju pilihan HR, **0** punya Manager, **0** berjenis pimpinan. Satu departemen tanpa `is_supervisor` aktif (General Affair, ikut Human Resource lewat `supervised_by`).
- 23 izin tahap persetujuan (payroll, pengajuan barang, pengajuan HR, pelatihan, rekrutmen, triase, serah GA): **0** tanpa pemegang. Tiga tahap payroll (`payroll.approve.cost_control`, `.hrd`, `.finance`) masing-masing **dipegang satu orang**. Hitungan ini hanya dari paket izin (akun + posisi); fallback `system_roles` dan gerbang lama "anggota departemen HR" belum ikut dihitung.

Jadi risiko yang nyata hari ini bukan tahap kosong melainkan tahap satu orang, dan celah berikut.

**Dua definisi "atasan departemen" yang berbeda** (kode `bip-erp` origin/main `e64ec53b`):
- Pengajuan karyawan, pelatihan, dan Live Support memakai rantai `atasanDepartemen` (`services/employee/supervisor_lookup.go:324`): penyetuju pilihan HR → `is_supervisor` → departemen induk → Manager → Direktur.
- Pengajuan Barang (`pb_spv_divisi`, `pb_spv_manufactur`, `pb_spv_quality`, `pb_leader_procurement`), Permintaan GA (`spv_divisi`, `spv_hr`), Realisasi PM, dan triase tiket memakai **cakupan token** `supervised_departments` (`SupervisedDepartmentsStrict`), yang hanya lahir dari `work_data.is_supervisor` (`services/employee/department_scope.go:66`).

Menetapkan penyetuju lintas departemen ([[ADR - 0193 Struktur Organisasi Direksi, Manager, Departemen dengan Unit Pimpinan Berjenis dan Penyetuju Lintas Departemen]] §4b, live 2026-10-23) mematikan `is_supervisor` anggota departemen itu. Akibatnya tahap atasan di empat modul tadi **kehilangan pemegang** untuk departemen tersebut, sementara notifikasi pengajuan barang tetap dikirim ke penyetuju pilihan lewat `/internal/department-approver`. Belum terjadi di prod hanya karena fiturnya belum dipakai.

**Peta Penyetuju tidak membaca penyetuju pilihan.** `peta_penyetuju.go:375` memasang `penyetujuPerDepartemenErr` (`department_approver.go:188`), yang hanya membaca `is_supervisor`, padahal komentar di `peta_penyetuju.go:178` menyatakan pilihan lintas departemen ikut terbaca. Penentu yang benar sudah ada: `penyetujuBaris` (`department_approver.go:264`).

**Yang sudah ada dan dipakai ulang:** `GET /internal/permission-holders` (izin → orang, gabungan jalur akun + posisi; `services/employee/permission_holders.go:87`), `GET /internal/department-approver` (`department_approver_lookup.go:74`), sumber tunggal tahap → izin (`shared-library/common/izin_tahap_pengajuan_barang.go`, `TahapJenjangPayroll` + `permissionUntukTahapPayroll`), endpoint tulis penyetuju departemen, Manager, booking ruang (`PUT /peminjaman/penyetuju`), admin space (`PUT /spaces/:id`), dan pola agregator `registriAntrean` (`services/employee/antrean_pengajuan.go`).

**Kategori yang tidak berbentuk "tahap persetujuan":** Permintaan GA sejak 2026-10-13 tanpa persetujuan untuk sebagian jenis (tinggal serah terima); triase tiket diputus admin space atau pemegang `ticket.triage`. Keduanya tetap ditampilkan dengan mekanisme apa adanya.

Status dok yang menjadi dasar: ADR 0193 dan 0194 🟢 Diterima; [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]] 🟡 Diusulkan dengan Decision TBD; [[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]] 🟡 Diusulkan dan rutenya sudah dihapus dari kode (koleksi `pengaturan_penyetuju_pembelian` yatim).

## Decision

### 1. Satu definisi "atasan departemen"

Setiap tahap yang maknanya "atasan/penyetuju departemen X" di modul mana pun ditentukan oleh resolver penyetuju departemen yang sama dengan pengajuan karyawan (`/internal/department-approver`, rantai `atasanDepartemen`), bukan oleh cakupan token `supervised_departments`. Berlaku untuk Pengajuan Barang (tahap berbasis hubungan), Permintaan GA (`spv_divisi`, `spv_hr`), Realisasi PM (verifikasi SPV GA), dan triase tiket (cabang "supervisor divisi"; admin space tetap menang lebih dulu). Berlaku untuk **gerbang** dan **antrean** sekaligus, lewat fungsi yang sama.

Cakupan token `supervised_departments` **tidak berubah** (ADR 0193 §4b tetap: penyetuju lintas departemen tidak menambah cakupan token). Yang berubah hanya sumber kebenaran untuk tahap persetujuan atasan.

### 2. Peta Penyetuju membaca penyetuju pilihan

Wewenang `penyetuju_departemen` di Peta Penyetuju dihitung dengan penentu yang sama dengan layar penyetuju (`penyetujuBaris`), sehingga penyetuju pilihan lintas departemen tampil.

### 3. Tahap tetap milik tiap service; agregator mengisi pemegang

Tiap service sumber Portal Persetujuan membuka `GET /internal/tahap-penyetuju?company_id=` (bergerbang kunci internal) yang mengembalikan, per kategori, daftar tahap **berurutan** dengan bentuk:

```
{ kategori, tahap, label, urutan, mekanisme, kunci }
```
- `mekanisme`: `izin` (kunci = nama izin) | `departemen` (pemegang per departemen lewat resolver §1) | `penetapan` (kunci = sumber penetapan, mis. daftar penyetuju booking ruang, admin space) | `jabatan`.
- Daftar tahap dan pemetaan tahap → izin **tidak disalin** ke employee-service; sumber tunggalnya tetap di modul atau `shared-library` (mis. `IzinPerTahapPengajuanBarang`, `TahapJenjangPayroll`).

Agregator `GET /pengaturan-penyetuju` di employee-service (gerbang: supervisor HRIS atau IT) menyusun per kategori × tahap: pemegang (lewat `permission-holders` untuk `izin`, `department-approver` per departemen untuk `departemen`, sumber penetapan untuk `penetapan`), `mekanisme`, `layar_pengatur`, dan penanda **`kosong`** (0 pemegang aktif) serta **`satu_orang`** (tepat 1 pemegang aktif). Untuk mekanisme `departemen`, penanda dihitung per departemen. Sumber yang gagal dibaca masuk `tidak_terbaca`, tidak pernah terbaca sebagai "kosong". Hitungan pemegang `izin` wajib ikut menghitung jalur yang benar-benar dipakai gerbangnya (termasuk fallback peran lama bila gerbang itu memakainya), supaya "kosong" tidak palsu.

Untuk tahap berbasis izin, respons menyebut **tahap lain yang dibuka izin yang sama** (mis. `budget.approve.procurement` membuka `pb_procurement_beli`, `pb_tulis_po`, `pb_procurement_faktur`, `pb_kelebihan_bayar`), diturunkan dari sumber tunggal pemetaan tahap → izin.

### 4. Halaman: satu menu, dua tab

Pengaturan → Organisasi → **Pengaturan Penyetuju** menggantikan Penyetuju Pengajuan, Penyetuju Booking Ruang, dan Peta Penyetuju:
- **Per Kategori** (bawaan): daftar kategori Portal Persetujuan (label sama dengan portal), tahap berurutan, pemegang, mekanisme, tanda merah (kosong) dan kuning (satu orang); kategori dengan tanda muncul di daftar kiri.
- **Per Orang**: Peta Penyetuju (`GET /peta-penyetuju`) dalam tab.
- Rute lama dialihkan ke tab/kategori yang setara; `layar_pengatur` yang dikirim backend ikut diperbarui. Menu baru membawa panduannya (`isi/hrga.ts`).

### 5. Edit dari halaman: hanya penetapan (mengubah sebagian ADR 0194 §4)

Dari halaman ini boleh mengubah wewenang bermekanisme `penetapan` dan `departemen` yang endpoint tulisnya sudah ada: penyetuju departemen, Manager departemen, penyetuju booking ruang, admin space tiket. Tiap simpan menampilkan akibatnya (lintas departemen, siapa yang tergeser, pengajuan yang sedang menunggu). Wewenang bermekanisme `izin` dan `peran_lama` hanya ditautkan ke Hak Akses, dengan daftar tahap lain yang ikut terbuka; mengubahnya dari sini menunggu ADR 0137.

## Consequences

- ✅ "Tahap X dipegang siapa" dan "tahap mana yang bisa mentok" terjawab dari satu tempat; risiko satu-orang (payroll) terlihat.
- ✅ Penyetuju lintas departemen benar-benar memegang tahap atasan di semua modul; penerima notifikasi dan yang boleh memutus kembali sama.
- ⚠️ Gerbang tahap atasan di procurement, inventory, dan task-management memanggil employee-service; perlu cache per permintaan dan perilaku gagal-tertutup bila resolver tak terjangkau.
- ⚠️ Delapan service mendapat endpoint `/internal/tahap-penyetuju`; tiap endpoint bergerbang kunci internal (`/internal/` bukan privat).
- ⚠️ Rute lama tiga menu dialihkan; tautan panduan dan deep link ikut diperbarui.
- Deploy: bagian §1-§2 (procurement, inventory, task-management, employee-service naik bersama) **sebelum** penyetuju lintas departemen dipakai HR; agregator sebelum halaman web.

Terkait: [[ADR - 0181 Portal Persetujuan Memuat Keputusan dan Tindakan Operasional]] · [[ADR - 0193 Struktur Organisasi Direksi, Manager, Departemen dengan Unit Pimpinan Berjenis dan Penyetuju Lintas Departemen]] · [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]] · [[REF - Alur Persetujuan]] · [[CORE - RBAC dan Permission Set]]
