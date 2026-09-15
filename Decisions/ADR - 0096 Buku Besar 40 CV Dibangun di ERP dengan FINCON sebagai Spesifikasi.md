## Untuk Manajemen

Pembukuan 40 CV grup akan dikerjakan **di dalam ERP**, memakai aplikasi buku besar CV yang kini berjalan terpisah (FINCON) sebagai contoh isi dan sumber data lama; pembukuan PT tetap di Accurate. Tujuan pertamanya mengurangi ketik ulang di Finance, karena hari ini satu pembayaran CV dicatat berulang di voucher, AppSheet, internet banking, dan jurnal. **Yang berubah di layar, bertahap:** (1) pengajuan pembayaran yang memakai rekening CV masuk ke antrean Junior Accountant pemegang CV itu, lengkap dengan persetujuan dan unggah bukti transfer, tanpa WhatsApp, Excel, dan arsip AppSheet; (2) menu Finance memuat buku besar, laporan keuangan per CV, dan konsolidasi 40 CV, dijalankan berdampingan dengan aplikasi lama selama satu siklus tutup buku sebelum aplikasi lama dijadikan baca saja; (3) jurnal buku CV terbentuk otomatis dari pembayaran, kas kecil, gaji dan BPJS, serta penjualan marketplace; (4) mutasi rekening CV diimpor dan dicocokkan, dan buku tiap CV dikunci per bulan.

**Terdampak**: Junior Accountant pemegang CV, Senior Accountant (pemeriksa jurnal), SPV FAT (penyetuju, dan pemutus keputusan ini bersama IT), Tax, Account Payable, pemohon pembayaran di Marketing, HR, dan GA, serta Direktur sebagai pembaca laporan. **Yang TIDAK dijanjikan**: PT tidak pindah dari Accurate; transfer uang tetap dikerjakan orang di bank karena tidak ada koneksi API bank; pelaporan ke Coretax tetap di luar ERP; konsolidasi tahap pertama hanya 40 CV tanpa PT; data lama baru bisa dipindah setelah pemilik aplikasi lama menyerahkan ekspornya. **Besaran kerja**: besar dan bertahap, sepuluh task; antrean pembayaran per CV berukuran sedang dan bisa berjalan lebih dulu, buku besar setara aplikasi lama berukuran besar, dan tiap otomasi sesudahnya berukuran sedang.

## Deskripsi

*Menjawab [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]] dengan opsi keempat yang tidak ada di sana: buku besar dan konsolidasi 40 CV dibangun di dalam bip-erp dengan [[APP - Buku Besar Konsolidasi CV FINCON]] sebagai spesifikasi dan sumber migrasi, sementara PT tetap dibukukan di Accurate. Mengusulkan amandemen [[ADR - 0001 Akuntansi via Accurate]] khusus lapisan CV. Cara kerjanya di [[Finance - Buku Besar CV]].*

- **Status**: 🟡 **Diusulkan**, arah disetujui lewat `/analisa-kebutuhan` 2026-09-15, kode belum ada. Berlaku setelah disetujui SPV FAT dan IT, pemutus yang ditetapkan ADR 0068.
- **Path di repo**:
  - `bip-erp/services/finance/` modul buku besar CV: master entitas, COA, jurnal, laporan, konsolidasi (baru)
  - `bip-erp/shared-library/common/` katalog izin buku besar CV dan cakupan per CV (baru)
  - `bip-erp/services/procurement/pengajuan_barang*.go`, `pembayaran.go`, `bukti_transfer*.go` (CV tujuan, antrean transfer per pemegang CV)
  - `bip-erp/services/payroll/` daftar bayar dan rekap iuran per badan usaha (baru)
  - `bip-erp/services/integration/` pemetaan toko ke CV dan jurnal penjualan per CV (baru)
  - `erp-frontend/src/app/(main)/finance/buku-besar-cv/` (baru) · `erp-frontend/src/features/finance/buku-besar-cv/` (baru)
- **Tanggal**: 2026-09-15

## Context

1. **Keputusan yang ditantang.** [[ADR - 0001 Akuntansi via Accurate]] (✅) melarang bip-erp membangun buku besar double-entry sendiri dan belum dicabut. Sejak 2026-08-05 pembukuan 40 CV berjalan di aplikasi di luar ERP dan di luar Accurate. ADR 0068 mencatat keadaan itu beserta tiga opsi yang belum dipilih. ⚠️ ADR 0068 masih 🟡 Proposed: yang dipakai di sini hanya bagian faktanya (sistemnya berjalan, entitasnya sama dengan payroll dan Accurate, celah konsolidasi nyata), bukan arahnya.
2. **Kebutuhan dari manajemen (2026-09-15).** Prioritas pertama mengurangi kerja manual Finance. Transfer pembayaran tetap dikerjakan Junior Accountant pemegang CV, tidak dipusatkan ke Account Payable.
3. **Kerja manual yang terukur.** Survei alur kerja Finance lewat Form Builder (terbit 2026-09-14; per 2026-09-15 dijawab 9 dari 16 pegawai Finance berakun aktif, tujuh di antaranya Junior Accountant):
   - satu pembayaran CV dicatat 4 sampai 5 kali: voucher BKK di aplikasi buku besar CV, AppSheet, Kopra, jurnal, arsip kertas;
   - jadwal harian tujuh Junior Accountant: pembayaran (buat BKK, input bank) 34%, jurnal 22%, tarik dan hitung data marketplace 17%, arsip 15%, rekonsiliasi kas/bank 11%;
   - persetujuan SPV disebut sebagai kendala untuk gaji, iklan, pajak, hutang supplier, dan BPJS TK; data penarikan marketplace yang telat disebut enam orang.

   Angka jam berasal dari isian sendiri; dua pasang jawaban tersalin dan durasinya belum dikonfirmasi wawancara.
4. **FINCON cukup kecil untuk dijadikan spesifikasi, tetapi kodenya tidak memenuhi syarat untuk dipindahkan** (repo `consolidated-accounting-app`, `main` lokal 2026-08-28; `origin/main` 9 commit lebih maju per 2026-09-08):
   - lima tabel: `transactions` (baris jurnal dalam JSON), `eliminations` (tanpa entitas), `coa` (satu COA bersama, sekitar 66 akun bawaan), `companies` (`CV01` sampai `CV40`), `assets`;
   - Next.js langsung ke Supabase dari peramban, tanpa backend dan tanpa test; pembagian CV per akun hanya ditegakkan di klien;
   - aturan yang terbukti rawan dan wajib diperbaiki saat dibangun ulang, bukan disalin: arus kas menggolongkan akun berawalan 12 sebagai investasi; neraca konsolidasi dihitung dari transaksi yang tersaring tanggal mulai sehingga tidak kumulatif (`accounting.js` `calculateConsolidatedData`); eliminasi akun laba rugi tidak mengalir ke Laba Tahun Berjalan; baris eliminasi yang akunnya tak ada di COA diabaikan diam-diam, termasuk baris bawaan form eliminasi; nomor voucher dihitung dari jumlah transaksi sebulan sehingga tidak unik; impor mode ganti menghapus transaksi semua CV.
5. **Yang sudah ada di ERP** (`origin/main` 2026-09-15):
   - Pengajuan Barang lima tipe dengan rantai persetujuan sampai tahap transfer AP dan review bukti; jurnal tipe uang ke Accurate lewat outbox di balik `ACCURATE_KAS_PUSH` yang mati kecuali bernilai `true`. CV hanya tersirat dari `sumber_dana` (rekening PT 1298xx atau CV 1299xx). Prod 2026-09-15: 1 pengajuan, 0 pembayaran.
   - Kas kecil mengalokasikan beban per CV sebagai satu Journal Voucher per CV ke Accurate; prod 69 transaksi.
   - Accurate tersambung sebagai **satu database** ([[ADR - 0014 Accurate Token DB-backed via OAuth]]); CV di sana tampil sebagai rekening bank anak COA 1299, dan bagan akunnya bisa dibaca lewat integration. Probe entitas di procurement menanyakan apakah 40 CV satu database, 40 database, atau tidak dibukukan di Accurate, tetapi jawabannya hanya ditulis ke log.
   - Faktur, penerimaan, dan retur marketplace dikirim ke Accurate per toko; jurnal penarikan saldo hanya untuk Lazada.
   - Payroll menggaji per badan usaha: `payroll_company` 41 dokumen (1 PT + 40 CV), satu run terbit.
6. **Yang belum ada di mana pun** (dibuktikan `git grep` atas `origin/main` 2026-09-15): model buku besar, COA, atau konsolidasi milik ERP (temuan hanya passthrough dan probe endpoint Accurate); cakupan akses per CV (jangkauan izin hanya `own`, `division`, `all` atas departemen); ekspor transfer gaji, rekap iuran BPJS per badan usaha, dan jurnal gaji; klien bank atau impor mutasi rekening; pemetaan toko ke CV.
7. **Identitas CV hidup di banyak tempat tanpa kunci bersama** (prod 2026-09-15): `payroll_company` (rekening dan NPWP kosong semua), rekening Accurate 1299xx, `companies` FINCON, katalog cabang "(CV)" procurement. 38 dari 40 nama CV cocok persis antara payroll dan rekening Accurate, dua sisanya beda singkatan, dan satu nama di Accurate diawali karakter tak terlihat. 56 toko di `accurate_shops` tidak punya field CV; `bank_account_no` mereka berupa kode 6 digit yang tidak cocok dengan nomor maupun ID rekening Accurate.
8. **Batas penyimpanan.** MongoDB prod finance, procurement, integration, dan payroll berjalan standalone, tanpa replica set, sehingga transaksi multi-dokumen tidak tersedia.

**Kenapa bukan opsi di ADR 0068:**

- **A, CV di Accurate**: integrasi ERP hanya mengenal satu database dan jalur baca akuntansinya buta entitas; 40 database berarti integrasi multi-database dan biaya lisensi (TBD); input berpindah ke Accurate, tidak hilang; konsolidasi tetap dibangun dari nol.
- **B, lapisan konsolidasi di atas Accurate**: mengandaikan saldo per CV di Accurate, padahal CV di sana hanya rekening di satu database.
- **C, FINCON dipagari**: dua platform permanen di luar gateway dan RBAC ERP; otomasi dari ERP harus menyeberang ke aplikasi tanpa backend; cakupan per CV dibangun dua kali.

## Decision

### 1. Buku besar 40 CV milik ERP, PT tetap di Accurate

Buku besar, bagan akun, jurnal, laporan keuangan, dan konsolidasi **lapisan 40 CV** dimiliki finance-service. Pembukuan PT tetap domain Accurate. [[ADR - 0001 Akuntansi via Accurate]] diusulkan **diamandemen, bukan dicabut**: larangannya tetap berlaku untuk PT dan untuk entitas lain di luar 40 CV. FINCON dipakai sebagai **spesifikasi dan sumber migrasi**; kodenya tidak dipindahkan.

### 2. Satu identitas CV

finance-service memegang master entitas CV berkode `CV01` sampai `CV40` (mengikuti FINCON), dengan rujukan ke badan usaha payroll, rekening Accurate 1299xx, dan nama resmi. Konsumen lain merujuk kodenya. Salinan yang sudah ada tidak diketik ulang; kecocokannya dijaga pemindai drift, sesuai syarat salinan sah di [[REF - Kepemilikan Data]]. Toko marketplace dipetakan ke kode CV di master yang sama. Nama yang tidak cocok persis ditetapkan manusia, tidak dicocokkan otomatis.

### 3. Cakupan akses per CV ditegakkan server

Penugasan pemegang CV disimpan **per karyawan**, menggantikan akun bersama per kelompok CV di FINCON. Izin buku besar CV diberi dimensi cakupan CV: Junior Accountant menulis hanya CV yang ditugaskan; Senior Accountant, SPV FAT, Tax, dan Direktur membaca semua CV. Penugasan **menyempitkan** izin dan tidak pernah memberi hak, mengikuti pola [[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]]. Antrean dan gerbang aksi memakai fungsi yang sama.

### 4. Aturan pembukuan yang dikunci sejak awal

- **Satu jurnal satu dokumen** berisi seluruh barisnya, ditulis atomik.
- **Nominal disimpan sebagai bilangan bulat** dalam satuan sen, bukan float. Server menolak jurnal yang debit tidak sama dengan kredit, kurang dari dua baris, bernilai nol, atau memakai akun di luar COA.
- **Nomor voucher** mengikuti format FINCON dan diterbitkan penghitung atomik ber-index unik per CV, jenis, dan bulan.
- **Jurnal terposting tidak diedit dan tidak dihapus**; koreksi lewat jurnal balik.
- **Kunci periode per CV**; jurnal ke periode terkunci ditolak.
- **Jejak sumber** tiap jurnal: manual, pengajuan, kas kecil, payroll, marketplace, atau impor bank, beserta nomor dokumen asalnya; sumber otomatis idempoten per dokumen asal.
- **Jurnal manual diperiksa Senior Accountant** sebelum terposting. Jurnal otomatis dari dokumen yang sudah disetujui terposting langsung dan menaut dokumennya.

### 5. Setara FINCON lebih dulu, bugnya diperbaiki

Cakupan pertama buku besar CV: COA, lima jenis jurnal, saldo awal, buku besar, neraca saldo, laba rugi bertingkat, neraca kumulatif, arus kas metode langsung, perubahan ekuitas, laporan bulanan 12 kolom, aset tetap dan penyusutan, konsolidasi 40 CV dengan eliminasi yang menyimpan pasangan entitas. Aturan rawan di Context butir 4 diperbaiki dan dikunci test regresi. Spesifikasinya di [[Finance - Buku Besar CV]].

### 6. Dua jalur paralel, lalu otomasi

- **Jalur A, uang keluar per CV.** Pengajuan Barang mendapat CV tujuan eksplisit. Tahap transfer pengajuan bersumber dana **rekening CV** ditindak pemegang CV itu; bersumber dana **rekening PT** tetap Account Payable. Bukti transfer dan arsip digital menggantikan WhatsApp, Excel, AppSheet, dan cetak. Jalur ini tidak menunggu buku besar; jurnal ke Accurate PT tetap seperti sekarang.
- **Jalur B, buku besar CV.** Butir 4 dan 5, lalu migrasi data FINCON dan jalan paralel satu siklus tutup buku. Selama paralel, data FINCON diimpor berkala untuk dibandingkan dan staf tidak menginput dua kali. Sesudah laporan cocok, FINCON dijadikan baca saja.
- **Sesudah keduanya**: jurnal otomatis dari pembayaran dan kas kecil; daftar bayar, rekap iuran BPJS TK, dan jurnal gaji per badan usaha; jurnal penjualan marketplace per CV; impor mutasi rekening dan rekonsiliasi; tutup buku dan pemetaan KPI Accounting CV; FINCON dipensiunkan.

### 7. Hubungan dengan Accurate PT

Jurnal ke Accurate PT yang sudah berjalan (pengajuan, kas kecil, marketplace) tidak diubah oleh keputusan ini, dan `ACCURATE_KAS_PUSH` tetap keputusan terpisah. Saldo rekening CV 1299xx di Accurate PT direkonsiliasi dengan kas buku CV per bulan. Makna akuntansi 1299xx di buku PT, dan buku mana yang dipakai untuk laporan pajak CV, belum diketahui (TBD) dan wajib dijawab SPV FAT sebelum task rekonsiliasi dimulai.

### 8. Jurnal penjualan otomatis tunduk pada gerbang kolom

Baris jurnal penjualan per CV hanya dibentuk dari komponen sejajar identitas income. Kolom yang merupakan bagian dari kolom lain atau tumpang tindih (antara lain `TotalShippingRebate`, `TotalOrderAdjustment`, pecahan `FeeCommission` dan `FeeProcess`, `PerubahanSaldo`, `BundleProfit`) tidak dijumlahkan sebagai baris tersendiri. Daftar lengkapnya, berikut berkas kodenya, dijaga di satu tempat: [[Finance - Buku Besar CV]] §Gerbang kolom.

## Consequences

### Yang membaik

- Satu pembayaran CV dicatat sekali: pengajuan, bukti transfer, dan jurnal terhubung di satu sistem.
- Buku 40 CV berada di infrastruktur perusahaan, dengan login, izin, dan jejak audit di server.
- Celah konsolidasi dan eliminasi tertutup di sistem yang teruji; baris KPI Accounting CV bisa dipetakan ke data.
- Identitas CV punya satu pemilik.

### Yang memburuk atau tetap terbuka

- ⚠️ **ERP memikul kebenaran akuntansi 40 CV.** Salah hitung kini bug ERP. Rumus laporan dan konsolidasi wajib jadi fungsi murni yang diuji dengan data FINCON sebagai pembanding.
- ⚠️ **Dua buku tetap ada**: buku CV di ERP dan rekening CV di Accurate PT. Selisihnya hanya terlihat bila rekonsiliasi bulanan benar-benar dijalankan.
- **Rantai Pengajuan Barang bercabang menurut sumber dana**: pelaku tahap transfer untuk rekening CV berbeda dari rancangan kode hari ini, yang menaruhnya di Account Payable.
- **Migrasi bergantung pada pemilik FINCON** untuk mengekspor data; isi dan volume Supabase belum diketahui.
- **Pekerjaan terbesar** di antara opsi yang ada, dan jalan paralel satu siklus tutup buku menambah beban pembandingan.
- **Katalog izin di shared-library** membuat seluruh service ter-build saat pre-push; employee-service, procurement, dan finance-service naik bersama saat cakupan CV dirilis, backend sebelum frontend. Kategori inbox baru untuk antrean transfer menuntut service pengirim dan notification-service naik bersama.
- **Status ADR 0001 dan ADR 0068 tidak diubah dokumen ini**; keduanya hanya diberi tautan. Bila SPV FAT dan IT menyetujui, ADR 0001 diberi amandemen lapisan CV dan ADR 0068 ditandai Superseded.

### Yang sengaja tidak dilakukan

- **Tidak memindahkan kode FINCON** ke dalam ERP.
- **Tidak memusatkan transfer ke Account Payable** untuk pengajuan bersumber dana rekening CV.
- **Tidak membangun koneksi API bank**; mutasi rekening diimpor dari berkas.
- **Tidak memindahkan PT dari Accurate** dan tidak menggabungkan PT ke konsolidasi tahap pertama.

## Dokumen Terkait

- [[Finance - Buku Besar CV]]: cara kerja modul yang diputuskan di sini
- [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]] yang dijawab · [[ADR - 0001 Akuntansi via Accurate]] yang diusulkan diamandemen · [[APP - Buku Besar Konsolidasi CV FINCON]] spesifikasi dan sumber migrasi
- [[Finance - FAT Persona]] · [[Finance - Kas Kecil dan Pengajuan Budget]] · [[Finance - Rancangan Finance Service]] · [[Finance - Big Pictures]]
- [[Microservices - Procurement Service]] · [[Microservices - Payroll Service]] · [[Microservices - Integration Service]] · [[Microservices - Notification Service]] · [[External - Accurate]] · [[ADR - 0014 Accurate Token DB-backed via OAuth]]
- [[REF - Kepemilikan Data]] · [[CORE - RBAC dan Permission Set]] · [[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]] · [[HRIS - Matriks KPI per Departemen]] · [[RUN - Deploy Microservices bip-erp]]
