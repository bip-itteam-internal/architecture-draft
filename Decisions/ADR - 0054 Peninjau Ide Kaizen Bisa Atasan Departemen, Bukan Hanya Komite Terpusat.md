**Status**: 🟡 Diputuskan dan **kode selesai di branch**, belum merge, belum deploy. `feat/kaizen-peninjau-atasan` di [bip-erp](https://github.com/bip-itteam-internal/bip-erp) (3 commit) dan [erp-frontend](https://github.com/bip-itteam-internal/erp-frontend) (1 commit). Menggantikan sebagian keputusan "Siapa peninjau: **Komite Kaizen terpusat**" di [[HRIS - Kaizen (Ide Perbaikan)]].

> Mode lama TIDAK dicabut. `reviewer_mode` bawaan tetap `committee`, dan dua program kaizen yang sudah ada di prod tak berubah perilaku sama sekali.

## Context

Form manual HR **"BERITA ACARA INOVASI"** memakai kolom **"Catatan Evaluasi Atasan"**. Implementasi Kaizen yang sudah live menyerahkan keputusan ke **komite terpusat** (`settings.kaizen.committee_employee_ids`) ditambah pengelola departemen pemilik form. Keduanya bertentangan, dan yang menang seharusnya form manual: ia yang dipakai orang.

Kata "atasan" di ERP ini punya **dua** bentuk yang berbeda jauh kesiapan datanya. Diukur langsung ke `employee_db.work_data` prod 2026-08-26, 207 dokumen:

| Bentuk | Field | Kesiapan |
|---|---|---|
| Atasan **langsung** (per orang) | `work_data.supervisor_id` | 78 terisi, **129 KOSONG** (62%) |
| **Supervisor departemen** | `work_data.is_supervisor` | **11 orang**, menutup 11 departemen |

Yang tanpa atasan langsung, per departemen: Manufaktur 33, Beauty Hacks 21, Finance 19, Kyura 17, Printing 14, Quality 6, Tech Development 6, Kesekretariatan 4, Procurement 3, Human Resource 3, General Affair 2, Marketing Offline Distribution 1.

**Atasan langsung karena itu gugur.** Menggerbang peninjauan pada `supervisor_id` berarti ide dari 129 orang masuk antrean yang tak punya pemilik, dan gagalnya senyap dengan cara yang khas program ini: kepatuhan dihitung dari ide yang **diajukan** sehingga pengaju tetap tercatat patuh dan tak ada yang mengeluh, sementara skor KPI yang dihitung dari ide yang **diterapkan** diam-diam nol untuk 62% karyawan. Pemisahan dua angka itu memang disengaja ([[HRIS - Kaizen (Ide Perbaikan)]] §Dua Angka yang Sengaja Dipisah), tapi di sini justru dialah yang menyembunyikan kerusakannya.

Dua temuan kode membentuk sisa keputusannya:

1. ⛔ **`common.SupervisedDepartments` BUKAN pemeriksaan supervisor.** Ia selalu menyertakan departemen pemanggil sendiri, dan jatuh ke `[departemen sendiri]` saat header cakupan hilang atau rusak (`shared-library/common/department_scope.go`). Menggerbang peninjauan dengannya membuat **setiap staf jadi peninjau departemennya sendiri, termasuk idenya sendiri**. Varian ketat `SupervisedDepartmentsStrict` memang sudah ada untuk jalur tulis (dibuat di [bip-erp #1012](https://github.com/bip-itteam-internal/bip-erp/pull/1012)), dan itu yang benar di sini.
2. **Tidak ada klaim `is_supervisor` di header gateway mana pun.** Jadi "atasan" tak bisa dibuktikan di dalam form-builder tanpa menambah mekanisme.

Sementara itu form-builder **sudah** punya katalog izin sendiri ber-ADR ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]): `formbuilder.view`, `formbuilder.work`, `formbuilder.rules.manage`, lengkap dengan paket per posisi, gerbang, kill-switch, dan fallback tier.

## Decision

**Peninjau ditentukan `settings.kaizen.reviewer_mode` per program, bernilai `committee` (bawaan) atau `supervisor`.** Pada mode `supervisor`, yang berwenang adalah pemegang izin **baru** `formbuilder.kaizen.review` yang departemen pengajunya ada dalam cakupan supervisinya.

Empat aturan turunannya, masing-masing membayar kegagalan konkret:

1. ⛔ **Izin `formbuilder.kaizen.review` SENGAJA di luar `FormBuilderTierDefault`.** Ketiga izin formbuilder lama mencerminkan gerbang yang sudah berlaku, sehingga menetes lewat tier justru yang membuat penyalaannya tak mengubah akses siapa pun. Yang ini wewenangnya **baru**. Karena `tierFallbackEnabled` default `true`, memasukkannya ke tier akan menjadikan **setiap** pemegang tier lama peninjau tanpa seorang pun memasang paket.
2. **Cakupan dibaca `SupervisedDepartmentsStrict`, bukan varian longgar.** Untuk gerbang tulis, header yang tak terbaca harus berarti **tidak berwenang**.
3. **Pemilik modul HRIS TIDAK menembus.** Dipakai `common.DepartmentInScope(false, ...)`, bukan `common.CanManageDepartment` yang meloloskan pemegang modul HRIS untuk departemen mana pun. Jalan darurat anti-form-yatim sudah dipegang pengelola departemen pemilik form; lubang kedua yang berlaku lintas departemen tak dibayar apa pun.
4. **Tak seorang pun memutuskan idenya sendiri**, termasuk pengelola form. Supervisor juga anggota departemennya sendiri, jadi tanpa aturan ini ia bisa menerima lalu menandai idenya sendiri diterapkan, dan angka itu masuk ke skor KPI-nya sendiri.

**Gerbangnya dipecah DUA TINGKAT**, dan ini inti perubahannya:

```
bolehMasukAntreanKaizen(c, form)   -> boleh membuka antrean form INI
izinMeninjauIde(mode, ..., ide)    -> boleh memutuskan ide INI
```

Pada mode komite keduanya sama, sebab wewenangnya memang selebar form. Pada mode supervisor tidak: seorang atasan boleh membuka antrean tapi hanya berwenang atas sebagian isinya, jadi gerbang tingkat form saja akan meloloskan keputusan atas ide departemen orang lain. Antrean ikut dipersempit ke cakupan yang sama supaya yang **dilihat** dan yang bisa **ditindak** tak pernah berbeda; `?department=` hanya boleh mempersempit, tak pernah memperluas.

**`committee_employee_ids` wajib kosong pada mode `supervisor`.** Satu fakta satu tempat: daftar yang tetap terisi akan tersimpan, tak pernah dibaca, lalu menyesatkan siapa pun yang membuka pengaturannya berbulan kemudian.

### Yang TIDAK diputuskan di sini

- **Status "Diproses"** dari form manual belum dipetakan. Mesin keputusan tetap `belum ditinjau → accepted/rejected → implemented`; `accepted` sudah berarti "diterima, belum diterapkan", jadi kemungkinan besar ini soal label i18n, bukan status keempat. Menunggu pemilik produk.
- **Memperbaiki `is_supervisor`** yang diturunkan frontend dari nama jabatan. Keputusan ini sengaja tidak bergantung padanya.

## Consequences

**Yang didapat.** HR mengubah "siapa atasan yang meninjau" sendiri lewat layar Hak per Posisi, tanpa deploy. Keputusan itu tidak bergantung pada `is_supervisor` yang rapuh (di prod, supervisor Printing berjabatan **"Admin"** dan supervisor Procurement berjabatan **"Leader"**, karena flag-nya diturunkan FE dari string nama jabatan) maupun pada 129 `supervisor_id` yang kosong. **General Affair tertutup otomatis**, padahal ia satu-satunya departemen tanpa `is_supervisor`, karena HRD Supervisor membawahinya lewat `master_department.supervised_by` yang memang sudah terbaca `SupervisedDepartments`.

**Harganya, dan ini dijalani sadar:**

- ⚠️ **Program bermode `supervisor` TIDAK berfungsi sampai HR memasang paket "Kaizen: Peninjau"** ke jabatan atasan tiap departemen sasaran. Itu memang yang diinginkan (izin baru tak boleh menetes), tapi berarti ada jendela di mana programnya hidup dan antreannya tak dibuka siapa pun.
- ⛔ **Tidak ada gerbang yang mencegah HR menerbitkan program tanpa peninjau.** Menjawab "departemen mana yang punya peninjau" menuntut menyilangkan `master_department.position_items[].permission_sets` dengan `work_data` dan cakupan supervisi tiap pemegangnya — seluruhnya milik [[Microservices - Employee Service]], dan menuntut endpoint introspeksi izin yang belum ada. **Sengaja tidak dibangun sekarang.**
- **Sebagai gantinya papan kepatuhan melaporkan `menganggur`**: ide yang belum diputuskan siapa pun lebih dari **14 hari**, berikut ambangnya. Ia mengukur **akibat**, bukan sebab, sehingga sekaligus menangkap peninjau yang sudah dipasang tapi tak pernah bertindak — kegagalan yang tak akan pernah terlihat oleh pemeriksaan daftar izin, dan yang lebih sering terjadi. Sisanya: jeda 14 hari sebelum angkanya naik.
- **Menu Komite Kaizen tetap TANPA gerbang `perm`.** Ia kini melayani dua mode, dan menggerbangnya pada izin baru justru akan menyembunyikannya dari anggota komite mode lama yang tak memegang izin itu. Halamannya menemukan haknya sendiri lewat `GET /me/kaizen/committee`.
- **Kill-switch `FORMBUILDER_PERMISSION_ENFORCEMENT=off` mematikan mode supervisor**, menyisakan hanya jalur pengelola departemen pemilik form. Gerbang peran lama tak punya padanan mode ini, jadi tak ada perilaku lama yang bisa dikembalikan.

**Konsekuensi deploy.** Paket izin baru **tidak** muncul lewat `seedPermissionSets`, yang melewati koleksi yang sudah terisi. Yang menyisipkannya adalah `migrateMissingDefaultPermissionSets()` saat **employee-service start**, jadi employee-service **wajib ikut naik** bersama form-builder, bukan form-builder saja. Kelas kopling lewat biner yang sama dengan kategori inbox; prosedurnya di [[RUN - Deploy Microservices bip-erp]].

## Dokumen Terkait

- [[HRIS - Kaizen (Ide Perbaikan)]] — keputusan "komite terpusat" yang sebagian digantikan di sini
- [[Microservices - Form Builder Service]] · [[API - Form Builder Service]]
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] — sumbu modul/izin/reach yang dipakai ulang
- [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]] — asal kerapuhan `is_supervisor`
- [[Microservices - Employee Service]] — pemilik data supervisi dan paket izin
- [[HRIS - Organization Structure]] — `supervised_by` dan cakupan supervisi
