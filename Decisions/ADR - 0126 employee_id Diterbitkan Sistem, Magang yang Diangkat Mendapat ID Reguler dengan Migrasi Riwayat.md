## Untuk Manajemen

**Apa yang berubah di layar.** Form Tambah Karyawan tidak lagi punya kolom ID Karyawan. Sistem membuat ID sendiri saat data disimpan, dan HR melihatnya di ringkasan akhir. Karyawan bertipe Magang otomatis mendapat ID berawalan `MG` (contoh `BIP-MG-1013-10-26`), karyawan lain mendapat ID reguler (contoh `BIP-0265-10-26`). Nomor dobel dan magang tanpa `MG`, dua masalah yang ada di data hari ini, tidak bisa terjadi lagi.

**Saat magang diangkat menjadi karyawan kontrak**, ia mendapat ID reguler baru, dan seluruh datanya (absen, cuti, KPI, kontrak, payroll, formulir, notifikasi) ikut dipindah ke ID baru itu. Riwayat kontrak Magang dan PKWT-nya terlihat berurutan di halaman Kontrak yang sudah ada. Pemindahan ini dijalankan tim IT per angkatan atas permintaan HR, bukan tombol di layar HR.

**Siapa yang terdampak.** HR (tidak lagi mengetik ID), karyawan magang yang diangkat (harus login ulang di MyBharata dengan ID baru dan mengaktifkan ulang sidik jari/wajah), tim IT (menjalankan pemindahan per angkatan), dan Finance bila magang yang diangkat punya proyek di Accurate. **Yang TIDAK dijanjikan:** tombol "Angkat Karyawan" yang bisa dijalankan HR sendiri (pemindahan tetap lewat tim IT); mengganti nomor proyek di Accurate (tetap langkah manual Finance); memindah folder foto dan dokumen lama (berkasnya tetap terbuka dari folder lamanya).

**Perkiraan besaran.** ID otomatis: dua perubahan (backend lalu frontend), beberapa hari kerja. Alat pemindahan ID dan panduannya: satu sampai dua hari termasuk uji di server development. Sesudah itu tiap angkatan pengangkatan butuh sekitar satu jam kerja tim IT.

## Deskripsi

*`employee_id` diterbitkan employee-service dari dua deret berpenghitung atomik (reguler dan magang), tidak pernah diketik HR. Magang yang diangkat ke kontrak mendapat ID reguler baru dan seluruh rujukan lamanya dimigrasi, satu-satunya pengecualian atas [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]]. Mengangkat spesifikasi 2026-08-19 yang tak pernah dikerjakan ke vault, dengan satu keputusan yang dibalik.*

- **Status**: 🟡 **Diusulkan** 2026-09-25, disetujui pemilik produk lewat `/analisa-kebutuhan`. Kode belum ada. Papan kerja: [[ANALISA - ID Karyawan Otomatis dan Pengangkatan Magang]]
- **Path di repo**: `bip-erp/services/employee/employee_id_counter.go` (baru) · `bip-erp/services/employee/func.go` (transaksi create-employee) · `bip-erp/services/employee/main.go` (handler create-employee) · `bip-erp/orchestrator/hris/handler.go`, `transactions.go` · `erp-frontend/src/features/hris/employee/components/modals/create-employee/` (field ID dihapus) · `erp-frontend/src/features/hris/employee/utils/id.ts` · alat migrasi pengangkatan + runbook (baru)
- **Tanggal**: 2026-09-25

## Context

**ID diketik manusia, dan datanya menunjukkan akibatnya.** `POST /internal/transaction/create-employee` menerima `employee_id` dari body, dan satu-satunya pemeriksaannya menolak nilai kosong (`services/employee/main.go:494-527`). Form memakai input 11 kotak berkelompok 3-4-2-2 (`erp-frontend/src/components/form/input-otp.tsx:36,45-66`), jadi bentuk magang `BIP-MG-...` mustahil diketik di sana. Diukur di prod 2026-09-25 atas 215 karyawan BIP:

- **6 pasang nomor urut dipakai dua orang berbeda** (0082, 0236, 0251, 0252, 0253, 0262). Empat pasang melibatkan pindahan Percetakan ber-akhiran `-07-26`.
- **Hanya 58 dari 207 ID reguler** yang bulan-tahunnya sama dengan tanggal masuk.
- **13 magang, dua konvensi**: 8 ber-`BIP-MG-1000..1007` (Juni), 5 ber-`BIP-1008..1012` tanpa `MG` (September). `BIP-MG-1004-06-26` sudah PKWT (Evaluasi) tapi ID-nya masih `MG`.
- Nomor tertinggi: reguler **0264**, magang **1012**.

**Keputusan yang sama sudah pernah dikunci dan tak pernah dikerjakan.** `.task-plans/2026-08-19-employee-id-otomatis-SPEC.md` memutuskan format, penghitung per perusahaan dan per tipe, alokasi atomik, dan tanpa override manual. Berkas itu hidup di `.task-plans` lokal, bukan di vault, jadi tak satu pun pencarian menemukannya dan HR tetap mengetik ID selama lima minggu berikutnya; seed yang ditulisnya (0251 dan 1008) kini sudah terpakai. ADR ini menggantikan SPEC itu.

**Satu keputusan SPEC dibalik: pengangkatan magang.** SPEC memutuskan magang yang diangkat mendapat ID baru **tanpa** migrasi, riwayat tertinggal di ID magang, dengan harga "tak satu layar pun menyatukannya". Pemilik produk menolaknya 2026-09-25: ID `MG` pada karyawan kontrak menyulitkan laporan HR, payroll, dan ID yang tercetak, dan menurut HR aturan kepegawaian mewajibkan nomor induk baru saat diangkat.

⚠️ **Aturan "nomor induk baru" TIDAK tertulis di Peraturan Perusahaan.** PDF `mybharata-app/assets/docs/company_policy.pdf` (41 halaman, dibaca 2026-09-25) tak memuat nomor induk, ID karyawan, maupun kata "magang"; yang ada hanya jenis perjanjian kerja (hal. 13) dan pengangkatan lewat SK/perjanjian kerja (hal. 11). Turunannya `BUSINESS_LOGIC_IMPLEMENTATION.md` juga tidak. Keputusan ini karena itu berdiri di atas SOP HR yang **belum dikonfirmasi tertulis** (K1 di papan kerja).

⚠️ **Untuk payroll, alasannya lebih lemah dari kedengarannya.** Payroll sudah membedakan magang dari `employment_type`, bukan dari awalan ID, dan itu disengaja ([[Microservices - Payroll Service]]; `services/payroll/lingkup_run.go:17-33`). Yang benar-benar menuntut ID baru adalah ID yang dibaca manusia: laporan HR dan ID yang tercetak.

**Migrasi ganti ID sudah terbukti bisa, dan terbukti bisa bolong.** Dua skrip mongosh yang dijalankan manusia sudah pernah mengganti ID di prod: 14 orang ELT→BIP (`.task-plans/migrasi-id-elt-ke-bip.js`) dan 8 magang `BIP-100N`→`BIP-MG-100N` (`.task-plans/migrasi-id-magang.js`, Agustus 2026). Diukur 2026-09-25 atas `BIP-1004-06-26`: rujukan yang tersisa hanya path foto dan KTP di MinIO (disengaja) dan **satu field yang terlewat**, `form_builder_db.forms.subject.resolved[].employee_id` pada form uji tertutup. Daftar target skrip itu ditulis tangan, dan field yang tak ada di daftar tertinggal tanpa satu pun galat.

**Radius satu orang**, diukur di prod 2026-09-25 untuk `BIP-MG-1004-06-26` (3,5 bulan bekerja): sekitar **230 dokumen di 30 koleksi dan 9 database** (employee 12, attendance 93, notification 44, marketing_analytics `live_shifts` 40, form_builder 21, integration 8, recruitment 3, payroll 2). 22 koleksi di atas 50.000 dokumen **tidak dipindai** (pesanan marketplace, `manufacture_resi`, `fulfillment_orders`), jadi angka ini batas bawah. Peta field per service (16+ database, termasuk array bersarang dan `metadata.created_by` di hampir setiap koleksi) ada di laporan grounding papan kerja.

**Di luar Mongo**, ID juga hidup di: login MyBharata (password, PIN, biometrik terikat `employee_id`, disimpan di secure storage), username dan password awal (keduanya default = ID, `orchestrator/hris/transactions.go:228`, `helper.go:471-475`), JWT 72 jam, kunci cache gateway `cache:{module}:{employeeID}:{url}`, path MinIO, dan **nomor proyek Accurate** (67 dari 81 proyek bernomor `employee_id`, `services/integration/internal/usecase/beban_marketing.go:49-55`).

## Decision

### 1. ID diterbitkan sistem, tidak pernah diketik

`employee_id` dialokasikan employee-service di dalam alur create-employee. Nilai dari body diabaikan atau ditolak, form tidak lagi menampilkan kolomnya, dan **tidak ada override manual**, sama dengan SPEC 2026-08-19. Jalur rekrutmen (hire lalu create-employee) ikut: kandidat tak pernah membawa ID.

### 2. Format dan deret

```
reguler : <KODE>-<NNNN>-<MM>-<YY>        BIP-0265-10-26
magang  : <KODE>-MG-<NNNN>-<MM>-<YY>     BIP-MG-1013-10-26
```

- `<KODE>` = `master_company.code` tanpa tanda hubung.
- `<NNNN>` = nomor urut 4 digit, **boleh meluber** lebih dari 4.
- `<MM>-<YY>` = bulan dan tahun **`join_date`** dalam WIB.
- **Deret ditentukan `employment_type` kontrak pertama**: `Magang` masuk deret magang, selain itu deret reguler. Tak ada deret untuk `EXT-` (akun eksternal punya ruang-nama sendiri).

### 3. Penghitung per (awalan, deret), atomik

- Satu dokumen penghitung per pasangan awalan dan deret, dinaikkan `FindOneAndUpdate` + `$inc` + upsert. **Bukan** `max()+1`, yang menerbitkan ID kembar pada dua simpan bersamaan.
- **Seed diukur saat deploy, bukan disalin dari dokumen ini.** Per 2026-09-25 nilainya reguler 0264 dan magang 1012, tetapi HR masih mengetik ID sampai fitur ini hidup, jadi angka itu basi begitu ditulis. Seed diambil dari nilai tertinggi yang **wajar** (SPEC mencatat satu ID salah ketik `BIP-2005` yang nyaris melompatkan seed ~1.750 nomor), dihitung dari **awalan ID**, bukan dari `company_id` pemiliknya.
- Alokator **memeriksa ID hasil rakitan belum dipakai** sebelum mengembalikannya, dan mengulang bila sudah. Indeks unik `employee_id` di `work_data`, `personal_data`, dan `system_authentication` (`services/employee/identitas_index.go:32-44`) menjadi jaring terakhir.
- Parser apa pun wajib menoleransi ID yang tak cocok pola (`SystemInitAdmin`), tidak memanik.

### 4. Pengangkatan magang: ID reguler baru, seluruh rujukan dimigrasi

Magang yang diangkat ke PKWT atau PKWTT mendapat ID dari **penghitung reguler**, dan seluruh rujukan ke ID magangnya di semua database diganti ke ID baru. Riwayat kontraknya (Magang, lalu PKWT) berada di bawah satu ID dan tampil di `/hris/contract` tanpa layar baru.

**Bulan-tahun ID baru = bulan-tahun TANGGAL DIANGKAT** (mulai kontrak PKWT/PKWTT), bukan `join_date` awal magang (keputusan pemilik produk 2026-09-26, kasus pertama Fitri Baniaturrohmah `BIP-MG-1004-06-26` → `BIP-0271-09-26`). Alasannya: nomor induk baru menandai sejak kapan orang itu menjadi karyawan; masa kerja sejak magang tetap terbaca dari riwayat kontrak.

⚠️ **Riwayat kontrak hanya utuh bila kontrak Magang DITAMBAH, bukan diubah.** Pada kasus pertama, satu-satunya kontrak Fitri adalah PKWT (Evaluasi) 2026-09-26 s/d 2027-03-25 bernomor `001/Magang/BIP/VI/2026`: kontrak magangnya ditimpa jadi PKWT, sehingga masa magang lenyap dari riwayat tanpa satu pun galat. Pengangkatan yang benar di `/hris/contract` adalah **Perpanjang** (dokumen kontrak baru), bukan **Perbaiki**.

**Ini membatasi cakupan [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]], tidak membatalkannya.** Promosi, mutasi, dan mutasi antar-perusahaan tetap mempertahankan ID. Pengangkatan magang satu-satunya peristiwa yang menerbitkan ID ulang, dengan alasan yang tidak dimiliki mutasi: ia mengubah status kepegawaian yang dibaca manusia dari ID-nya.

### 5. Migrasi dijalankan manusia per angkatan, lewat alat yang memindai, bukan daftar tangan

> ⛔ **DIGANTIKAN untuk pengangkatan magang oleh [[ADR - 0128 Pengangkatan Magang Dijalankan HR dari ERP, Ganti employee_id oleh Tiap Service]] (2026-09-26).** Pemilik produk memutuskan HR mengangkat sendiri dari ERP tanpa IT; tiap service mengganti ID di databasenya sendiri lewat fungsi bersama. Alat di bawah tetap sah sampai fitur itu live, dan untuk penggantian ID di luar pengangkatan (mis. perapian nomor §6).

Bukan fitur di layar HR. Alasannya ukuran: fitur mandiri menuntut endpoint ganti-ID di 16+ service beserta penanganan kegagalan sebagian, persis risiko yang ditolak ADR 0044, untuk peristiwa yang terjadi per angkatan bootcamp beberapa kali setahun.

Alatnya wajib:

1. **Menemukan targetnya dengan memindai** semua database untuk string ID lama, bukan membaca daftar koleksi yang ditulis tangan. Itulah yang membuat migrasi Agustus melewatkan `forms.subject.resolved`, dan field yang lahir kelak akan terlewat dengan cara yang sama. Koleksi besar dipindai per field terindeks yang diketahui memuat ID, dan yang tak bisa dipindai **dilaporkan**, tidak dilewati diam-diam.
2. **Dry-run lebih dulu**, mencetak jumlah per koleksi dan field.
3. **`mongodump` semua database yang tersentuh** sebelum menulis apa pun.
4. **Menolak berjalan** bila ID tujuan sudah dipakai di mana pun.
5. **Mengalokasikan ID baru dari penghitung reguler yang sama** dengan alokator §3, supaya penghitung tak pernah bentrok dengan ID hasil migrasi.
6. **Gerbang sisa nol** sesudahnya: pemindaian ulang harus nol rujukan ID lama, kecuali path MinIO yang sengaja dibiarkan.
7. **Menutup dengan daftar langkah manual** yang tak bisa dikerjakan skrip: karyawan login ulang dan mengaktifkan ulang biometrik; username yang sama dengan ID lama diganti; proyek Accurate bernomor ID lama diganti Finance; cache gateway basi sampai TTL habis.

Prosedurnya ditulis sebagai runbook di vault. Yang menekan enter di prod tetap manusia.

**Alatnya ada sejak 2026-09-26**: `.task-plans/jalankan-migrasi-ganti-id.ps1 -Konfig <berkas.json>` + `migrasi-ganti-id.js`, diturunkan dari skrip T7 yang dijalankan di PROD. Satu berkas konfigurasi per run (`.task-plans/ganti-id/*.json`: daftar `{lama, nama, akhiran}`, teks konfirmasi, langkah manual). Target ditemukan dari nilai PERSIS ID lama di koleksi mana pun; potongan teks hanya boleh di path berkas MinIO/foto dan teks notifikasi; koleksi besar dipindai per field ber-ID dari sampel; nomor dipesan atomik bersyarat dari penghitung; backup hanya database yang terkena. Uji dry pengangkatan pertama menangkap dua field yang tak ada di daftar tangan migrasi September (`system_authentication.web_browser[].employee_id`, `forms.audience.employee_ids[]`).

### 6. Data lama

- **5 magang September** (`BIP-1008..1012-09-26`) diganti ke `BIP-MG-1008..1012-09-26` dengan alat §5 sebelum penghitung magang di-seed. Nomornya dipertahankan, hanya disisipi `MG`, sama seperti Agustus.
- **6 pasang nomor urut dobel DIRAPIKAN** (diubah 2026-09-26 oleh pemilik produk; semula "dibiarkan"). String ID-nya memang unik sehingga sistem tak patah, tetapi nomor urut yang dipakai dua orang membuat penyebutan "karyawan nomor N" dan laporan urut-nomor ambigu. Aturannya: dari tiap pasangan, **ID yang terbit lebih dulu (bulan-tahun di ID lebih awal) mempertahankan nomornya**; yang lain mendapat nomor baru dari penghitung reguler §3, **bulan-tahun ID lamanya dipertahankan** (hanya nomor urut yang berganti, sama seperti rename magang). Pemetaan 2026-09-26: `BIP-0082-10-24`→`0265-10-24`, `BIP-0236-04-26`→`0266-04-26`, `BIP-0251-08-26`→`0267-08-26`, `BIP-0252-07-26`→`0268-07-26`, `BIP-0253-08-26`→`0269-08-26`, `BIP-0262-09-26`→`0270-09-26`. ⚠️ **Satu pengecualian, pasangan 0252:** yang diganti justru ID yang terbit lebih dulu (`BIP-0252-07-26`, Percetakan), karena `BIP-0252-08-26` adalah **nomor proyek Accurate** (`integration_db.incentive_opex_accurate.proyek_no`, 9 periode; `beban_marketing_orang`, 7 periode). Mengganti ID pemegang proyek di ERP tanpa mengganti proyeknya di Accurate memutus beban marketing dan insentifnya tanpa satu pun galat. Kelas umumnya: **ID yang juga menjadi kunci di sistem luar (Accurate) tidak diganti lewat migrasi Mongo saja**; bila harus, penggantian di sistem luar dijadwalkan bersamaan. Data proyek itu sudah ada sejak periode 2025-08, sebelum pemegangnya tercatat masuk (2026-08-26); asal-usulnya belum diperiksa Finance. Dijalankan dengan alat migrasi §5 SESUDAH backend #2079/#2086 ada di PROD, karena nomornya dipesan dari penghitung itu.
- **ID yang bulan-tahunnya tak cocok tanggal masuk dibiarkan.** Aturan §2 berlaku untuk ID baru saja.

## Consequences

**Yang diterima sadar:**

- **Setiap angkatan pengangkatan adalah penulisan ke prod** oleh manusia, dengan cadangan dan gerbang. Bila frekuensinya naik jadi bulanan, keputusan "bukan fitur" di §5 layak ditinjau ulang.
- **Login putus untuk orang yang diangkat.** JWT memuat `employee_id`, dan MyBharata menyimpan ID lama untuk login PIN, sehingga orangnya login ulang dengan ID baru dan mengaktifkan ulang biometrik (`biometric_employee_id` tak lagi cocok).
- **Berkas MinIO tetap di folder ID lama.** Dokumen menyimpan path lengkapnya, jadi berkas tetap terbuka; yang tertinggal hanya nama foldernya.
- **QR kartu di MyBharata dibaca live** dari profil, jadi otomatis berganti; salinan yang sudah dicetak atau di-screenshot menunjuk ID lama.
- **Impor karyawan ber-ID warisan tertutup lewat jalur normal**, sama dengan SPEC. Akuisisi perusahaan berikutnya butuh jalur tersendiri.
- **Konsumen yang mengurai format**: `services/procurement/kas_katalog_accurate.go:100` hanya menerima `^BIP-\d{4}-\d{2}-\d{2}$` sehingga menolak `BIP-MG-`; `services/integration/.../beban_marketing.go:55` menerima keduanya. Selama magang tak memegang kas, yang pertama tak berdampak, tetapi ia mengunci awalan `BIP` dan akan patah untuk perusahaan lain.

**Risiko yang belum tertutup:**

- **SOP HR tentang nomor induk belum dikonfirmasi tertulis** (lihat Context). Bila ternyata tak ada aturannya, §4 tetap sah sebagai keputusan pemilik produk, tetapi alasannya tinggal kebutuhan laporan dan cetak.
- **Koleksi di atas 50.000 dokumen belum diukur** untuk rujukan magang. Alat §5 wajib menjawabnya sebelum dipakai pertama kali.

**Menggantikan:** `.task-plans/2026-08-19-employee-id-otomatis-SPEC.md` (lokal, bukan vault). Bagian yang tetap berlaku sudah dipindahkan ke §1 sampai §3; bagian "magang diangkat tanpa migrasi" dibalik oleh §4.

## Terkait

- [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]] (cakupannya dibatasi oleh §4)
- [[HRIS - Personalia]] (cara kerja ID dan pengangkatan) · [[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]] (riwayat kontrak)
- [[Microservices - Employee Service]] · [[Microservices - Payroll Service]] · [[Microservices - Recruitment Service]]
- [[ANALISA - ID Karyawan Otomatis dan Pengangkatan Magang]] (papan kerja)
