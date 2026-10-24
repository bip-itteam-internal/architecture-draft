**Status**: 🟡 Daftar task dari `/analisa-kebutuhan` 2026-10-24. Keputusannya di [[ADR - 0204 Pengaturan Penyetuju per Kategori dan Tahap, Satu Definisi SPV Departemen]]; cara kerja penyetuju departemen di [[HRIS - Organization Structure]] dan inventaris gerbang di [[REF - Alur Persetujuan]]. Dok ini papan kerja, bukan arsitektur.

**Menunggu ADR "Pengaturan Penyetuju per Kategori dan Tahap, Satu Definisi SPV Departemen" Diterima: sebelum itu ANALISA ini BUKAN keputusan yang bisa ditunjuk `/brief`.**

- **Ukuran**: **Besar**. `bip-erp` butuh empat PR (perbaikan tahap atasan di tiga service + Peta Penyetuju; agregator; endpoint tahap pengajuan barang + payroll; endpoint tahap modul sisanya) dan `erp-frontend` dua PR (halaman baca; penggabungan menu + edit). Repo FE memang harus berubah: belum ada halaman bersumbu tahap (`git grep` pola `tahap-penyetuju|pengaturan-penyetuju` di erp-frontend origin/main 2026-10-23: nihil). MyBharata tidak tersentuh.
- **Pemutus**: irfanarfianto

## Kebutuhan yang dijawab

HR/IT tidak bisa menjawab "tahap X dipegang siapa, dan apakah ada pengajuan yang bakal mentok" dari satu tempat. Diukur prod 2026-10-23: tidak ada tahap berbasis izin yang kosong, tetapi tiga tahap payroll dipegang satu orang, dan penyetuju lintas departemen (live 2026-10-23, belum dipakai) akan membuat tahap atasan di empat modul kehilangan pemegang. Keputusan bentuk dari user 2026-10-23: tahap atasan pakai resolver; halaman untuk supervisor HRIS/IT; tandai kosong dan satu orang.

## Urutan

1. [BE] 1/4 **paling dulu dan mendesak**: harus live sebelum HR memakai penyetuju lintas departemen.
2. [BE] 2/4 (agregator) sesudah 1/4; [BE] 3/4 dan 4/4 sesudah 2/4, boleh paralel satu sama lain.
3. [FE] 1/2 deploy sesudah [BE] 2/4-4/4 live; [FE] 2/2 sesudah [FE] 1/2.

---

### Induk: Pengaturan Penyetuju per kategori × tahap

- **Repo**: bip-erp
- **Issue**: [bip-erp#3528](https://github.com/bip-itteam-internal/bip-erp/issues/3528)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Siapa memegang tiap tahap persetujuan tersebar di tiga menu, Hak Akses, dan aturan di kode; tahap kosong atau satu-orang tak terlihat siapa pun. Dua definisi "atasan departemen" yang berbeda membuat penyetuju lintas departemen tidak memegang tahap atasan di Pengajuan Barang, Permintaan GA, Realisasi PM, dan triase tiket.

## Keputusan

ADR "Pengaturan Penyetuju per Kategori dan Tahap, Satu Definisi SPV Departemen" (layak `Siap Agent` sesudah ADR berstatus Diterima). Induk tanpa PR; ditutup manual saat semua sub-issue merged.

## Yang harus benar

- [ ] Sub-issue [BE] 1/4-4/4 dan [FE] 1/2-2/2 merged dan ter-deploy berurutan sesuai bagian Urutan.

## Di luar cakupan

Mengubah izin akun dari halaman ini (menunggu ADR 0137); delegasi; rangkap jabatan; mengubah urutan tahap.

## Data / bukti pendukung

Lihat ADR §Context (ukur prod 2026-10-23).

## Prasyarat

ADR di atas Diterima.

---

### [BE] Pengaturan penyetuju bagian 1/4: tahap atasan departemen memakai resolver penyetuju departemen

- **Repo**: bip-erp
- **Issue**: [bip-erp#3529](https://github.com/bip-itteam-internal/bip-erp/issues/3529)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Tahap "atasan departemen" di procurement (`pb_spv_divisi`, `pb_spv_manufactur`, `pb_spv_quality`, `pb_leader_procurement`), inventory (Permintaan GA `spv_divisi`/`spv_hr`, verifikasi Realisasi PM), dan task-management (cabang supervisor divisi pada triase) membaca cakupan token `supervised_departments`, yang hanya lahir dari `is_supervisor` (`services/employee/department_scope.go:66`). Menetapkan penyetuju lintas departemen mematikan `is_supervisor` anggota, sehingga tahap itu kehilangan pemegang. Peta Penyetuju juga tidak menampilkan penyetuju pilihan (`peta_penyetuju.go:375` memakai `penyetujuPerDepartemenErr`, `department_approver.go:188`).

## Keputusan

ADR "Pengaturan Penyetuju per Kategori dan Tahap, Satu Definisi SPV Departemen" §1 dan §2 (layak `Siap Agent` sesudah ADR berstatus Diterima). Bentuk: siapa atasan departemen X = hasil `/internal/department-approver` (rantai `atasanDepartemen`), dipakai gerbang dan antrean lewat fungsi yang sama; cakupan token tidak diubah.

## Yang harus benar

- [ ] Departemen dengan penyetuju pilihan lintas departemen: penyetuju itu bisa melihat dan memutus `pb_spv_divisi` pengajuan barang staf departemen itu, `spv_divisi` Permintaan GA, dan muncul di antreannya (test gerbang + antrean, procurement dan inventory).
- [ ] Anggota departemen yang `is_supervisor`-nya dimatikan tidak lagi bisa memutus tahap atasan departemen itu (test).
- [ ] Verifikasi Realisasi PM dan `spv_hr` Permintaan GA = penyetuju departemen General Affair menurut resolver (rantai induk HRGA tetap jalan) (test).
- [ ] Triase tiket: admin space tetap menang; cabang "supervisor divisi" memakai resolver untuk `space.division` (test).
- [ ] Resolver tak terjangkau = gagal-tertutup (403/503 berpesan), bukan lolos; satu panggilan per departemen per permintaan (cache per permintaan).
- [ ] Peta Penyetuju menampilkan `penyetuju_departemen` untuk penyetuju pilihan lintas departemen, memakai `penyetujuBaris` (test).
- [ ] Departemen tanpa penyetuju pilihan: perilaku hari ini tidak berubah (penyetuju = `is_supervisor` / induk) (test regresi).
- [ ] `go build ./...` dan `go test` per service tersentuh tanpa kegagalan baru.

## Di luar cakupan

Mengubah cakupan token `supervised_departments`; tahap berbasis izin; halaman baru.

## Data / bukti pendukung

Prod 2026-10-23: 0 dari 13 departemen punya penyetuju pilihan (celah belum terjadi, akan terjadi saat dipakai). Kode: `services/procurement/pengajuan_barang_gate.go:22-29,90-103`, `pengajuan_barang_handler.go:323-346`, `services/inventory/permintaan_daftar.go:70-91`, `permintaan_gate.go:140`, `pm_realisasi.go:503-515`, `services/task-management/space_admin.go:98-106`, `task_filter.go:236-238`.

## Prasyarat

ADR di atas Diterima. Deploy: procurement, inventory, task-management, employee-service naik bersama.

---

### [BE] Pengaturan penyetuju bagian 2/4: agregator `GET /pengaturan-penyetuju` + tahap pengajuan karyawan, pelatihan, Live Support

- **Repo**: bip-erp
- **Issue**: [bip-erp#3530](https://github.com/bip-itteam-internal/bip-erp/issues/3530)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Belum ada endpoint yang menjawab "kategori → tahap → pemegang" lintas modul (`git grep` origin/main 2026-10-23: nihil).

## Keputusan

ADR "Pengaturan Penyetuju per Kategori dan Tahap, Satu Definisi SPV Departemen" §3 (layak `Siap Agent` sesudah ADR berstatus Diterima). Bentuk tahap dari service: `{kategori, tahap, label, urutan, mekanisme, kunci}`; agregator mengisi pemegang + `kosong` + `satu_orang` + `tidak_terbaca`.

## Yang harus benar

- [ ] `GET /pengaturan-penyetuju` (gerbang supervisor HRIS atau IT; lainnya 403) mengembalikan per kategori: tahap berurutan, pemegang aktif (id, nama, jabatan), `mekanisme`, `layar_pengatur`, `kosong`, `satu_orang`; slice tak pernah null.
- [ ] Registri sumber di employee-service berpola `registriAntrean` (kategori = kunci yang sama dengan Portal Persetujuan); sumber yang gagal masuk `tidak_terbaca`, tidak pernah `kosong` (test).
- [ ] `GET /internal/tahap-penyetuju` di attendance (pengajuan karyawan: tahap atasan berbasis `departemen`, tahap HR berbasis izin `hris.pengajuan.approve` + fallback yang dipakai gerbangnya), learning (SPV `departemen`, HR izin `training.work`), marketing-analytics (Live Support `departemen`); bergerbang kunci internal (test 401/403 tanpa kunci).
- [ ] Mekanisme `departemen`: penanda dihitung per departemen; departemen yang jatuh ke Direktur ditandai (bukan `kosong`).
- [ ] Hitungan pemegang `izin` memakai jalur yang sama dengan gerbangnya (termasuk fallback peran lama bila gerbang memakainya) (test dengan kontrol: izin hanya lewat posisi, hanya lewat akun).
- [ ] Endpoint GET baru: keputusan Copilot ditulis di PR (`Copilot: ya / tidak, karena ...`).

## Di luar cakupan

Tahap pengajuan barang, payroll, GA, PM, tiket, rekrutmen (bagian 3/4 dan 4/4); menulis.

## Data / bukti pendukung

Prod 2026-10-23 (`employee_db`): `hris.pengajuan.approve` 3 pemegang (akun 1, posisi 2); `training.work` 3 pemegang. Agregator pembanding: `services/employee/antrean_pengajuan.go:373-660`; resolver: `permission_holders.go:87`, `department_approver_lookup.go:74`.

## Prasyarat

[BE] 1/4 merged.

---

### [BE] Pengaturan penyetuju bagian 3/4: tahap pengajuan barang dan payroll

- **Repo**: bip-erp
- **Issue**: [bip-erp#3531](https://github.com/bip-itteam-internal/bip-erp/issues/3531)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Agregator butuh tahap pengajuan barang (21 kode tahap) dan payroll (4 tahap) dari sumber tunggalnya, termasuk izin yang membuka beberapa tahap sekaligus.

## Keputusan

ADR "Pengaturan Penyetuju per Kategori dan Tahap, Satu Definisi SPV Departemen" §3 (layak `Siap Agent` sesudah ADR berstatus Diterima). Pemetaan tahap → izin diturunkan dari `IzinPerTahapPengajuanBarang` dan `permissionUntukTahapPayroll`, tidak disalin.

## Yang harus benar

- [ ] `GET /internal/tahap-penyetuju` di procurement: tahap berbasis izin dengan kunci izin dari `common.IzinPerTahapPengajuanBarang`, tahap berbasis hubungan bermekanisme `departemen`, `pb_ap_transfer` menyebut cabang PT/CV.
- [ ] `GET /internal/tahap-penyetuju` di payroll: `TahapJenjangPayroll` berurutan dengan izin dari `permissionUntukTahapPayroll`.
- [ ] Respons agregator untuk tahap berbasis izin memuat `juga_membuka`: tahap lain yang dibuka izin yang sama (mis. `budget.approve.procurement` → `pb_procurement_beli`, `pb_tulis_po`, `pb_procurement_faktur`, `pb_kelebihan_bayar`) (test: mengubah peta izin di shared-library mengubah respons tanpa menyunting agregator).
- [ ] Test kesetaraan: kode tahap di respons = konstanta `Tahap*` di procurement.

## Di luar cakupan

Mengubah siapa pemegang izin; menghidupkan kembali koleksi `pengaturan_penyetuju_pembelian` (ADR 0057).

## Data / bukti pendukung

Prod 2026-10-23: `payroll.approve.cost_control`, `.hrd`, `.finance` masing-masing 1 pemegang (harus tampil `satu_orang`); izin `budget.*` 2-8 pemegang. Kode: `shared-library/common/izin_tahap_pengajuan_barang.go:20-38`, `services/payroll/models_payroll_run.go:24-53`.

## Prasyarat

[BE] 2/4 merged.

---

### [BE] Pengaturan penyetuju bagian 4/4: tahap Permintaan GA, Realisasi PM, triase tiket, rekrutmen

- **Repo**: bip-erp
- **Issue**: [bip-erp#3532](https://github.com/bip-itteam-internal/bip-erp/issues/3532)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Agregator butuh tahap dari inventory (Permintaan GA, Realisasi PM), task-management (triase tiket), dan recruitment (requisition, offer).

## Keputusan

ADR "Pengaturan Penyetuju per Kategori dan Tahap, Satu Definisi SPV Departemen" §3 (layak `Siap Agent` sesudah ADR berstatus Diterima).

## Yang harus benar

- [ ] `GET /internal/tahap-penyetuju` di inventory: Permintaan GA (`spv_divisi`/`spv_hr` = `departemen`, `serah_ga` = izin `ga.request.serah`; jenis tanpa persetujuan tampil apa adanya), Realisasi PM (verifikasi = `departemen` General Affair).
- [ ] `GET /internal/tahap-penyetuju` di task-management: triase per space = `penetapan` (admin space) + `izin` `ticket.triage` ∩ divisi; space tanpa admin dan tanpa pemegang triase divisi = `kosong`.
- [ ] `GET /internal/tahap-penyetuju` di recruitment: requisition dan offer = izin `recruitment.approve` + fallback HR supervisor yang dipakai gerbangnya.
- [ ] Semua bergerbang kunci internal (test).

## Di luar cakupan

Mengubah alur Permintaan GA atau triase.

## Data / bukti pendukung

Prod 2026-10-23: `ticket.triage` 7 pemegang, `recruitment.approve` 4, `ga.request.serah` 3. Kode: `services/inventory/permintaan_jenjang.go:18-25`, `pm_realisasi.go:38-41`, `services/task-management/routes.go:40-41`, `services/recruitment/routes.go:30-31`, `offer_setujui.go:11-13`.

## Prasyarat

[BE] 2/4 merged.

---

### [FE] Pengaturan penyetuju bagian 1/2: halaman Per Kategori (baca) + tab Per Orang

- **Repo**: erp-frontend
- **Issue**: [erp-frontend#2805](https://github.com/bip-itteam-internal/erp-frontend/issues/2805)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Belum ada halaman bersumbu tahap.

## Keputusan

ADR "Pengaturan Penyetuju per Kategori dan Tahap, Satu Definisi SPV Departemen" §4 (layak `Siap Agent` sesudah ADR berstatus Diterima).

## Yang harus benar

- [ ] Rute `/pengaturan/organisasi/pengaturan-penyetuju` (pola `HalamanSubPengaturan`), tab Per Kategori (bawaan) dan Per Orang (Peta Penyetuju yang sudah ada dipakai ulang), tab di query string.
- [ ] Daftar kategori memakai label kategori yang sama dengan Portal Persetujuan (satu kunci i18n, tidak disalin).
- [ ] Tiap tahap: urutan, label, pemegang, mekanisme; `kosong` = tanda merah, `satu_orang` = tanda kuning; kategori bertanda muncul di daftar kiri; `tidak_terbaca` = peringatan, bukan "kosong".
- [ ] Tahap berbasis izin menampilkan "juga membuka tahap …" dan tautan ke Hak Akses; tanpa tombol ubah.
- [ ] Lima keadaan layar, `Skeleton`, i18n id+en, responsif 390px tanpa luber, mode gelap.
- [ ] `pnpm tsc --noEmit`, `pnpm lint`, `pnpm build` hijau; `pnpm test` tanpa kegagalan baru terhadap baseline.

## Di luar cakupan

Menggabung/menghapus menu lama dan edit (bagian 2/2).

## Data / bukti pendukung

Desain Figma disetujui user 2026-10-23 (file privat tim, tautan di issue). Pola: `src/app/(main)/pengaturan/organisasi/peta-penyetuju/page.tsx`, `src/features/hris/pengaturan/lib/sections.ts`.

## Prasyarat

Deploy sesudah `bip-erp` [BE] 2/4, 3/4, 4/4 live.

---

### [FE] Pengaturan penyetuju bagian 2/2: gabung tiga menu, alihkan rute lama, edit penetapan

- **Repo**: erp-frontend
- **Issue**: [erp-frontend#2806](https://github.com/bip-itteam-internal/erp-frontend/issues/2806)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Tiga menu lama (Penyetuju Pengajuan, Penyetuju Booking Ruang, Peta Penyetuju) tetap terpisah, dan pengubahan penyetuju masih harus dicari di layar masing-masing.

## Keputusan

ADR "Pengaturan Penyetuju per Kategori dan Tahap, Satu Definisi SPV Departemen" §4 dan §5 (layak `Siap Agent` sesudah ADR berstatus Diterima).

## Yang harus benar

- [ ] Sidebar Organisasi hanya memuat satu menu Pengaturan Penyetuju; rute lama dialihkan ke tab/kategori setara (tautan lama tidak 404) (test sections + redirect).
- [ ] Panduan menu di `src/features/panduan/isi/hrga.ts` ditulis dari kunci i18n halaman (penjaga panduan hijau); entri tiga menu lama dirapikan.
- [ ] Dari halaman: ubah penyetuju departemen, Manager, penyetuju booking ruang, admin space lewat endpoint tulis yang sudah ada; tiap simpan menampilkan akibat (lintas departemen, siapa tergeser, pengajuan menunggu) dan toast dari pesan server.
- [ ] Wewenang izin/peran lama tetap hanya tautan.
- [ ] `layar_pengatur` yang dikirim backend Peta Penyetuju menunjuk rute baru (koordinasi dengan `bip-erp`; FE tetap menerima rute lama lewat pengalihan).
- [ ] tsc/lint/build hijau; test tanpa kegagalan baru.

## Di luar cakupan

Mengubah izin akun dari halaman ini (ADR 0137).

## Data / bukti pendukung

Komponen tulis yang sudah ada: `department-approver-manager.tsx` (penyetuju + Manager), halaman penyetuju booking ruang.

## Prasyarat

[FE] 1/2 merged.
