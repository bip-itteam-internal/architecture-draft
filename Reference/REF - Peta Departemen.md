## Deskripsi

*Peta dari tiap departemen yang tercatat di sistem ke kunci modulnya, kategori sidebar-nya, dan dok vault yang menjadi titik masuknya. Menjawab dua pertanyaan: "departemen X didokumentasikan di mana" dan "departemen mana yang belum punya rumah di vault". Dok ini BUKAN daftar departemen yang hidup; ia pintu ke dok lain.*

- **Status**: ⚠️ Implemented (ada catatan). Kolom kode diverifikasi ke `origin/main` bip-erp `72183415` dan erp-frontend `bd7320d3` pada 2026-09-14. Daftar departemennya diambil dari sensus produksi **2026-08-19** di [[HRIS - Organization Structure]] dan **belum diukur ulang**, karena pembacaan produksi dari sesi penyusunan ditolak. Departemen yang lahir sesudah tanggal itu belum tentu ada di sini. ⚠️ **Ukur ulang sebelum dipakai mengambil keputusan.**
- **Daftar hidupnya** ada di `GET /master/departments` ([[Microservices - Employee Service]]) dan tab **Peta Struktur** di `/pengaturan/organisasi?tab=peta-struktur`. Tab itu sengaja menarik isinya hidup; menurut komentarnya, menuliskan daftar departemen sebagai gambar tetap "akan melahirkan sumber kebenaran kedua yang membusuk diam-diam". Tabel di bawah karena itu bertanggal, dan fungsinya memetakan ke dok, bukan menggantikan layar itu.

## Peta departemen

Kunci modul dari `deptKeyToNames` (`shared-library/common/roles.go`). Kategori sidebar utama dari `KATEGORI_UTAMA_DEPARTEMEN` (`erp-frontend/src/components/layout/sidebar-kategori.ts`).

| Departemen (`name`) | `key` | Kategori sidebar utama | Dok induk di vault | Titik masuk lain |
|---|---|---|---|---|
| Human Resource | `hris` | `hris` (label HRGA) | [[HRIS - Big Pictures]] | [[HRIS - Organization Structure]] · [[HRIS - Dashboard per Posisi]] |
| General Affair | `ga` | `hris` (menu GA menumpang di blok HRGA) | [[GA - Big Pictures]] | [[GA - Dashboard per Posisi]] |
| Tech Development | `it` | `it` | [[IT - Big Pictures]] | [[IT - Dashboard per Posisi]] |
| Kesekretariatan | `secretary` | `secretary` (label SEKRETARIAT) | [[Unlisted - Kesekretariatan (Big Pictures)]] | [[QA - Register Perizinan & Sertifikasi]] · [[QA - R&D Regulatory (Registrasi & Pipeline Produk)]] · [[Unlisted - Dashboard per Posisi (Kesekretariatan)]] |
| Finance | `finance` | `finance` (label FAT) | [[Finance - Big Pictures]] | [[Finance - Dashboard per Posisi (FAT)]] · [[Finance - Rancangan Finance Service]] |
| Beauty Hacks | `beauty_hacks` | `marketing` | [[Sales - Big Pictures]] | [[Sales - Dashboard per Posisi (Beauty Hacks & Kyura)]] |
| Kyura | `kyura` | `marketing` | [[Sales - Big Pictures]] | [[Sales - Dashboard per Posisi (Beauty Hacks & Kyura)]] |
| Manufaktur | `manufacture` | `manufacture` (label WMS ERP OPERATIONAL), juga memegang `warehouse` | tidak ada dok induk tunggal | [[Manufacture - Dashboard per Posisi]] · [[WH - Management System]] · [[Microservices - Manufacture Service]] · [[Microservices - Warehouse Service]] |
| Quality | `quality` | `quality` | [[QA - Big Pictures]] | [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]] · [[QA - Dashboard per Posisi]] |
| Procurement | `procurement` | `procurement` | tidak ada dok induk tunggal | [[Microservices - Procurement Service]] · [[GA - Dashboard per Posisi]] (memuat Procurement) · [[GA - Form Pengadaan dan Pengajuan Dana]] |
| Marketing Offline Distribution | `marketing` | tidak ada | **tidak ada**, lihat bab di bawah | [[HRIS - Organization Structure]] |
| Printing | `printing` | tidak ada | **tidak ada**, lihat bab di bawah | [[HRIS - Organization Structure]] · [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]] |
| Percetakan (tenant ELT) | `pct` | tidak ada | tidak ada | [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]]; nol karyawan sesudah perpindahan 2026-08-19 |

Catatan tabel:

- **General Affair tidak punya kategori sidebar utama sendiri.** Menu GA tinggal di kategori `hris`, dan blok `ga` digabung ke blok HRGA oleh `gabungBlokHrga` setelah penyaringan izin. `HRGA` adalah `supervision_label`, bukan nama departemen siapa pun.
- **Beauty Hacks dan Kyura berbagi kategori `marketing`.** Kategori itu tidak ada hubungannya dengan departemen ber-key `marketing` (Marketing Offline Distribution); lihat bab berikut.
- **`deptKeyToNames.finance` memetakan ke Finance DAN Procurement.** Gerbang yang membaca peta ini (mis. akses KPI per departemen bagi peran bernilai `supervisor`/`admin`) karena itu meloloskan pemegang peran `finance` ke departemen Procurement.

## Kunci yang terdengar seperti departemen, tapi bukan

| Kunci / label | Apa sebenarnya | Sumber |
|---|---|---|
| `legal` ("Legal"), `rnd` ("R&D Regulatory") | Masih tercatat di `deptKeyToNames`, tetapi **bukan departemen di produksi**. Keduanya dilebur ke modul `secretary` 2026-08-13 dan kini berwujud jabatan `Legal` dan `QA RND` di Kesekretariatan. Peran lamanya tetap hidup sebagai tier fallback dan dialiaskan ke kategori `secretary`. | `catalog_secretary.go`, `modul-aktif.ts` |
| `printing` di `deptKeyToNames` | Entri **inert**: nol akun memegang peran `printing`. Ditulis supaya Printing tidak mengulang keadaan departemen `marketing` yang hidup tanpa pemetaan. | komentar `roles.go` |
| kategori sidebar `marketing` | Wilayah kerja Beauty Hacks dan Kyura (analitik laba, penugasan akun ICC, komplain ke QC). **Bukan** departemen ber-key `marketing`. | `sidebar-kategori.ts` |
| kategori sidebar `audit` (label AUDIT INTERNAL) | Modul pemeriksaan internal, bukan departemen. | [[APP - Audit Internal]] |
| kategori sidebar `warehouse` | Kategori kedua milik Manufaktur. | `sidebar-kategori.ts` |
| kategori sidebar `erp`, `integration` | Tidak dipetakan ke departemen mana pun di `KATEGORI_UTAMA_DEPARTEMEN`. | `sidebar-menus.tsx`, `sidebar-kategori.ts` |
| label `HRGA` | `supervision_label` gabungan Human Resource dan General Affair; tak seorang pun ber-`work_data.department` = `HRGA`. | [[HRIS - Organization Structure]] |

## Departemen tanpa dok induk, dan kenapa dibiarkan begitu

Dua departemen hidup di master data produksi tanpa kategori sidebar, modul, pemetaan peran yang berlaku, maupun template KPI. Dok induk untuk keduanya hari ini akan berisi TBD hampir seluruhnya, jadi **keberadaannya dicatat di sini dan di [[HRIS - Organization Structure]], bukan di dok domain tersendiri**.

### Printing (`printing`)

- Ditambahkan ke tenant BIP 2026-08-19 sebagai tujuan perpindahan 14 karyawan CV Elit (dari `pct` "Percetakan"), dengan 13 jabatan disalin dari ELT. Riwayat dan aturannya di [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]] dan [[HRIS - Organization Structure]].
- **Yang ada di kode**: jadwal kerja khusus di attendance-service. `services/attendance/schedule_list.go` memberi Printing paket jadwal produksi ditambah jadwal satpam pabrik (19:00 sampai 07:00, tujuh hari, bukan bergilir; `func.go`), didefinisikan di region Printing pada `setup.go`. Rinciannya di [[Microservices - Attendance Service]].
- **Yang tidak ada**: kategori sidebar, modul, turunan peran di `peran_dari_jabatan.go`, dan template KPI (per salinan 2026-08-01, saat departemennya masih bernama Percetakan di ELT).
- ⚠️ **Penyetuju pengajuannya hanya bertumpu pada flag `is_supervisor` eksplisit**: `supervised_by` kosong dan tak ada jabatan yang cocok pola `Supervisor|^Leader$` ([[HRIS - Organization Structure]]).

### Marketing Offline Distribution (`marketing`)

- Lahir murni sebagai master data: tidak ada di `DefaultDepartments()` maupun `deptKeyToNames` ([[HRIS - Organization Structure]]). **1 karyawan** (diukur produksi 2026-08-04, [[Finance - Kas Kecil dan Pengajuan Budget]]), tanpa template KPI per salinan 2026-08-01.
- ⚠️ **Tanpa pemetaan peran, supervisor yang kelak diberi peran departemen ini tidak menjangkau departemennya sendiri, dan gagalnya berupa daftar kosong, bukan galat** (komentar `roles.go` di entri `printing`).

### Kapan dok induk layak dibuat

Begitu salah satu departemen di atas mendapat **kategori sidebar, modul, atau template KPI**. Saat itu ada perilaku sistem yang bisa didokumentasikan, dan dok induknya mengikuti pola [[Unlisted - Kesekretariatan (Big Pictures)]].

## Selisih yang ditemukan saat menyusun peta (2026-09-14)

1. **Printing di master data.** Komentar `services/employee/kpi_grup_departemen.go` menyatakan "`Printing` ada di work_data tapi tak terdaftar di master", sedangkan [[HRIS - Organization Structure]] mencatat `printing` ditambahkan ke `master_department` BIP 2026-08-19 dan terverifikasi lewat gateway. Salah satunya basi. Yang bisa memutuskannya hanya sensus produksi; sampai itu dilakukan, **jangan menyimpulkan dari salah satunya**.
2. **Posisi Internal Audit.** [[APP - Audit Internal]] menulis posisi auditor internal "belum ada; direncanakan", sementara seed kode memuat jabatan `Internal Audit` di Kesekretariatan dan salinan produksi memuat template KPI `INTERNAL AUDIT`. Belum diukur apakah jabatan itu punya pemegang.
3. **Manufaktur dan Procurement tidak punya dok induk tunggal.** Keduanya tetap tercakup lewat dok service, dok dashboard, dan (untuk Manufaktur) folder `Manufacture` serta `Warehouse`. [[GA - Procurement System]] berstatus konsep yang sudah digantikan, jadi jangan dipakai sebagai titik masuk Procurement.
4. **Catatan "belum merge" untuk bagan kanvas dan tab Peta Struktur** di [[HRIS - Organization Structure]] sudah basi: ketiga commit-nya ada di `origin/main` erp-frontend (`5ae2f31c`, `34e50bf6`, `297501b8`, semuanya 2026-08-28). Diperbarui di sesi yang sama; status deploy produksinya belum diukur.

## Cara memperbarui

1. Sensus ulang produksi, baca saja, di `employee_db`: isi `master_department` (`key`, `name`, `company_id`), jumlah `work_data` per `department`, dan `kpi_template` per `department`. Bandingkan dengan tabel.
2. Departemen baru: tambah baris, lalu putuskan dok induknya memakai aturan "Kapan dok induk layak dibuat".
3. `deptKeyToNames` atau `KATEGORI_UTAMA_DEPARTEMEN` berubah: perbarui kolom kode dan catat commit acuannya.

## Dokumen Terkait

- [[HRIS - Organization Structure]]: mekanisme master departemen, grup supervisi, dan penyetuju
- [[REF - Kepemilikan Data]]: pemilik tiap fakta bisnis, pasangan peta ini dari sisi data
- [[REF - Dashboard per Posisi (Indeks Cakupan)]]: cakupan dashboard per divisi
- [[HRIS - Matriks KPI per Departemen]]: template KPI per departemen
- [[CORE - RBAC dan Permission Set]]: peran, izin, dan peta departemen di RBAC
- [[APP - Web ERP]]: kategori sidebar
- [[HOMEPAGE]]
