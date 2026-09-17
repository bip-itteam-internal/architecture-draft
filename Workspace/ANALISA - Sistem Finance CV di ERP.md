**Status**: 🟡 Daftar task dari `/analisa-kebutuhan` 2026-09-15. Keputusannya di [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]], cara kerjanya di [[Finance - Buku Besar CV]]; dok ini papan kerja, bukan arsitektur. Coret item begitu PR-nya merge, dan pindahkan keadaannya ke dok domain lewat `/sync-docs`, jangan menumpuk status di sini.

## Kebutuhan yang dijawab

Pembayaran CV dicatat berkali-kali oleh Junior Accountant (voucher BKK di FINCON, AppSheet, Kopra, jurnal, arsip kertas), dan buku 40 CV berjalan di aplikasi di luar ERP. Manajemen (2026-09-15) memprioritaskan pengurangan kerja manual, memutuskan transfer tetap dikerjakan pemegang CV, dan menyetujui buku besar 40 CV dibangun di ERP dengan FINCON sebagai spesifikasi; PT tetap di Accurate. Bahan survei beserta analisa awal (2026-09-15) dan lanjutannya (2026-09-17) disimpan di luar vault (`.task-plans/2026-09-14-survei-alur-kerja-finance/` di workspace erp) karena memuat jawaban bernama; jangan disalin ke vault. Pola prosesnya yang aman dibagikan sudah naik ke [[Finance - FAT Persona]] (butir bertanda *survei 2026-09*), dan dampaknya ke task ini di § Masukan survei lanjutan.

## Prasyarat non-kode

- **Persetujuan SPV FAT dan IT** atas ADR 0096. Sebelum itu T1 dan T2 boleh berjalan karena tidak menyentuh buku besar; T3 dan seterusnya menunggu.
- **Jawaban SPV FAT** untuk TBD 1, 2, dan 8 di dok domain: makna rekening 1299xx di buku PT, hutang supplier CV, pembagian pemegang CV.
- **Ekspor data FINCON** dari pemiliknya (fitur backup JSON atau XLSX) untuk T5. Kredensial yang tertulis di repo FINCON tidak dipakai.
- **Paket izin** Junior Accountant, Account Payable, dan Tax yang hari ini kosong di prod, oleh IT. Survei lanjutan menguatkan ini: pembayaran rekening PT dan pekerjaan pajak masih dikerjakan sepenuhnya di luar ERP walau alurnya sudah ada di kode. Pemegang CV butuh **dua** paket sekaligus, "Budget: Transfer Kas CV" dan "Buku Besar CV: Pemegang"; satu saja membuat antrean transfernya tidak terlihat.
- **Data penugasan CV** di dev dan prod masih nol (diukur 2026-09-17): Supervisor FAT menyemai 40 CV dan menugaskan pemegangnya sebelum T2 bisa dipakai siapa pun.
- **Data volume**: ekspor AppSheet tiga bulan (jumlah BKK per jenis per CV) dan jumlah transaksi Kopra per rekening, untuk ukuran antrean T2.
- **Contoh berkas mutasi rekening** untuk T9.

## Urutan deploy yang mengikat

- Katalog izin dan cakupan CV hidup di `shared-library`: pre-push mem-build seluruh service; employee-service, procurement, dan finance-service naik bersama. BE sebelum FE.
- Kategori inbox baru (antrean transfer pemegang CV): service pengirim dan notification-service naik bersama, lalu picu satu notifikasi sungguhan.
- Env baru (saklar posting jurnal otomatis ke buku CV, bawaan mati): `--force-recreate`.
- Rute finance-service didaftarkan di akar modul karena gateway membuang prefix `/api/finance`.
- Prod dijalankan manusia (skill `deploy-bip-erp` §0); migrasi dan impor FINCON lewat skrip ber-dry-run dan backup.
- `ACCURATE_KAS_PUSH` tidak dinyalakan bersama rilis ini.

## Task

### ~~T1. Master entitas CV, penugasan pemegang CV, dan cakupan akses per CV~~
- ✅ **Merge 2026-09-16**: bip-erp #1905, erp-frontend #1592. Keadaannya di [[Finance - Buku Besar CV]].
- **Repo**: bip-erp `services/finance/` (baru), `shared-library/common/` (katalog izin dan cakupan CV); erp-frontend layar master di `finance/` (baru), i18n id dan en.
- **Isi**: master `CV01` sampai `CV40` dengan rujukan `payroll_company`, rekening Accurate 1299xx (dibaca lewat integration), dan nama resmi; seed dari pencocokan nama (38 cocok persis, 2 beda singkatan ditetapkan manusia, karakter tak terlihat dibersihkan); pemindai drift terhadap payroll dan rekening Accurate; penugasan pemegang CV per karyawan; izin buku besar CV dengan cakupan CV yang menyempitkan, ditegakkan server.
- **Test**: fungsi pencocokan nama dengan kontrol negatif (beda singkatan tidak dianggap sama tanpa penetapan); gerbang cakupan lewat Fiber (403 untuk CV di luar penugasan) dengan kontrol positif.
- **Verifikasi**: baca prod sesudah seed, 40 CV terpetakan ke 40 badan usaha payroll dan 40 rekening 1299xx; di dev lewat gateway, akun uji Junior Accountant hanya melihat CV tugasnya.
- **Dependensi**: tidak ada.

### ~~T2. Jalur A: pembayaran keluar per CV lewat Pengajuan Barang~~
- ✅ **Merge 2026-09-16 dan 17**: bip-erp #1926 dan #1929, erp-frontend #1614 (menu dikelompokkan di #1617). Sisa di luar kode: data penugasan dan paket izin (§ Prasyarat non-kode), lalu satu perjalanan utuh sebagai orang di dev yang belum dijalankan.
- **Repo**: bip-erp `services/procurement/` (`pengajuan_barang*.go`, `pembayaran.go`, `bukti_transfer*.go`); erp-frontend `features/procurement/pengajuan-barang/`, `app/(main)/finance/ap/`.
- **Isi**: kode CV tujuan pada pengajuan bersumber dana rekening CV, divalidasi terhadap `sumber_dana` 1299xx; tahap transfer untuk sumber dana CV ditindak pemegang CV (irisan izin transfer dan penugasan T1), sumber dana PT tetap Account Payable; antrean "perlu ditransfer" per pemegang CV dengan notifikasi; unggah bukti oleh pemegang CV; review bukti tetap Senior Accountant. Jurnal ke Accurate PT tidak berubah.
- **Test**: antrean dan gerbang aksi memakai fungsi yang sama (kontrol negatif: pemegang CV lain ditolak di keduanya); pengajuan bersumber dana PT tidak masuk antrean Junior Accountant.
- **Verifikasi**: satu perjalanan utuh di dev sebagai pemohon Marketing, SPV FAT, Junior Accountant pemegang CV (transfer dan unggah bukti), lalu Senior Accountant; bandingkan bentuk respons, bukan status.
- **Dependensi**: T1.

### T3. Jalur B: inti buku besar CV
- **Repo**: bip-erp `services/finance/` (baru); erp-frontend `app/(main)/finance/buku-besar-cv/`, `features/finance/buku-besar-cv/` (baru), i18n id dan en.
- **Isi**: COA (seed COA bawaan FINCON), lima jenis jurnal dan saldo awal, aturan ADR 0096 §4 (satu dokumen atomik, nominal bilangan bulat sen, penghitung voucher ber-index unik, jurnal balik, kunci periode, jejak sumber, pemeriksaan Senior Accountant), buku besar per akun, neraca saldo, register aset dan penyusutan; tabel memakai `MainTable` dengan ekspor Excel bawaannya.
- **Test**: fungsi murni validasi jurnal dengan kontrol negatif per aturan; dua penerbitan voucher bersamaan tidak menghasilkan nomor sama; jalur galat handler lewat Fiber.
- **Verifikasi**: di dev, jurnal manual dibuat, diperiksa, terposting, lalu tampil di buku besar dan neraca saldo; jurnal ke periode terkunci ditolak.
- **Dependensi**: T1, persetujuan ADR 0096.

### T4. Laporan keuangan dan konsolidasi 40 CV
- **Repo**: bip-erp `services/finance/`; erp-frontend `features/finance/buku-besar-cv/`.
- **Isi**: laba rugi bertingkat, neraca kumulatif, arus kas metode langsung, perubahan ekuitas, laporan bulanan 12 kolom, rasio; kertas kerja konsolidasi dengan eliminasi berpasangan entitas.
- **Test**: rumus sebagai fungsi murni dengan dataset pembanding dari ekspor FINCON; test regresi untuk tiap aturan rawan FINCON (arus kas akun berawalan 12, neraca konsolidasi kumulatif, eliminasi laba rugi ke Laba Tahun Berjalan, baris eliminasi ke akun di luar COA ditolak).
- **Verifikasi**: laporan per CV satu periode uji identik dengan FINCON (toleransi di bawah Rp1), kecuali selisih yang dijelaskan perbaikan aturan rawan.
- **Dependensi**: T3.

### T5. Migrasi data FINCON dan jalan paralel satu siklus tutup buku
- **Repo**: bip-erp `services/finance/` (importer); skrip `.ps1` di `.task-plans/` untuk prod.
- **Isi**: importer idempoten berkunci id FINCON untuk transaksi, eliminasi, COA, perusahaan, dan aset dari ekspor FINCON; laporan selisih ERP vs FINCON per CV per bulan; impor berkala selama satu siklus; keputusan cutover dan FINCON baca saja bersama SPV FAT dan pemilik FINCON.
- **Verifikasi**: selisih nol atau terjelaskan untuk seluruh CV pada siklus paralel; skrip prod ber-dry-run dan backup, dijalankan manusia.
- **Dependensi**: T4, ekspor FINCON.

### T6. Jurnal otomatis buku CV dari pembayaran dan kas kecil
- **Repo**: bip-erp `services/procurement/`, `services/finance/`.
- **Isi**: pembayaran berbukti dari T2 dan alokasi kas kecil per CV membentuk jurnal di buku CV dengan jejak dokumen asal, idempoten per dokumen, di balik saklar bawaan mati.
- **Test**: dokumen yang sama diproses dua kali menghasilkan satu jurnal; dokumen tanpa CV ditahan dengan sebab tertulis.
- **Verifikasi**: satu pengajuan IKLAN di dev menghasilkan jurnal BKK bernomor unik di buku CV tanpa input manual.
- **Dependensi**: T2, T5.

### T7. Payroll per badan usaha: daftar bayar, rekap iuran BPJS TK, jurnal gaji
- **Repo**: bip-erp `services/payroll/`, `services/finance/`.
- **Isi**: daftar transfer gaji per badan usaha (rekening karyawan dari employee-service), rekap iuran BPJS TK sisi karyawan dan perusahaan per badan usaha, jurnal gaji otomatis ke buku CV; melengkapi rekening dan NPWP badan usaha yang hari ini kosong.
- **Aturan bisnis**: angka potongan dan iuran mengikuti perhitungan payroll yang ada; bila menyentuh potongan, buka `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` lebih dulu.
- **Verifikasi**: rekap satu run dev per badan usaha sama dengan jumlah baris run; jurnal gaji seimbang.
- **Dependensi**: T1 untuk daftar bayar dan rekap; T5 untuk jurnalnya.

### T8. Penjualan marketplace per CV
- **Repo**: bip-erp `services/integration/`, `services/finance/`.
- **Isi**: pemetaan 56 toko ke kode CV di master T1; jurnal per CV dari data yang sudah dikirim ke Accurate (penjualan, potongan platform, ongkir, retur, penerimaan) dan dari penarikan saldo Shopee, TikTok, dan Lazada; tunduk pada §Gerbang kolom di [[Finance - Buku Besar CV]]; hutang CV ke PT menunggu jawaban TBD 2.
- **Test**: identitas jurnal seimbang per toko per hari; kontrol negatif kolom bagian (mis. `TotalShippingRebate`) tidak ikut dijumlah.
- **Dependensi**: T1, T5, jawaban TBD 2.

### T9. Impor mutasi rekening dan rekonsiliasi
- **Repo**: bip-erp `services/finance/`; erp-frontend `features/finance/buku-besar-cv/`.
- **Isi**: impor berkas mutasi per rekening CV, pencocokan dengan jurnal kas, jurnal beban adm dan bunga bank; rekonsiliasi bulanan kas buku CV terhadap rekening 1299xx di Accurate PT.
- **Dependensi**: T5, jawaban TBD 1 dan 3, contoh berkas mutasi.

### T10. Tutup buku, KPI Accounting CV, pensiun FINCON, sinkron keputusan
- **Isi**: daftar periksa tutup buku per CV dan peran pengunci periode; pemetaan baris KPI Accounting CV (bobot 0,30, tenggat tanggal 4); kartu dashboard posisi Accounting CV dan Senior Accountant yang kini belum ada; FINCON dipensiunkan; ADR 0096 ke ✅ dengan catatan, amandemen ADR 0001, ADR 0068 ditandai Superseded, baris identitas CV di [[REF - Kepemilikan Data]] pindah dari §Duplikasi ke §Peta.
- **Dependensi**: T4 sampai T9 sesuai cakupan yang disetujui.

## Masukan survei lanjutan (2026-09-17)

Jawaban tambahan datang dari sisi yang pada analisa awal masih kosong: pemeriksa, pembayar, dan AR. Sisi persetujuan belum terwakili, jadi **jangan menyimpulkan apa pun tentang antrean persetujuan** dari survei ini. Pola prosesnya di [[Finance - FAT Persona]]; di sini hanya dampaknya ke task.

**Dampak ke task yang sudah ada:**

| Task | Temuan | Yang berubah |
|---|---|---|
| T2 | Pembayaran rekening PT dan kas CV masih dikerjakan di luar ERP walau alurnya sudah ada di kode; permintaan "otomasi proses pengajuan" juga sudah dijawab Pengajuan Barang | Nilai T2 bergantung pada **adopsi**: paket izin dan data penugasan (§ Prasyarat non-kode). Tidak ada kode tambahan yang menyelesaikannya. |
| T8 | Rekap penarikan saldo per CV sudah dikerjakan lewat alat web terpisah di luar ERP karena data sistem belum sesuai | Telusuri alat itu (isi, aturan, pemilik) sebelum `/start-task T8`, supaya T8 tidak membangun tandingannya dari nol. |
| T9 | Beban terbesar lintas jabatan adalah rekonsiliasi **kas toko marketplace** (saldo seller center terhadap Accurate), berulang karena tiap perbaikan menggeser saldo, dan terjadi di PT maupun CV. Fitur rekonsiliasi yang ada di ERP disebut belum cocok formatnya | Prioritas T9 **naik**. Lingkup T9 hari ini hanya mutasi rekening CV; apakah kas toko masuk T9, jadi task sendiri, atau di luar ADR 0096 diputuskan saat `/start-task T9`. Tambah prasyarat: contoh format kerja rekonsiliasi yang dipakai sekarang, di samping contoh berkas mutasi. |

Kandidat di luar ADR 0096 yang muncul dari survei ini dipetakan bersama kebutuhan lain di [[Finance - Proses Bisnis dan Kebutuhan Sistem]].

**Langkah berikut untuk survei:** tunggu jawaban sisi persetujuan; wawancara singkat untuk alat web rekap penarikan CV dan pemeriksaan rekap gaji; ambil data objektif (rekap retur manual, jumlah putaran rekonsiliasi kas toko per bulan). Durasi isian responden tidak dipakai.

## Peta kebutuhan sistem Finance

Sudah naik kelas ke dok domain [[Finance - Proses Bisnis dan Kebutuhan Sistem]] (2026-09-17): sebelas proses bisnis Finance, untuk tiap proses alur hari ini, yang sudah ada di ERP, alur target, celah kelompok A/B/C, kontrol wajib, dan ukuran efisiensi; ditambah urutan pengerjaan, keputusan yang dibutuhkan, dan yang sengaja tidak dibangun. Jangan salin ulang ke sini; papan ini hanya melacak task T1 sampai T10.

## Task pertama

`/start-task T1 Master entitas CV, penugasan pemegang CV, dan cakupan akses per CV (ADR 0096)`

T1 dan T2 sudah merge. T3 dan seterusnya menunggu persetujuan ADR 0096 (§ Prasyarat non-kode).
