# ADR - 0182 Badan Usaha Satu Daftar untuk HR dan Finance, Entitas CV Menempel Tanpa Nama Sendiri

> **Status**: 🟡 Diusulkan, 2026-10-15. Arahnya (satu daftar badan usaha untuk HR dan Finance, rekening tetap di Accurate) disetujui user dalam sesi 2026-10-15. Merevisi sebagian [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]], jadi masih menunggu persetujuan pemutus ADR itu (SPV FAT bersama IT) dan pemilik data badan usaha di HR. Kode di bip-itteam-internal/bip-erp#3178 (BE) dan bip-itteam-internal/erp-frontend#2493 (FE), belum merged.

## Untuk Manajemen

**Apa yang berubah.**
- **Satu daftar badan usaha.** PT Bharata, seluruh CV, dan seluruh PT lain tercatat **sekali** di ERP, di daftar Badan Usaha yang hari ini dipakai HR untuk gaji dan BPJS. Finance tidak lagi memegang daftar kedua.
- **Menambah CV atau PT baru tanpa rilis, lewat HR saja.** HR menambahkannya di Pengaturan Gaji › Badan Usaha, seperti yang sudah bisa dilakukan hari ini. Badan usaha baru itu sudah muncul di Entitas CV sebagai "Badan usaha tanpa entitas"; yang ditambahkan hanya tombol **Daftarkan** di sana, supaya Finance bisa memberinya kode CV/PT baru dan singkatan BKK. Hari ini kode baru hanya bisa lahir lewat perubahan kode program.
- **Nama cukup diketik sekali.** Finance menampilkan nama dari daftar itu dan tidak bisa mengetiknya ulang.
- **Rekening tetap di Accurate.** Rekening CV (1299) dan PT (1298) dibuat di Accurate untuk pencatatan; ERP hanya menyimpan nomornya dan memeriksa rekening itu ada.

**Siapa yang terdampak.** HR (pemilik daftar Badan Usaha), Finance pengelola Entitas CV, dan pengaju yang memilih pembayar di pengajuan barang dan dana.

**Apa yang TIDAK dijanjikan.**
- Kode yang sudah dipakai (CV01 sampai CV40, PT00 sampai PT21), singkatan BKK, pemegang, penandatangan, dan kop **tidak berubah**. Pengajuan, BKK, dan slip yang sudah terbit tetap seperti apa adanya.
- Rekening tidak dibuat dari ERP; tetap dibuat di Accurate.

**Perkiraan besaran kerja.** Dua PR, berurutan: finance (BE) lalu layar Entitas CV (FE). Payroll tidak berubah. Sesudahnya satu langkah data: HR membetulkan dua nama, Finance menekan Semai.

## Deskripsi

*Menjadikan daftar Badan Usaha payroll (`payroll_company`) satu-satunya tempat identitas badan usaha grup (nama, NPWP, kota), dan master Entitas CV di finance-service sebagai bagian keuangan yang menempel padanya lewat `payroll_company_id` tanpa nama sendiri.*

- **Status**: 🟡 Diusulkan 2026-10-15; kode di PR bip-erp#3178 dan erp-frontend#2493, belum merged
- **Path di repo** (rencana):
  - `bip-erp/services/payroll/` tidak berubah: daftar badan usaha (`routes.go` rute `/companies`) dan rute baca internal `GET /internal/badan-usaha` sudah ada
  - `bip-erp/services/finance/akuntansi_cv_entitas.go`, `akuntansi_cv_handler.go`, `akuntansi_cv_semai.go`, `akuntansi_cv_pencocokan_individu.go`
  - `erp-frontend/src/features/finance/entitas-cv/`
- **Tanggal**: 2026-10-15

## Context

Diukur 2026-10-15 ke bip-erp dan erp-frontend `origin/main` serta data PROD (baca saja).

1. **Ada dua daftar badan usaha.**
   - **HR:** `payroll_db.payroll_company`, **62 baris** (PT Bharata, 21 PT lain, 40 CV; NPWP terisi 61). Dikelola di Pengaturan Gaji › Badan Usaha (`/pengaturan/payroll`) lewat `POST/PUT/DELETE /companies` (`services/payroll/routes.go:40-43`, izin `payroll.manage` dan admin HR). ⚠️ [[REF - Kepemilikan Data]] masih mencatat 41 baris (diukur 2026-09-15); 21 PT lain ditambahkan HR sesudahnya.
   - **Finance:** `finance_db.akuntansi_cv_entitas`, **62 baris** (PT00, 40 CV, 21 PT lain). Isinya hanya bisa **disemai** dari daftar tetap di kode (`EntitasCVBawaan`, `daftarEntitasPTBawaan` di `services/finance/akuntansi_cv_entitas.go`) dan **disunting** (`PATCH /akuntansi-cv/entitas/:kode`). Tidak ada rute atau tombol untuk menambah entitas baru (`services/finance/akuntansi_cv_handler.go:96-125`).
2. **Sambungan keduanya baru separuh.** 40 CV merujuk badan usaha HR lewat `payroll_company_id`; tidak ada rujukan yatim dan tidak ada nama yang berbeda. 22 PT (PT00 dan 21 PT lain) **belum tersambung**: 20 cocok tunggal lewat nama, 2 berbeda, yaitu PT00 ("PT Bharata Internasional Pharmaceutical" di Finance, "PT Bharata Internasional" di HR) dan PT05 ("PT Zavira Kirana Mandiri" di Finance, "PT. ZAVIRA KIARANA MANDIRI" di HR). Dialog ubah entitas menyembunyikan pilihan badan usaha untuk PT, dan `PATCH` menolaknya untuk PT00.
3. **Nama hidup di dua tempat.** Finance menyimpan `nama` sendiri yang bisa disunting, sehingga perubahan nama di HR tidak ikut; bedanya hanya muncul di laporan kecocokan (`GET /akuntansi-cv/kecocokan`, `NAMA_PAYROLL_BEDA`), yang membandingkan sesudah normalisasi. Tulisan persisnya: 40 CV sama huruf demi huruf, sedangkan 20 PT berbeda gaya. HR menulisnya huruf besar dengan titik ("PT. BOGASVARA PANGAN SEJAHTERA"), Finance huruf biasa ("PT Bogasvara Pangan Sejahtera"). 21 dari 62 nama di HR seluruhnya huruf besar.
4. **Daftar PT lain di dropdown pembayar dibaca dari Accurate.** Rekening anak 1298 dibaca langsung tiap form dibuka lalu dicocokkan lewat nama ke entitas PT aktif (`DaftarSemuaCVPT`, `bacaAkunPTNonBharataAccurate`). Rekening PT tidak disimpan di entitas karena `PATCH` hanya menerima rekening 1299.
5. **Badan usaha HR tanpa entitas sudah terdeteksi.** Laporan kecocokan memuat temuan `BADAN_USAHA_TANPA_ENTITAS` (`services/finance/akuntansi_cv_kecocokan.go:194-199`), tampil di layar sebagai "Badan usaha tanpa entitas" dengan saran "petakan ke CV yang tepat lewat tombol Ubah". Saran itu hanya bisa menyambung ke kode yang sudah ada, padahal 40 kode CV sudah terpakai; dan badan usaha bernama PT dilewati (`badanUsahaBerbentukPT`).
6. **Sudah dipakai.** 254 dari 390 pengajuan barang merujuk kode CV (40 CV berbeda), 50 dibayar dari rekening PT lain (16 PT berbeda). 61 entitas punya pemegang, 62 merujuk penandatangan, 61 punya kop.
7. **Pencocokan otomatis sumber dana hanya membaca CV** (`CocokkanCVIndividu` melewati kode bukan `CV\d{2}`), jadi menyambungkan PT ke badan usaha HR tidak mengubah sumber dana siapa pun.

## Decision

1. **Satu daftar badan usaha = `payroll_company` di payroll-service.** Setiap PT Bharata, CV, dan PT lain ada tepat satu kali di sana. Nama, NPWP, dan kota hanya hidup di sana. Ini merevisi [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]] yang menyebut master entitas CV di finance-service sebagai pemilik identitas CV: master itu tetap pemilik **kode** CV/PT dan data keuangannya, bukan identitasnya.
2. **Entitas CV di finance-service menempel ke satu badan usaha** lewat `payroll_company_id`, **wajib untuk semua kode**, termasuk PT lain dan PT00. Isinya hanya bagian keuangan: kode (`CV\d{2}`/`PT\d{2}`, tak berubah), singkatan BKK, rekening Accurate, pemegang, penandatangan, kop.
3. **Nama di Finance mengikuti HR.** `nama` di entitas tidak bisa disunting lagi; ia salinan satu arah dari badan usaha yang dirujuk, sah menurut syarat salinan di [[REF - Kepemilikan Data]] (satu arah, tak ditulis tangan, berpenjaga laporan kecocokan).
4. **Menambah badan usaha hanya lewat HR**, di Pengaturan Gaji › Badan Usaha yang sudah ada. Finance tidak punya pintu kedua untuk membuat badan usaha. Badan usaha HR yang belum punya entitas sudah tampil di laporan kecocokan Entitas CV sebagai **"Badan usaha tanpa entitas"**; temuan itu diperluas ke badan usaha bernama PT, dan diberi tindakan **Daftarkan**. Finance **mendaftarkannya**: jenisnya (CV atau PT) terisi dari awalan nama dan dipastikan Finance, kodenya terbit otomatis (nomor CV atau PT berikutnya), lalu Finance melengkapi singkatan BKK, rekening, pemegang, penandatangan, dan kop. Sampai didaftarkan, badan usaha itu tidak muncul di dropdown pembayar maupun BKK.
5. **Rekening tetap milik Accurate.** Rekening dibuat di Accurate (1299 untuk CV, 1298 untuk PT). Entitas menyimpan nomornya; untuk PT, `PATCH` kini menerima rekening 1298. Daftar PT lain di dropdown pembayar diambil dari entitas aktif yang berekening, bukan dari pencocokan nama ke Accurate setiap form dibuka.
6. **Sebelum nama di Finance mengikuti HR, HR merapikan nama di daftarnya** (layar yang sudah ada, sekali saja): 21 nama PT ke penulisan resmi, nama lengkap PT Bharata, dan salah ketik PT05. Tanpa itu, dropdown pembayar dan BKK berganti menampilkan nama huruf besar dari HR.
7. **Data yang sudah ada disambungkan, tidak dibuat ulang.** Pemasangan otomatis saat semai (`PasangkanSemua`) diperluas ke PT: rujukan badan usaha dan rekening 1298 diisi bila cocok tunggal lewat nama. Dua yang tidak cocok diselesaikan dengan membetulkan nama di **HR**, lalu semai diulang. Kode, dokumen, dan isian lain tidak disentuh.

## Consequences

- Nama badan usaha cukup diketik sekali, dan CV atau PT baru bisa ditambahkan tanpa rilis.
- HR dan Finance melihat daftar yang sama; perubahan nama di HR terlihat di BKK dan dropdown berikutnya.
- finance-service tetap hanya **membaca** payroll-service lewat `GET /internal/badan-usaha` yang sudah ada; tidak ada rute tulis baru antar-service. Urutan deploy: finance-service, lalu frontend.
- Badan usaha yang ditambahkan HR baru bisa dipakai membayar sesudah Finance mendaftarkannya. Jedanya disengaja: kode CV/PT, singkatan BKK, dan rekening adalah keputusan Finance.
- **Wewenang payroll tidak ikut berubah.** Daftar pemegang badan usaha yang dibaca payroll untuk menandai LUNAS (`gabungPemegangBadanUsaha`, kontrak `PemegangBadanUsahaBersama`) tetap hanya memuat CV, walau PT dan PT00 kini tersambung ke badan usaha HR. Tanpa itu pemegang PT mendapat wewenang baru di payroll tanpa keputusan yang memintanya.
- **Daftarkan menolak badan usaha yang cocok dengan entitas belum tersambung** (mis. PT Bharata dengan PT00): jalannya Sambungkan, supaya tidak lahir kode ganda.
- Daftar PT lain di dropdown berhenti bergantung pada Accurate saat form dibuka, sehingga satu panggilan Accurate per pembukaan form hilang. Rekening 1298 yang baru dibuat di Accurate tetap perlu dipasang ke entitasnya (otomatis saat semai, atau lewat dialog ubah).
- [[REF - Kepemilikan Data]] dan [[Finance - Buku Besar CV]] wajib disinkronkan sesudah kode merged: baris "Master entitas CV grup", "Identitas CV", dan angka 41 di sana.

## Belum Diputuskan (TBD)

- **Apakah PT lain dipakai untuk gaji.** 21 PT lain sudah ada di daftar HR. Bila tidak satu pun menggaji lewat ERP, pilihan badan usaha di layar gaji perlu disaring supaya PT lain tidak tampil; ukur dulu jumlah karyawan per badan usaha sebelum memutuskan.
- **Mekanisme salinan nama**: dibaca hidup saat ditampilkan, atau disalin ulang saat layar Entitas CV dibuka dan saat semai.

## Dokumen Terkait

- [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]] (direvisi sebagian: pemilik identitas CV)
- [[ADR - 0131 Tanda Tangan Direktur-Sekutu pada BKK Otomatis Tanpa Approval]] (PT lain di master entitas, penandatangan)
- [[REF - Kepemilikan Data]] · [[Finance - Buku Besar CV]] · [[Microservices - Payroll Service]] · [[HRIS - Payroll]] · [[Finance - Proses Gaji dan Iuran BPJS]] · [[Microservices - Procurement Service]]
