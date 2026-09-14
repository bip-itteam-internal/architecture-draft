## Deskripsi

*Peta dari tiap departemen yang tercatat di sistem ke kunci modulnya, kategori sidebar-nya, dan dok vault yang menjadi titik masuknya. Menjawab dua pertanyaan: "departemen X didokumentasikan di mana" dan "departemen mana yang belum punya rumah di vault". Dok ini BUKAN daftar departemen yang hidup; ia pintu ke dok lain.*

- **Status**: ⚠️ Implemented (ada catatan). Kolom kode diverifikasi ke `origin/main` bip-erp `72183415` dan erp-frontend `bd7320d3`. Daftar departemen, jumlah karyawan, dan jumlah template diukur dari sensus produksi baca-saja `employee_db` pada **2026-09-14**. ⚠️ **Ukur ulang sebelum dipakai mengambil keputusan.** Temuan terpenting sensus itu: departemen ber-key `printing` bernama `Percetakan` di data, tetapi `Printing` di kode dan di template KPI; lihat bab "Selisih nama Printing dan Percetakan".
- **Daftar hidupnya** ada di `GET /master/departments` ([[Microservices - Employee Service]]) dan tab **Peta Struktur** di `/pengaturan/organisasi?tab=peta-struktur`. Tab itu sengaja menarik isinya hidup; menurut komentarnya, menuliskan daftar departemen sebagai gambar tetap "akan melahirkan sumber kebenaran kedua yang membusuk diam-diam". Tabel di bawah karena itu bertanggal, dan fungsinya memetakan ke dok, bukan menggantikan layar itu.

## Peta departemen

Kunci modul dari `deptKeyToNames` (`shared-library/common/roles.go`). Kategori sidebar utama dari `KATEGORI_UTAMA_DEPARTEMEN` (`erp-frontend/src/components/layout/sidebar-kategori.ts`). Kolom karyawan dan template dari sensus produksi 2026-09-14: `work_data` per nilai `department` (total / akun aktif) dan `kpi_template` per nilai `department` (aktif / arsip).

| Departemen (`name` di master) | `key` | Karyawan (total / aktif) | Template KPI (aktif / arsip) | Kategori sidebar utama | Dok induk di vault | Titik masuk lain |
|---|---|---|---|---|---|---|
| Human Resource | `hris` | 7 / 5 | 5 / 4 | `hris` (label HRGA) | [[HRIS - Big Pictures]] | [[HRIS - Organization Structure]] · [[HRIS - Dashboard per Posisi]] |
| General Affair | `ga` | 15 / 14 | 5 / 6 | `hris` (menu GA menumpang di blok HRGA) | [[GA - Big Pictures]] | [[GA - Dashboard per Posisi]] |
| Tech Development | `it` | 11 / 6 | 3 / 4 | `it` | [[IT - Big Pictures]] | [[IT - Dashboard per Posisi]] |
| Kesekretariatan | `secretary` | 11 / 8 | 7 / 1 | `secretary` (label SEKRETARIAT) | [[Unlisted - Kesekretariatan (Big Pictures)]] | [[QA - Register Perizinan & Sertifikasi]] · [[QA - R&D Regulatory (Registrasi & Pipeline Produk)]] · [[Unlisted - Dashboard per Posisi (Kesekretariatan)]] |
| Finance | `finance` | 19 / 16 | 12 / 2 | `finance` (label FAT) | [[Finance - Big Pictures]] | [[Finance - Dashboard per Posisi (FAT)]] · [[Finance - Rancangan Finance Service]] |
| Beauty Hacks | `beauty_hacks` | 54 / 47 | 12 / 7 | `marketing` | [[Sales - Big Pictures]] | [[Sales - Dashboard per Posisi (Beauty Hacks & Kyura)]] |
| Kyura | `kyura` | 38 / 32 | 12 / 5 | `marketing` | [[Sales - Big Pictures]] | [[Sales - Dashboard per Posisi (Beauty Hacks & Kyura)]] |
| Manufaktur | `manufacture` | 34 / 33 | 11 / 10 | `manufacture` (label WMS ERP OPERATIONAL), juga memegang `warehouse` | tidak ada dok induk tunggal | [[Manufacture - Dashboard per Posisi]] · [[WH - Management System]] · [[Microservices - Manufacture Service]] · [[Microservices - Warehouse Service]] |
| Quality | `quality` | 6 / 6 | 4 / 0 | `quality` | [[QA - Big Pictures]] | [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]] · [[QA - Dashboard per Posisi]] |
| Procurement | `procurement` | 4 / 3 | 2 / 0 | `procurement` | tidak ada dok induk tunggal | [[Microservices - Procurement Service]] · [[GA - Dashboard per Posisi]] (memuat Procurement) · [[GA - Form Pengadaan dan Pengajuan Dana]] |
| Marketing Offline Distribution | `marketing` | 1 / 1 | 0 | tidak ada | **tidak ada**, lihat bab di bawah | [[HRIS - Organization Structure]] |
| Percetakan | `printing` | 14 / 13 | 0 atas nama `Percetakan`; ⚠️ **4 / 0 atas nama `Printing`** | tidak ada | **tidak ada**, lihat bab di bawah | [[HRIS - Organization Structure]] · [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]] |
| Percetakan (tenant ELT) | `pct` | 0 | 0 | tidak ada | tidak ada | [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]]; masih ada di master dengan 14 jabatan |

Catatan tabel:

- **Nama master dan data selaras, kecuali satu.** Kedua belas nama departemen BIP di `master_department` muncul persis sebagai nilai `work_data.department`, dan setiap nilai `kpi_template.department` cocok dengan nama master **kecuali `Printing`**.
- **General Affair tidak punya kategori sidebar utama sendiri.** Menu GA tinggal di kategori `hris`, dan blok `ga` digabung ke blok HRGA oleh `gabungBlokHrga` setelah penyaringan izin. `HRGA` adalah `supervision_label`, bukan nama departemen siapa pun.
- **Beauty Hacks dan Kyura berbagi kategori `marketing`.** Kategori itu tidak ada hubungannya dengan departemen ber-key `marketing` (Marketing Offline Distribution); lihat bab berikut.
- **`deptKeyToNames.finance` memetakan ke Finance DAN Procurement.** Gerbang yang membaca peta ini (mis. akses KPI per departemen bagi peran bernilai `supervisor`/`admin`) karena itu meloloskan pemegang peran `finance` ke departemen Procurement.
- **Jumlah akun.** `system_authentication` berisi 216 akun (186 aktif), sedangkan `work_data` berjumlah 214 (184 dengan akun aktif). Dua akun tanpa `work_data` belum diperiksa apakah keduanya akun pihak luar.

## Selisih nama Printing dan Percetakan

Keadaan per sensus produksi 2026-09-14:

| Tempat | Nilai | Sumber |
|---|---|---|
| `master_department` key `printing` (BIP) | `name` = **`Percetakan`**, 19 jabatan | sensus produksi |
| `work_data.department` (14 karyawan, 13 aktif) | **`Percetakan`**; nol dokumen bernilai `Printing` | sensus produksi |
| `kpi_template.department` (4 template aktif) | **`Printing`** | sensus produksi |
| `employee.DeptPrinting` | **`"Printing"`** | `shared-library/models/employee/master_data.go` |
| `deptKeyToNames["printing"]` | **`{"Printing"}`** | `shared-library/common/roles.go` |

**Asal-usulnya.** Departemen ini dibuat 2026-08-19 dengan nama `Printing` dan 13 jabatan ([[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]]), dan migrasi hari itu menulis `work_data.department = "Printing"` untuk 14 karyawan pindahan (verifikasinya menghitung 14 dokumen `Printing`). Sesudah itu nama di master dan di `work_data` berubah jadi `Percetakan`, dan jabatannya bertambah jadi 19. Kapan dan lewat jalur apa belum diketahui: pencarian di employee-service tidak menemukan kode yang merambatkan ganti nama departemen ke `work_data`, sementara `kpi_template` dan konstanta kode tidak ikut berubah.

**Akibat yang terbukti dari kode** (belum dicoba di layar):

1. **Picker jadwal kerja.** `scheduleListForDepartment` (`services/attendance/schedule_list.go`) memilih paket jadwal per NAMA departemen, dan hanya `case employee.DeptPrinting` (`"Printing"`) yang memberi paket produksi ditambah jadwal satpam pabrik `SecurityElit`. Nama `Percetakan` jatuh ke `default: return nil, false`, sehingga `schedule-list` untuk departemen itu dibalas 400. Frontend mengirim departemen asli dari posisi terpilih (`departemenUntukJadwal` di `features/hris/employee/lib/schedule-department.ts`), yaitu `Percetakan`. Uji attendance bahkan mengunci `"Percetakan"` sebagai nama yang ditolak. Menurut [[Microservices - Attendance Service]], gejalanya di layar adalah simpan Data Pekerjaan gagal tanpa satu kata pun soal jadwal. Validasi jadwal buatan HR (`jadwal_buatan_hr.go`) juga menolak `Percetakan` sebagai departemen tak dikenal.
2. **Template KPI.** Pratinjau KPI Saya mencari kandidat template dengan `{department, position}` persis dari `work_data` (`services/employee/kpi_me_pratinjau.go`), jadi keempat template `Printing` tidak pernah jadi kandidat bagi karyawan `Percetakan`. Jalur KPI lain (penetapan, penilaian, halaman KPI per departemen) belum ditelusuri.

**Yang belum diukur:** apakah keempat template itu punya penetapan atau skor untuk karyawan Percetakan, dan kapan namanya berganti.

**Belum diputuskan (TBD), dan bukan keputusan dok ini:** nama mana yang dipakai. Menyamakan ke `Percetakan` berarti mengubah `DeptPrinting`, entri `deptKeyToNames`, uji attendance yang menolak `"Percetakan"`, dan `kpi_template.department`. Menyamakan ke `Printing` berarti mengganti nama di master dan `work_data` kembali. Keduanya menyentuh data produksi, jadi dijalankan manusia.

## Kunci yang terdengar seperti departemen, tapi bukan

| Kunci / label | Apa sebenarnya | Sumber |
|---|---|---|
| `legal` ("Legal"), `rnd` ("R&D Regulatory") | Masih tercatat di `deptKeyToNames`, tetapi **bukan departemen di produksi**. Keduanya dilebur ke modul `secretary` 2026-08-13 dan kini berwujud jabatan `Legal` dan `QA RND` di Kesekretariatan. Peran lamanya tetap hidup sebagai tier fallback dan dialiaskan ke kategori `secretary`. | `catalog_secretary.go`, `modul-aktif.ts` |
| `printing` di `deptKeyToNames` | Entri **inert**: nol akun memegang peran `printing`. Namanya `Printing`, sedangkan departemennya di data kini `Percetakan`, jadi entri ini tidak cocok dengan departemen mana pun bila kelak diberi pemegang. | komentar `roles.go`, sensus 2026-09-14 |
| kategori sidebar `marketing` | Wilayah kerja Beauty Hacks dan Kyura (analitik laba, penugasan akun ICC, komplain ke QC). **Bukan** departemen ber-key `marketing`. | `sidebar-kategori.ts` |
| kategori sidebar `audit` (label AUDIT INTERNAL) | Modul pemeriksaan internal, bukan departemen. | [[APP - Audit Internal]] |
| kategori sidebar `warehouse` | Kategori kedua milik Manufaktur. | `sidebar-kategori.ts` |
| kategori sidebar `erp`, `integration` | Tidak dipetakan ke departemen mana pun di `KATEGORI_UTAMA_DEPARTEMEN`. | `sidebar-menus.tsx`, `sidebar-kategori.ts` |
| label `HRGA` | `supervision_label` gabungan Human Resource dan General Affair; tak seorang pun ber-`work_data.department` = `HRGA`. | [[HRIS - Organization Structure]] |

## Departemen tanpa dok induk, dan kenapa dibiarkan begitu

Dua departemen hidup di master data produksi tanpa kategori sidebar, modul, maupun pemetaan peran yang berlaku. Dok induk untuk keduanya hari ini akan berisi TBD hampir seluruhnya, jadi **keberadaannya dicatat di sini dan di [[HRIS - Organization Structure]], bukan di dok domain tersendiri**.

### Percetakan (`printing`)

- Ditambahkan ke tenant BIP 2026-08-19 dengan nama `Printing`, sebagai tujuan perpindahan 14 karyawan CV Elit (dari `pct` "Percetakan"). Kini bernama `Percetakan` dengan 19 jabatan; lihat bab "Selisih nama Printing dan Percetakan". Riwayat perpindahannya di [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]].
- **Yang ada di kode**: jadwal kerja khusus di attendance-service. `services/attendance/schedule_list.go` memberi departemen ini paket jadwal produksi ditambah jadwal satpam pabrik (19:00 sampai 07:00, tujuh hari, bukan bergilir; `func.go`), didefinisikan di region Printing pada `setup.go`. ⚠️ Paket itu terikat pada nama `Printing`, jadi **tidak terjangkau** selama departemennya bernama `Percetakan`.
- **Yang tidak ada**: kategori sidebar, modul, dan turunan peran di `peran_dari_jabatan.go`. Template KPI sebenarnya sudah ada (4 aktif), tetapi atas nama `Printing`.
- ⚠️ **Penyetuju pengajuannya hanya bertumpu pada flag `is_supervisor` eksplisit**: `supervised_by` kosong dan tak ada jabatan yang cocok pola `Supervisor|^Leader$` ([[HRIS - Organization Structure]]).

### Marketing Offline Distribution (`marketing`)

- Lahir murni sebagai master data: tidak ada di `DefaultDepartments()` maupun `deptKeyToNames` ([[HRIS - Organization Structure]]). Sensus 2026-09-14: **1 karyawan aktif**, 2 jabatan di master, tanpa template KPI.
- ⚠️ **Tanpa pemetaan peran, supervisor yang kelak diberi peran departemen ini tidak menjangkau departemennya sendiri, dan gagalnya berupa daftar kosong, bukan galat** (komentar `roles.go` di entri `printing`).

### Kapan dok induk layak dibuat

Begitu salah satu departemen di atas mendapat **kategori sidebar, modul, atau template KPI yang benar-benar cocok dengan karyawannya**. Saat itu ada perilaku sistem yang bisa didokumentasikan, dan dok induknya mengikuti pola [[Unlisted - Kesekretariatan (Big Pictures)]]. Untuk Percetakan, dok induknya baru berguna setelah selisih nama di atas diputuskan.

## Selisih lain yang ditemukan saat menyusun peta (2026-09-14)

1. **Komentar kode soal Printing sudah tidak sesuai data.** `services/employee/kpi_grup_departemen.go` (commit 2026-08-28) menyatakan "`Printing` ada di work_data tapi tak terdaftar di master". Sensus 2026-09-14 menunjukkan keadaan lain: master dan `work_data` sama-sama bernama `Percetakan`, dan tidak ada `work_data` bernama `Printing`.
2. **Posisi Internal Audit.** [[APP - Audit Internal]] menulis posisi auditor internal "belum ada; direncanakan", sementara seed kode memuat jabatan `Internal Audit` di Kesekretariatan dan salinan produksi memuat template KPI `INTERNAL AUDIT`. Belum diukur apakah jabatan itu punya pemegang.
3. **Manufaktur dan Procurement tidak punya dok induk tunggal.** Keduanya tetap tercakup lewat dok service, dok dashboard, dan (untuk Manufaktur) folder `Manufacture` serta `Warehouse`. [[GA - Procurement System]] berstatus konsep yang sudah digantikan, jadi jangan dipakai sebagai titik masuk Procurement.
4. **Catatan "belum merge" untuk bagan kanvas dan tab Peta Struktur** di [[HRIS - Organization Structure]] sudah basi: ketiga commit-nya ada di `origin/main` erp-frontend (`5ae2f31c`, `34e50bf6`, `297501b8`, semuanya 2026-08-28). Diperbarui di sesi yang sama; status deploy produksinya belum diukur.

## Cara memperbarui

1. Sensus ulang produksi, baca saja, di `employee_db`: isi `master_department` (`key`, `name`, `company_id`), jumlah `work_data` per `department` (total dan akun aktif), dan `kpi_template` per `department`. Bandingkan dengan tabel, termasuk kecocokan nama antar-ketiganya.
2. Departemen baru: tambah baris, lalu putuskan dok induknya memakai aturan "Kapan dok induk layak dibuat".
3. `deptKeyToNames`, `KATEGORI_UTAMA_DEPARTEMEN`, atau konstanta `Dept*` berubah: perbarui kolom kode dan catat commit acuannya.

## Dokumen Terkait

- [[HRIS - Organization Structure]]: mekanisme master departemen, grup supervisi, dan penyetuju
- [[Microservices - Attendance Service]]: picker jadwal per nama departemen
- [[REF - Kepemilikan Data]]: pemilik tiap fakta bisnis, pasangan peta ini dari sisi data
- [[REF - Dashboard per Posisi (Indeks Cakupan)]]: cakupan dashboard per divisi
- [[HRIS - Matriks KPI per Departemen]]: template KPI per departemen
- [[CORE - RBAC dan Permission Set]]: peran, izin, dan peta departemen di RBAC
- [[APP - Web ERP]]: kategori sidebar
- [[HOMEPAGE]]
