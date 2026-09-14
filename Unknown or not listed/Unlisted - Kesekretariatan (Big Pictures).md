## Deskripsi

*Dok induk departemen **Kesekretariatan** (`master_department.key` = `secretary`). Departemen ini tidak punya folder domain di vault karena isinya bercampur: pimpinan (Direktur dan Corporate Secretary), pendukung Direktur, branding dan desain korporat, Legal, R&D Regulatory, dan Internal Audit. Dok ini tidak menyalin isi dok detail. Tugasnya memetakan tiap jabatan ke modul sistem yang benar-benar dipakainya, lalu menunjuk dok yang memilikinya.*

- **Status**: ⚠️ Implemented (ada catatan). Modul `secretary` hidup di kode dengan dua area kerja (Legal dan R&D) ditambah satu layar KPI departemen, tetapi sebagian besar jabatan di departemen ini tidak punya modul kerja apa pun di sistem. Kolom kode diverifikasi ke `origin/main` bip-erp `72183415` dan erp-frontend `bd7320d3` pada 2026-09-14. Angka karyawan dan template bertanggal sesuai sumber yang disebut di tiap baris dan **belum diukur ulang ke produksi**.
- **Implementasi**: [[Microservices - Employee Service]] (register Legal dan R&D di-host di sini) · [[APP - Web ERP]] (kategori sidebar SEKRETARIAT dan Ruang Direktur)
- **Dok detail**: [[QA - Register Perizinan & Sertifikasi]] · [[QA - R&D Regulatory (Registrasi & Pipeline Produk)]] · [[Unlisted - Dashboard per Posisi (Kesekretariatan)]]
- **Peta lintas departemen**: [[REF - Peta Departemen]]

## Latar Belakang

- Sebelum dok ini ditulis (2026-09-14), bagian-bagian departemen ini tercatat di tiga tempat tanpa satu titik masuk: register Legal dan R&D di folder `Quality & Regulatory`, rancangan dashboard di `Unknown or not listed`, dan Ruang Direktur di dalam [[APP - Web ERP]]. Dok dashboard-nya sendiri menyatakan divisi ini "tidak punya padanan domain di vault".
- Legal dan R&D semula dirancang sebagai departemen dan modul sendiri (`legal`, `rnd`). Keduanya dilebur ke modul `secretary` pada 2026-08-13 karena departemennya tidak pernah ada di `master_department` produksi, sementara satu-satunya karyawan berjabatan Legal duduk di Kesekretariatan (komentar `shared-library/common/catalog_secretary.go` dan `DefaultDepartments()` di `shared-library/models/employee/master_data.go`). Rute halaman `/legal/*` dan `/rnd/*` sengaja tidak ikut pindah karena `menu_hidden` menyimpan URL dan mencocokkannya persis.
- Ukuran: **11 karyawan** (diukur produksi 2026-08-04, [[Finance - Kas Kecil dan Pengajuan Budget]]). Empat di antaranya belum punya atasan langsung (`supervisor_id`) per 2026-08-26 ([[ADR - 0054 Peninjau Ide Kaizen Bisa Atasan Departemen, Bukan Hanya Komite Terpusat]]).

## Ruang Lingkup / Cakupan

### Jabatan dan modul yang dipakainya

Daftar jabatan di bawah adalah **seed kode** (`DefaultDepartments()`, key `secretary`). `master_department` produksi dikelola manual lewat Master Data, jadi isinya bisa berbeda. Kolom template KPI diambil dari salinan produksi 2026-08-01 di [[HRIS - Matriks KPI per Departemen]].

| Jabatan (seed) | Modul / layar kerja di sistem | Peran yang diturunkan dari jabatan | Template KPI (prod 2026-08-01) |
|---|---|---|---|
| Direktur | Ruang Direktur `/direktur` | 15 kunci modul, lihat catatan di bawah tabel | tidak tercatat |
| Corporate Secretary | Ruang Direktur | `secretary: supervisor` | `CORPORATE SECRETARY`, 4 metrik |
| Legal | Perizinan & Sertifikasi, Kontrak & SLA, Dispute & Advis (`/legal/*`) | `legal: staff` | tidak tercatat |
| QA RND | Registrasi NIE / BPOM / Halal, Pengembangan Produk (`/rnd/*`) | `rnd: staff` ⚠️ | `R&D REGULATORY`, 4 metrik |
| Internal Audit | [[APP - Audit Internal]] (aplikasi terpisah, masuk lewat SSO) | tidak ada | `INTERNAL AUDIT`, 5 metrik |
| Personal Assistant | tidak ada modul khusus | tidak ada, sengaja ([[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]]) | `PERSONAL ASSISTANT`, 4 metrik |
| Company Branding | tidak ada modul khusus | tidak ada | `COMPANY BRANDING`, 4 metrik |
| Graphic Design | tidak ada modul khusus | tidak ada | `GRAPHIC DESIGNER`, 3 metrik |
| Video Editor | tidak ada modul khusus | tidak ada | `VIDEOGRAPHER & EDITOR COMPANY`, 4 metrik |
| Administrative | tidak ada modul khusus | tidak ada | tidak tercatat |
| Business Unit Assistant | tidak ada modul khusus | tidak ada | tidak tercatat |

Catatan tabel:

- **Peran turunan** dibaca dari blok `kesekretariatan` di `services/employee/peran_dari_jabatan.go`, dan hanya mengisi `system_roles` akun yang masih kosong ([[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]]). Direktur menerima `secretary`, `procurement`, `manufacture`, `quality`, `rnd`, `ga`, `integration`, `insentive`, `beauty_hacks`, `kyura`, dan `it` bernilai `supervisor`; `hris`, `finance`, dan `legal` bernilai `admin`; `warehouse` bernilai `spv`. Keputusan 2026-08-11 dengan hak tulis diterima eksplisit. `it: supervisor` membuka IT Orchestrator, sehingga jabatan ini bisa mengubah RBAC-nya sendiri, dan itu diterima sadar.
- **Corporate Secretary setara Direktur dalam MEMUTUS, bukan dalam akses modul.** Daftarnya satu sumber di `shared-library/common/jabatan_direktur.go` (`SetaraDirektur`: `direktur`, `corporate secretary`), dipakai slot persetujuan cuti dan perjalanan dinas di attendance-service serta penyetuju Pesanan Pembelian di procurement-service. Menambah jabatan ke daftar itu memberi wewenang Direktur di seluruh alur tersebut, jadi itu keputusan organisasi, bukan pembersihan kode.
- ⚠️ **`qa_rnd` dipetakan ke `rnd: staff` berdasarkan nama jabatannya dan belum dikonfirmasi ke pemilik produk** (komentar di `peran_dari_jabatan.go`). Bila keliru, yang terbuka adalah dua register registrasi produk, dan pencabutannya satu baris.

### Modul `secretary`

- **Katalog izin**: `shared-library/common/catalog_secretary.go`. Izin dipecah per AREA: `secretary.legal.view/work/manage` dan `secretary.rnd.view/work/manage`. Tanpa `approve` (tak satu pun dari 25 rute menyetujui apa pun), dan reach selalu `all`. Paketnya `secretary_legal_*` dan `secretary_rnd_*`. Rincian mekanisme izin di [[CORE - RBAC dan Permission Set]].
- **Backend**: 25 rute di employee-service. Legal 15 rute (`legal_perizinan.go`, `legal_kontrak.go`, `legal_dispute.go`) dan R&D 10 rute (`rnd_regulatory.go`, `rnd_product.go`), seluruhnya digerbang `secretary_gate.go`.
- ⛔ **`system_roles.secretary` SENGAJA tidak membuka Legal maupun R&D.** Peran itu hanya berarti "boleh melihat KPI departemen Kesekretariatan" lewat `deptKeyToNames`. Memetakannya ke register akan memberi seluruh departemen, termasuk Graphic Design dan Video Editor, akses register Legal. Ditahan uji `TestPeranSecretaryTidakMemberiLegalAtauRnd`.
- **Sidebar** (`erp-frontend/src/components/layout/sidebar-menus.tsx`, kunci `secretary`). Labelnya `SEKRETARIAT`, atau `WORKSPACE` bagi anggota departemen ini (`KATEGORI_UTAMA_DEPARTEMEN` di `sidebar-kategori.ts`). Isinya:
  - **KPI** (`/secretary/kpi`, merender `KpiPageContent` terkunci ke departemen `Kesekretariatan`). Disaring `bolehKpiSekretariat` di `sekretariat-menu.ts`: lolos bila peran `hris` bernilai `staff`/`supervisor`, atau `secretary` bernilai `supervisor`/`admin`. `secretary: staff` tidak lolos, cermin gerbang KPI lama di backend.
  - **Perizinan & Sertifikasi**, **Kontrak & SLA**, **Dispute & Advis** (izin `secretary.legal.view`).
  - **Registrasi NIE / BPOM / Halal**, **Pengembangan Produk** (izin `secretary.rnd.view`).
  - **Referensi Procurement**: Kontrak Vendor dan Master Pemasok, baca-saja (izin `secretary.legal.view`).
  - **Data WMS**: Master Produk (BOM), Gudang RM, Analisa Stok, baca-saja (izin `secretary.rnd.view`).
- **Alias kategori** (`modul-aktif.ts`): pemegang `system_roles.legal` atau `rnd` diarahkan ke kategori `secretary`. Tanpa alias itu mereka kehilangan seluruh menunya tanpa galat, karena kunci `legal` dan `rnd` sudah tidak ada di objek menu.

### Ruang Direktur

Layar `/direktur` dengan tab Persetujuan, Kinerja Divisi, dan Keuangan, disusun dari endpoint yang sudah ada. Menunya digerbang izin `finance.profit.view`, yang juga dicerminkan `features/erp/portal/lib/gerbang-departemen.ts` untuk pilihan dashboard portal. Isi dan cakupan tiap antreannya didokumentasikan di [[APP - Web ERP]] dan sengaja tidak disalin di sini.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| Direktur | jabatan `Direktur`, Kesekretariatan | peran turunan di 15 modul; izin `finance.profit.view` untuk Ruang Direktur | Web ERP |
| Corporate Secretary | jabatan `Corporate Secretary`, Kesekretariatan | `secretary: supervisor`; wewenang memutus setara Direktur lewat `SetaraDirektur` | Web ERP |
| Staf Legal | jabatan `Legal`, Kesekretariatan | `legal: staff` atau paket Sekretariat Legal | Web ERP |
| R&D Regulatory | jabatan `QA RND`, Kesekretariatan | `rnd: staff` atau paket Sekretariat R&D | Web ERP |
| Internal Audit | jabatan `Internal Audit`, Kesekretariatan | paket `audit_auditor` di aplikasi Audit Internal | Web (aplikasi terpisah) |
| Pendukung Direktur dan kreatif | Personal Assistant, Administrative, Business Unit Assistant, Company Branding, Graphic Design, Video Editor | tanpa modul kerja khusus | MyBharata (presensi, pengajuan) |

- **Tujuan**: pimpinan memutus antrean persetujuan lintas modul dari satu layar; staf Legal dan R&D Regulatory memegang register izin, kontrak, sengketa, dan registrasi produk di ERP.
- **Pain point**: pekerjaan sebagian besar jabatan di departemen ini tidak melewati sistem. Hasilnya **0 dari 28 metrik KPI** departemen ini otomatis ([[HRIS - Matriks KPI per Departemen]], salinan 2026-08-01), dan register Legal serta R&D lahir untuk menggantikan pencatatan di luar sistem.
- **Aksi utama**: memutus persetujuan di Ruang Direktur; mencatat dan memperbarui register di `/legal/*` dan `/rnd/*`; melihat KPI departemen di `/secretary/kpi`.

## Konsumen Data

- [[HRIS - Matriks KPI per Departemen]]: bab Kesekretariatan, 7 template dan 28 metrik, seluruhnya manual (salinan produksi 2026-08-01).
- [[REF - Dashboard per Posisi (Indeks Cakupan)]] dan [[Unlisted - Dashboard per Posisi (Kesekretariatan)]]: divisi yang paling tidak terukur; lima dari tujuh posisi ber-template tidak direkomendasikan dibuatkan dashboard.
- [[HRIS - Organization Structure]]: bagan organisasi menaruh Direktur di dalam Kesekretariatan, bukan di puncak, karena `work_data.department` Direktur bernilai `Kesekretariatan`.

## Kendala

- **Sebagian besar jabatan tak punya jejak kerja di sistem.** Tracker garapan desain dan video, integrasi akun organik perusahaan, dan tracker izin BPOM belum ada. Urutan kebutuhannya di [[Unlisted - Dashboard per Posisi (Kesekretariatan)]].
- **Data peran pernah terbalik.** [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]] mencatat Direktur tanpa satu pun peran, sementara seorang Personal Assistant memegang tujuh termasuk `group: admin` dan `it: supervisor`. Penurunan peran dari jabatan hanya mengisi akun yang `system_roles`-nya kosong, jadi peran yang telanjur terpasang tidak dikoreksi otomatis. Keadaan terkininya belum diukur ulang.

## Belum Diputuskan (TBD)

- Apakah Kesekretariatan perlu folder domain sendiri di vault (rulebook §2), atau cukup dok induk ini di `Unknown or not listed`.
- Konfirmasi pemilik produk atas pemetaan jabatan `QA RND` ke `rnd: staff`.
- **Posisi Internal Audit.** [[APP - Audit Internal]] menulis posisi auditor internal "belum ada; direncanakan", sementara seed kode memuat jabatan `Internal Audit` di departemen ini dan salinan produksi memuat template KPI `INTERNAL AUDIT`. Yang belum diukur: apakah jabatan itu punya pemegang di produksi.
- Isi `master_department` Kesekretariatan di produksi dibanding seed kode. Jabatan `Direktur`, `Legal`, `Administrative`, dan `Business Unit Assistant` tidak tercatat punya template KPI.

## Dokumen Terkait

- [[REF - Peta Departemen]]: posisi departemen ini di antara departemen lain
- [[QA - Register Perizinan & Sertifikasi]] · [[QA - R&D Regulatory (Registrasi & Pipeline Produk)]]: dua area modul `secretary`
- [[Unlisted - Dashboard per Posisi (Kesekretariatan)]]: rancangan dashboard per posisi
- [[APP - Web ERP]]: sidebar SEKRETARIAT dan Ruang Direktur
- [[APP - Audit Internal]] · [[Finance - Audit Internal]]: modul jabatan Internal Audit
- [[CORE - RBAC dan Permission Set]] · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]]: izin dan peran
- [[HRIS - Organization Structure]] · [[HRIS - Matriks KPI per Departemen]]
- [[Microservices - Employee Service]]
