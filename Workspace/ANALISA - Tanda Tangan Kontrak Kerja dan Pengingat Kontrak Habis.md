# ANALISA - Tanda Tangan Kontrak Kerja dan Pengingat Kontrak Habis

Daftar task hasil `/analisa-kebutuhan` 2026-09-11. Keputusan arsitekturalnya di [[ADR - 0089 Tanda Tangan Kontrak Kerja dengan PIN di Sistem Sendiri, e-Meterai Dibubuhkan HR]]; cara kerja domainnya di [[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]].

**Dibuat**: 2026-09-11 · **Status**: siap dikerjakan. Gelombang 0 bisa langsung jalan. Rilis tanda tangan (Gelombang 3-4) menunggu N1 (konfirmasi legal).

---

## 0. Masalah yang diselesaikan

| # | Masalah (wawancara 2026-09-11) | Yang menjawab |
|---|---|---|
| A | Kertas dan biaya cetak PKWT, yang sering diperpanjang | tanda tangan PIN + e-Meterai oleh HR (Gelombang 1-4) |
| B | Kontrak habis tak terpantau | pengingat (Gelombang 0). **Tidak butuh tanda tangan** |

Keputusan pemilik proses yang mengikat: tanpa PSrE dan e-KYC; e-Meterai dibubuhkan HR di luar sistem; karyawan menyetujui isi sebelum meterai; Pihak Pertama = direktur, dengan akun bersama Sekretariat diterima apa adanya.

⛔ **Jebakan yang menggagalkan rancangan naif** (semua dicek ke `origin/main` 2026-09-11, rinciannya di dok domain §Prasyarat Keamanan):
- `verify-pin` mencari akun dari body, dan `/login/pin` tanpa login maupun limiter. Memakai ulang endpoint itu untuk tanda tangan berarti PIN bisa ditebak.
- Reset akun IT = password sementara `employee_id`. Tanpa jejak reset, siapa pun yang tahu ID karyawan bisa "menandatangani".
- `common.SetaraDirektur` meloloskan Corporate Secretary. Jangan dipakai sebagai gerbang Pihak Pertama.
- Lampiran kontrak sekarang di prefix `employee/`, yang kunci bacanya ada di bundel browser.
- `device_id` Android = Build.ID, tidak unik.

---

## 1. Urutan kerja

Nomor dalam kurung = prasyarat. Tiap item cukup jelas untuk langsung dilempar ke `/start-task`.

### Gelombang 0: pengingat kontrak habis (masalah B)

**T1. Pengingat kontrak habis.** Cron harian di employee-service mengirim inbox ke staf HR saat kontrak masuk status `ending`, H-30, dan untuk kontrak yang sudah kedaluwarsa tapi karyawannya masih aktif; plus ke atasan langsung paling lambat 7 hari kerja sebelum berakhir untuk penilaian kinerja (Pasal 2 ayat 6 template PKWT). Klasifikasi status **wajib** memakai `klasifikasiKontrak` yang sama dengan daftar dan ringkasan, bukan ambang sendiri. Kategori inbox baru di `shared-library` + pemetaan di MyBharata dan Web ERP. Idempoten: satu pengingat per kontrak per jadwal.
*Prasyarat: tidak ada.* ⚠️ Deploy: notification-service lebih dulu, lalu employee-service.

### Gelombang 1: pengamanan PIN (prasyarat tanda tangan menjadi bukti)

**T2. Verifikasi PIN untuk tindakan bertanda tangan + limiter.** Fungsi server yang memverifikasi PIN milik **pemegang token** (identitas header gateway), dengan batas percobaan dan penguncian yang tercatat; dipakai endpoint tanda tangan nanti. Pasang limiter di gateway untuk `/auth/login/pin` dan `/auth/verify/pin`, yang hari ini tanpa batas.
*Prasyarat: tidak ada.*

**T3. Jejak reset akun + blokir tanda tangan setelah reset.** Catat tiap `PATCH /account/reset` dan `forget-device` (siapa, kapan, akun mana). Akun yang direset tidak bisa menandatangani kontrak sampai HR menandai identitasnya sudah diverifikasi ulang.
*Prasyarat: tidak ada.*

**T4. ID instalasi persisten di MyBharata.** Ganti Build.ID dengan UUID yang disimpan di secure storage, dikirim pada tindakan tanda tangan. Sekalian verifikasi temuan sampingan: tap notifikasi yang melewati gerbang PIN karena `user_pin` tak pernah ditulis.
*Prasyarat: tidak ada.* ⚠️ Butuh rilis aplikasi.

### Gelombang 2: pondasi dokumen

**T5. Nomor kontrak unik + format HR.** Konfirmasi format ke HR (`…/HRD/PKWT/…/…`), urut per perusahaan dan periode, index unik pada nomor. Tentukan perlakuan nomor kontrak lama.
*Prasyarat: tidak ada.*

**T6. Data penandatangan per perusahaan + field tempat lahir.** Nama, jabatan, dan alamat direktur per perusahaan (bukan `SetaraDirektur`), plus `tempat lahir` di `personal_data` beserta form pengisiannya.
*Prasyarat: tidak ada.*

**T7. Template PKWT + generator PDF draft.** Isi dari `personal_data`, `work_data`, `employee_contract`, `employee_salary` (Lampiran 1, dengan pemetaan komponen ke kolom), versi template dicatat per kontrak. Kolom tanda tangan bertuliskan "ditandatangani secara elektronik". Periksa font untuk karakter di luar ASCII (preseden slip gaji hanya font inti).
*Prasyarat: T5, T6.*

**T8. Prefix arsip MinIO + kunci lampiran.** Prefix baru tanpa kunci baca di browser (pola `audit/`), dibaca lewat proxy employee-service; lampiran yang sudah dikunci tidak bisa diganti atau dihapus.
*Prasyarat: tidak ada.* ⚠️ Deploy: file-service `up -d --build`, kunci unik di `.env` dev dan prod, employee-service `--force-recreate`, bukti lewat hitungan prefix di log boot.

### Gelombang 3: alur tanda tangan (backend)

**T9. Status tanda tangan + catatan tanda tangan + endpoint.** Status pada `employee_contract`; koleksi catatan tanda tangan hanya-tambah tanpa TTL; endpoint kirim draft ke karyawan, setuju/minta koreksi, unggah PDF bermeterai (hash SHA-256 + kunci), tanda tangan karyawan (PIN via T2), tanda tangan direktur massal (PIN via T2), batal. Lembar bukti PDF terpisah + salinan ke karyawan. Kategori inbox untuk tiap langkah. Akses PDF: HR berizin HRIS, karyawan yang bersangkutan, direktur.
*Prasyarat: T2, T3, T7, T8.*

### Gelombang 4: layar

**T10. MyBharata: Kontrak Saya + tinjau + tanda tangan.** Daftar kontrak milik sendiri, buka PDF terproteksi (unduh byte lewat `DioApi`, tampilkan dengan `SfPdfViewer.memory`), setuju/minta koreksi, tanda tangan dengan PIN **per tindakan** (bukan `PinSession`), lembar bukti, deep link notifikasi ke kontrak tertentu.
*Prasyarat: T4, T9.* ⚠️ Rilis aplikasi: version name dan code naik bersama.

**T11. Web ERP HR: status tanda tangan di halaman Kontrak.** Kirim draft, unggah PDF bermeterai, lihat status dan lembar bukti di panel riwayat; unggah dikunci setelah final; halaman membaca `?employee=` untuk deep link.
*Prasyarat: T9.*

**T12. Ruang Direktur: antrean kontrak + tanda tangan massal.** Antrean "Kontrak menunggu tanda tangan" di infrastruktur antrean yang ada, seleksi banyak baris, konfirmasi PIN sekali untuk kelompok terpilih. Ingat jebakan dialog di panel persetujuan direktur (`modal={false}`, baris yang lenyap setelah mutasi).
*Prasyarat: T9.*

### Non-kode

**N1. Konfirmasi legal** keabsahan tanda tangan tidak tersertifikasi untuk PKWT, termasuk klausul denda Pasal 4. Menahan rilis T9-T12, tidak menahan T1-T8.

**N2. SOP HR e-Meterai**: akun enterprise di distributor resmi, jenis kontrak yang dimeteraikan, jumlah meterai per kontrak, pencatatan biaya ke finance.

**N3. Ukur data prod**: jalankan `.task-plans/cek-kontrak-esign-prod.ps1` (volume kontrak per bulan, kontrak kedaluwarsa pada karyawan aktif, cakupan akun/PIN MyBharata). Hasilnya menentukan seberapa besar bantuan aktivasi yang dibutuhkan sebelum T10 dirilis.

---

## 2. Belum diputuskan (TBD)

Rinciannya di dok domain §Belum Diputuskan. Yang menahan task tertentu:
- Format nomor kontrak → T5.
- Letak data penandatangan per perusahaan → T6.
- Lokasi kerja dan jam kerja di template, pemetaan komponen gaji Lampiran 1 → T7.
- Penerima dan jadwal final pengingat → T1.
- Retensi arsip → T8.

---

## 3. Mulai dari mana

Task pertama: **T1**, karena menjawab masalah B tanpa menunggu apa pun. Jalankan `/start-task Pengingat kontrak habis: cron employee-service kirim inbox ke HR dan atasan (lihat Workspace/ANALISA - Tanda Tangan Kontrak Kerja dan Pengingat Kontrak Habis §T1)`.

T2, T3, T5, T6, T8 bisa berjalan paralel dengan T1.
