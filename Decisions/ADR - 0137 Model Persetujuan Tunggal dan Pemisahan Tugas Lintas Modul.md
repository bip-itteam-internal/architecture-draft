# ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul

> **Status**: 🟡 **Diusulkan**, 2026-09-29, BELUM diputuskan dan nol kode. Pengambil keputusan: **TBD** (manajemen bersama pemilik alur uang dan tim IT; lihat §Pertanyaan untuk manajemen, butir 1). Dok ini memetakan masalah, opsi, dan usulan penulis; ia tidak menetapkan apa pun sampai bagian §Decision diisi orang yang berwenang.

%% Status di blockquote atas supaya terbaca VAULT-INDEX.json (15 baris pertama), pola sama dengan ADR 0136. %%

%% Vault ini PUBLIK. Celah yang belum ditambal hanya ditulis sebagai kategori, dampak, tingkat, dan rujukan issue Linear. Jangan menambahkan rute, nama berkas, nomor baris, atau cara memicunya ke dok ini. %%

## Untuk Manajemen

**Masalahnya dalam satu kalimat.** Setiap modul ERP menulis sendiri aturan "siapa boleh menyetujui" dan "siapa tidak boleh menyetujui miliknya sendiri", dengan enam cara berbeda, sehingga ada alur uang di mana satu orang bisa meloloskan dokumen sendirian dan tak satu pun gerbang berbunyi.

**Yang perlu diputuskan.** (1) Apakah persetujuan di seluruh ERP memakai **satu model yang sama** (siapa menyetujui ditentukan lewat hak per tahap atau penunjukan yang tercatat, bukan nama jabatan), dengan aturan pemisahan tugas bawaan: pengaju bukan penyetuju, satu orang satu tanda tangan per dokumen, pembuat bukan pembayar. (2) Bagaimana perlakuan akun ber-akses luas (supervisor IT, Direktur, akun developer) terhadap gerbang bisnis. (3) Siapa di perusahaan yang memiliki daftar "tugas mana tak boleh dirangkap satu orang" untuk tiap alur uang.

**Yang tidak dijanjikan.** ADR ini belum menutup celah apa pun; celah yang sudah diketahui ditangani lewat issue Linear masing-masing dan tidak menunggu keputusan ini. Setelah diputuskan, migrasinya bertahap per modul, dimulai dari alur uang.

## Deskripsi

*Usulan untuk menyatukan cara ERP Bharata menentukan penyetuju tiap tahap persetujuan dan menegakkan pemisahan tugas (segregation of duties, SoD) di semua modul, dengan pola persetujuan payroll bertingkat ([[ADR - 0129 Persetujuan Payroll Run Bertingkat dan Dibayar per Badan Usaha sebelum Terbit]]) sebagai acuan yang sudah terbukti. Empat opsi dibandingkan; usulan penulis ditandai jelas sebagai usulan.*

- **Tanggal**: 2026-09-29
- **Diukur ke**: bip-erp `origin/main` `89296af7`, erp-frontend `origin/main` `44c780311`, data PROD baca-saja (audit hak akses 2026-09-29). Angka agregat saja; rincian celah ada di Linear.
- **Hubungan dengan ADR lain**: **memperluas** [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] (menambah aturan SoD di atas tiga sumbu hak), [[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]] (penunjukan-menyempitkan menjadi pola umum), dan [[ADR - 0094 Booking Ruang lewat MyBharata, Penyetuju Ditunjuk HR, Satu Sumber Ruang Kantor]] (penunjukan HR sebagai bentuk sah penunjukan berjejak). **Bila diputuskan sesuai usulan, mengganti sebagian**: kalimat [[ADR - 0129 Persetujuan Payroll Run Bertingkat dan Dibayar per Badan Usaha sebelum Terbit]] §1 yang menolak mesin persetujuan lintas modul "karena baru dua pemakai", butir [[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]] §2 yang meloloskan supervisor IT sebagai jalan darurat, dan baris Direktur di tabel [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]]. **Tidak mengubah**: penolakan alur yang dikonfigurasi dari layar ([[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]] §7, ADR 0057 Consequences), dan pembedaan tanda tangan tercetak dari persetujuan di [[ADR - 0131 Tanda Tangan Direktur-Sekutu pada BKK Otomatis Tanpa Approval]].

## Context

### Fondasi hak akses sudah ada, dan ia tidak menjawab SoD

[[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] menetapkan hak lewat paket bernama yang menempel di jabatan, dengan katalog izin terpusat di pustaka bersama. Per `origin/main` 2026-09-29 ada **24 katalog modul** terdaftar (diverifikasi ulang: 24 pemanggilan pendaftaran katalog di employee-service) dan sekitar 175 izin; penegakannya deny-by-default dan header identitas diisi ulang gateway ([[CORE - RBAC dan Permission Set]]).

RBAC menjawab **"siapa boleh melakukan aksi X"**. Ia tidak menjawab **"siapa tidak boleh melakukan X atas dokumen ini karena ia sudah melakukan Y atas dokumen yang sama"**. Pertanyaan kedua itulah SoD, dan ia tak bisa dinyatakan lewat paket: orang yang memegang dua izin tahap memang boleh keduanya menurut RBAC, dan satu-satunya yang bisa menolaknya adalah pemeriksaan atas riwayat dokumen.

### Kenyataan data hak akses di PROD (baca-saja, 2026-09-29)

| Ukuran | Angka |
|---|---|
| Jabatan yang sudah dipasangi paket | **36 dari 126 (29%)** |
| Akun aktif | 184, dengan 32 berpaket per-akun, 99 ber-`system_roles`, dan **76 tanpa keduanya** |
| Paket ber-`reach` "all" | 109 dari 122 |
| Kunci modul di `system_roles` tanpa definisi master | 9 |
| Nilai peran | bebas ketik; dua ejaan untuk peran yang sama ditemukan hidup berdampingan |

Artinya sebagian besar hak hari ini masih mengalir lewat tier `system_roles` dan fallback-nya ([[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]], [[CORE - RBAC dan Permission Set]] §Fase dua), bukan lewat paket yang bisa dibaca HR.

### Enam pola penentuan penyetuju

[[REF - Alur Persetujuan]] sudah menginventaris alur persetujuan per mekanisme gerbang. Dilihat dari **cara penyetuju ditentukan**, ada enam pola yang hidup bersamaan:

| # | Pola | Contoh alur | Catatan |
|---|---|---|---|
| 1 | Supervisor departemen (`work_data.is_supervisor`), kini lewat penyetuju per departemen berjejak | cuti, dinas, koreksi presensi, tukar jadwal, permintaan barang | penyetuju tercatat di slot dokumen |
| 2 | **Nama jabatan** | persetujuan Pesanan Pembelian ERP, pengalihan cuti supervisor ke "Direktur" | `common.SetaraDirektur` (Direktur dan Corporate Secretary); konstanta penyetuju PO berisi string `"Direktur"` |
| 3 | **Izin per tahap** | pengajuan barang/budget (`budget.approve.atasan`, `.aset`, `.procurement`, `.finance`, `.direksi`, `.pembayaran`), kas kecil, payroll jenjang, `hris.pengajuan.approve`, `recruitment.approve`, izin approve batch/K3/gudang WMS | pola yang paling dekat dengan ADR 0030 |
| 4 | **Penunjukan di koleksi** | penunjukan pembelian per (perusahaan, tahap) ADR 0057, daftar penyetuju Booking Ruang ADR 0094 | menyempitkan, tidak memberi hak |
| 5 | **Tier `system_roles` yang dicocokkan ke nilai literal** | penyetuju CAPA produksi/gudang | rapuh terhadap ejaan nilai peran (lihat BHA-216) |
| 6 | Relasi `work_data.supervisor_id` | hanya cakupan tampilan KPI tim | bukan gerbang persetujuan |

Pola 2 adalah satu-satunya yang memeriksa **nama jabatan**. Kata `Direktur` muncul **236 kali di 76 berkas Go non-test** (diverifikasi ulang 2026-09-29 dengan `git grep -c` atas `origin/main`, termasuk komentar), dan audit frontend mencatat 84 baris serupa. Tiap literal adalah tempat wewenang bisa menyimpang dari keputusan organisasi tanpa galat; [[REF - Alur Persetujuan]] §Wewenang setingkat Direktur sudah mencatat gejalanya ("antrean berisi, tombolnya 403").

### Penjaga "tak boleh menyetujui milik sendiri" ditulis per modul

Penjaga pengaju ≠ penyetuju ditulis ulang di sekitar **10 tempat** tanpa satu pun fungsi bersama. Yang sudah tertutup dan terverifikasi: cuti, dinas, dan tukar jadwal (dokumen milik pemanggil tak pernah terambil sebagai bahan review), koreksi presensi, **payroll jenjang**, bukti transfer AP, permintaan barang GA, peminjaman ruang.

**Payroll jenjang adalah satu-satunya yang menegakkan ketiga aturan SoD sekaligus** (diverifikasi ulang di kode 2026-09-29): pengaju pertama ditolak menyetujui; siapa pun yang pernah mengajukan atau mengajukan ulang run ikut ditolak (karena ia penyusun angkanya); dan orang yang sudah menandatangani satu tahap ditolak di tahap berikutnya pada run yang sama, walau memegang kedua izin. Gerbang dan antrean memakai fungsi yang sama. Inilah bentuk yang diusulkan menjadi acuan.

### Pemisahan tugas yang masih terbuka

Ditulis sebagai kategori, dampak, dan tingkat saja; rute, berkas, dan cara memicunya sengaja tidak ditulis di vault publik. Rincian dan pemetaan butir ke issue ada di Linear (issue keamanan BHA-309 sampai BHA-314, serta issue yang disebut per butir); keputusan ADR ini dilacak di BHA-315, penuntasan migrasi hak akses di BHA-316.

| Kategori | Dampak | Tingkat (penilaian penulis) | Rujukan |
|---|---|---|---|
| Satu pemegang akses luas bisa menuntaskan **seluruh tahap** pengajuan barang/budget atas dokumen orang lain; tak ada aturan "satu orang satu tanda tangan per dokumen" seperti di payroll | pengeluaran bisa lolos dengan satu keputusan manusia | Tinggi | BHA-314 |
| Dua slot penyetuju CAPA bisa diisi orang yang sama | persetujuan ganda yang sebenarnya tunggal | Sedang | BHA-216 |
| Serah-terima aset: pihak penyerah bisa menyetujui serah-terimanya sendiri | perpindahan aset tanpa pemeriksa independen | Sedang | BHA-312, BHA-194 |
| Kas kecil: pembuat dan verifikator hanya dipisah lewat isi paket, tanpa pemeriksaan di kode | pemisahan hilang begitu satu jabatan diberi dua paket | Sedang | BHA-314 |
| Jalur lama permintaan pembelian: pembuat bisa menyetujui | nol dokumen di PROD saat diukur, jadi dampak nyata belum ada | Rendah | BHA-314, BHA-300 |
| Pemberian hak (pemasangan paket) tanpa persetujuan kedua dan tanpa jejak yang memadai | hak bisa dinaikkan tanpa pemeriksa, termasuk hak menyetujui | Tinggi | BHA-313 |

### Super-akses melewati gerbang bisnis

- **Supervisor/admin IT** lolos **20 dari 34** gerbang berbasis tier di backend, dan memegang seluruh izin budget. ADR 0057 §2 bahkan menuliskannya sebagai jalan darurat yang disengaja.
- **Direktur** otomatis diturunkan `it: supervisor` plus 14 peran modul lain dari jabatannya (tabel [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]]; diverifikasi ulang di kode 2026-09-29: 15 entri modul untuk jabatan Direktur di Kesekretariatan). Wewenang bisnis Direktur dan akses teknis IT tercampur dalam satu turunan.
- **Akun developer** di PROD: tiga akun Tech Development memegang tier tinggi di **8 sampai 10 modul bisnis**, satu di antaranya ditambah puluhan paket. Akun yang dipakai untuk menguji dan memperbaiki sistem sekaligus bisa menyetujui dokumen bisnis.

[[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]] sudah pernah memutuskan "tak ada pengecualian super-akses" untuk menu terbatas, lalu menemukan bahwa satu lapisan (penyaring sidebar) tetap meloloskan IT dan Direktur. Prinsipnya ada; penerapannya tidak seragam.

### Penegakan tersebar

- Aturan "klaim izin modul menang, selain itu fallback tier" ditulis ulang di sekitar **15 fungsi gerbang di 10 service**, dengan urutan menang yang berbeda: payroll tanpa fallback, manufacture menjumlahkan, sisanya klaim-menang ([[ADR - 0078 Fase Satu WMS Menggabungkan Matriks dan Paket Hak, Bukan Menggantikannya]]).
- Frontend menyalin **55 entri** tabel fallback; **124 berkas** frontend memutuskan dari tier saja; baru **17** yang membaca tanda keputusan dari server (`boleh_*`/`can_*`). Tombol yang digerbang salinan akan menyimpang dari gerbang server.
- Hak menempel di token **72 jam** (diverifikasi: umur token bawaan 72 jam di pustaka auth); pencabutan dini ada tetapi terbatas (rincian di Linear). Mencabut hak menyetujui seseorang tidak langsung berlaku.

### Kenapa belum pernah diputuskan

1. **Tiap alur lahir dari kebutuhan sah satu modul**, dan tiap penulisnya menambal SoD sebatas alurnya.
2. **"Tunggu pemakai ketiga" dipakai dengan benar**, dan ambangnya kini sudah terlampaui. ADR 0055/0057 menolak mesin alur yang dikonfigurasi "sampai ada tiga pemakai nyata"; ADR 0129 §1 menolak mesin persetujuan lintas modul "karena baru dua pemakai". Per hari ini pola izin-per-tahap dengan riwayat dipakai sedikitnya oleh pengajuan barang/budget, payroll jenjang, kas kecil, dan approve WMS; penunjukan berjejak oleh pengadaan dan booking ruang. Yang sudah melampaui ambang adalah **primitif bersamanya**; alur yang dikonfigurasi dari layar tetap tidak (lihat Opsi 2).
3. **Tak ada pemilik bisnis untuk matriks SoD.** Pertanyaan "tugas mana yang tak boleh dirangkap" adalah pertanyaan pengendalian internal, bukan pertanyaan kode, dan belum ada bagian yang ditunjuk menjawabnya.

## Opsi

Semua opsi memakai definisi yang sama. **Aturan SoD bawaan** yang diusulkan berlaku di setiap alur yang punya persetujuan:

- **SoD-1** pengaju (dan siapa pun yang pernah mengajukan ulang atau menyusun isi dokumen) bukan penyetuju tahap mana pun pada dokumen itu;
- **SoD-2** satu orang satu tanda tangan per dokumen, walau memegang izin beberapa tahap;
- **SoD-3** pembuat pengeluaran bukan pembayar, dan pembayar bukan penyetuju pembayarannya sendiri;
- **SoD-4** pemberi hak bukan penerima hak yang sama, dan pemberian hak menyetujui butuh jejak (BHA-313).

### Opsi 0 (pembanding): tidak memutuskan

Tiap modul terus menulis penentuan penyetuju dan penjaga SoD-nya sendiri. **Ongkos**: nol sekarang. **Risiko**: sudah terukur di §Context: celah SoD per alur yang baru ketahuan lewat audit, literal jabatan yang terus bertambah, dan alur baru (mis. pembayaran CV, BKK) yang akan memilih salah satu dari enam pola lagi.

### Opsi 1: tetap per modul, ditambah helper SoD bersama

Satu set fungsi murni di pustaka bersama (`shared-library/common`) untuk SoD-1 sampai SoD-3 yang menerima riwayat dokumen dan pemanggil, dipanggil tiap modul dari gerbang dan antreannya. Penentuan penyetuju tetap per modul (keenam pola hidup terus).

- **Konsekuensi**: celah SoD bisa ditutup cepat dengan kalimat penolakan yang sama di semua modul; test tabel SoD bisa ditulis sekali.
- **Ongkos**: kecil. Tiap modul hanya mengganti penjaga lokalnya dengan pemanggilan helper, dan menambah pemanggilan di alur yang belum punya.
- **Risiko**: tidak menyentuh akar kedua (penyetuju dari nama jabatan dan dari tier literal). Helper hanya bekerja bila **dipanggil**; modul yang lupa memanggilnya tetap terbuka tanpa gejala, sehingga penjaganya harus berupa pemindai, bukan disiplin. Bentuk riwayat dokumen berbeda per modul, jadi helper butuh adapter per modul.

### Opsi 2: satu "mesin persetujuan" sebagai pustaka bersama, dokumen tetap di service pemiliknya

Pustaka di `shared-library` yang memegang **aturannya**, bukan datanya. Tiap service tetap menyimpan dokumennya sendiri ([[ADR - 0002 Database-per-Service]]); yang dibagi adalah bentuk dan fungsinya:

1. **Definisi tahap per jenis dokumen, ditulis di kode**, dengan urutan tetap. Alur yang dikonfigurasi dari layar **tetap ditolak** (ADR 0055 §7, ADR 0057).
2. **Penyetuju tiap tahap = pemegang izin tahap itu, opsional disempitkan penunjukan berjejak** (pola ADR 0057 §1: penunjukan tak pernah memberi hak). **Bukan nama jabatan dan bukan nilai tier literal.** Tahap "atasan" tetap datang dari resolver penyetuju per departemen yang sudah ada.
3. **SoD-1 sampai SoD-3 bawaan**, dijalankan di setiap transisi; pengecualian per alur harus dinyatakan eksplisit di definisi tahapnya dan diberi alasan, bukan dengan tidak memanggil.
4. **Riwayat keputusan seragam** (tahap, pelaku, aksi, alasan, waktu), bentuk yang sudah dipakai payroll jenjang dan pengadaan.
5. **Gerbang dan antrean memakai fungsi yang sama** (ADR 0057 §3, ADR 0129 §2), supaya dokumen tak pernah tampil di antrean orang yang lalu ditolak.
6. **Penerima notifikasi dari pemegang izin tahap berikutnya** lewat pembacaan pemegang izin yang sudah ada di employee-service, tanpa fallback tier.
7. **Tanda boleh-putus dikirim server** ke frontend per dokumen, sehingga tombol tidak lagi diputuskan dari salinan tabel tier.

Pustaka ini **diekstrak dari payroll jenjang** (dan pola jenjang pengadaan yang menjadi induknya), bukan ditulis baru.

- **Konsekuensi**: satu jawaban untuk "siapa menyetujui tahap ini" di seluruh ERP, dan jawabannya bisa dibaca HR di layar Hak per Posisi. Nama jabatan berhenti menjadi sumber wewenang; Direktur menyetujui karena memegang izin tahap `direksi`, bukan karena namanya. Antrean terpadu (Portal Persetujuan yang sudah dipakai payroll) bisa membaca bentuk yang sama.
- **Ongkos**: sedang sampai besar, tetapi bertahap. Ekstraksi pustaka dari payroll kecil; migrasi tiap modul sedang (ganti status, riwayat, gerbang, antrean, dan frontend-nya). Alur yang paling mahal adalah yang hari ini bergantung pada nama jabatan (Pesanan Pembelian, pengalihan cuti ke Direktur) karena paket izinnya harus terpasang lebih dulu, dan hanya 29% jabatan yang berpaket.
- **Risiko**: pustaka bersama berarti perubahan aturan menuntut **semua service yang memakainya dibangun ulang** (kelas yang sama dengan kategori inbox di ingatan tim). Abstraksi yang terlalu umum bisa memaksa alur sederhana (booking ruang satu tahap) memakai bentuk berat; mitigasinya definisi tahap minimal satu tahap tanpa beban tambahan. Selama migrasi ada dua model hidup bersamaan.

### Opsi 3: layanan persetujuan terpusat (service baru)

Service baru menyimpan seluruh dokumen persetujuan, tahapnya, dan riwayatnya; modul memanggilnya lewat HTTP untuk membuka, memajukan, dan membaca status persetujuan.

- **Konsekuensi**: satu antrean, satu jejak audit lintas modul (lubang "audit trail lintas modul" yang dicatat [[REF - PRD ERP]] tertutup sekaligus), dan satu tempat menegakkan SoD.
- **Ongkos**: besar. Service, koleksi, kontrak, dan migrasi status dari tiap modul; setiap modul mengubah jalur tulisnya menjadi dua langkah lintas service.
- **Risiko**: **status dokumen di modul dan status persetujuan di service baru bisa menyimpang**, dan MongoDB yang dipakai tidak menjamin transaksi lintas service; itu bentuk sinkron dua arah yang paling sering salah diam-diam. Service baru menjadi jalur kritis bagi payroll, pengadaan, dan presensi sekaligus: bila ia mati, tak ada yang bisa disetujui. Data sensitif (angka gaji, nominal pengeluaran) ikut mengalir ke service lain. Menambah satu lompatan gateway untuk tiap aksi mendekatkan aksi berat ke batas 30 detik.

### Acuan pembanding: payroll jenjang (ADR 0129)

| Kriteria | Payroll jenjang hari ini | Opsi 1 | Opsi 2 | Opsi 3 |
|---|---|---|---|---|
| Penyetuju dari izin per tahap, bukan jabatan | ya | tidak disentuh | ya, wajib | ya |
| SoD-1 pengaju ≠ penyetuju | ya | ya | ya, bawaan | ya |
| SoD-2 satu orang satu tanda tangan | ya | ya | ya, bawaan | ya |
| Riwayat keputusan seragam | ya (lokal) | tidak | ya | ya, terpusat |
| Gerbang = antrean | ya | per modul | ya, bawaan | ya |
| Dokumen tetap di service pemilik | ya | ya | ya | tidak |
| Titik gagal baru | tidak | tidak | tidak (pustaka) | ya |

## Super-akses: opsi yang perlu dipilih

Bukan keputusan; masing-masing butir bisa dipilih terpisah.

- **SA-1. Supervisor/admin IT tidak otomatis lolos gerbang bisnis** (persetujuan, pembayaran, pemberian hak menyetujui). Akses teknis IT tetap; keputusan bisnis butuh izin tahap seperti orang lain. Untuk keadaan darurat disediakan **jalan darurat berjejak**: dinyalakan orang kedua, berbatas waktu, tercatat di riwayat dokumen sebagai aksi darurat. Mencabut butir ADR 0057 §2 yang meloloskan supervisor IT.
- **SA-2. Akun pribadi developer di PROD turun ke hak jabatannya**; pengujian di PROD memakai **akun uji terpisah** yang namanya jelas, tanpa hak menyetujui dokumen nyata, dan tercatat di satu daftar. Hak tinggi sementara untuk perbaikan insiden lewat jalan darurat SA-1.
- **SA-3. Direktur menyetujui lewat izin eksplisit, bukan jabatan.** Wewenang Direktur dan Corporate Secretary dipasang sebagai paket (mis. "Persetujuan: Direksi") yang berisi izin tahap `direksi` per alur. Turunan `it: supervisor` dan peran modul lain dari jabatan Direktur dicabut setelah paket terpasang (baris ADR 0043). `common.SetaraDirektur` menyusut menjadi label tampilan, lalu dipensiunkan bila tak dipakai.
- **SA-4. Pemberian hak menyetujui butuh orang kedua** (SoD-4): paket yang memuat izin tahap persetujuan atau pembayaran hanya aktif setelah disetujui pihak selain pemasangnya (BHA-313).

## Pertanyaan untuk manajemen

1. **Siapa pemilik matriks SoD per alur uang?** Bagian mana yang menetapkan "tugas mana tak boleh dirangkap satu orang" untuk pengajuan barang/budget, kas kecil, pembayaran AP, payroll, dan pembayaran CV (Finance, Internal Audit, Direksi, atau fungsi pengendalian internal tersendiri), dan siapa yang meninjaunya berkala?
2. **Apakah Direktur boleh menuntaskan beberapa tahap pada satu dokumen?** Misalnya tahap atasan dan tahap direksi sekaligus saat pengajunya bawahan langsung Direktur. Payroll menjawab "tidak" (satu orang satu tanda tangan); apakah itu berlaku untuk semua alur uang, atau ada ambang nominal di bawahnya boleh?
3. **Apakah Corporate Secretary setara Direktur untuk semua alur**, atau hanya sebagian? Hari ini keduanya disamakan di satu daftar jabatan.
4. **Bila penyetuju satu-satunya berhalangan atau menjadi pengaju sendiri**, dokumen dinaikkan ke tahap di atasnya, dialihkan ke delegasi berjejak berbatas waktu, atau menunggu?
5. **Apakah tim IT boleh memutus persetujuan bisnis dalam keadaan darurat?** Bila ya, siapa yang menyalakan jalan daruratnya dan siapa yang meninjau pemakaiannya (SA-1)?
6. **Apakah akun developer boleh memegang akses baca data bisnis di PROD** (gaji, pengeluaran), atau hanya lewat akun uji dan jalan darurat (SA-2)?
7. **Siapa yang menyetujui pemberian hak menyetujui** (SA-4), dan apakah pemberian hak lain (lihat saja) juga butuh orang kedua?
8. **Ambang nominal tahap direksi** ditetapkan siapa, dan di dokumen kebijakan mana? Kode tidak boleh menjadi tempat satu-satunya angka itu hidup.
9. **Rangkap jabatan**: orang yang memegang dua jabatan (mis. merangkap SPV) hanya boleh satu tanda tangan per dokumen; apakah itu diterima sebagai konsekuensi, atau butuh pengecualian tertulis?

## Rekomendasi penulis (USULAN, bukan keputusan)

Penulis mengusulkan **Opsi 2, dijalankan dengan Opsi 1 sebagai langkah pertamanya**, dan menolak Opsi 3 untuk saat ini:

1. **Helper SoD lebih dulu** (bentuk Opsi 1), diekstrak dari penjaga payroll jenjang, karena bisa menutup celah SoD dengan kalimat yang sama di semua alur tanpa menunggu migrasi model penyetuju. Helper ini menjadi inti mesin Opsi 2, jadi tak ada kerja yang dibuang.
2. **Mesin persetujuan sebagai pustaka** (Opsi 2), diekstrak dari payroll jenjang dan pola jenjang pengadaan, dengan definisi tahap di kode. Nama jabatan dan nilai tier literal berhenti menjadi sumber wewenang di gerbang baru.
3. **Super-akses**: SA-1, SA-2, SA-3, dan SA-4 seluruhnya, dengan urutan paket-terpasang-dulu-baru-cabut (pola fase dua ADR 0030), supaya tak ada alur yang mendadak tak punya penyetuju.
4. **Opsi 3 ditolak** karena memindahkan masalah ke titik gagal baru dan melahirkan status ganda lintas service. Kebutuhan sahnya (satu antrean, satu jejak audit) dijawab Opsi 2 lewat antrean terpadu yang membaca bentuk seragam dari tiap service.

Alasannya: payroll jenjang sudah membuktikan bentuknya bekerja di alur paling sensitif, jadi yang dibutuhkan adalah mengangkatnya, bukan merancang ulang. Kelemahan usulan ini: selama migrasi dua model hidup bersamaan, dan kecepatannya dibatasi pemasangan paket ke jabatan (29% hari ini), yang merupakan pekerjaan HR dan manajemen, bukan kode.

## Decision

**TBD.** Diisi setelah §Pertanyaan untuk manajemen dijawab dan pengambil keputusan ditetapkan. Sampai saat itu dok ini tidak boleh dikutip sebagai keputusan. Yang **tetap berlaku** tanpa menunggu: celah yang tercatat di Linear ditutup lewat issue masing-masing, dan alur persetujuan baru sebaiknya tidak menambah literal nama jabatan baru di gerbangnya.

## Langkah sesudah diputuskan (daftar task kasar)

Urutan mengikuti usulan penulis; disesuaikan bila opsi lain dipilih.

1. **Ukur dulu** (baca-saja, PROD): per alur uang, jumlah dokumen historis di mana pengaju sama dengan penyetuju atau satu orang menandatangani lebih dari satu tahap, dan jumlah jabatan yang harus dipasangi paket tahap sebelum gerbang jabatan dicabut. Tanpa angka ini ongkos migrasi dan dampak celah hanya tebakan.
2. **Pemilik matriks SoD** ditetapkan (§Pertanyaan butir 1), dan matriks per alur uang ditulis di dok domain masing-masing, bukan hanya di kode.
3. **Helper SoD** di pustaka bersama, diekstrak dari payroll jenjang, beserta test tabelnya.
4. **Mesin persetujuan** (definisi tahap, penyetuju dari izin ∩ penunjukan, riwayat seragam, gerbang = antrean, tanda boleh-putus dari server), payroll jenjang dipindah menjadi pemakai pertamanya tanpa perubahan perilaku.
5. **Migrasi per modul, alur uang dulu**: pengajuan barang/budget → kas kecil → Pesanan Pembelian (ganti gerbang nama jabatan dengan izin tahap direksi) → pembayaran AP dan bukti transfer → persetujuan insentif. Lalu alur non-uang: CAPA, serah-terima aset, cuti/dinas/koreksi (pengalihan ke "Direktur" diganti izin), rekrutmen, booking ruang.
6. **Super-akses sesuai keputusan**: paket "Persetujuan: Direksi" dipasang ke Direktur dan Corporate Secretary, lalu baris Direktur di tabel peran-dari-jabatan dicabut; akun uji PROD dibuat, akun pribadi developer diturunkan; jalan darurat berjejak dibuat sebelum lolos-otomatis IT dicabut.
7. **Frontend**: tombol persetujuan membaca tanda boleh-putus dari server; entri tabel fallback yang menyangkut persetujuan dihapus setelah modulnya pindah.
8. **Sinkron dok**: [[REF - Alur Persetujuan]] (inventaris per pola baru), [[CORE - RBAC dan Permission Set]], amandemen di ADR 0043, 0057, 0129, dan dok service yang dimigrasi.

## Penjaga yang dibutuhkan

- **Pemindai sumber: larangan literal jabatan baru di gerbang.** Test yang menolak kemunculan `"Direktur"` (dan nama jabatan lain) di berkas gerbang dan pemeriksaan persetujuan, dengan daftar-izin berkas lama yang **hanya boleh menyusut** (ratchet). Kontrol negatif: tambahkan satu literal di berkas baru dan pastikan test merah pada pesan yang benar.
- **Test SoD per alur**, berbentuk tabel: pengaju menyetujui, penyusun ulang menyetujui, satu orang di dua tahap, pembuat membayar, pemegang akses luas menuntaskan semua tahap; semuanya harus ditolak. **Fixture wajib memakai `employee_id` yang berbeda** untuk pengaju, penyetuju tahap 1, dan penyetuju tahap 2; fixture yang menyamakan identitas lulus untuk implementasi yang salah. Kontrol negatif: matikan pemeriksaan SoD sebentar dan pastikan test merah pada assertion yang diklaimnya.
- **Test gerbang = antrean**: satu test yang memanggil gerbang dan antrean untuk kombinasi yang sama dan menuntut jawaban sama (pola ADR 0057 §3).
- **Pemindai transisi**: perubahan status ke "disetujui"/"lunas" hanya boleh lewat fungsi mesin; penulisan status langsung di luar itu membuat test merah. Nama koleksi ditulis literal di argumen supaya pemindai tidak lulus tanpa memeriksa (ingatan tim, butir soft-delete).
- **Pemindai super-akses**: fungsi lolos-otomatis IT tidak boleh dipanggil dari gerbang persetujuan atau pembayaran; pemakaian jalan darurat wajib menulis riwayat (test yang memeriksa riwayatnya, bukan hanya status 200).
- **Test frontend**: tombol setujui/bayar di layar yang sudah dimigrasi dibaca dari tanda server, bukan dari tabel fallback.
- **Pemeriksaan data berkala** (baca-saja): dokumen yang riwayatnya memuat orang sama di dua tahap, dan akun uji yang tercatat pernah menyetujui dokumen nyata, dilaporkan ke pemilik matriks SoD.

## Dokumen Terkait

- [[REF - Alur Persetujuan]] (inventaris per mekanisme gerbang) · [[REF - Rantai Pengajuan Lintas Modul]] · [[REF - Kepemilikan Data]] · [[REF - PRD ERP]]
- [[CORE - RBAC dan Permission Set]] · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]] · [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]] · [[ADR - 0078 Fase Satu WMS Menggabungkan Matriks dan Paket Hak, Bukan Menggantikannya]]
- [[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]] · [[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]] · [[ADR - 0094 Booking Ruang lewat MyBharata, Penyetuju Ditunjuk HR, Satu Sumber Ruang Kantor]] · [[ADR - 0129 Persetujuan Payroll Run Bertingkat dan Dibayar per Badan Usaha sebelum Terbit]] · [[ADR - 0131 Tanda Tangan Direktur-Sekutu pada BKK Otomatis Tanpa Approval]]
- [[ADR - 0002 Database-per-Service]] · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]
- [[Microservices - Procurement Service]] · [[Microservices - Payroll Service]] · [[Microservices - Employee Service]] · [[Microservices - Inventory Service]]
