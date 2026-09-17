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

Kandidat di luar ADR 0096 yang muncul dari survei ini dipetakan bersama kebutuhan lain di § Peta kebutuhan sistem Finance.

**Langkah berikut untuk survei:** tunggu jawaban sisi persetujuan; wawancara singkat untuk alat web rekap penarikan CV dan pemeriksaan rekap gaji; ambil data objektif (rekap retur manual, jumlah putaran rekonsiliasi kas toko per bulan). Durasi isian responden tidak dipakai.

## Peta kebutuhan sistem Finance (2026-09-17)

Disusun dari survei alur kerja Finance, pembacaan kode `origin/main` 2026-09-17, dan [[REF - Kepemilikan Data]]. Urutannya mengikat: **pakai yang sudah ada, lalu perbaiki yang sudah ada, baru bangun yang belum ada**. Keadaan bertanggal di bawah wajib diukur ulang sebelum dipakai memutuskan.

### A. Sudah ada, tinggal dipakai (tanpa kode baru)

| Sistem | Pemakai di Finance | Syarat supaya jalan | Departemen lain yang terlibat |
|---|---|---|---|
| Pengajuan Barang sampai bukti transfer dan pembayaran ke Accurate, termasuk cabang kas CV dari T2 ([[Microservices - Procurement Service]]) | AP, Junior Accountant, Cost Control, Supervisor FAT | Paket izin; data 40 CV dan pemegangnya; keputusan dokumen pengajuan menggantikan BKK dan AppSheet; ambang Direktur diatur; saklar jurnal kas ke Accurate dinyalakan sesudah diuji. Per 2026-09-12 prod baru berisi 1 pengajuan dan 0 dokumen pembayaran | Marketing, GA, Procurement sebagai pemohon |
| Tax Control: kewajiban per masa, pengingat, unggah BPE ([[API - Finance Service]]) | Tax | Master jenis pajak diisi, paket `finance_pajak` dipasang | IT |
| Payroll per badan usaha ([[Microservices - Payroll Service]]) | Cost Control dan Senior Accountant (cek gaji), Junior Accountant | HR memakainya sebagai sumber gaji, sehingga pengecekan pindah dari hard file ke data absen dan izin di ERP. Per akhir Agustus 2026 baru 2 run di prod | HR |
| Gerbang scan retur gudang ([[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]]) | AR retur, AR piutang, Senior Accountant | Retur baru dibukukan ke Accurate sesudah gudang men-scan barangnya, jadi disiplin scan menentukan antrean Finance. Per 2026-08-06: 908 baris PENDING, 900 menunggu scan ([[Microservices - Integration Service]]) | Gudang |

### B. Sudah ada, perlu diperbaiki atau dilengkapi

| Sistem | Masalah | Pemakai | Bukti di kode |
|---|---|---|---|
| Rekonsiliasi kas toko | Formatnya belum cocok dengan kerja rekonsiliasi; retur yang lolos sinkron diunggah manual (ukur dulu besar celahnya di prod, rekap yang dikirim pengguna ke IT adalah sumber volumenya); sebagian income masih diinput manual (kanal mana: TBD) | Senior Accountant, AR | Layar tiga tab (rekap, rincian, akumulasi) di `erp-frontend/src/app/(main)/integration-accurate/rekonsiliasi/page.tsx` |
| Pengajuan tersambung ke pos anggaran | Pengajuan tidak membawa pos anggaran yang dibebaninya, jadi pengecekan anggaran oleh Cost Control manual | Cost Control, Supervisor FAT | Metrik "Expense di luar anggaran" berstatus `belum`, dan kodenya sendiri menyebut yang belum ada adalah pengajuan beserta pos anggaran yang dibebankannya (`erp-frontend/src/features/finance/posisi/data/ap.ts:64-71`) |
| Varians anggaran | Hanya total dan cacah pos; tak bisa ditelusuri ke transaksi pembentuk realisasinya | Cost Control | Rincian di persona Cost Control, [[Finance - FAT Persona]] |
| Kotak persetujuan Supervisor FAT | Pengajuan barang yang menunggu Supervisor FAT tidak tampil di kotak persetujuan dashboard | Supervisor FAT | `bip-erp/services/integration/internal/interface/http/persetujuan_handler.go:16-19` |

### C. Belum ada, perlu dibangun

| Sistem | Kerja manual yang digantikan | Pemakai | Status |
|---|---|---|---|
| Payroll ke daftar transfer bank, rekap iuran BPJS per badan usaha, jurnal gaji | Ketik ulang gaji dan BPJS ke Kopra dan jurnal | Junior Accountant, Cost Control, Senior Accountant | T7 |
| Impor mutasi rekening dan rekonsiliasi bank | Rekonsiliasi kas/bank harian, cek mutasi AP | Junior Accountant, AP, Senior Accountant | T9. Lingkupnya kini rekening CV; rekening PT (dibukukan di Accurate) masuk atau tidak perlu diputuskan |
| Pemetaan toko ke CV, penjualan dan penarikan per CV | Alat web rekap penarikan, olah ulang penjualan per CV, omzet untuk PPh final | AR piutang, Junior Accountant, Tax | T8 |
| Buku besar CV, laporan dan konsolidasi, migrasi FINCON, jurnal otomatis | FINCON di luar ERP, jurnal CV manual | Junior Accountant, Senior Accountant, Tax | T3 sampai T6, menunggu persetujuan ADR 0096 |
| Daftar periksa tutup buku per entitas | Pengendalian tutup buku manual | Senior Accountant | T10 |
| **(baru)** Pertanggungjawaban dana kegiatan: uang muka, laporan, bukti, lalu sisa dikembalikan atau reimburse | Pemeriksaan realisasi dana kegiatan oleh Cost Control | Cost Control | Belum jadi task. `git grep` atas `bip-erp/services` 2026-09-17 tidak menemukan alur ini. Butuh `/analisa-kebutuhan` |
| **(baru)** Costing HPP produk: formula, harga bahan, kapasitas produksi, persetujuan | Templat Excel dan WhatsApp | AP | Belum jadi task dan belum diputuskan masuk ERP. Sebagian bahannya sudah ada: BOM/formula di [[Manufacture - Stock & Material Management]]; ERP kini hanya mengukur hasilnya lewat kartu "Costing HPP valid" (`ap.ts:72-78`). Melibatkan Procurement, PPIC, dan APJ; butuh `/analisa-kebutuhan` |

### D. Sengaja tidak dibangun

- **Buku PT tetap di Accurate** ([[ADR - 0001 Akuntansi via Accurate]]); ERP mengirim ke sana, bukan menggantikannya.
- **Coretax dan e-billing tetap di DJP.** Yang dibutuhkan Tax adalah data acuan dari satu sumber, bukan aplikasi pajak baru.
- **Transfer uang tetap di internet banking.** ERP mencatat, menyetujui, dan menyimpan bukti.
- **BKK kertas dan AppSheet tidak dibuatkan versi ERP.** Dokumen pengajuan menggantikannya.
- **Tidak ada basis data kerja AR baru.** Yang dibutuhkan adalah data marketplace di ERP yang bisa dipercaya untuk rekonsiliasi.

### Kebutuhan per posisi

| Posisi | Kebutuhan utama |
|---|---|
| Junior Accountant | Pengajuan Barang (A), payroll ke bank (C), mutasi bank (C), penjualan per CV (C), buku besar CV (C) |
| Account Payable | Pengajuan Barang (A), mutasi bank (C), costing HPP (C, perlu analisa) |
| AR Staff | Rekonsiliasi kas toko (B), scan retur gudang (A), penarikan per CV (C) |
| Senior Accountant | Rekonsiliasi kas toko (B), buku besar CV (C), daftar periksa tutup buku (C) |
| Cost Control | Pengajuan tersambung anggaran (B), varians yang bisa ditelusuri (B), cek gaji dari payroll ERP (A), pertanggungjawaban dana (C) |
| Tax | Tax Control aktif (A), omzet per CV dan data pembelian/pembayaran dari satu sumber (C) |
| Supervisor FAT | Kotak persetujuan terpusat (B) |

### Urutan dan keputusan yang dibutuhkan

1. **Kelompok A**: paling murah dan berdampak terbesar, tetapi butuh keputusan manajemen serta keterlibatan HR, gudang, dan pemohon.
2. **Kelompok B**: perbaikan kecil yang langsung terasa AR, Senior Accountant, dan Cost Control.
3. **T7 dan T9**, karena tidak menunggu ADR 0096.
4. **T8, lalu T3 sampai T6** sesudah ADR 0096 disetujui.

Keputusan Supervisor FAT atau manajemen yang dibutuhkan sebelum langkah 1: persetujuan ADR 0096; dokumen pengajuan menggantikan BKK dan AppSheet atau tidak; pemisahan pembuat, pemeriksa, dan penyetuju; hutang supplier CV adalah hutang ke PT atau bukan (TBD 2 di [[Finance - Buku Besar CV]]); pemeriksaan rekap gaji oleh dua jabatan dipertahankan atau tidak.

Catatan: menunggu perbaikan data atau sistem dari IT (1 sampai 5 hari per kasus, disebut AR dan Senior Accountant) bukan kebutuhan sistem Finance. Bila perlu diukur, sumbernya tiket IT, bukan survei.

## Task pertama

`/start-task T1 Master entitas CV, penugasan pemegang CV, dan cakupan akses per CV (ADR 0096)`

T1 dan T2 sudah merge. T3 dan seterusnya menunggu persetujuan ADR 0096 (§ Prasyarat non-kode).
