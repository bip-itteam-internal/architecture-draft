## Deskripsi

*Recruiter yang bekerja di satu perusahaan grup menangani rekrutmen **seluruh** perusahaan grup lewat izin `recruitment.cross_company` yang dipasang sadar ke posisi. Data proses rekrutmen kini ber-`company_id` yang diturunkan satu arah dari requisition, dan pengguna lain tetap terkunci ke perusahaannya sendiri. Memperluas [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]] (override perusahaan tak lagi eksklusif admin pusat) dan menutup jebakan paket sempit yang dicatat [[ADR - 0080 Permission Set Menggerbangi Pengajuan Requisition Lintas-Departemen]].*

- **Status**: ⚠️ Implemented (ada catatan): merged 2026-09-12 (bip-erp [#1853](https://github.com/bip-itteam-internal/bip-erp/pull/1853), erp-frontend [#1543](https://github.com/bip-itteam-internal/erp-frontend/pull/1543), career-bharata [#12](https://github.com/bip-itteam-internal/career-bharata/pull/12)). **Backend dan Web ERP live di prod** sejak 2026-09-12 (image dibangun 07:32 dan 07:35 WIB, gerbang biner dan bundel lulus, backfill `company_id` sudah jalan) dan terverifikasi lewat gateway dev 2026-09-12. Yang tersisa (diukur 2026-09-12): portal karir prod **belum di-deploy**; paket **belum dipasang** di prod, tetapi kedua pemegang posisi target sudah admin pusat sehingga lintas perusahaan sudah aktif bagi mereka; halaman Permintaan Rekrutmen melempar galat saat disaring ke perusahaan tanpa departemen (`data-type/department` membalas `{"data":null}`), perbaikannya di erp-frontend branch `fix/use-data-types-null`.
- **Path di repo**: `bip-erp/shared-library/common/catalog_recruitment.go` · `shared-library/common/company_scope.go` · `services/recruitment/perusahaan.go` · `services/recruitment/permission_gate.go` · `services/recruitment/migrate_company.go` · `services/employee/perusahaan_referensi.go` · `erp-frontend/src/features/hris/recruitment/lib/izin-perusahaan.ts` · `src/features/hris/recruitment/hooks/use-perusahaan.ts`
- **Tanggal**: 2026-09-11

## Context

Sebelum keputusan ini recruitment-service tak mengenal perusahaan sama sekali: model data proses tanpa `company_id`, dan identitas pemanggil tak membaca `BIP-Company-ID`. [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]] mencatatnya sebagai "Recruitment, tanpa field company". Satu-satunya jalan melihat perusahaan lain adalah peran admin pusat (`system_roles.group = admin`). Akibat turunannya: "Tambah Karyawan dari kandidat" terkunci ke BIP, dan email kandidat menuliskan nama BIP untuk semua lowongan.

Kebutuhannya datang dari lapangan: posisi rekrutmen menangani beberapa perusahaan grup walau orangnya karyawan satu perusahaan.

Keputusan user (2026-09-11):

1. Recruiter lintas perusahaan menangani **semua** perusahaan grup, bukan daftar perusahaan tertentu.
2. Requisition untuk perusahaan B boleh diajukan SPV B (tercatat perusahaan sendiri) **dan** recruiter lintas atas nama B.
3. Satu portal karir untuk semua perusahaan; tiap lowongan menyebut perusahaannya; halaman legal per perusahaan TBD.
4. Email kandidat memakai nama perusahaan dari `master_company`; logo tetap satu.

## Decision

**Wewenang lintas perusahaan datang dari satu izin aditif yang dipasang sadar ke posisi, dan perusahaan setiap data proses rekrutmen diturunkan satu arah dari induknya.**

### 1. Satu izin aditif, satu paket berisi satu izin

`recruitment.cross_company` dan paket `recruitment_lintas_perusahaan` ("Rekrutmen: Lintas Perusahaan") berisi **tepat** satu izin (`shared-library/common/catalog_recruitment.go`). Izin ini **tidak** masuk `RecruitmentTierDefault` maupun paket admin, dengan alasan yang sama persis dengan [[ADR - 0080 Permission Set Menggerbangi Pengajuan Requisition Lintas-Departemen]] §3: fallback tier akan memberikannya ke setiap pemegang `hris`. Penjaganya `TestRecruitmentTierDefaultTanpaIzinLintasPerusahaan` dan `TestPaketAdminTanpaIzinLintasPerusahaan`.

Izinnya **aditif**: ia melebarkan cakupan perusahaan izin pipeline yang sudah dipegang, tidak pernah memberi izin pipeline itu sendiri. Satu-satunya hak yang ia buka sendiri adalah `POST /requisitions` (gerbang `isSupervisor` ATAU pemegang izin), karena perusahaan tujuan bisa belum punya atasan yang memakai ERP.

Aturan "siapa boleh lintas" tinggal di satu tempat, `common.BolehLintasPerusahaan(c, izin)` = admin pusat ATAU pemegang izin, dan dipakai recruitment-service maupun employee-service.

### 2. Izin aditif tidak lagi mencabut fallback tier

`izinRecruitmentEfektif` (`services/recruitment/permission_gate.go`) tidak menghitung izin aditif (`requisition_cross_dept`, `cross_company`) saat menilai apakah klaim memuat izin modul recruitment, dan selalu menyertakannya ke hasil. Daftar izin aditif diturunkan dari katalog dikurangi izin pipeline, bukan diketik ulang.

Ini menutup jebakan yang dicatat ADR 0080 §Consequences: memasang satu paket aditif ke posisi yang belum punya paket recruitment lain membuat klaim "memuat izin modul" lalu mencabut seluruh izin tier-nya. Menurut komentar kode, itu terjadi di produksi 2026-09-08 pada posisi Direktur.

### 3. Perusahaan diturunkan satu arah, anak kandidat tanpa salinan

```
requisition.company_id  (SPV: perusahaan sendiri | lintas: dipilih, divalidasi aktif di master)
    -> posting.company_id     (selalu dari requisition)
        -> candidate.company_id   (dari lowongan; tanpa lowongan: perusahaanTujuan)
            -> interview / offer / hasil tes / BGC / psikotes: TIDAK disimpan, dibaca lewat kandidat
manpower_plan, onboarding_review, onboarding_instance: distempel perusahaanTujuan
```

Enam koleksi membawa `company_id`, dan data lama di-backfill `BIP` saat service start (`migrate_company.go`, idempoten). Saringan BIP sengaja ikut menangkap dokumen tanpa field, supaya backfill yang gagal sebagian tak membuat data lama lenyap tanpa galat.

`POST /public/recruitment/apply` kini **wajib** `posting_id`. Perusahaan kandidat publik diturunkan dari lowongan yang masih Open, tidak pernah dari header: rute publik tak melewati validasi JWT, jadi header `BIP-*` di sana bisa dikarang siapa pun.

### 4. Aturan baca dan tulis

- **Daftar**: non-lintas selalu perusahaan sendiri, dan `?company=` diabaikan; lintas melihat semua, atau `?company=X`.
- **Per-ID di luar cakupan**: 404, supaya keberadaan data perusahaan lain tak bocor. Pengaju requisition tetap boleh membuka pengajuannya sendiri.
- **Tulis**: non-lintas selalu perusahaan sendiri, dan `company_id` di body diabaikan. Pemegang izin lintas memilih perusahaan yang divalidasi aktif di master: tak dikenal atau nonaktif 400, tak bisa dipastikan **503**. Kegagalan memastikan TIDAK diturunkan jadi perusahaan sendiri, karena itu menyimpan data ke perusahaan yang salah dengan status 201.
- **Portal Job Requisitions** (`scope=department`): atasan dan HR melihat cakupan departemennya di perusahaannya sendiri plus pengajuannya sendiri; recruiter lintas yang bukan keduanya hanya melihat pengajuannya sendiri.

### 5. Override data referensi employee-service untuk pemegang izin, sempit

Ini **penyimpangan sadar** dari ADR 0029, yang menetapkan override `?company=` hanya untuk admin pusat. Varian berizin `common.EffectiveCompanyIDDenganIzin` dipakai **hanya** oleh `perusahaanReferensi` di employee-service, untuk data yang dibutuhkan layar rekrutmen: `/data-type/position`, `/data-type/headcount`, `/data-type/department-groups`, `/data-type/department`, dan `/list?type=employee`. Jumlah pemanggilnya dikunci per berkas oleh `TestPerusahaanReferensiHanyaDiCabangBacaRekrutmen`; menambah pemanggil berarti memperluas wewenang izin, jadi keputusan, bukan perapian. `EffectiveCompanyID` lama tetap terkunci ke admin pusat.

Daftar karyawan perusahaan lain yang dibuka izin (bukan admin pusat) disempitkan lagi, keputusan user saat `/review` 2026-09-11:
- `role_system`, `role_value`, `with_supervisor`, `include_external`, `include_inactive` ditolak 403;
- `username`, `phone_number`, `photo` dikosongkan.

Bendera ditolak, bukan diabaikan. Filter yang diabaikan diam-diam membalas 200 berisi daftar lebih luas dari yang diminta, dan akun luar dimuat per perusahaan pemakai sehingga akan tercampur ke daftar perusahaan lain.

### 6. Nama perusahaan dibaca dari master, tidak disalin

recruitment-service membaca `GET /master/companies` milik employee-service ([[REF - Kepemilikan Data]]) lewat cache 5 menit. Kegagalan diingat 30 detik, dan salinan lama yang dipakai ditandai basi. Nama itu dipakai untuk:
- `{{perusahaan}}` di email kandidat dan undangan;
- `company_name` di portal karir;
- notifikasi requisition baru;
- validasi perusahaan tujuan;
- rute `GET /api/recruitment/companies` untuk pemilih di layar rekrutmen.

## Consequences

**Yang didapat**

- Satu posisi rekrutmen melayani semua perusahaan grup, sementara batas data ADR 0029 tetap berlaku bagi pengguna lain.
- Melebarkan atau menyempitkan pemegangnya tak butuh deploy kode: cukup memasang paket lewat layar Hak per Posisi.
- Tambah Karyawan dari kandidat berlaku untuk semua perusahaan.
- Penjaga perusahaan dikunci pemindai sumber (`services/recruitment/penjaga_perusahaan_test.go`), dan setiap pemindainya dibuktikan merah lewat kontrol negatif:
  - FindOne wajib memanggil penjaganya;
  - daftar wajib tersaring;
  - rute per-ID wajib mencapai penjaga;
  - helper tanpa penjaga hanya boleh dipanggil pemanggil terdaftar;
  - insert/replace wajib menstempel `CompanyID`.

**Yang dibayar**

- ⚠️ **Berlaku sesudah login ulang**, sama seperti ADR 0080: izin dipanggang ke klaim JWT. Cache respons gateway yang berkunci `employee_id` juga bisa menahan respons lama sampai TTL habis.
- ⚠️ **Penyetuju requisition dan offer adalah satu tim di BIP.** Posisi SPV HRD penyetuju wajib ikut dipasangi paket (keputusan user 2026-09-11). Tanpa paket itu mereka tetap menerima notifikasi requisition perusahaan lain, yang kini menyebut nama perusahaannya, tapi mendapat 404 saat membukanya.
- ⚠️ **Urutan deploy mengikat.** employee-service tak boleh tertinggal dari recruitment-service: tanpa `company_id` di `/internal/mpp-vacancies`, posisi kosong perusahaan lain terbaca BIP. Perubahan katalog izin menuntut kedua container naik bersama (pola ADR 0080).
- ⚠️ **Endpoint publik portal karir kini bergantung employee-service** untuk nama perusahaan. Dampaknya dikurangi cache dan jeda gagal; bila tetap tak terjangkau, key perusahaan yang tampil.
- Pemindai sumber tidak membaca argumen: mengoper perusahaan yang salah ke penjaga tetap lolos, begitu pula koleksi yang dioper lewat variabel.

**Belum diputuskan / utang yang sengaja tidak disentuh**

- Halaman legal dan pengendali data pelamar per perusahaan: TBD bersama legal.
- Logo per perusahaan tidak dibuat (keputusan user); `master_company` belum punya field logo. Filter perusahaan di portal karir belum diminta.
- Master dan katalog rekrutmen (babak interview, psikotes, lookup, template email, lokasi) tetap global.
- `requireInternalKey` employee-service hanya membandingkan `BIP-Gateway-ID`, yang dipasang gateway pada semua request ber-JWT, sehingga `/api/employee/internal/*` terjangkau pemakai login mana pun. Ini sudah ada sebelum keputusan ini; kelasnya dicatat di [[ADR - 0031 Prefix internal Bukan Batas Keamanan]].

## Dokumen Terkait

- [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]: batas data `company_id` yang diperluas
- [[ADR - 0080 Permission Set Menggerbangi Pengajuan Requisition Lintas-Departemen]]: pola izin aditif dan jebakan paket sempit yang ditutup
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[CORE - RBAC dan Permission Set]]
- [[Microservices - Recruitment Service]] · [[API - Recruitment Service]]
- [[Microservices - Employee Service]] · [[API - Employee Service]]
- [[HRIS - Recruitment]] · [[APP - Portal Karir Bharata]] · [[APP - Web ERP]]
- [[REF - Kepemilikan Data]]
