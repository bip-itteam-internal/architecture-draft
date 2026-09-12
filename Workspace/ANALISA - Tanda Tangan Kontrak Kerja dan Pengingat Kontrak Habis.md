# ANALISA - Tanda Tangan Kontrak Kerja dan Pengingat Kontrak Habis

Daftar task hasil `/analisa-kebutuhan` 2026-09-11, direvisi hari yang sama. Keputusan arsitekturalnya di [[ADR - 0089 Tanda Tangan Kontrak Kerja di Sistem Sendiri, Didampingi HRD, e-Meterai Dibubuhkan HR]]; cara kerja domainnya di [[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]].

**Dibuat**: 2026-09-11 · **Status**: T1 merged (bip-erp PR #1851), naik di DEV 2026-09-11 dan PROD 2026-09-12; jalan cron DEV 2026-09-12 terverifikasi, jalan PROD pertama 2026-09-13 07:00 WIB belum dibaca. Rilis tanda tangan (Gelombang 2-3) menunggu N1 (konfirmasi legal) dan S1 (uji PDF bermeterai).

---

## 0. Masalah yang diselesaikan

| # | Masalah (wawancara 2026-09-11) | Yang menjawab |
|---|---|---|
| A | Kertas dan biaya cetak PKWT, yang sering diperpanjang | tanda tangan tatap muka didampingi HRD + e-Meterai oleh HR (Gelombang 1-3) |
| B | Kontrak habis tak terpantau | pengingat (Gelombang 0). **Tidak butuh tanda tangan** |

Keputusan pemilik proses yang mengikat:
- tanpa PSrE dan e-KYC;
- karyawan baru **dan** perpanjangan menandatangani **di kantor, didampingi HRD**; tidak ada tanda tangan jarak jauh;
- kontrak karyawan baru dikirim lewat email; karyawan aktif membuka salinannya di MyBharata;
- e-Meterai dibubuhkan HR di luar sistem;
- Pihak Pertama = direktur, dengan akun bersama Sekretariat diterima apa adanya;
- pengingat memakai kategori `reminder`, ringkasan harian ke supervisor HR, atasan H-14 kalender, kedaluwarsa mingguan;
- verifikasi DEV pengingat lewat jalan cron 07:00 WIB, dan deploy PROD pengingat menunggu data prod diukur (2026-09-11; diukur 2026-09-12: tidak ada kontrak kedaluwarsa, jadi tidak ada data yang dirapikan dan aturan tidak diubah);
- draf kontrak **tidak dikirim ke karyawan lebih dulu**: karyawan menerima dokumennya saat bertemu HR. Selama masa transisi, HR boleh mengirim dokumen isian otomatis secara opsional untuk menemukan kekurangan (2026-09-12, T18).

⛔ **Jebakan yang menggagalkan rancangan naif** (dicek ke `origin/main` 2026-09-11, rinciannya di dok domain):
- `common.SetaraDirektur` meloloskan Corporate Secretary. Jangan dipakai sebagai gerbang Pihak Pertama.
- Lampiran kontrak sekarang di prefix `employee/`, yang kunci bacanya ada di bundel browser.
- Menempel goresan ke PDF yang sudah bermeterai bisa merusak e-Meterai dan sidik jarinya. Urutan ditentukan S1.
- Status kontrak dulu punya dua aturan batas hari (`klasifikasiKontrak` vs `statusKontrak`), dan tanggal disimpan sebagai tengah malam WIB. Disatukan dalam tanggal WIB oleh T1 (PR #1851).
- `PATCH /contract/:id` memakai `ReplaceOne`: field yang tidak ada di struct ikut terhapus. Status tanda tangan wajib masuk struct, catatan di koleksi sendiri.
- Data kandidat tidak punya NIK, sedangkan record kontrak, pencocokan NIK, dan salinan email bertumpu pada data karyawan. Usulan: calon karyawan menandatangani sesudah dibuatkan data karyawan (dok domain §Calon karyawan dan karyawan aktif).
- Akun karyawan baru langsung aktif saat dibuat (`services/employee/func.go:188-190`): calon karyawan yang sudah dibuatkan data ikut terhitung karyawan aktif sebelum menandatangani.
- Data kontrak DEV tidak mewakili PROD: DEV 2026-09-11, 110 dari 172 karyawan aktif kedaluwarsa, semuanya `migrated`; PROD 2026-09-12, 0 dari 186, karena HR sudah mencatat 197 kontrak pada Agustus. Ukur PROD sebelum merancang dari data. Durasi kontrak migrasi juga tak bermakna, karena tanggal mulainya `join_date`.
- `masa_evaluasi` di offer teks bebas (`"2"`, `"3 bulan"` di DEV), sedangkan jenis kontrak dan tanggal berakhir kontrak pertama diketik manual saat Tambah Karyawan: durasi di offer, data karyawan, dan PKWT bisa berbeda tanpa ketahuan.

---

## 1. Urutan kerja

Nomor dalam kurung = prasyarat. Tiap item cukup jelas untuk langsung dilempar ke `/start-task`.

### Gelombang 0: pengingat kontrak habis (masalah B)

**T1. Pengingat kontrak habis.** Rencana disetujui: `.task-plans/2026-09-11-pengingat-kontrak-habis.md` (branch `feat/employee-pengingat-kontrak`). Cron harian 07:00 WIB di employee-service; ringkasan harian ke supervisor HR (masuk "segera berakhir", H-30, H-7, kedaluwarsa mingguan); atasan H-14 kalender; kategori `reminder`; menyatukan aturan status kontrak dalam tanggal WIB; catatan terkirim per (kontrak, tahap, penerima).
*Prasyarat: tidak ada.* Deploy: employee-service saja.
*Status 2026-09-11*: merged (PR #1851). Pipeline dev melewatkannya, jadi dideploy manual ke DEV 22:01 WIB (gerbang biner lolos; `GET /api/employee/contract` lewat gateway sudah menunjukkan aturan tanggal WIB).
*Status 2026-09-12*: jalan cron DEV 07:00 WIB terverifikasi (133 kontrak jatuh jadwal, 7 pesan terkirim dan ketujuhnya ada di inbox, 0 gagal, 151 catatan, 0 duplikat). PROD diukur (N3): tidak ada kontrak kedaluwarsa, jadi tak ada keputusan soal data migrasi. Image employee-service PROD dibangun 07:32 WIB dari `198ff789` bersama deploy lain; gerbang biner dan index unik terverifikasi, koleksinya masih kosong. Sisa: baca jalan PROD pertama 2026-09-13 07:00 WIB (perkiraan dari data 2026-09-12: sekitar 55 kontrak jatuh jadwal, satu ringkasan HR, pesan atasan untuk 30 kontrak), lalu cek dedupe di DEV (usul: jalan cron 2026-09-13 yang masih di minggu ISO sama, sebagai pengganti recreate ber-env).

**T13. Tautan dari pesan pengingat ke halaman Kontrak.** Pesan T1 tanpa rute, karena halaman `/hris/contract` tidak membaca query string dan belum ada pemetaan rute inbox ke sana. Butuh pemetaan tautan inbox dan halaman yang membuka karyawan dari `?employee=` (sejalan dengan T11).
*Prasyarat: T1.*

**T14. Hasil penilaian kinerja atasan kembali ke HR.** T1 meminta atasan menilai kinerja H-14, tetapi hasilnya tidak tercatat di sistem dan HR tidak diberi tahu. Putuskan bentuknya lebih dulu: catatan pada kontrak, form, atau tetap di luar sistem.
*Prasyarat: T1; butuh keputusan pemilik proses.*

**T15. Filter `ending_month` di `GET /contract` dalam tanggal WIB.** Bulan masih dibaca dari `contract_ending` dalam UTC, jadi kontrak yang tersimpan tengah malam WIB tanggal 1 masuk ke bulan sebelumnya. Perbaikannya mengubah hasil filter yang terlihat HR.
*Prasyarat: T1 (memakai `tanggalWIB` yang sama).*

**T16. Aturan pengingat untuk kontrak `PKWT (Evaluasi)`.** Masa evaluasi di DEV 2-3 bulan, sedangkan tahap T1 dirancang untuk PKWT belasan bulan. Kontrak evaluasi 2 bulan sudah "segera berakhir" sejak hari pertama, dan HR langsung menerima tahap "Berakhir dalam 2 bulan" begitu data karyawannya dibuat; kontrak 3 bulan menerima tahap itu sesudah sekitar sebulan, dan H-30 jatuh di pertengahan masa kerja. Pesan atasan H-14 juga menjadi saluran penilaian kedua di samping Performance Review Onboarding. Opsi yang dibahas 2026-09-12: untuk jenis ini lewati tahap 2 bulan (dan mungkin H-30), pertahankan H-7, arahkan penilaian ke Performance Review; atau biarkan. Di PROD 2026-09-12 baru satu karyawan aktif yang kontrak terakhirnya `PKWT (Evaluasi)`, jadi belum mendesak.
*Prasyarat: T1; butuh keputusan pemilik proses.*

### Prasyarat tanda tangan

**S1. Uji PDF bermeterai asli.** HR memeteraikan satu PDF contoh lewat portal distributor resmi yang akan dipakai. Periksa: (1) apakah isi PDF asli tetap utuh byte per byte di dalam berkas bermeterai; (2) apakah e-Meterai-nya masih lolos verifikasi resmi sesudah dibuka ulang. Lolos keduanya → urutan A (tanda tangan dulu, goresan di PDF, meterai terakhir). Gagal → urutan B (meterai dulu, goresan di lembar bukti). Tulis hasilnya di dok domain §Alur Tanda Tangan.
*Prasyarat: akun distributor HR (N2).* Menahan T7 dan T9.

### Gelombang 1: pondasi dokumen

**T5. Nomor kontrak unik + format HR.** Konfirmasi format ke HR (`…/HRD/PKWT/…/…`), urut per perusahaan dan periode, index unik pada nomor. Tentukan perlakuan nomor kontrak lama.
*Prasyarat: tidak ada.*

**T6. Data penandatangan per perusahaan + field tempat lahir.** Nama, jabatan, dan alamat direktur per perusahaan (bukan `SetaraDirektur`), plus tempat lahir di `personal_data` beserta form pengisiannya. Tempat lahir calon karyawan sudah ada di data kandidat (`tempat_lahir`), jadi bisa terisi saat Tambah Karyawan dari kandidat.
*Prasyarat: tidak ada.*

**T17. Masa evaluasi di offer jadi angka bulan + kontrak pertama terisi otomatis.** `masa_evaluasi` sekarang teks bebas (`services/recruitment/models_offer.go:43`, form `offer-form-dialog.tsx`; DEV berisi `"2"` dan `"3 bulan"`) dan hanya dipakai surat penawaran (`{{masa_evaluasi}}`), sedangkan jenis kontrak dan tanggal berakhir diketik manual saat Tambah Karyawan dari kandidat (`create-employee/index.tsx:219`). Ubah jadi angka bulan (nilai lama yang bisa diurai dimigrasikan, sisanya ditandai untuk HR), surat penawaran merender "N bulan", dan Tambah Karyawan dari kandidat mengisi `PKWT (Evaluasi)` + tanggal berakhir = tanggal mulai + masa evaluasi (HR tetap bisa mengubah).
*Prasyarat: tidak ada.* Repo: recruitment-service + erp-frontend; deploy BE sebelum FE.

**T18. Dokumen PKWT masa transisi: isi otomatis + kirim opsional.** Keputusan pemilik proses 2026-09-12: sebelum alur tanda tangan (T9) ada, HR bisa membuat dokumen PKWT dari template HR yang diisi data sistem, dan boleh mengirimnya ke email karyawan **secara opsional** (per kontrak, hanya lewat tombol yang ditekan HR, tanpa kiriman otomatis dan tanpa lampiran di pesan pengingat). Tujuannya menemukan data dan isi template yang masih kurang: isian yang datanya belum ada (Pihak Pertama, tempat lahir, lokasi dan jam kerja, rincian gaji Lampiran 1, format nomor kontrak) ditandai jelas di dokumen, bukan dikosongkan diam-diam. Tanda tangan tetap basah; PDF bertanda tangan diunggah ke riwayat kontrak seperti sekarang. Rancangan akhir tetap: dokumen diberikan saat HR bertemu karyawan, tidak dikirim lebih dulu.
*Prasyarat: berkas template PKWT dari HR (tidak disimpan di vault).* Diputuskan saat `/plan`: format keluaran (PDF lewat `go-pdf/fpdf` seperti slip gaji, atau isian template Word), sumber gaji Lampiran 1 (payroll atau ditandai belum ada), dan apakah kiriman dicatat. Repo: bip-erp (employee-service; email lewat notification-service `POST /email/send`) + erp-frontend (panel riwayat kontrak). Hasilnya dipakai ulang T7.

**T7. Template PKWT + generator PDF draft + lembar bukti.** Isi dari `personal_data`, `work_data`, `employee_contract`, `employee_salary` (Lampiran 1, dengan pemetaan komponen ke kolom); versi template dicatat per kontrak; kotak tanda tangan mengikuti hasil S1. Periksa font untuk karakter di luar ASCII (preseden slip gaji hanya font inti). Durasi di Pasal 2 dihitung dari tanggal mulai dan berakhir saat PDF dibuat, tidak disimpan terpisah. Untuk calon karyawan, gaji di offer hanya satu angka (`gaji_evaluasi`/`gaji_kontrak`): putuskan sumber rincian komponennya (payroll diisi dulu, atau offer diperluas).
*Prasyarat: T5, T6, S1; T17 disarankan lebih dulu supaya durasi kontrak pertama sama dengan offer; kekurangan yang ditemukan lewat T18 jadi masukan.*

**T8. Prefix arsip MinIO + kunci lampiran.** Prefix baru tanpa kunci baca di browser (pola `audit/`), dibaca lewat proxy employee-service; lampiran yang sudah dikunci tidak bisa diganti atau dihapus.
*Prasyarat: tidak ada.* Deploy: file-service `up -d --build`, kunci unik di `.env` dev dan prod, employee-service `--force-recreate`, bukti lewat hitungan prefix di log boot.

### Gelombang 2: alur tanda tangan (backend)

**T9. Status + sesi tatap muka + catatan + salinan.** Status tanda tangan pada `employee_contract` (field masuk struct); koleksi catatan tanda tangan hanya-tambah tanpa TTL. Endpoint:
- buka sesi tanda tangan oleh HRD (izin kerja HRIS), dengan pencocokan NIK;
- simpan goresan + pernyataan setuju, atau minta koreksi;
- tanda tangan direktur massal;
- unggah PDF bermeterai (hash, kunci; urutan A: periksa PDF bermeterai memuat PDF yang ditandatangani);
- batal.

Lembar bukti PDF terpisah; salinan email lewat `POST /email/send` untuk karyawan baru.

Tambahan dari telaah 2026-09-11:
- kontrak pertama (dari create-employee) maupun perpanjangan lahir berstatus menunggu tanda tangan, bukan langsung berlaku;
- sesuaikan pengingat T1: kontrak lama tetap diingatkan sampai kontrak baru `SELESAI`, atau ada pengingat terpisah untuk tanda tangan yang tertunda;
- sediakan jalan membatalkan calon karyawan yang batal datang atau menolak menandatangani (akunnya sudah aktif sejak dibuat);
- penolakan NIK di sesi menautkan ke layar perbaikan data karyawan.

Keputusan 2026-09-12: draf tidak dikirim ke karyawan lebih dulu; karyawan menerima dokumennya saat sesi tatap muka, dan salinan final tetap dikirim sesudah selesai. Kirim opsional T18 hanya berlaku di masa transisi.

*Prasyarat: T7, T8, S1.*

### Gelombang 3: layar

**T10. MyBharata: Kontrak Saya (baca-saja).** Daftar kontrak milik sendiri dan buka PDF terproteksi (unduh byte lewat `DioApi`, tampilkan dengan `SfPdfViewer.memory`), **di balik gerbang PIN** seperti slip gaji karena memuat gaji. Sekalian verifikasi temuan sampingan: tap notifikasi yang melewati gerbang PIN karena `user_pin` tak pernah ditulis.
*Prasyarat: T9.* Rilis aplikasi: version name dan code naik bersama.

**T11. Web ERP HR: sesi tanda tangan tatap muka + status.** Layar tanda tangan di perangkat HR (input NIK dari KTP, tampilan kontrak, kanvas goresan, setuju/minta koreksi), status tanda tangan di halaman Kontrak dan panel riwayat, unggah PDF bermeterai, lembar bukti; unggah dikunci setelah final; halaman membaca `?employee=` untuk deep link.
*Prasyarat: T9.*

**T12. Ruang Direktur: antrean kontrak + tanda tangan massal.** Antrean "Kontrak menunggu tanda tangan" di infrastruktur antrean yang ada, seleksi banyak baris, konfirmasi eksplisit untuk kelompok terpilih. Ingat jebakan dialog di panel persetujuan direktur (`modal={false}`, baris yang lenyap setelah mutasi).
*Prasyarat: T9.*

### Keamanan akun (terpisah, tidak menahan tanda tangan)

Tanda tangan tidak memakai akun maupun PIN karyawan, jadi task ini tidak menahan Gelombang 1-3. Tetap nyata dan relevan untuk "Kontrak Saya" (T10), yang berada di balik PIN.

**K1. Limiter PIN + verifikasi PIN terikat token.** Limiter di gateway untuk `/auth/login/pin` dan `/auth/verify/pin`; `verify-pin` memakai identitas token, bukan `employee_id` dari body.
**K2. Jejak reset akun dan forget-device.** Siapa, kapan, akun mana; pemiliknya diberi tahu.
**K3. Password awal acak untuk karyawan baru.** Ganti password awal = `employee_id` (`orchestrator/hris/helper.go:471-485`) dengan pola acak `services/employee/external_account_password.go`, dikirim lewat WhatsApp seperti sekarang.
**K4. ID instalasi persisten di MyBharata.** Ganti Build.ID sebagai `device_id`.

### Non-kode

**N1. Konfirmasi legal** keabsahan tanda tangan tidak tersertifikasi untuk PKWT, termasuk klausul denda Pasal 4. Menahan rilis T9-T12, tidak menahan T1-T8.

**N2. SOP HR**: akun enterprise di distributor resmi e-Meterai, jenis kontrak yang dimeteraikan, jumlah meterai per kontrak, pencatatan biaya ke finance; SOP sesi tatap muka (pencocokan KTP, penolakan di tempat).

**N3. Ukur data prod**: jalankan `.task-plans/cek-kontrak-esign-prod.ps1` (volume kontrak per bulan, kontrak kedaluwarsa pada karyawan aktif, dan sebaran tahap pengingat: migrasi vs bukan, umur lewat, jendela H-14 tanpa `supervisor_id`, supervisor HR aktif per perusahaan). Hasilnya menentukan beban HRD dan direktur, dan apakah deploy PROD T1 perlu data dirapikan atau aturan diubah dulu. Temuan DEV 2026-09-11 sebagai pembanding: 110 dari 172 karyawan aktif kedaluwarsa, semuanya migrasi.
*Hasil 2026-09-12* (ukur ulang sebelum dipakai): 408 kontrak (204 migrasi), semuanya BIP (PKWT 348, `PKWT (Evaluasi)` 46, Magang 13, PKWTT 1), **0 berlampiran**; kontrak mulai 4 sampai 30 per bulan dalam 12 bulan terakhir (rata-rata sekitar 16, termasuk migrasi); 186 karyawan aktif, 2 tanpa kontrak, **0 kedaluwarsa**; PIN terisi di 185 akun aktif; jendela pengingat 55 kontrak (30 berakhir 25-26 September, 25 berakhir 25 Oktober), 17 dari 30 kontrak H-14 tanpa `supervisor_id`, satu supervisor HR aktif. Deploy PROD T1 tidak perlu merapikan data maupun mengubah aturan.

---

## 2. Belum diputuskan (TBD)

Rinciannya di dok domain §Belum Diputuskan. Yang menahan task tertentu:
- Format nomor kontrak → T5.
- Letak data penandatangan per perusahaan → T6.
- Lokasi kerja dan jam kerja di template, pemetaan komponen gaji Lampiran 1, rincian gaji calon karyawan dari offer → T7.
- Format masa evaluasi di offer (teks bebas vs angka bulan) → T17.
- Format dokumen masa transisi (PDF atau isian template Word) dan sumber rincian gaji Lampiran 1 untuk dokumen itu → T18.
- Hasil S1 (urutan A/B) → T7, T9.
- Bentuk penolakan di tempat → T9.
- Calon karyawan menandatangani sesudah dibuatkan data karyawan (usulan), jalan membatalkan calon yang batal atau menolak, kontrak belum ditandatangani terhadap pengingat → T9.
- Retensi arsip → T8.
- Bentuk hasil penilaian kinerja atasan → T14.
- Aturan tahap pengingat dan pesan atasan untuk `PKWT (Evaluasi)` → T16.

---

## 3. Mulai dari mana

T1: baca jalan PROD pertama 2026-09-13 07:00 WIB dan cek dedupe di DEV. Paralel dengannya: T18 (sesudah HR menyerahkan berkas template PKWT), S1 (minta HR memeteraikan satu PDF contoh), T5, T6, T8, T15, T16, T17, dan K1-K4.
