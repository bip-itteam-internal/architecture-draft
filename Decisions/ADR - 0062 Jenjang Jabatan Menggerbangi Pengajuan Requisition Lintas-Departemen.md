## Deskripsi

*Kewenangan mengajukan Job Requisition untuk posisi di **departemen mana pun** digerbang **jenjang jabatan** (`position_items[].level_key` terhadap `master_job_level`), bukan daftar nama jabatan. Ini pemakaian PERTAMA jenjang sebagai sumbu keputusan, yang sampai sekarang dilarang eksplisit di kode, dan sekaligus mencabut Corporate Secretary dari kewenangan itu.*

- **Status**: 🟡 Konsep / Direncanakan — kode sudah ditulis dan diuji di branch `feat/recruitment-requisition-jenjang-direktur` (bip-erp) + `feat/requisition-jenjang-direktur` (erp-frontend), **belum merged, belum deployed**.
- **Path di repo**: `bip-erp/services/recruitment/jenjang.go` · `models_requisition.go` · `requisition_handlers.go` · `erp-frontend/src/hooks/use-jenjang-jabatan.ts` · `src/features/hris/recruitment/requisitions/components/requisition-form.tsx` · `src/app/(main)/portal/requisitions/create/page.tsx`
- **Tanggal**: 2026-08-29

## Context

Requisition dibuat atasan dari Portal Saya, dan departemennya **ditentukan server** dari identitas pengaju sejak PR #478 ([[Microservices - Recruitment Service]], increment "Requisition se-departemen + pengetatan"). Direktur berdepartemen `Kesekretariatan`, sehingga ia hanya bisa mengajukan posisi Kesekretariatan padahal wewenangnya mencakup seluruh perusahaan.

Versi pertama pelonggaran ini (mendarat di `main` 2026-08-29, BE `d607aea2` / FE `f6e9eee6`) memakai **`common.SetaraDirektur`**, yaitu daftar nama jabatan `["direktur", "corporate secretary"]`. Dua hal salah dengannya untuk pertanyaan ini:

1. **Daftar itu menyatakan wewenang MEMUTUS**, dan Corporate Secretary memang setara Direktur untuk menyetujui cuti, perjalanan dinas, dan pesanan pembelian (keputusan organisasi 2026-08-10). Mengajukan kebutuhan karyawan untuk seluruh perusahaan adalah kewenangan yang berbeda. Pemilik produk menegaskan 2026-08-29: yang boleh **hanya Direktur**.
2. **Pencocokannya PERSIS**, sehingga `"Direktur Utama"` tidak akan pernah cocok dan fiturnya mati diam-diam bagi pemegangnya. Nama jabatan diketik manusia di Master Data dan memang berubah tanpa migrasi (lihat `POSISI_ICC` yang di-rename 2026-08).

Preseden pembedaan ini sudah ada dan disengaja: `erp-frontend/src/utils/akses-penuh.ts` memakai daftar `["direktur"]` yang berdiri sendiri, dengan komentar yang melarang menyatukannya dengan `JABATAN_SETARA_DIREKTUR` justru supaya Corporate Secretary tidak diam-diam ikut.

**Yang membuat ini butuh ADR**: `models/employee/master_data.go` dan `services/employee/job_level.go` menyatakan jenjang **bukan sumbu hak akses** dan "tidak boleh jadi gerbang endpoint mana pun", dengan alasan yang benar — menaikkan jenjang seseorang lalu diam-diam memberinya wewenang yang tak pernah diputuskan siapa pun. Berkas itu juga menyebut jalan keluarnya: *"Kalau suatu saat ada yang ingin menggerbang sesuatu dengan jenjang, itu keputusan arsitektur baru, bukan penambahan satu `if`."* ADR inilah keputusan tersebut.

Kesiapan data diukur langsung sebelum keputusan diambil (2026-08-29, baca saja):

| | Prod | Dev |
|---|---|---|
| Total jabatan (`position_items`) | 118 | 92 |
| Punya `level_key` | 100 | 13 |
| Berjenjang `direktur` | **1** (`Kesekretariatan / Direktur`) | **0** |

Di produksi sumbu ini tepat sasaran: persis satu jabatan, dan Corporate Secretary tidak ikut karena jabatannya tidak berjenjang direktur.

## Decision

**Jenjang jabatan menggerbangi kewenangan MENGAJUKAN requisition lintas-departemen, dengan batas yang sempit dan tertulis.**

### 1. Sumbunya jenjang, dibandingkan dengan KESAMAAN

Pengaju boleh menyetel `department` requisition dari body bila jabatannya (`work_data.department` + `work_data.position`) berjenjang `direktur` menurut `master_department.position_items[].level_key`.

Perbandingannya **kesamaan**, bukan `RankOf(...) >= RankOf(direktur)`. Pertanyaannya keanggotaan satu jenjang, bukan urutan; memakai `>=` akan membuat jenjang baru yang disisipkan di atasnya (mis. Komisaris) **diam-diam mewarisi** wewenang ini, yaitu persis kekhawatiran yang membuat larangan di atas ditulis. Memperluasnya harus jadi perubahan sadar di `jenjang.go`. Konsekuensi sampingannya menguntungkan: `master_job_level` tak perlu dimuat sama sekali, jadi cukup satu panggilan lintas-service.

### 2. Batasnya, dan apa yang TIDAK diizinkan ADR ini

- Jenjang memberi wewenang **MENGAJUKAN**, tidak pernah menyetujui. Requisition tetap disetujui SPV HRD lewat `gate(common.PermRecruitmentApprove, isHRSupervisor)`.
- Jenjang **tidak boleh** dibaca `permission_resolve.go`, tidak boleh jadi gerbang rute, dan tidak boleh jadi sumbu izin modul. Hak akses tetap dari permission set ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]).
- Jabatan **tanpa** `level_key` (18 dari 118 di prod) berperilaku seperti pengaju biasa. Fail-closed, bukan fail-open.

### 3. Jenjang ditanyakan lintas-service, hanya saat dibutuhkan

`level_key` **tidak ikut** di klaim JWT maupun header gateway (`common.Header` hanya membawa EmployeeID, Username, SystemRoles, Fullname, Department, Position, SupervisedDepartments, CompanyID, Permissions). Recruitment-service karena itu menanyakannya ke employee-service `GET /master/departments`.

Panggilan itu dilakukan **hanya bila departemen yang diminta berbeda** dari departemen pengaju (dibandingkan case-insensitive). Pengajuan biasa tidak menyentuh jaringan sama sekali dan tidak ikut menanggung ketersediaan service lain.

Menaruh `level_key` di JWT **ditolak** untuk lingkup ini: ia memaksa seluruh pemakai login ulang dan menjadikan jenjang sumbu identitas di semua service, jauh melampaui satu layar. Bila kelak ada service kedua yang membutuhkannya, itu keputusan tersendiri.

### 4. Gagal memastikan jenjang = TOLAK, bukan turunkan jadi "tidak berhak"

Bila employee-service tidak menjawab, permintaan lintas-departemen dibalas **503 berpesan**. Menurunkannya jadi `false` akan menyimpan requisition ke departemen pengaju dengan status **201** tanpa satu pun gejala, dan salahnya baru ketahuan berhari-hari kemudian. Ini kelas kegagalan senyap yang berulang kali menggigit di sistem ini.

## Consequences

**Yang didapat**

- Batasnya persis seperti yang diputuskan organisasi: satu jabatan di prod, tanpa daftar nama yang harus dirawat.
- Tahan terhadap penggantian nama jabatan. `"Direktur Utama"` ikut bila jenjangnya direktur; `"Asisten Direktur"` tidak ikut meski namanya memuat kata itu.
- Nol endpoint baru, nol perubahan employee-service, nol migrasi, nol login ulang.

**Yang dibayar**

- **Menaikkan jenjang sebuah jabatan kini punya efek samping wewenang.** Diterima sadar: dampaknya terbatas pada mengajukan, dan requisition tetap harus disetujui SPV HRD. Master Data perlu tahu ini.
- **Corporate Secretary kehilangan** kemampuan yang sempat dimilikinya sejak versi pertama mendarat di `main` hari yang sama. Karena belum di-deploy, tak ada yang benar-benar kehilangan sesuatu yang sedang dipakai.
- **Dev punya nol jabatan berjenjang direktur**, jadi verifikasi di dev akan tampak seperti fitur rusak sampai `level_key` diisi. Ini prasyarat verifikasi, bukan bug.
- Satu panggilan lintas-service pada jalur tulis untuk pengaju berjenjang direktur. Untuk SPV lintas-grup (mis. HRGA yang memilih posisi General Affair) panggilan itu juga terjadi dan hasilnya tetap benar, hanya tak diperlukan.

**Yang sengaja tidak diputuskan di sini**

- Apakah requisition SPV HRGA untuk posisi General Affair seharusnya tercatat di departemen asli posisi (keputusan HRGA 2026-07-23) alih-alih departemen SPV. Kode hari ini menyimpannya di departemen SPV; itu gap terpisah yang tidak disentuh ADR ini.

## Dokumen Terkait

- [[Microservices - Recruitment Service]] — implementasi requisition & alur approval
- [[HRIS - Recruitment]] — konsep/bisnis rekrutmen
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] — hak akses tetap dari permission set, bukan jenjang
- [[Microservices - Employee Service]] — pemilik `master_department` & `master_job_level`
