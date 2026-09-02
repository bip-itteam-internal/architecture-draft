# ANALISA - Modul Audit Internal

Papan kerja untuk [[ADR - 0073 Modul Audit Internal di finance-service dan Kertas Kerja yang Dipegang Sendiri]]. Dok domainnya [[Finance - Audit Internal]].

Disusun 2026-09-02, diperbarui hari yang sama setelah fase 1 selesai.
**Status: Fase 1 backend SELESAI dan ter-push** (branch `feat/finance-audit-internal`, 7 commit). Belum di-deploy, belum ada layar.

---

## Fase 0 — Gerbang kelayakan (BELUM dikerjakan)

Ketiganya membaca produksi dan **dijalankan manusia, bukan agent**. Hasilnya menentukan ruang lingkup uji yang masih tersandera.

- [ ] **T0.1 — Jalankan probe jejak audit Accurate ke produksi.** `services/integration/cmd/incaudit` sudah ada dan dibangun persis untuk pertanyaan ini; hasilnya tidak pernah tercatat di mana pun.
  **Menyandera**: 2 uji (waktu pembuatan transaksi, sebaran aktivitas pengguna).
  **Selesai bila**: hasilnya tertulis di dok domain dan kedua uji dipindahkan ke "bisa" atau "dinyatakan mustahil". Tidak boleh berhenti sebagai "belum dicek".
- [ ] **T0.2 — Coba tarik matriks hak akses Accurate** lewat `access-privilege/list.do`. Terdaftar di schema resmi, baca-saja, belum pernah dipanggil dari mana pun.
  **Menyandera**: seluruh Modul G. Sekalian periksa lock period, konfigurasi penyetuju, dan status 2FA — ketiganya belum ditemukan di schema.
- [ ] **T0.3 — Periksa apakah dokumen Bayar Uang membawa rekening penerima.**
  **Selesai bila**: bila tidak ada, uji itu **dinyatakan tidak dijanjikan** di dok domain, bukan ditunda diam-diam.

---

## Fase 1 — Backend (SELESAI)

- [x] **T1.1 — Katalog izin modul `audit`.** `shared-library/common/catalog_audit.go`; empat izin dengan `audit.master.save` terpisah dari `audit.tinjau`. Didaftarkan di **tiga** tempat (employee-service, setup test shared-library, dan finance-service sebagai penegak).
- [x] **T1.2 — Modul di dalam `services/finance`**, bukan service baru. Rute akar benar, urutan literal sebelum ber-`:param` dijaga test pemindai.
- [x] **T1.3 — Registry 36 uji sebagai kode**, dengan sumber dideklarasikan per sisi (lima jenis). Seluruhnya terdaftar termasuk yang belum berimplementasi.
- [x] **T2.1 — Penarik lewat pembaca yang sudah ada**, gagal-tertutup dan berisik.
- [x] **T2.2 sampai T2.3 — Enam penjalan uji**, mencakup tiga jenis sumber sehingga rancangan adapternya benar-benar teruji.
- [x] **T2.4 — Penyimpanan hasil per periode**, idempoten lewat index unik.
- [x] **T3.1 — Kertas kerja yang bisa disimpan sebagian**, delapan keadaan baris.
- [x] **T3.2 — Jejak before/after**, dan kegagalan menulisnya menggagalkan aksinya.
- [x] **T3.3 — Register temuan lima unsur**, terpisah dari `quality_capa`.
- [x] **Mesin sampling** — lantai 5 untuk acak, benih `crypto/rand`, populasi tercatat, metode diambil dari registry bukan dari permintaan.
- [x] **Endpoint `/accounting/riwayat-akun`** di integration, bergerbang kunci layanan.

---

## Fase 1b — Utang dari review (WAJIB sebelum dipakai)

- [ ] ⛔ **Bangun `/internal/audit/pemasok` di procurement-service.** Mengembalikan `vendor_no`, nama, nama wajib pajak, tipe & nomor wajib pajak, email, telepon. **Bergerbang sendiri** — `/internal/` bukan batas keamanan.
- [ ] ⛔ **Bangun `/internal/audit/karyawan` di employee-service.** Mengembalikan `employee_id`, nama, NIK, NPWP, email, telepon. Bergerbang sendiri.
  Sampai keduanya ada, uji silang pemasok berkeadaan `gagal_tarik` dengan sebab terbaca — bukan bersih. Ini uji yang matriksnya sendiri sebut harus didahulukan.
- [ ] ⚠️ **Perbaiki kontrak `SetelanSampel.Akun`** yang didokumentasikan sebagai NAMA tetapi dipakai sebagai NOMOR pada jalur buku besar. Pisahkan jadi dua field, atau satukan lewat resolusi nama-ke-nomor yang rumahnya di integration-service.
  ⛔ **Wajib selesai sebelum Direksi menyetel akun untuk pertama kali** — sesudah itu menuntut migrasi setelan.
- [ ] **Putuskan nasib mesin pencatat reproduksibilitas sampel** (`PenarikanSampel`, `BenihAcak`, `auditSampelCollection`): buang, atau sambungkan saat uji bermetode acak pertama berjalan.

---

## Fase 2 — Layar (belum mulai)

- [ ] **Halaman kertas kerja bulanan.** Struktur tabel HRIS: satu kartu, `Banner bare` di dalam `toolbar` milik `MainTable`, keadaan di `useTableState`. Ikuti skill `/migrasi-tabel-hris`.
  ⛔ Urutan menaikkan **kelompok 1** ke atas, bukan yang paling merah. Baris `menunggu_data` dan `belum_diimplementasi` **tidak disembunyikan**.
  ⛔ Daftar 36 uji dibaca dari `GET /audit/uji`, jangan disalin ke sisi layar.
  ⚠️ Jangan menambah `p-6`; tombol kembali memakai `SidebarBackButton`; teks lewat `react-i18next` di **dua** locale.
- [ ] **Halaman detail satu uji.** Acuan reuse: layar rekonsiliasi tiga lapis di `integration-accurate/rekonsiliasi` sudah punya pola dua kolom selisih dan status berwarna.
- [ ] **Menu, izin sidebar, dan gerbang rute.**
  ⛔ **Izin tanpa entri di tabel `FALLBACK` DILOLOSKAN untuk semua orang.** Lupa menulisnya bukan menu yang hilang, melainkan menu audit yang terbuka bagi siapa saja.
- [ ] **Tutup titik putus alur**: baris yang ditinjau harus punya tautan langsung ke pembuatan temuan, kalau tidak penelusuran keluar sistem tak punya tempat kembali.

---

## Fase 3 — Verifikasi

- [ ] ⛔ **Tambahkan blok `finance-service` ke `docker-compose.dev.yml`.** Sekarang tidak ada sama sekali, jadi seluruh modul ini **tak dapat dicoba lewat gateway di mana pun**. Ini penghalang terbesar untuk gerbang `/wrap`.
- [ ] **Satu perjalanan utuh sebagai orang**: buka kertas kerja, buka uji yang berbunyi, tandai wajar dengan alasan, naikkan satu jadi temuan, isi lima unsurnya.
  ⛔ `curl` ke endpoint **tidak menggantikan ini**.
- [ ] **Kontrol negatif per uji**: buktikan tiap uji bisa MERAH, bukan cuma hijau. Uji yang selalu lolos karena penarikannya diam-diam gagal tak bisa dibedakan dari uji yang lolos karena bukunya benar.
- [ ] **Matikan `INTEGRATION_MODULE_URL` di dev**, pastikan barisnya `gagal_tarik` dan bukan nol.
- [ ] **Urutan deploy**: integration-service lebih dulu, baru finance-service, keduanya `--force-recreate` karena ada env baru.

---

## Yang sengaja TIDAK ada di daftar ini

- **Pembukuan 40 CV** — menunggu [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]]; pengambil keputusannya SPV FAT + IT.
- **Rekonsiliasi rekening koran terhadap buku besar** — benar-benar kosong, menuntut alur unggah tersendiri. Layak jadi ADR sendiri.
- **Modul I (transaksi antar-entitas)** — keempat endpoint laporan yang dipakai hari ini buta entitas.
- **Penilaian kewajaran otomatis** — modul menunjukkan selisih lalu berhenti.
