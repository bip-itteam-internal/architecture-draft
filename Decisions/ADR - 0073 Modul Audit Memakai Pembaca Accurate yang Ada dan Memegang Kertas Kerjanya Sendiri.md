## Untuk Manajemen

- **Yang berubah di layar**: modul baru berisi kertas kerja audit bulanan, satu baris per pengujian, dan register temuan yang menuliskan kondisi, kriteria, akar penyebab, dampak, dan rekomendasi. Angka kedua sisi pembanding sudah berdampingan beserta selisihnya, sehingga auditor **menilai**, bukan menghitung ulang.
- **Siapa terdampak**: auditor internal sebagai pemakai utama. Posisi itu **belum ada**, dan sampai terisi modulnya dipakai review silang antar-divisi. Direktur sebagai penerima laporan. Finance sebagai pihak yang dimintai klarifikasi, bukan sebagai pemakai.
- **Tidak dijanjikan**: modul ini **tidak menyimpulkan kecurangan**, ia menunjukkan selisih lalu berhenti. Ia **tidak menggantikan** hitung fisik kas dan gudang, konfirmasi saldo ke pelanggan, maupun pengambilan rekening koran dari bank. Ia **tidak mencakup pembukuan 40 CV**. Dan lima pengujian yang tampak otomatis di atas kertas bergantung pada jejak pelaku di Accurate yang **belum terbukti tersedia** lewat API.
- **Besaran kerja**: sedang. Sebagian besar datanya sudah ditarik sistem hari ini, jadi yang dibangun adalah penjalan uji, kertas kerja, dan register temuan. Yang bisa membesar tak terduga hanya bila ketiga gerbang kelayakan di bawah menjawab tidak.

## Deskripsi

*Modul audit dibangun sebagai konsumen pembaca Accurate yang sudah ada, bukan sebagai klien Accurate keempat, dan memegang sendiri kertas kerja beserta jejak tinjauannya alih-alih menumpang form-builder. Kedua sisi keputusan ini berangkat dari alasan yang sama: yang menentukan kelayakan pakai-ulang bukan kemiripan bentuk, melainkan kontrak yang harus dipenuhi.*

- **Status**: 🟡 **Diusulkan**, 2026-09-02. Kode belum ada. Tiga gerbang kelayakan di §6 belum dijalankan, dan dua di antaranya menentukan apakah sebagian modul bisa ada sama sekali.
- **Path di repo**: `bip-erp/services/audit/` (baru) · `bip-erp/shared-library/common/catalog_audit.go` (baru) · `bip-erp/services/employee/permission_catalogs.go` (disunting) · `bip-erp/docker-compose.yml` + `docker-compose.dev.yml` (disunting) · `erp-frontend/src/app/(main)/audit/**` (baru) · `erp-frontend/src/components/layout/sidebar-menus.tsx` + `src/utils/menu-permission.ts` (disunting)
- **Tanggal**: 2026-09-02

## Context

Kebutuhan datang sebagai solusi: sebuah dokumen prosedur berisi sembilan modul pengujian bulanan atas pembukuan Accurate, lengkap dengan jadwal H+1 sampai H+8, disusul matriks 48 pengujian yang memetakan tiap uji ke asal sisi pembandingnya. Wawancara menyempitkannya jadi kebutuhan yang berbeda: **auditnya sudah berjalan manual dan prosedurnya sudah terbukti sekali dipakai; yang membakar waktu adalah menarik dan mencocokkan datanya.** Kertas kerja audit posisi 6 Agustus 2026 adalah buktinya.

Satu hal yang tidak disadari dokumen sumbernya perlu dicatat karena ia justru nilai terbesar modul ini. Dokumen itu menulis bahwa otomasi tidak memperbaiki independensi karena datanya tetap diekspor manusia lebih dulu. Itu benar untuk ekspor Excel, tetapi tidak berlaku bila ERP menarik lewat kredensial sistem: angka yang diperiksa tidak pernah melewati tangan divisi yang sedang diaudit.

**Yang sudah ada jauh lebih banyak dari yang diperkirakan dokumen itu.** `integration-service` sudah menjadi pembaca Accurate yang serius dan **nol tulis**, menyuplai dashboard FAT lewat grup `/accounting/*` ([[API - Integration Service]] `:131-153`): laporan keuangan, saldo per akun, jurnal umum berhalaman sekitar 96 ribu baris, umur piutang B2B beserta DSO, aset tetap dari salinan Mongo, PPN masukan, dan saldo satu akun generik. Buku besar per akun ditarik lewat `glaccount/history.do` (`services/integration/internal/infrastructure/clients/accurate_client_riwayat_akun.go:90`), umur utang sudah tayang lewat `services/procurement/aging_utang.go`, dan deteksi edit manual di Accurate sudah menyimpan diff utuh di koleksi `external_edit_drafts`.

[[ADR - 0001 Akuntansi via Accurate]] tidak menghalangi ini. Yang dilarangnya **membangun** general ledger sendiri (`:13`) dan **menulis balik sembarangan** (`:20`); pembacaan read-only justru dicatat sebagai konsekuensi positif (`:18`).

Tiga kenyataan membatasi rancangannya, dan ketiganya ditemukan lewat penelusuran kode, bukan diasumsikan:

1. **Sudah ada tiga klien Accurate terpisah** (`services/integration/.../accurate_client.go`, `services/procurement/accurate_client.go`, `shared-library/accurate/accurate.go`), dan seluruhnya berbagi limiter yang dijaga 6 permintaan per detik dengan pemutus arus per slot token (`accurate_client.go:315-320`, `:483-535`). Klien keempat memakan jatah yang sama sekaligus melahirkan pembaca kedua atas angka yang sudah dibaca dashboard FAT.
2. **Master pemasok tidak menyimpan nomor rekening sama sekali** (`services/procurement/models.go:91-155`). Dua pengujian di matriks bersandar pada rekening sebagai sumbu silang, dan keduanya karena itu tidak dapat dijalankan dengan data yang ada.
3. **Jejak pelaku di Accurate belum terbukti ada.** Tidak ada endpoint log aktivitas di schema resmi, dan bip-erp tidak pernah memanggilnya. Repo bahkan sudah punya probe yang dibangun persis untuk pertanyaan ini, `services/integration/cmd/incaudit/main.go`, yang membuka dirinya dengan kalimat *"menjawab satu pertanyaan yang terlanjur saya jawab tanpa memeriksanya"* — dan hasilnya tidak pernah tercatat di mana pun.

⚠️ **Schema resmi Accurate terbukti tidak lengkap**, jadi ketiadaan di sana bukan bukti ketiadaan endpoint. `glaccount/history.do`, `report/profit-loss.do`, dan `report/balance-sheet.do` dipanggil produksi hari ini dan tak satu pun terdaftar di `account.accurate.id/open-api/json.do`.

**Form-builder diperiksa sebagai kandidat mesin checklist dan tidak menampung.** Dari lima sifat yang dibutuhkan, satu terpenuhi. Rinciannya di §2 Decision.

## Decision

### 1. Modul audit adalah KONSUMEN, bukan pembaca Accurate keempat

Seluruh angka ditarik lewat `/accounting/*` dan saudara-saudaranya yang sudah ada, dengan pola `routes.InternalRequest` yang sudah dipakai sumber KPI di employee-service (`services/employee/kpi_sumber_aset.go:106-123`). Modul audit **tidak memegang kredensial Accurate** dan tidak menambah satu pun panggilan langsung.

Konsekuensi yang diterima sadar: modul terikat pada bentuk endpoint yang ada, dan beberapa uji menuntut field yang belum diekspos. Yang paling nyata, `/accounting/journals` punya filter tanggal tetapi **tidak punya penanda mana jurnal yang merupakan koreksi**, sehingga yang terhitung seluruh jurnal (sudah tercatat di `erp-frontend/src/features/finance/posisi/data/senior-acc.ts:73`). Menambah field ke endpoint yang sudah ada lebih murah daripada memelihara pembaca kedua.

**Ditolak: menempelkan modul ini ke dalam `integration-service`** supaya tak ada lompatan HTTP sama sekali. Alasannya RBAC: service itu tidak memanggil `RegisterCatalog` satu kali pun, dan satu-satunya gerbang izinnya `RequireMenuLaporanKeuangan` pada satu rute. Menaruh modul yang harus dibatasi ke satu peran di dalam service yang sengaja tak punya perkakas izin berarti membangun perkakas itu di tempat yang salah.

### 2. Kertas kerja dan jejak tinjauan dipegang modul sendiri, BUKAN form-builder

Pemeriksaan `services/form-builder` menemukan empat dari lima sifat tidak terpenuhi, dan dua di antaranya fatal:

- ⛔ **Tidak bisa simpan sebagian.** `FormResponse` tidak punya field status maupun draft; yang ada hanya `submitted_at` yang diisi saat insert (`models_response.go:20-70`), dan validasi `required` dijalankan penuh saat kirim. Audit berjalan H+1 sampai H+8, jadi ini bukan penyesuaian kecil melainkan pembatalan alur kerjanya.
- ⛔ **Tidak ada jejak perubahan, bahkan `updated_by` pun tidak.** Field itu hanya ada di `form_type_rules` (`models_type_rules.go:38`), tidak pernah pada response maupun form. Lebih jauh, jejak keputusan lama justru **dihapus** saat sebuah butir diperbaiki lewat `$unset` (`laporan_handlers.go:621-624`). Untuk modul yang seluruh nilainya terletak pada catatan tinjauan yang bisa dipertanggungjawabkan, ini mendiskualifikasi.
- ⛔ **Baris tidak bisa membawa nilai terhitung.** `FormField` tidak punya slot nilai (`models_form.go:222-254`) dan `Answer` hanya `Key` + `Value` (`models_response.go:14-17`). Memaksakan empat nilai per baris jadi empat field berarti 192 field, melewati `maxFieldsPerForm = 100` (`validate.go:15`).
- ⚠️ **Alasan tertulis hanya diwajibkan saat MENOLAK**, tidak saat menerima (`kaizen_decision.go:73-75`). Yang kita butuhkan justru kebalikannya: setiap "wajar" wajib beralasan.

⛔ **`FormTypeChecklist` tidak memberi apa pun selain namanya.** Komentar di `models_form.go:102-110` menyatakannya sendiri: tipe `request` sudah dihapus karena cuma label dan satu tab, lalu ditambahkan bahwa *"`checklist` berdiri sama persis, jadi yang membedakan keduanya keputusan produk, BUKAN keterikatan di kode"*.

Argumen penutupnya datang dari peringatan form-builder sendiri (`laporan_decision.go:55-59`): mengganti sebuah key membuat kiriman lama tersangkut permanen, dan menghapus key membuat kiriman yang masih menunggu terbaca "disetujui" lalu lenyap dari antrean tanpa pernah ditinjau siapa pun. Untuk survei itu ketidaknyamanan; untuk kertas kerja yang harus dapat dibandingkan antar bulan, itu berarti temuan bulan lalu bisa hilang karena seseorang menyunting redaksi ujinya.

**Jejak tinjauan meniru pola `audit_logs` di insentive-service** (`services/insentive/main.go:369-414`), satu-satunya di repo yang menyimpan `before` dan `after` per field.

### 3. Register temuan terpisah dari `quality_capa`

Modul Quality sudah punya register temuan lengkap dengan persetujuan berjenjang dan dua jenis bukti. Ia tidak dipakai ulang karena `CAPA_AREAS` dikunci `["Produksi", "Gudang"]` dan nilainya **mencerminkan backend serta dipakai metrik KPI `temuan_capa_produksi`**, dengan komentar yang menuntut nilainya sama persis (`erp-frontend/src/features/quality/capa/types/capa.ts:41-44`). Menambahkan area finance ke sana mengotori metrik yang sudah berjalan demi satu pemanggil baru.

### 4. Gagal-TERTUTUP dan berisik, kebalikan dari gerbang presensi

`services/attendance/form_gate.go:19-31` sengaja **gagal-terbuka** di semua jalur galat, dan itu benar di sana: kehilangan gerbang form lebih ringan daripada karyawan tak bisa absen.

Untuk modul audit keputusannya **dibalik**. Daftar uji yang kosong karena sumbernya tak terjangkau terbaca sebagai "tidak ada yang perlu diperiksa", dan itu persis kelas kegagalan yang modul ini ada untuk menutupnya. Setiap kegagalan pengambilan wajib muncul sebagai keadaan tersendiri di layar, tidak boleh jatuh jadi nol maupun jadi baris yang hilang.

Berlaku juga untuk penamaan: `salinan_kosong: true` berarti belum pernah disinkron, **bukan** nilai nol, mengikuti pola yang sudah dipakai `/accounting/ppn-masukan` dan `/accounting/fixed-assets`.

### 5. Hasil uji berpembanding internal TIDAK menjadi ringkasan teratas

Matriks 48 uji mengelompokkannya menurut asal sisi pembanding. Kelompok yang kedua sisinya sama-sama dari dalam Accurate berjumlah 13 dan hampir seluruhnya otomatis, dan **justru karena itu paling lemah**: pembukuan yang dirapikan secara utuh lolos semuanya tanpa memunculkan apa pun.

Karena itu layar tidak boleh membuka dengan hasil kelompok tersebut. Yang naik ke atas adalah uji berpembanding dari luar perusahaan beserta keadaan pengerjaannya, meski sebagian besarnya menunggu manusia. Layar yang membuka dengan dua belas uji hijau memproduksi rasa aman yang tidak dijamin oleh ujinya.

### 6. Tiga gerbang kelayakan dijalankan SEBELUM implementasi

1. **Jalankan `cmd/incaudit` ke prod (baca saja).** Apakah dokumen Accurate membawa jejak pelaku. **Lima uji bertanda Sistem berdiri di atas jawabannya**: penghapusan bukti kas keluar, penghapusan jurnal, perubahan harga beli, pembuat lawan penyetuju, dan sebaran aktivitas pengguna. Yang terakhir menuntut alamat IP per pengguna dan paling tipis harapannya.
2. **Coba `access-privilege/list.do`.** Terdaftar di schema resmi dan hanya berbentuk baca, yang justru pas untuk audit, tetapi belum pernah dipanggil dari mana pun. Seluruh Modul G berdiri di atasnya.
3. **Periksa apakah dokumen Bayar Uang di Accurate membawa rekening penerima.** Bila tidak, dua pengujian dinyatakan mustahil dan **tidak dijanjikan ke manajemen**, bukan ditunda diam-diam.

Ketiganya berbentuk pembacaan produksi. Menulis prod dijalankan manusia, bukan agent.

### 7. Cakupan berhenti di pembukuan PT, dan itu dicatat sebagai risiko terbuka

Penjualan ke konsumen akhir, sebagian besar beban iklan, dan payroll advertiser dibukukan di 40 CV lewat aplikasi di luar ERP maupun Accurate. Aplikasi itu berjalan **tanpa jejak audit** (tidak ada `created_by`/`updated_by`/`deleted_at` maupun tabel log), **tanpa kunci periode**, dengan tujuh kredensial plaintext di bundel yang terkirim ke setiap peramban, dan tombol yang menghapus transaksi seluruh 40 CV sekaligus. Rinciannya di [[APP - Buku Besar Konsolidasi CV FINCON]].

Modul audit **tidak** menjangkaunya, karena arahnya masih terkunci [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]] yang belum diputuskan dan pengambil keputusannya SPV FAT + IT. Yang tidak boleh terjadi adalah cakupan ini hilang diam-diam: modul yang memeriksa buku pertama dengan teliti sementara buku kedua tak punya satu pun kontrol akan terbaca sebagai jaminan yang tidak pernah diberikan.

## Consequences

- ➕ Tidak ada integrasi Accurate baru untuk sebagian besar modul. Lima belas dari 24 uji bertanda Sistem sumbernya sudah ditarik hari ini.
- ➕ Independensi terjaga di lapisan penarikan: angka tidak pernah melewati tangan divisi yang diaudit. Ini manfaat yang bahkan tidak diklaim dokumen prosedurnya.
- ➕ Limiter Accurate tidak menerima beban pemanggil baru, dan tidak lahir pembaca kedua atas angka yang sama.
- ➖ Modul terikat pada bentuk endpoint yang ada. Uji yang menuntut field belum tersedia harus menunggu endpointnya diperluas, bukan diselesaikan sendiri.
- ➖ Lima uji tidak dapat direncanakan sampai gerbang §6.1 dijawab, dan dua uji kemungkinan dinyatakan mustahil oleh §6.3.
- ⚠️ **Service baru menuntut perhatian deploy.** Riwayat repo ini menunjukkan `deploy.yml` tidak dengan sendirinya mencakup service baru, dan gateway menuntut `--force-recreate` untuk env baru, bukan `restart`. Lihat [[RUN - Deploy Microservices bip-erp]].
- ⚠️ **Izin wajib didaftarkan DUA kali**: di service penegaknya dan di `services/employee/permission_catalogs.go`. Tanpa yang kedua, izinnya tidak muncul di dropdown penyusun permission set dan akan ditolak `ValidatePermissionSet`.
- ⚠️ **Di frontend, izin tanpa entri di tabel `FALLBACK` DILOLOSKAN untuk semua orang** (`erp-frontend/src/utils/menu-permission.ts:503-505`). Lupa menulisnya bukan menghasilkan menu yang hilang, melainkan menu audit yang terbuka bagi siapa saja.
- ⚠️ Pemakai utamanya belum ada. Sampai posisi auditor internal terisi, modul dipakai review silang antar-divisi, dan rancangan layarnya harus tetap masuk akal untuk pemakai sementara itu.

## Dokumen Terkait

- [[Finance - Audit Pembukuan Accurate]] — dok domain: cara kerjanya, 48 uji, dan batas tiap kelompok
- [[ADR - 0001 Akuntansi via Accurate]] · [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]]
- [[ADR - 0066 Salinan Dokumen Retur Accurate + Pemindai Drift]] — pola cermin dan pemindai drift yang dipakai ulang di sini
- [[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]] · [[ADR - 0067 Opname Perlengkapan GA via Rekonsiliasi Accurate]] — pola menyajikan dua angka berdampingan
- [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] · [[CORE - RBAC dan Permission Set]]
- [[API - Integration Service]] · [[Microservices - Integration Service]] · [[External - Accurate]]
- [[APP - Buku Besar Konsolidasi CV FINCON]] · [[Finance - Big Pictures]]
