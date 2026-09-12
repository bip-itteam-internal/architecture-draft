## Deskripsi

*Kewenangan mengajukan Job Requisition untuk posisi di **departemen mana pun** digerbang **permission set** (`recruitment.requisition_cross_dept`), bukan jenjang jabatan. Menggantikan [[ADR - 0062 Jenjang Jabatan Menggerbangi Pengajuan Requisition Lintas-Departemen]] yang berumur sembilan hari, sekaligus melebarkan pemegangnya dari satu orang jadi tiga posisi.*

- **Status**: ⚠️ Implemented (ada catatan) — izin & paket sudah di `main` (bip-erp [#1774](https://github.com/bip-itteam-internal/bip-erp/pull/1774)); sumbu jenjang **masih hidup sebagai jalur transisi** sampai paket terpasang ke posisi di produksi dan terverifikasi. Pembuangannya PR tahap dua.
- **Path di repo**: `bip-erp/shared-library/common/catalog_recruitment.go` · `services/recruitment/requisition_handlers.go` · `erp-frontend/src/features/hris/recruitment/lib/izin-requisition.ts` · `src/app/(main)/portal/requisitions/create/page.tsx`
- **Tanggal**: 2026-09-07

## Context

[[ADR - 0062 Jenjang Jabatan Menggerbangi Pengajuan Requisition Lintas-Departemen]] menjadikan `position_items[].level_key == "direktur"` sumbu wewenang. ADR itu sendiri menyatakan bahwa itu **penyimpangan yang disengaja** dari [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]], dan bahwa `models/employee/master_data.go` beserta `services/employee/job_level.go` melarang jenjang jadi gerbang endpoint mana pun. Ongkosnya diterima waktu itu karena alternatifnya adalah daftar nama jabatan yang lebih rapuh.

Pemilik produk memutuskan 2026-09-07 dua hal sekaligus:

1. **Sumbunya kembali ke permission set.** Satu sumbu untuk seluruh hak akses, sesuai ADR 0030. Master Data berhenti punya efek samping wewenang.
2. **Pemegangnya dilebarkan.** Penegasan 2026-08-29 ("yang boleh hanya Direktur") diperbarui: HR yang sehari-hari membuka lowongan atas nama departemen lain juga berhak. Ini membalik keputusan sebelumnya secara sadar, dan dicatat di sini supaya perubahannya tidak tersirat dari kode saja.

Keadaan produksi diukur langsung sebelum keputusan diambil (2026-09-07, baca saja):

| Yang diukur | Hasil |
|---|---|
| Jabatan berjenjang `direktur` | 1 (`Kesekretariatan / Direktur`) |
| `position_items` total / punya `level_key` | 119 / 100 |
| Posisi punya `permission_sets` | 11 dari 119 |
| Posisi punya paket recruitment | 2 (`HR / HRD Supervisor`, `HR / Recruitment & Onboarding`) |
| Pemegang `system_roles.hris` supervisor/admin | 10, **6 di antaranya developer Tech Development** |

Baris terakhir yang paling menentukan bentuk keputusan ini: fallback tier `RECRUITMENT_TIER_FALLBACK` mensintesis izin recruitment dari `system_roles["hris"]`, sehingga apa pun yang masuk tier otomatis dipegang keenam developer itu.

## Decision

**Kewenangan mengajukan lintas-departemen datang dari permission set yang dipasang sadar ke sebuah posisi, dan hanya dari sana.**

### 1. Izinnya ADITIF, bukan pengganti gerbang rute

`POST /requisitions` tetap digerbang `isSupervisor` (atasan di modul mana pun). `recruitment.requisition_cross_dept` hanya melebarkan **pilihan departemen**, dan tidak pernah memberi hak mengajukan kepada yang belum punya.

> Diperluas [[ADR - 0092 Rekrutmen Lintas Perusahaan lewat Paket Izin]] (merged, live prod 2026-09-12): gerbangnya kini `isSupervisor` ATAU pemegang `recruitment.cross_company`, untuk perusahaan tujuan yang belum punya atasan pemakai ERP. `requisition_cross_dept` sendiri tetap tidak membuka rute ini.

Pembedaan ini wajib. `catalog_recruitment.go` sudah mencatat sejak awal bahwa memetakan gerbang dasar `POST /requisitions` ke izin recruitment akan **mencabut** hak SPV departemen non-HR, sebab pengajunya justru orang di luar HR.

### 2. Paketnya berisi TEPAT satu izin

`recruitment_pengaju_lintas` ("Rekrutmen: Pengaju Lintas Departemen") dipasang ke posisi yang **sudah** punya paket recruitment lain, jadi isi tambahan apa pun akan diam-diam melebarkan hak mereka di luar yang diputuskan. Dikunci `TestPaketPengajuLintasBerisiSatuIzin`.

Pemegang awal: `Kesekretariatan / Direktur`, `Human Resource / HRD Supervisor`, `Human Resource / Recruitment & Onboarding`. Ketiganya masing-masing dipegang satu orang per 2026-09-07.

### 3. Izin ini TIDAK ikut tier, dan tidak ikut paket admin

Katalog izin (`RecruitmentPermissionCatalog`) dipisah dari izin yang disintesis tier dan diberikan paket admin (`recruitmentIzinPipeline`). Keduanya sempat sama isinya, dan menyamakannya adalah jebakan: menambahkan izin ke katalog **wajib** supaya `ValidatePermissionSet` menerimanya, tapi begitu masuk katalog ia ikut tersintesis ke tier `admin` DAN ikut masuk paket "Rekrutmen: Admin" yang di produksi sudah terpasang di dua posisi. Dua jalur pelebaran yang tak seorang pun putuskan.

Terjadi nyata saat izin ini ditulis; yang menangkapnya `TestRecruitmentTierDefaultTanpaIzinLintasDept`, sebelum satu baris pun sampai ke produksi. Penjaganya kini dua test, dan keduanya sudah dibuktikan merah pada assertion yang diklaimnya.

**Aturan turunannya**: izin yang wewenangnya harus dipasang **sadar** ke sebuah posisi masuk katalog saja, tidak ke `recruitmentIzinPipeline`.

### 4. Peralihannya dua tahap, bukan satu

Tahap satu menerbitkan izin dengan gerbang `izin OR jenjang`, sehingga tak seorang pun kehilangan apa pun. Jenjang baru dibuang di tahap dua, setelah paket terpasang dan terbukti bekerja di produksi.

Sebabnya `Kesekretariatan / Direktur` **tidak punya paket izin sama sekali** hari ini; ia lolos lewat fallback tier. Membuang jenjang dalam satu tahap akan membuatnya kehilangan wewenang selama jendela antara deploy dan pemasangan paket, dan gejalanya cuma "pemilih departemen hilang", bukan penolakan.

## Consequences

**Yang didapat**

- Satu sumbu untuk seluruh hak akses; Master Data berhenti punya efek samping wewenang, dan larangan di `master_data.go` tak lagi dilanggar.
- Nol panggilan lintas-service di jalur tulis ini. Jalur 503 "tidak bisa memastikan jenjang" hilang bersama jenjang.
- Melebar atau menyempitkan pemegangnya kini **tak butuh deploy kode**, cukup memasang paket lewat layar Hak per Posisi.

**Yang dibayar**

- ⛔ **Setuju-sendiri diterima sadar.** SPV HRD boleh mengajukan requisition lintas-departemen lalu menyetujuinya sendiri: `hrReviewRequisition` tak punya penjaga `RequestedBy != EmployeeID`. Jejaknya hanya `writeAudit("requisition.approved", ...)`. Sebelum perubahan ini kemampuan itu sudah ada tapi terbatas departemennya sendiri; sekarang cakupannya seluruh perusahaan. Bila kelak dianggap masalah, perbaikannya satu penjaga di handler itu, dan tidak buntu karena tiga posisi berbeda memegang `recruitment.approve`.
- ⚠️ **Berlaku setelah login ulang.** Izin dipanggang ke klaim JWT saat login (`shared-library/auth/jwt.go`), beda dari jenjang yang ditanya hidup-hidup ke employee-service dan langsung berlaku. Memasang paket tanpa login ulang **gagal senyap**: paket terpasang, orangnya mencoba, tak terjadi apa-apa.
- ⚠️ **Memasang paket ke posisi yang tadinya tanpa paket bisa MENCABUT izin.** `izinRecruitmentEfektif` berhenti memakai fallback tier begitu klaim memuat izin modul recruitment. Karena itu posisi Direktur wajib menerima `recruitment_pelaksana` + `recruitment_penyetuju` **berbarengan** dengan paket baru; memasang paket baru sendirian justru mencabut `view` dan `approve` yang hari ini ia dapat dari tier. **Ditutup** di [[ADR - 0092 Rekrutmen Lintas Perusahaan lewat Paket Izin]] §2 (merged, recruitment-service prod dibangun ulang 2026-09-12 07:32 WIB): izin aditif tak lagi dihitung saat menilai klaim modul, jadi paket aditif tak mencabut tier. Peringatan ini hanya berlaku untuk biner yang dibangun sebelum itu.
- **Perubahan katalog izin menuntut deploy DUA container**: `employee-service` (menyisipkan paket ke `master_permission_set` lewat `migrateMissingDefaultPermissionSets`, dan memvalidasi pemasangan) dan `recruitment-service` (menegakkan gerbangnya). Naik sendiri-sendiri gagal senyap di dua arah.

**Utang yang sengaja tidak disentuh**

- `RECRUITMENT_TIER_FALLBACK` masih menyala dan membocorkan `recruitment.approve` ke 6 developer Tech Development. Nyata dan terukur, tapi pemegang keputusannya berbeda; menggabungkannya ke sini akan mencampur dua perubahan akses yang harus bisa dinilai terpisah.
- Gap lama dari ADR 0062 yang tetap terbuka: requisition SPV HRGA untuk posisi General Affair masih tercatat di departemen SPV, bukan departemen asli posisi.
- `level_key` **tidak dihapus** dari master data. Ia tetap jejak organisasi yang sah; yang dicabut hanya perannya sebagai sumbu wewenang.

## Dokumen Terkait

- [[ADR - 0062 Jenjang Jabatan Menggerbangi Pengajuan Requisition Lintas-Departemen]] — keputusan yang digantikan
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] — sumbu hak akses yang dipulihkan
- [[ADR - 0092 Rekrutmen Lintas Perusahaan lewat Paket Izin]]: izin aditif kedua (`recruitment.cross_company`) dan penutupan jebakan paket sempit
- [[Microservices - Recruitment Service]] — implementasi requisition & alur approval
- [[HRIS - Recruitment]] — konsep/bisnis rekrutmen
- [[Microservices - Employee Service]] — pemilik `master_department` & `master_permission_set`
