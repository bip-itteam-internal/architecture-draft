# ANALISA - Pengangkatan Magang dari ERP

Papan kerja untuk [[ADR - 0128 Pengangkatan Magang Dijalankan HR dari ERP, Ganti employee_id oleh Tiap Service]]. Dibuat 2026-09-26 lewat `/analisa-kebutuhan`. Bukan dok terbit; keputusan dan alasannya di ADR, cara kerjanya di [[HRIS - Personalia]] §ID Karyawan & Pengangkatan Magang. Lanjutan dari [[ANALISA - ID Karyawan Otomatis dan Pengangkatan Magang]] (T4/T6 di sana).

**Kebutuhan:** HR mengangkat magang ke PKWT/PKWTT sendiri dari ERP tanpa IT, dan sesudahnya orang itu tidak lagi tampil ber-`MG` di mana pun ID-nya dilihat.

**Opsi yang ditolak:** nomor induk terpisah. Grounding 2026-09-26: ~70 berkas erp-frontend menampilkan `employee_id` tanpa komponen bersama; slip gaji (label "NIK"), ekspor, impor payroll/BPJS, pencarian, onboarding, Accurate, dan MyBharata semuanya memakai `employee_id` langsung. Rinciannya di bagian Grounding di bawah.

## Konfirmasi yang ditunggu (bukan kode)

- [ ] **K1 Finance**: apakah integrasi Accurate bisa mengganti nama proyek lewat API (bila ya, §4 ADR 0128 bisa diotomatisasi kemudian). Sampai terjawab, Finance menerima tugas inbox.

## Task (berurutan)

- [~] **T1 status 2026-09-26:** paket `shared-library/database/mongodb/idreplace`, bip-erp PR [#2094](https://github.com/bip-itteam-internal/bip-erp/pull/2094) (judge lolos percobaan 2/3; gerbang 46 lolos, 0 gagal baru). Percobaan 1 gagal karena koleksi besar memilih kandidat field hanya dari kemunculan ID yang sedang diganti di `$sample`, sehingga koleksi diam-diam tak terpindai dan apply tetap sukses; kini pola kandidat parameter pemanggil (`Options.CandidatePattern`) dan apply menolak koleksi tak terpindai kecuali `AllowUnscannable`. ⚠️ **Syarat turunan dari judge**: T2 WAJIB memberi `CandidatePattern` setara pola ID karyawan (tanpa pola, field kedua milik orang yang sama bisa terlewat bila sampel kebetulan memuat ID lama di field lain); T3 WAJIB menjalankan dry di SEMUA service dulu dan apply hanya bila semuanya lolos (fungsi bekerja per database, skrip lama memutuskan per container), dan daftar-izin potongan teks dijaga per database.
- [ ] **T1 BE shared-library: fungsi ganti employee_id atas satu database.** Angkat logika `.task-plans/migrasi-ganti-id.js` (teruji PROD 3x) ke Go: pindai seluruh koleksi database pemanggil; ganti setiap nilai PERSIS ID lama, termasuk elemen array satu tingkat (`arr.$[].field`, `arr.$[]`); tolak bila ID lama muncul sebagai potongan teks di luar daftar-izin (path berkas MinIO/foto, teks inbox); koleksi >50 ribu dokumen lewat field ber-ID dari sampel; kembalikan ringkasan per koleksi + daftar koleksi yang tak bisa dipindai; idempoten. Uji: fixture yang meniru bentuk nyata (termasuk `system_authentication.device[]`/`web_browser[]`, `forms.audience.employee_ids[]`, `live_shifts.host[]`), kontrol negatif potongan teks di tempat tak dikenal. Dependensi: tidak ada.
- [ ] **T2 BE semua service: rute internal ganti-ID.** Tiap service yang punya database mendaftarkan satu rute internal (gerbang internal, sama untuk semua) yang memanggil T1 atas databasenya sendiri. Satu test pemindai sumber yang gagal bila service ber-database tak mendaftarkan rute. Dependensi: T1.
- [ ] **T3 BE employee-service: koordinator pengangkatan.** Koleksi status pengangkatan (menunggu/berjalan/selesai/gagal, status per service, pemetaan permanen, pelaku); pesan ID reguler dari penghitung dengan bulan-tahun = mulai kontrak PKWT/PKWTT pertama; tolak berjalan bila ada service tanpa rute; panggil tiap service, employee-service terakhir; ulang per service yang gagal; kirim tugas inbox Finance bila ada data turunan Accurate ber-ID lama (`beban_marketing_orang`, `incentive_opex_accurate`). Syarat mulai: ID ber-`MG` dan punya kontrak PKWT/PKWTT. Dependensi: T1, T2.
- [ ] **T4 FE halaman Kontrak: tombol "Angkat" + status.** Muncul di riwayat kontrak untuk karyawan ber-ID magang yang punya kontrak PKWT/PKWTT; dialog konfirmasi menyebut ID baru dan akibatnya (login putus); status proses per service; peringatan pakai Perpanjang bukan Perbaiki. i18n id+en. Dependensi: T3 deployed (BE dulu).
- [ ] **T5 Runbook** `RUN - Pengangkatan Magang` untuk HR (langkah layar) dan IT (membaca status gagal, pembalikan). Dependensi: T4.
- [ ] **T6 Deploy**: `shared-library` berubah → seluruh service yang mendaftarkan rute naik bersama; verifikasi tiap container memuat rute (koordinator menolak bila tidak). Dependensi: T2, T3.

## Terpisah, jangan disisipkan

- **Fitri Baniaturrohmah** (`BIP-MG-1004-06-26`) bisa diangkat sekarang lewat alat (`.task-plans/ganti-id/2026-09-26-angkat-fitri.json`, dry run lolos) atau menunggu T4. Kontrak magangnya tertimpa; HR menambahkannya kembali.
- **Label "NIK" pada slip gaji** yang berisi `employee_id` (`services/payroll/payslip_pdf.go:222`) bertabrakan makna dengan NIK KTP. Brief terpisah bila ingin diganti "ID Karyawan".
- **Saringan proyek Accurate di procurement** (`services/procurement/kas_katalog_accurate.go:100`) tak menerima `MG-`.

## Grounding (2026-09-26, origin/main)

- Login: 180 dari 181 akun aktif memakai username sendiri (PROD); `/auth/login` mencari username dulu lalu employee_id (`services/employee/main.go:2819-2821`); biometrik/refresh berkunci employee_id (`:3020`, `:3090`).
- Pemicu data: `segarkanSalinan` (`services/employee/contract.go:211`) satu-satunya penulis `employment_type`, dipanggil POST (`:325`) dan PATCH (`:403`).
- Alokator: `services/employee/employee_id_alokator.go` (`AlokasikanEmployeeID`, deret dari `employment_type`, penghitung `employee_id_counter`).
- Tampilan/masukan ber-`employee_id`: ekspor karyawan (`orchestrator/hris/employee_export.go:121,184`), slip (`services/payroll/payslip_pdf.go:151,222`), impor payroll (`services/payroll/impor_run.go:60`), upah BPJS (`bulk_bpjs_base.go:35`), Accurate (`services/integration/internal/usecase/beban_marketing.go:49-55`), QR (`services/employee/main.go:143`); FE ~70 berkas (mis. `features/hris/employee/components/summary-card.tsx:53`, `features/hris/payroll/components/payroll-run-detail.tsx:288`), MyBharata profil/Data Kerja/QR.
