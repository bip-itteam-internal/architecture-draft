# ANALISA - Modul Audit Pembukuan Accurate

Pecahan kerja untuk [[ADR - 0073 Modul Audit Memakai Pembaca Accurate yang Ada dan Memegang Kertas Kerjanya Sendiri]]. Dok domainnya [[Finance - Audit Pembukuan Accurate]].

**Bukan rencana per berkas.** Tiap item cukup jelas untuk langsung dilempar ke `/start-task`, dan `/plan` yang menurunkannya jadi langkah.

Disusun 2026-09-02. Status keseluruhan: 🟡 belum ada satu pun kode.

---

## Fase 0 — Gerbang kelayakan (WAJIB lebih dulu, tanpa kode produksi)

Ketiganya membaca produksi dan tak satu pun menulis. Menulis prod dijalankan manusia, bukan agent.
Total perkiraan hitungan jam, dan hasilnya menentukan ruang lingkup Fase 2 sampai 4.

### T0.1 — Jalankan probe jejak audit Accurate ke produksi
Jalankan `services/integration/cmd/incaudit` terhadap beberapa dokumen nyata, lalu **catat hasilnya di dok domain**, bukan cuma di terminal. Probe ini sudah ada dan dibangun persis untuk pertanyaan ini; hasilnya tidak pernah tercatat di mana pun.
**Menjawab**: apakah dokumen Accurate membawa penanda pembuat, pengubah, dan waktunya.
**Menyandera**: 5 uji (penghapusan bukti kas keluar, penghapusan jurnal, perubahan harga beli, pembuat lawan penyetuju, sebaran aktivitas pengguna).
**Selesai bila**: hasilnya tertulis di [[Finance - Audit Pembukuan Accurate]] §Belum Diputuskan, dan kelima uji itu dipindahkan ke "bisa" atau ke "dinyatakan mustahil". Tidak boleh berhenti sebagai "belum dicek".
**Dependensi**: tidak ada.

### T0.2 — Coba tarik matriks hak akses Accurate
Panggil `access-privilege/list.do` dan `detail.do` sekali terhadap database produksi. Endpoint ini terdaftar di schema resmi dan hanya berbentuk baca, tetapi belum pernah dipanggil dari mana pun di repo.
**Menjawab**: apakah seluruh Modul G bisa ada.
**Sekalian periksa**: apakah pembatasan tanggal transaksi, periode tutup buku, dan status 2FA terekspos lewat jalur mana pun. Ketiganya tidak ditemukan di schema, tetapi schema itu terbukti tidak lengkap.
**Selesai bila**: bentuk responsnya tercatat, dan Modul G dinyatakan bisa atau tidak.
**Dependensi**: tidak ada.

### T0.3 — Periksa apakah dokumen Bayar Uang membawa rekening penerima
Tarik satu dokumen `purchase-payment` dan periksa amplop mentahnya.
**Menjawab**: apakah uji "penerima pembayaran" dan "master vendor lawan karyawan" punya sumbu rekening.
**Selesai bila**: bila tidak ada, kedua uji itu **dinyatakan tidak dijanjikan** di dok domain, bukan ditunda diam-diam. Sumbu silang yang tersisa (NPWP, NIK, nama, alamat, telepon, email) ditegaskan sebagai satu-satunya yang dipakai.
**Dependensi**: tidak ada.

---

## Fase 1 — Kerangka modul

### T1.1 — Katalog izin modul `audit`
Buat `shared-library/common/catalog_audit.go` berisi konstanta modul, izin, dan paket bawaan; daftarkan lewat `RegisterCatalog` di service penegaknya **dan** di `services/employee/permission_catalogs.go`.
⚠️ Tanpa pendaftaran kedua, izinnya tidak muncul di dropdown penyusun permission set dan ditolak `ValidatePermissionSet`.
**Pertimbangkan**: pemisahan antara melihat kertas kerja, menandai tinjauan, dan menerbitkan laporan. Yang menandai tidak otomatis boleh menerbitkan.
**Dependensi**: tidak ada.

### T1.2 — Kerangka `services/audit` + rute akar
Service baru, koleksi sendiri, terdaftar di compose dev dan prod, dan **rute akar didaftarkan di `app.Get("/")`, bukan `app.Get("/audit")`** karena gateway membuang prefiks modul.
⚠️ Rute literal wajib didaftarkan sebelum saudara ber-`:param` di prefiks yang sama; yang tertelan membalas 200 berisi data yang masuk akal, bukan 404.
**Selesai bila**: satu rute sehat terpanggil **lewat gateway**, bukan lewat path lokal ke Fiber.
**Dependensi**: T1.1.

### T1.3 — Registry uji sebagai satu sumber
Definisi 48 uji hidup di satu tempat: kode uji, modul A sampai I, kelompok pembanding 1 sampai 4, pelaksana (sistem/campuran/manual), sumber tiap sisi, dan ambangnya.
⛔ **Satu fakta satu tempat.** Daftar ini tidak boleh disalin ke frontend; layar membacanya dari API.
**Dependensi**: T1.2, dan hasil Fase 0 menentukan uji mana yang berstatus "mustahil".

---

## Fase 2 — Penjalan uji

### T2.1 — Penarik data lewat pembaca yang sudah ada
Klien internal ke `/accounting/*` dan saudaranya memakai pola `routes.InternalRequest`.
⛔ **Gagal-TERTUTUP dan berisik**, kebalikan dari gerbang presensi di attendance. Kegagalan pengambilan wajib jadi keadaan tersendiri di layar, tidak boleh jatuh jadi nol atau baris yang hilang.
⚠️ URL service jangan dimasukkan ke map yang divalidasi `ValidateInternalURL`; nilai kosong di sana memanik dan menolak boot.
**Dependensi**: T1.2.

### T2.2 — Uji kelompok 4 (pembandingnya aturan) lebih dulu
Mulai dari yang tidak butuh sisi lawan: saldo kas tidak pernah negatif, barang dalam proses tidak negatif, hitung ulang penyusutan, umur uang muka, vendor baru bervolume besar, duplikasi alamat kirim pelanggan.
**Alasan urutan**: paling sedikit ketergantungan, dan langsung menghasilkan uji yang berbunyi di baseline.
**Dependensi**: T2.1, T1.3.

### T2.3 — Uji kelompok 3 (kedua sisi dari Accurate)
Buku besar lawan buku pembantu piutang dan utang, aset tetap lawan neraca, PPN keluaran lawan pendapatan.
⛔ **Baca dulu §Aturan Kolom di dok domain sebelum menulis satu baris pun.** Enam aturan di sana masing-masing menghasilkan angka salah yang masuk akal bila dilanggar.
⛔ Hasil kelompok ini **tidak boleh** jadi ringkasan teratas layar.
**Dependensi**: T2.2.

### T2.4 — Penyimpanan hasil uji per periode
Hasil disimpan supaya bisa dibandingkan antar bulan, dan item yang berulang terlihat berulang beserta alasan yang ditulis periode lalu.
**Alasan**: selisih piutang di baseline bertahan dua periode. Tanpa ini, tiap bulan terbaca sebagai temuan baru dan yang bertahan enam bulan tidak pernah terlihat menua.
**Dependensi**: T2.2.

---

## Fase 3 — Kertas kerja & temuan

### T3.1 — Kertas kerja yang bisa disimpan sebagian
Keadaan per baris: menunggu data, sudah dibandingkan, ditinjau-wajar, ditinjau-jadi-temuan, tidak berlaku. Pengisian berlangsung H+1 sampai H+8.
**Dependensi**: T2.4.

### T3.2 — Jejak tinjauan dengan before dan after
⛔ **Menandai "wajar" WAJIB menuntut alasan tertulis**, dan perubahannya menyimpan siapa, kapan, dan nilai sebelum serta sesudah. Catatan ini **adalah bukti auditnya**, bukan metadata.
Pola acuannya `audit_logs` di insentive-service, satu-satunya di repo yang menyimpan before/after per field. `metadata.updated_by` **tidak cukup** karena hanya mencatat siapa terakhir menyentuh.
**Alasan**: checklist yang bisa dicentang tanpa alasan berubah jadi stempel, dan hasilnya lebih buruk daripada tidak ada modul karena menghasilkan bukti tertulis bahwa 48 uji sudah diperiksa.
**Dependensi**: T3.1.

### T3.3 — Register temuan lima unsur
Kondisi, kriteria, akar penyebab, dampak, rekomendasi, plus klasifikasi mayor, moderat, atau minor.
⛔ **Koleksi terpisah, jangan menumpang `quality_capa`.** `CAPA_AREAS` dikunci `["Produksi","Gudang"]` dan dipakai persis oleh metrik KPI yang sudah berjalan.
**Catatan rancangan**: kolom akar penyebab lahir kosong dan diisi pemeriksa. Sistem tidak menyimpulkan sebab.
**Dependensi**: T3.1.

---

## Fase 4 — Layar

### T4.1 — Halaman kertas kerja bulanan
Struktur tabel HRIS: satu kartu, `Banner bare` di dalam prop `toolbar` milik `MainTable`, seluruh keadaan di `useTableState`. Ikuti skill `/migrasi-tabel-hris`.
⛔ Urutan menaikkan **kelompok 1** ke atas, bukan yang paling merah. Baris "menunggu data" tidak disembunyikan: uji yang hilang dari layar terbaca sebagai uji yang lolos.
⚠️ Jangan menambah `p-6`; `Container` sudah memasang padding. Tombol kembali memakai `SidebarBackButton`.
⚠️ Teks user-facing lewat `react-i18next`, key di `id.ts` **dan** `en.ts`.
**Dependensi**: T3.1.

### T4.2 — Halaman detail satu uji
Dua sisi pembanding berdampingan, selisihnya, sumber tiap sisi, batas yang diterima, dan umur selisihnya.
**Acuan reuse**: layar rekonsiliasi tiga lapis di `integration-accurate/rekonsiliasi` sudah punya pola dua kolom selisih, status empat keadaan, dan toleransi pembulatan. Pakai komponennya, jangan bikin tiruan.
**Dependensi**: T4.1.

### T4.3 — Menu, izin sidebar, dan gerbang rute
⛔ **Izin tanpa entri di tabel `FALLBACK` DILOLOSKAN untuk semua orang.** Lupa menulisnya bukan menghasilkan menu yang hilang, melainkan menu audit yang terbuka bagi siapa saja.
⚠️ Prefiks izin menentukan kategori sidebar, jadi prefiksnya bukan sekadar penamaan.
**Dependensi**: T4.1, T1.1.

---

## Fase 5 — Verifikasi

### T5.1 — Satu perjalanan utuh sebagai orang
Buka modul, lihat kertas kerja bulan berjalan, buka satu uji yang berbunyi, tandai wajar dengan alasan, buka satu lagi dan naikkan jadi temuan, lalu isi lima unsurnya.
⛔ **`curl` ke endpoint tidak menggantikan ini.** Test hijau bukan bukti fitur bisa dipakai; riwayat repo ini punya fitur yang merged, deployed, dan tetap mustahil dipakai selama tiga hari karena lapisan pengikatan request tidak ikut diperbarui.
**Dependensi**: seluruh Fase 4.

### T5.2 — Kontrol negatif untuk tiap uji yang dibangun
Buktikan tiap uji **bisa merah**, bukan cuma hijau. Uji yang selalu lolos karena penarikannya diam-diam gagal tidak dapat dibedakan dari uji yang lolos karena bukunya benar.
**Dependensi**: T5.1.

---

## Yang sengaja TIDAK ada di daftar ini

- **Pembukuan 40 CV.** Menunggu [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]] diputuskan; pengambil keputusannya SPV FAT + IT.
- **Rekonsiliasi rekening koran terhadap buku besar.** Benar-benar kosong dan menuntut alur unggah tersendiri. Layak jadi ADR sendiri, bukan menempel di sini.
- **Modul I (transaksi antar-entitas).** Keempat endpoint laporan yang dipakai hari ini buta entitas.
- **Penilaian kewajaran otomatis.** Modul menunjukkan selisih lalu berhenti.
