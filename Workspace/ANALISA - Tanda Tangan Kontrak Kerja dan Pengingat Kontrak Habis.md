# ANALISA - Tanda Tangan Kontrak Kerja dan Pengingat Kontrak Habis

Daftar task hasil `/analisa-kebutuhan` 2026-09-11, direvisi hari yang sama. Keputusan arsitekturalnya di [[ADR - 0089 Tanda Tangan Kontrak Kerja di Sistem Sendiri, Didampingi HRD, e-Meterai Dibubuhkan HR]]; cara kerja domainnya di [[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]].

**Dibuat**: 2026-09-11 · **Status**: T1 rencana disetujui (`.task-plans/2026-09-11-pengingat-kontrak-habis.md`), sedang dikerjakan. Rilis tanda tangan (Gelombang 2-3) menunggu N1 (konfirmasi legal) dan S1 (uji PDF bermeterai).

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
- pengingat memakai kategori `reminder`, ringkasan harian ke supervisor HR, atasan H-14 kalender, kedaluwarsa mingguan.

⛔ **Jebakan yang menggagalkan rancangan naif** (dicek ke `origin/main` 2026-09-11, rinciannya di dok domain):
- `common.SetaraDirektur` meloloskan Corporate Secretary. Jangan dipakai sebagai gerbang Pihak Pertama.
- Lampiran kontrak sekarang di prefix `employee/`, yang kunci bacanya ada di bundel browser.
- Menempel goresan ke PDF yang sudah bermeterai bisa merusak e-Meterai dan sidik jarinya. Urutan ditentukan S1.
- Status kontrak punya dua aturan batas hari (`klasifikasiKontrak` vs `statusKontrak`), dan tanggal disimpan sebagai tengah malam WIB. Hitung dalam tanggal WIB; T1 menyatukan keduanya.
- `PATCH /contract/:id` memakai `ReplaceOne`: field yang tidak ada di struct ikut terhapus. Status tanda tangan wajib masuk struct, catatan di koleksi sendiri.

---

## 1. Urutan kerja

Nomor dalam kurung = prasyarat. Tiap item cukup jelas untuk langsung dilempar ke `/start-task`.

### Gelombang 0: pengingat kontrak habis (masalah B)

**T1. Pengingat kontrak habis.** Rencana disetujui: `.task-plans/2026-09-11-pengingat-kontrak-habis.md` (branch `feat/employee-pengingat-kontrak`). Cron harian 07:00 WIB di employee-service; ringkasan harian ke supervisor HR (masuk "segera berakhir", H-30, H-7, kedaluwarsa mingguan); atasan H-14 kalender; kategori `reminder`; menyatukan aturan status kontrak dalam tanggal WIB; catatan terkirim per (kontrak, tahap, penerima).
*Prasyarat: tidak ada.* Deploy: employee-service saja.

### Prasyarat tanda tangan

**S1. Uji PDF bermeterai asli.** HR memeteraikan satu PDF contoh lewat portal distributor resmi yang akan dipakai. Periksa: (1) apakah isi PDF asli tetap utuh byte per byte di dalam berkas bermeterai; (2) apakah e-Meterai-nya masih lolos verifikasi resmi sesudah dibuka ulang. Lolos keduanya → urutan A (tanda tangan dulu, goresan di PDF, meterai terakhir). Gagal → urutan B (meterai dulu, goresan di lembar bukti). Tulis hasilnya di dok domain §Alur Tanda Tangan.
*Prasyarat: akun distributor HR (N2).* Menahan T7 dan T9.

### Gelombang 1: pondasi dokumen

**T5. Nomor kontrak unik + format HR.** Konfirmasi format ke HR (`…/HRD/PKWT/…/…`), urut per perusahaan dan periode, index unik pada nomor. Tentukan perlakuan nomor kontrak lama.
*Prasyarat: tidak ada.*

**T6. Data penandatangan per perusahaan + field tempat lahir.** Nama, jabatan, dan alamat direktur per perusahaan (bukan `SetaraDirektur`), plus tempat lahir di `personal_data` beserta form pengisiannya.
*Prasyarat: tidak ada.*

**T7. Template PKWT + generator PDF draft + lembar bukti.** Isi dari `personal_data`, `work_data`, `employee_contract`, `employee_salary` (Lampiran 1, dengan pemetaan komponen ke kolom); versi template dicatat per kontrak; kotak tanda tangan mengikuti hasil S1. Periksa font untuk karakter di luar ASCII (preseden slip gaji hanya font inti).
*Prasyarat: T5, T6, S1.*

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

**N3. Ukur data prod**: jalankan `.task-plans/cek-kontrak-esign-prod.ps1` (volume kontrak per bulan, kontrak kedaluwarsa pada karyawan aktif). Hasilnya menentukan beban HRD dan direktur.

---

## 2. Belum diputuskan (TBD)

Rinciannya di dok domain §Belum Diputuskan. Yang menahan task tertentu:
- Format nomor kontrak → T5.
- Letak data penandatangan per perusahaan → T6.
- Lokasi kerja dan jam kerja di template, pemetaan komponen gaji Lampiran 1 → T7.
- Hasil S1 (urutan A/B) → T7, T9.
- Draf lewat email sebelum datang, bentuk penolakan di tempat → T9.
- Retensi arsip → T8.

---

## 3. Mulai dari mana

T1 sedang dikerjakan. Paralel dengannya: S1 (minta HR memeteraikan satu PDF contoh), T5, T6, T8, dan K1-K4.
