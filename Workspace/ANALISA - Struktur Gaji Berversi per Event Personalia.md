# ANALISA - Struktur Gaji Berversi per Event Personalia

Papan kerja [[ADR - 0148 Struktur Gaji Berversi per Event Personalia dan Diprorata per Hari]] (disetujui user 2026-10-01 lewat `/analisa-kebutuhan`, Opsi 1). Keputusan dan alasannya ada di ADR; cara kerjanya di [[HRIS - Compensation & Benefits]]; di sini hanya urutan kerja. Tiap task cukup jelas untuk `/start-task`; rencana per berkas dibuat di `/plan` masing-masing.

Tiga tahap. **Tahap 1 berdiri sendiri** (menghentikan hilangnya angka lama). Tahap 2 mengubah angka slip, jadi **tak di-deploy sebelum S5 terjawab**. Tahap 3 menyambung hulu.

Urutan: S1 → (S2, S3, S4 paralel) → S5 → S6 → S7 → (S8+S9, S10+S11, S12 paralel) → S13. Backend naik sebelum web/mobile. Lintas repo = issue induk + sub-issue per repo (`buat-sub-issue.ps1`).

## Tahap 1: riwayat dan jejak

- [ ] **S1 BE payroll: koleksi versi struktur gaji.** Versi utuh (komponen struktur tetap, dasar upah BPJS Kesehatan/Ketenagakerjaan, kepesertaan, PTKP, `company_id`), tanggal mulai berlaku saja, status `menunggu_persetujuan`/`terjadwal`/`berlaku`/`lewat`/`batal`, rujukan hulu (jenis + id), pencatat, penyetuju. `PUT /employee-salary/:employeeId` berubah jadi pembuat versi; `employee_salary` jadi proyeksi versi berlaku yang ditulis payroll saja (konsumen lama: `contract_pkwt_gaji.go`, `thr.go:34`, `impor_run_handlers.go:395`, `run_jenjang_koreksi.go:232` tak boleh patah). Cron harian idempoten `terjadwal` → `berlaku` (pola `mutasi_routes.go:350`). Gerbang: GP/TJ berubah tanpa konfirmasi dasar BPJS ditolak; komponen variabel (Bonus, Insentif, Kasbon, Lain-lain) ditolak masuk versi; versi yang dipakai run di atas draft tak bisa diubah; pengisi ≠ penyetuju; penyetuju = paket SPV HRD (ADR 0129). Endpoint internal untuk hulu: buat / geser tanggal / batalkan versi terjadwal berdasarkan rujukan hulu (S8, S10 memakainya). Dependensi: tidak ada. Uji: tanggal berakhir diturunkan benar (tanpa celah/tumpang-tindih), proyeksi berpindah saat cron, versi terkunci tak bisa diubah, satu uji lewat Fiber per rute, `bpjs_base` tanpa konfirmasi ditolak.
- [ ] **S2 Migrasi prod: versi #1 dari `employee_salary` yang ada.** Skrip cek/terapkan/balik + backup, **dijalankan manusia**. Tiap dokumen jadi versi #1 bersumber `migrasi`, berlaku sejak awal periode payroll pertama yang dihitung engine sesudah migrasi; `effective_date` lama (diukur 2026-10-01: 134 kosong, 45 = `2027-08-25`) tidak dipakai; Kasbon/komponen variabel dibuang dan dilaporkan (2026-10-01: 1 dokumen). Ukur ulang angka sebelum menjalankan. Dependensi: S1 ter-deploy. Verifikasi: jumlah versi = jumlah `employee_salary`, proyeksi identik dengan sebelum migrasi kecuali komponen variabel.
- [ ] **S3 BE payroll: impor sheet HRD lewat versi.** Penimpaan `SCRIPT-SHEET-SEP-20261001` (160 dokumen dalam satu jam, 2026-10-01) berasal dari skrip di luar engine: **temukan dulu skripnya** (`.task-plans/`, cari `SCRIPT-SHEET`) lalu ganti jalurnya jadi pembuatan versi bersumber `impor_sheet` yang melewati gerbang S1. Dependensi: S1. Uji: impor dua kali tak menggandakan versi (idempoten per berkas + karyawan + tanggal).
- [ ] **S4 FE payroll: isian versi, riwayat, persetujuan.** `EmployeeSalaryForm` (mode embedded) dipakai sebagai isian versi: tanggal mulai berlaku, rujukan hulu tampil baca-saja, konfirmasi dasar BPJS saat GP/TJ berubah. Register gaji menampilkan riwayat versi per karyawan (asal, tanggal, penyetuju) dan antrean versi menunggu persetujuan bagi SPV HRD. i18n dua locale. Dependensi: S1. Verifikasi: satu versi dibuat → disetujui → berlaku di DEV sebagai orang.

## Tahap 2: prorata per hari

- [ ] **S5 Konfirmasi HRD (non-kode, gerbang sebelum S6 di-deploy).** Tanyakan ke Manajer HRD: (a) pembagi prorata: hari kalender (asumsi ADR §7) / 30 tetap / hari kerja; (b) komponen mana yang biasa berubah per event (mis. TH/TM masa evaluasi vs kontrak); (c) kenapa Tunjangan Kehadiran hanya terisi untuk 1 dari 183 karyawan (2026-10-01), padahal potongan kehadiran dihitung darinya. Jawaban (a) yang berbeda dari asumsi wajib mengamandemen ADR §7. Dependensi: tidak ada (boleh dikerjakan sekarang).
- [ ] **S6 BE payroll: engine membaca versi per hari.** `computeRunLines` (`run_handlers.go:188-253`) membaca versi yang berlaku tiap hari periode, bukan seluruh `employee_salary`; batas versi termasuk `join_date` (payroll belum membacanya untuk run bulanan) dan tanggal efektif resign (merevisi `resign_filter.go:21-23` + ADR 0035). Tiap komponen struktur tetap = Σ nilai × hari / hari periode; tarif potongan kehadiran per hari dari versi hari itu; THR tetap aturannya sendiri. Slip satu baris per komponen + keterangan hari (field baru di `PayslipLine` atau metadata; putuskan di `/plan`). Dependensi: S1, S2; deploy sesudah S5. Uji: tabel kasus promosi / masuk / resign / dua perubahan dalam satu periode / tanpa perubahan (angka harus identik dengan engine lama). Verifikasi: **run pertama dibandingkan berdampingan dengan hitungan HRD** sebelum diajukan.
- [ ] **S7 FE + Mobile: tampilan slip prorata.** Keterangan hari pada baris yang diprorata di detail run web dan slip MyBharata (`payslip`). Periksa dulu apakah slip mobile merender baris generik; bila ya, mungkin cukup BE. Dependensi: S6.

## Tahap 3: hulu mengalir

- [ ] **S8 BE recruitment: offer dua set komponen.** Ganti `gaji_evaluasi`/`gaji_kontrak` dengan dua set struktur berbentuk sama dengan versi; `masa_evaluasi` teks bebas → `tanggal_akhir_evaluasi` (5 offer prod, semua Draft per 2026-10-01: isi ulang manual, tanpa migrasi). Total dihitung, tidak disimpan. Offer Accepted dibekukan. Saat `PUT /candidates/:id/link-employee` (`candidate_handlers.go:302-311`): kirim set evaluasi (berlaku = `join_date` karyawan) dan set kontrak (terjadwal = sehari sesudah akhir evaluasi) ke payroll lewat endpoint S1. Env baru `PAYROLL_MODULE_URL` di blok recruitment compose → `--force-recreate`. Dependensi: S1. Uji: link dua kali tak menggandakan versi; kegagalan payroll tidak membatalkan link tetapi tercatat dan bisa diulang.
- [ ] **S9 FE recruitment: form offer dua set + total.** `offer-form-dialog.tsx` memakai isian versi untuk dua set; surat/tampilan kandidat menampilkan total. i18n dua locale. Dependensi: S8.
- [ ] **S10 BE employee: movement dan kontrak membuat versi.** Pembuatan `employee_movement` (Promosi/Mutasi/Antar-Perusahaan) membawa usulan struktur dan membuat versi terjadwal ber-rujukan movement; edit tanggal movement terjadwal menggeser versinya; pembatalan membatalkannya. Perpanjangan kontrak dan PKWT→PKWTT membuat versi konfirmasi ber-rujukan kontrak. Wajib-isi per jenis sesuai tabel ADR §5 (Promosi: TJ; Antar-Perusahaan: badan usaha). Dependensi: S1. Uji: kontrol negatif bahwa membatalkan movement membatalkan versi; movement tanpa struktur gaji tetap sah (struktur tak berubah).
- [ ] **S11 FE mutasi + kontrak: isian versi di form.** `mutasi-form-modal.tsx` dan form Perpanjang di `contract-history-sheet.tsx` menyematkan isian versi (terisi dari versi berlaku); panel sebelum → sesudah di `mutasi-detail-sheet.tsx` ikut menampilkan perubahan struktur gaji (hanya bagi pemegang izin baca gaji). Dependensi: S10.
- [ ] **S12 BE+FE: keputusan kenaikan massal (berkala/UMK).** Satu keputusan berisi tanggal berlaku + daftar karyawan + GP baru (atau persentase), menerbitkan versi ber-rujukan keputusan untuk tiap orang, melewati persetujuan S1 sebagai satu paket. Dependensi: S1.
- [ ] **S13 BE payroll: peringatan SP II aktif.** Versi yang menaikkan struktur untuk karyawan ber-SP II aktif memunculkan peringatan, tidak menolak (Pasal 55 jo. 53). Periksa dulu di mana status SP II tersimpan dan apakah sudah ada di kode ([[HRIS - Disciplinary (Surat Peringatan)]]); bila belum ada, task ini menunggu. Dependensi: S1.

## Asumsi yang dipakai (koreksi di sini bila berubah)

1. Pembagi prorata = hari kalender periode (menunggu S5).
2. Seluruh komponen struktur tetap ikut diprorata, termasuk TH. **TM bergantung pada bip-erp#2431**: bila TM menjadi tarif harian × hari terjadwal, ia keluar dari struktur tetap (struktur tetap diturunkan dari master komponen, jadi tanpa ubah kode S1).
3. Penyetuju versi = Manajer HRD lewat paket SPV HRD, sampai ADR 0137 diputuskan.
4. Visibilitas mengikuti ADR 0129 dan 0089 (atasan tidak melihat).
5. Versi #1 hasil migrasi berlaku sejak awal periode pertama yang dihitung engine sesudah migrasi.

## Belum diputuskan

- Bentuk keterangan hari di slip (S6 `/plan`).
- Kebijakan komponen per event (S5 b).
- Rentang gaji per jenjang: sengaja di luar ADR 0148.
