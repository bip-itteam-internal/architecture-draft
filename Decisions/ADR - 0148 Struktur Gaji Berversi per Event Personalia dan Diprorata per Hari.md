# ADR - 0148 Struktur Gaji Berversi per Event Personalia dan Diprorata per Hari

> **Status**: 🟡 **Diusulkan**, 2026-10-01. Diputuskan user (Tech Development) atas permintaan manajemen lewat `/analisa-kebutuhan`; kode belum ada. **Merevisi** [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]] pada satu butir: resign di tengah periode tidak lagi dibayar penuh. Nomor 0148 diklaim saat push; bila sudah terpakai, geser ke nomor bebas berikutnya.

%% Status di blockquote atas supaya terbaca VAULT-INDEX.json (15 baris pertama). %%

## Untuk Manajemen

**Masalahnya hari ini.** Gaji setiap karyawan di sistem disimpan sebagai satu catatan yang ditimpa setiap kali diubah. Begitu diubah, angka sebelumnya hilang tanpa jejak, sehingga pertanyaan "gaji si X naik kapan, berapa, dan atas keputusan apa" tidak bisa dijawab sistem. Pada 1 Oktober 2026, 160 dari 183 catatan gaji ditimpa sekaligus dari spreadsheet HRD bulan September, dan nilai sebelumnya tidak tersimpan di mana pun. Angka gaji juga diketik ulang di beberapa tempat (surat penawaran, sistem, spreadsheet), dan gaji pokok selalu dibayar penuh satu bulan walau orangnya baru masuk, resign, atau naik jabatan di tengah bulan.

**Yang diputuskan.**
- Gaji setiap karyawan menjadi **riwayat**: setiap perubahan menghasilkan catatan baru yang lengkap dengan tanggal mulai berlaku, dan catatan lama tetap tersimpan.
- Setiap perubahan **menunjuk dokumen asalnya**: surat penawaran, kontrak, SK promosi atau mutasi, atau keputusan kenaikan massal. Angkanya mengalir dari dokumen itu, tidak diketik ulang.
- Surat penawaran memuat **rincian komponen** (gaji pokok, tunjangan jabatan, tunjangan kehadiran, tunjangan makan, dan seterusnya) untuk masa evaluasi dan masa kontrak. Calon karyawan melihat **totalnya**.
- Bila dalam satu periode gaji ada perubahan, karyawan baru masuk, atau resign, gaji dihitung **proporsional per hari**.
- Spreadsheet HRD berhenti menimpa langsung; bila dipakai, ia masuk sebagai perubahan bercatatan.

**Yang berubah di layar.** HR mengisi rincian gaji di surat penawaran, di form promosi/mutasi, dan di perpanjangan kontrak memakai satu bentuk isian yang sama. Halaman gaji karyawan menampilkan riwayat beserta asal setiap perubahan. Slip gaji pada bulan terjadinya perubahan menampilkan bagian proporsionalnya.

**Siapa yang terdampak.** Personalia dan Manajer HRD (pengisi dan penyetuju), Cost Control dan Finance (angka slip berubah pada bulan yang ada perubahan), serta seluruh karyawan baru dan yang resign di tengah periode (gaji pokok bulan itu tidak lagi penuh).

**Yang tidak dijanjikan.**
- Rentang gaji per jenjang jabatan tidak termasuk; sistem mencatat angka yang diputuskan HR, tidak menyarankan atau membatasinya.
- Riwayat sebelum sistem ini berjalan tidak direkonstruksi; ia tetap tersedia lewat slip impor dari spreadsheet.
- Pembagi proporsional memakai **hari kalender** periode, dan itu masih **menunggu konfirmasi HRD**.
- Kejanggalan data yang ditemukan saat analisa (tunjangan kehadiran hanya terisi untuk 1 dari 183 karyawan) dicatat, tetapi tidak diselesaikan oleh keputusan ini.

**Besaran kerja.** Sekitar 13 pekerjaan di tiga aplikasi (satu di antaranya konfirmasi kebijakan ke HRD), dalam tiga tahap. Tahap pertama (riwayat dan jejak perubahan) sudah berguna sendiri dan menghentikan hilangnya angka lama.

## Deskripsi

*Struktur gaji tetap seorang karyawan disimpan sebagai rangkaian versi utuh bertanggal mulai berlaku, masing-masing menunjuk dokumen hulu yang memicunya (offer, kontrak, movement, keputusan massal, impor sheet, atau koreksi), dimiliki payroll-service, dan dibaca engine payroll per hari dalam periode sehingga perubahan, masuk, dan resign di tengah periode diprorata.*

- **Status**: 🟡 Diusulkan (lihat blockquote atas)
- **Path di repo** (semua akan disentuh, penanda `(baru)` untuk berkas baru):
  - `bip-erp/services/payroll/models_salary_version.go` (baru) · `salary_version_handlers.go` (baru) · `run_handlers.go` (`computeRunLines`) · `payroll_calc.go` · `employee_salary_handlers.go` · `impor_run*.go`
  - `bip-erp/services/recruitment/models_offer.go` · `candidate_handlers.go` (`link-employee`)
  - `bip-erp/services/employee/mutasi.go` · `mutasi_routes.go` · `contract.go`
  - `erp-frontend/src/features/hris/payroll/components/employee-salary-form.tsx` · `salary-register-page.tsx` · `src/features/hris/recruitment/offers/components/offer-form-dialog.tsx` · `src/features/hris/mutasi/components/mutasi-form-modal.tsx`
- **Tanggal**: 2026-10-01
- **Dok domain (cara kerja)**: [[HRIS - Compensation & Benefits]]

## Context

Diukur di kode `origin/main` dan data prod pada 2026-10-01.

1. **Satu dokumen per karyawan, ditimpa.** `employee_salary` (`services/payroll/models_employee_salary.go:28-50`) ditulis lewat `PUT /employee-salary/:employeeId` dengan `UpdateOne` + upsert (`employee_salary_handlers.go:306-311`). Tidak ada riwayat, versi, maupun log audit (`git grep` atas `salary_histor|riwayat_gaji|salary_version|audit` di `services/payroll` kosong). [[Microservices - Payroll Service]] sudah mencatat bahwa rekonstruksi lewat oplog mustahil.
2. **`effective_date` disimpan tapi tak pernah dibaca.** Satu-satunya penulisnya `employee_salary_handlers.go:298`; satu-satunya `EffectiveDate` yang dibaca payroll milik resign (`employee.go:107-122`). Isinya di prod juga kotor: dari 183 dokumen, **134 kosong** dan **45 bertanggal `2027-08-25`** (kemungkinan salah ketik untuk 2026-08-25). Tanggal ini aman hari ini **justru karena** tak dibaca, dan menjadi bug begitu engine mulai membacanya.
3. **Engine membaca keadaan saat run dihitung, bukan keadaan per tanggal.** `computeRunLines` mengambil seluruh `employee_salary` tanpa filter (`run_handlers.go:197`). Gaji pokok selalu penuh (`payroll_calc.go:415`). Resign di tengah periode dibayar penuh sebagai keputusan produk (`resign_filter.go:21-23`, [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]]), dan payroll sama sekali tak membaca `join_date` untuk run bulanan. Yang sudah diprorata hanya potongan kehadiran, berpembagi tetap 26 hari / 173 jam (`attendance_deduction_calc.go:196-203`).
4. **Angka diketik ulang di tiap mata rantai.** Offer menyimpan dua angka tanpa rincian (`gaji_evaluasi`, `gaji_kontrak`, `services/recruitment/models_offer.go:39-43`) dan tak pernah memanggil payroll; kandidat yang diterima ditautkan manual ke karyawan (`candidate_handlers.go:302-311`) tanpa membawa gaji. Modul Promosi & Mutasi (`employee_movement`, [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]]) tidak punya satu pun field gaji. Kontrak PKWT membaca gaji dari payroll tanpa menyimpannya (`services/employee/contract_pkwt_gaji.go:31-60`). Ini kelas yang dicatat [[REF - Rantai Pengajuan Lintas Modul]]: entitas hilir menyimpan ulang isi hulunya tanpa rujukan id.
5. **Spreadsheet HRD adalah sumber kedua yang menang.** Pada 2026-10-01 pukul 04 WIB, 160 dokumen `employee_salary` ditimpa `updated_by: SCRIPT-SHEET-SEP-20261001`. [[ADR - 0070 Impor Payroll Run dari Spreadsheet HRD untuk Backfill Riwayat Gaji]] mencatat riwayat gaji selama ini hanya hidup di Excel HRD.
6. **`masa_evaluasi` di offer teks bebas.** Lima offer prod (semuanya Draft, dibuat September) berisi "2 BULAN", "2 Bulan", "26 Agustus 2026", "20 Agutus 2026 - 25 Oktober 2026". Tanggal akhir probation tak bisa dihitung darinya.
7. **Rentang gaji per jenjang tidak ada.** `JobLevel` hanya `ID, Key, Name, Rank, Metadata` (`shared-library/models/employee/master_data.go:168-175`).
8. **Peraturan Perusahaan tidak mengatur prorata maupun saat struktur gaji berubah.** Satu-satunya yang menyentuh: SP II "dapat menghambat kenaikan upah, promosi" (Pasal 55 jo. 53, `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md:94`). Potongan SP II 25% gaji pokok sendiri bukan perubahan struktur, dan belum ada di kode ([[ADR - 0071 Peta Kepatuhan Peraturan Perusahaan dan Kewajiban ADR untuk Penyimpangan]]).

⚠️ **Keputusan ini berdiri sebagian di atas dok berstatus 🟡.** [[HRIS - Compensation & Benefits]] masih Konsep, [[ADR - 0089 Tanda Tangan Kontrak Kerja di Sistem Sendiri, Didampingi HRD, e-Meterai Dibubuhkan HR]] dan [[ADR - 0129 Persetujuan Payroll Run Bertingkat dan Dibayar per Badan Usaha sebelum Terbit]] masih Diusulkan/di balik flag, dan [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]] belum diputuskan. Yang dipakai dari ketiganya adalah arah (siapa boleh melihat dan menulis gaji), bukan kode yang sudah berjalan.

## Decision

### 1. Versi utuh, dimiliki payroll

Payroll-service memiliki koleksi versi struktur gaji. Setiap versi memuat **struktur tetap yang utuh**, bukan selisihnya:

- komponen ber-`input_type: manual` yang bersifat tetap: Gaji Pokok, Tunjangan Jabatan, Tunjangan Kehadiran (nilai dasar), Tunjangan Makan, Tunjangan Masa Kerja, Tunjangan Shift, Tunjangan PPh 21;
- dasar upah BPJS Kesehatan dan Ketenagakerjaan, kepesertaan BPJS, status PTKP, badan usaha penggaji (`company_id`);
- tanggal mulai berlaku, status, rujukan hulu, pencatat dan penyetuju.

Alasannya: prorata harus bisa menjawab "struktur apa yang berlaku pada hari X" dari satu catatan. Versi berisi selisih memaksa engine menyusun ulang dari rangkaian catatan, dan satu catatan yang hilang atau salah urut menghasilkan slip salah tanpa galat.

`employee_salary` yang ada tetap ada sebagai **proyeksi "versi yang berlaku hari ini"**, ditulis hanya oleh payroll saat versi berpindah, supaya konsumen yang sudah membacanya (PKWT `contract_pkwt_gaji.go`, THR `thr.go:34`, impor `impor_run_handlers.go:395`, koreksi `run_jenjang_koreksi.go:232`) tidak patah. Proyeksi ini tak boleh lagi ditulis tangan; `PUT /employee-salary/:employeeId` berubah menjadi pembuat versi.

### 2. Komponen variabel tidak pernah masuk versi

Bonus, Insentif, Kasbon, dan Lain-lain diisi per run; Lembur, BPJS, PPh 21, dan seluruh potongan kehadiran dihitung engine. Tak satu pun disalin ke versi baru. Kasbon yang terbawa ke versi berikutnya akan terpotong ulang setiap bulan tanpa galat; per 2026-10-01 ada satu `employee_salary` prod yang menyimpan Kasbon di struktur tetap, dan ia dibersihkan saat migrasi (§9).

### 3. Hanya tanggal mulai yang disimpan

Tanggal berakhir sebuah versi **diturunkan** dari tanggal mulai versi berikutnya, tidak disimpan. Dua tanggal yang sama-sama disimpan bisa tidak sambung: celah (hari tanpa gaji) atau tumpang-tindih (dua gaji sekaligus), keduanya senyap. Dengan satu tanggal, setiap hari punya tepat satu versi berlaku. Komponen sementara (Plt, acting) tidak mendapat field "sampai": HR menjadwalkan versi pengembaliannya saat menetapkan.

### 4. Status versi dan kekebalan versi yang sudah lewat

`terjadwal` (tanggal di depan, masih bisa diubah atau dibatalkan) · `berlaku` · `lewat` · `batal`. Perpindahan `terjadwal` ke `berlaku` dikerjakan cron harian yang idempoten, meniru pola mutasi dan resign (`mutasi_routes.go:350`, cron `15 0 * * *`). Versi yang **sudah dipakai sebuah payroll run berstatus di atas draft tidak boleh diubah**; koreksi menerbitkan versi baru. Slip yang terbit tetap beku seperti sekarang (`payroll_run_line.payslip`).

### 5. Setiap versi menunjuk hulunya, dan tanggalnya mengikuti hulu

| Event | Hulu | Tanggal mulai berlaku | Diisi HR |
|---|---|---|---|
| Offer, set evaluasi | offer | `join_date` sebenarnya, bukan tanggal mulai di offer | seluruh struktur (di offer) |
| Offer, set kontrak | offer | sehari sesudah tanggal akhir evaluasi | seluruh struktur (di offer) |
| Perpanjangan kontrak | kontrak | `start_date` kontrak baru | konfirmasi; terisi dari versi berlaku |
| PKWT ke PKWTT | kontrak | `start_date` kontrak PKWTT | konfirmasi; terisi dari versi berlaku |
| Promosi / demosi | movement | `effective_date` movement | wajib Tunjangan Jabatan |
| Mutasi lateral | movement | `effective_date` movement | terisi dari versi berlaku |
| Mutasi antar-perusahaan | movement | `effective_date` movement | wajib badan usaha penggaji |
| Kenaikan berkala / UMK | keputusan massal | tanggal keputusan | wajib Gaji Pokok |
| Impor sheet HRD | berkas impor | tanggal yang dinyatakan pengimpor | dari berkas |
| Koreksi / komponen sementara | tanpa hulu | diketik HR | bebas |

Kolom "wajib" adalah tanda, bukan kunci: sistem tak membatasi komponen mana yang boleh berubah per event, karena itu kebijakan HRD. Hulu yang tanggalnya berubah (modal edit movement terjadwal, `mutasi-edit-modal.tsx`) **menggeser** versinya; hulu yang batal **membatalkan** versinya. Versi gaji tidak menyalin tanggal hulu sebagai fakta kedua.

Rujukan hulu disimpan sebagai jenis + id. Inilah yang membuat pertanyaan "gaji ini dari keputusan apa" terjawab dengan menunjuk dokumen, dan menutup kelas [[REF - Rantai Pengajuan Lintas Modul]] untuk rantai gaji. Prefill ("ambil dari versi lama") bukan sambungan; yang dituntut adalah id hulu di versi.

### 6. Offer menyimpan dua set komponen; calon karyawan melihat total

Offer di recruitment menyimpan dua set struktur (evaluasi dan kontrak) dengan bentuk yang sama dengan versi, menggantikan `gaji_evaluasi` dan `gaji_kontrak`. `masa_evaluasi` teks bebas diganti **tanggal akhir evaluasi**. Total yang tampil ke calon karyawan dihitung dari komponen dan **tidak disimpan**. Rincian baru sampai ke karyawan di Lampiran 1 kontrak, yang angkanya diambil dari payroll ([[ADR - 0089 Tanda Tangan Kontrak Kerja di Sistem Sendiri, Didampingi HRD, e-Meterai Dibubuhkan HR]]).

Saat kandidat ditautkan ke karyawan (`link-employee`), recruitment mengirim kedua set ke payroll sebagai versi berlaku dan versi terjadwal. Ini salinan yang sah menurut [[REF - Kepemilikan Data]]: satu arah (recruitment ke payroll), tak pernah ditulis tangan di sisi tujuan, dan berpenjaga (offer yang sudah Accepted dibekukan; perubahan sesudahnya dikerjakan di payroll sebagai versi baru).

### 7. Prorata per hari, untuk semua batas versi

Dalam satu periode, setiap komponen struktur tetap dibayar sebesar `nilai × hari berlaku / hari periode` per versi, lalu dijumlahkan. Batas versi mencakup:

- perpindahan versi (promosi, probation ke kontrak, dan seterusnya);
- **karyawan masuk** di tengah periode: hari sebelum `join_date` tak punya versi;
- **karyawan resign** di tengah periode: hari sejak tanggal efektif resign tak punya versi.

Butir ketiga **merevisi** keputusan produk di [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]] ("resign di tengah periode dihitung penuh").

- **Pembagi = hari kalender periode** (mis. 26 Agustus s.d. 25 September = 31 hari). Ini **asumsi yang menunggu konfirmasi HRD**, bukan aturan Peraturan Perusahaan; ia sengaja tidak memakai pembagi 26 milik potongan kehadiran.
- ⚠️ **Tunjangan Makan bergantung pada issue bip-erp#2431** (terbuka, 2026-10-01), yang mengusulkan TM dihitung engine sebagai tarif harian × hari kerja terjadwal (sheet HRD September berbeda TM dari sistem untuk 160 dari 167 orang). Bila diterima, TM keluar dari struktur tetap dan sudah proporsional dengan sendirinya, sehingga tidak ikut prorata hari kalender di sini. Karena itu struktur tetap **diturunkan dari master komponen** (`input_type`), bukan dari daftar nama di kode.
- Tarif potongan kehadiran per hari memakai **nilai dasar Tunjangan Kehadiran dari versi yang berlaku pada hari pelanggaran**.
- Slip pada bulan prorata menampilkan **satu baris per komponen** beserta keterangan hari, bukan baris per versi, supaya pembaca slip tidak membaca dua Gaji Pokok sebagai dua pembayaran.

### 8. Gerbang saat menyimpan versi

- Perubahan Gaji Pokok atau Tunjangan Jabatan (dua komponen ber-`bpjs_base`) **tidak dapat disimpan** sebelum dasar upah BPJS dikonfirmasi, entah diubah atau sengaja dibiarkan. Dok Payroll mencatat nol dari 120 record lama punya dasar upah yang masuk akal; gerbang ini mencegah kelas itu tumbuh lagi.
- Versi yang menaikkan struktur untuk karyawan ber-SP II aktif memunculkan **peringatan** (Pasal 55 jo. 53), tidak menolak.
- **Persetujuan**: versi baru berstatus menunggu persetujuan **Manajer HRD** sebelum menjadi terjadwal atau berlaku. Sampai [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]] diputuskan, gerbangnya paket SPV HRD yang sudah ada di [[ADR - 0129 Persetujuan Payroll Run Bertingkat dan Dibayar per Badan Usaha sebelum Terbit]]. Pengisi dan penyetuju tak boleh orang yang sama.
- **Visibilitas** tetap mengikuti ADR 0129 dan 0089: staf payroll berizin, karyawan yang bersangkutan, dan Direktur. Atasan tidak.

### 9. Migrasi dan pensiun sheet

- Setiap `employee_salary` yang ada menjadi **versi #1** bersumber `migrasi`, berlaku sejak **awal periode payroll pertama yang dihitung engine sesudah migrasi**. `effective_date` lama (kosong atau 2027) tidak dipakai. Riwayat sebelumnya tetap di run impor ADR 0070.
	- 🔁 **Amandemen 2026-10-02 (S1 + S2):** versi #1 dibuat **identik dengan versi dasar otomatis S1**: sumber `baseline_proyeksi`, berlaku **`1970-01-01`** sebagai penanda "sebelum riwayat tercatat" (proyeksi dan layar tak memamerkan tanggal itu), bukan sumber `migrasi` bertanggal awal periode. Alasannya: dengan prorata (§7), periode lama yang dihitung ulang tetap menemukan versi berlaku; versi bertanggal awal periode akan membuat hari sebelumnya tanpa versi, alias gaji nol. Satu bentuk juga berarti migrasi dan pembuatan lazy S1 tak bisa menggandakan versi #1. Versi hasil migrasi diberi penanda `migrasi: "s2-20261002"` untuk pemulihan.
- Komponen variabel yang tersimpan di struktur (Kasbon) dibuang dari versi #1 dan dicatat di laporan migrasi.
	- Diukur prod 2026-10-02: satu karyawan (Kasbon Rp 1.000.000 di struktur). Diputuskan user 2026-10-02: kasbon punya **alur pengajuan sendiri** (masih manual, tanda tangan basah), bukan bagian struktur gaji; sesudah migrasi potongannya tidak lagi otomatis tiap run, dan HRD memasukkannya sebagai Kasbon per run sesuai pengajuan. Alur pengajuan kasbon di sistem = di luar ADR ini (calon rantai pengajuan → payroll, lihat [[REF - Rantai Pengajuan Lintas Modul]]).
- Skrip impor sheet HRD tak lagi menulis `employee_salary` langsung; ia membuat versi bersumber `impor_sheet`, melewati gerbang §8 yang sama.
- Migrasi adalah **tulis prod**: agent menyiapkan skrip dry-run dan apply beserta backup; manusia yang menjalankan.

## Consequences

### Yang membaik

- Pertanyaan "gaji si X kapan berubah, berapa, karena apa" terjawab dari sistem dengan menunjuk dokumennya.
- Angka mengalir dari offer, kontrak, dan movement ke payroll tanpa diketik ulang.
- Slip bulan yang memuat perubahan, masuk kerja, atau resign dibayar sesuai hari.
- Lampiran 1 kontrak dan payroll membaca sumber yang sama.

### Yang memburuk atau tetap terbuka

- ⚠️ **Angka slip berubah** untuk karyawan yang masuk atau resign di tengah periode: gaji pokok bulan itu tidak lagi penuh. Run pertama sesudah perubahan engine wajib dibandingkan berdampingan dengan hitungan HRD sebelum diterbitkan.
- ⚠️ **Pembagi hari kalender belum dikonfirmasi HRD.** Bila HRD memakai pembagi lain (mis. 30 tetap atau hari kerja), hanya fungsi prorata yang berubah, tetapi itu wajib diputuskan sebelum tahap 2 di-deploy.
- Engine payroll menjadi lebih rumit: satu karyawan bisa punya dua sampai tiga versi dalam satu periode.
- **recruitment-service mendapat ketergantungan baru ke payroll** (env `PAYROLL_MODULE_URL`, naik dengan `--force-recreate`). employee-service sudah memegangnya.
- Tunjangan Kehadiran hanya terisi untuk 1 dari 183 karyawan di prod (2026-10-01), sehingga potongan kehadiran praktis nol bagi 182 orang. Ini **di luar** keputusan ini dan perlu ditanyakan ke HRD terpisah.
- Selama spreadsheet HRD masih dipakai paralel, versi bersumber `impor_sheet` akan terus muncul; manfaat ketertelusuran baru penuh setelah HR mengisi lewat event.

### Yang sengaja tidak dilakukan

- **Struktur gaji tidak disimpan di dokumen hulu masing-masing** (offer, kontrak, movement) lalu dirakit payroll saat run. Itu menyebar satu fakta ke tiga service, membuat run gagal saat satu service mati, dan meninggalkan koreksi tanpa tempat.
- **Tidak berhenti di log audit + satu dokumen.** Lebih murah, tetapi engine tetap hanya tahu satu struktur per run sehingga prorata tak bisa dihitung benar.
- **Rentang gaji per jenjang** tidak dibangun: belum ada keputusan HRD tentang rentangnya, dan jenjang sengaja bukan sumbu hak.
- **Sistem tidak membatasi komponen mana yang boleh berubah per event.** Itu kebijakan HRD; sistem hanya menandai yang wajib disentuh.

## Dokumen Terkait

- [[HRIS - Compensation & Benefits]] (cara kerja versi struktur gaji)
- [[HRIS - Payroll]] · [[Microservices - Payroll Service]] · [[Microservices - Recruitment Service]] · [[Microservices - Employee Service]]
- [[HRIS - Career & Promotion]] · [[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]] · [[HRIS - Disciplinary (Surat Peringatan)]]
- [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]] (direvisi pada prorata resign)
- [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]] · [[ADR - 0070 Impor Payroll Run dari Spreadsheet HRD untuk Backfill Riwayat Gaji]] · [[ADR - 0089 Tanda Tangan Kontrak Kerja di Sistem Sendiri, Didampingi HRD, e-Meterai Dibubuhkan HR]] · [[ADR - 0129 Persetujuan Payroll Run Bertingkat dan Dibayar per Badan Usaha sebelum Terbit]] · [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]]
- [[ADR - 0002 Database-per-Service]] · [[REF - Kepemilikan Data]] · [[REF - Rantai Pengajuan Lintas Modul]] · [[HRIS - Kepatuhan Peraturan Perusahaan]]
