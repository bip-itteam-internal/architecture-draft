# ADR - 0181 Portal Persetujuan Memuat Keputusan dan Tindakan Operasional

> **Status**: 🟢 Diterima, 2026-10-15, oleh irfanarfianto. Pemutus: irfanarfianto. Kode belum ada. Nama menu dan judul tetap "Persetujuan" (keputusan user 2026-10-15). Butir 13 (aturan untuk fitur baru) ditambahkan saat diterima. ADR ini **mengubah sebagian** [[ADR - 0114 Antrean Persetujuan Terpusat di Web, Satu Tabel Seragam dari Agregator Employee-Service]] (butir 1, 4, 5, 10, dan arti "antrean" di seluruh dokumennya) dan [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]] (§4 butir "Persetujuan hanya berisi hal yang menunggu keputusan pembaca").

## Untuk Manajemen

**Apa yang berubah di layar.** Halaman "Persetujuan" di web tetap bernama sama, tetapi isinya bertambah: bukan hanya yang menunggu disetujui atau ditolak, tetapi juga pekerjaan yang menunggu tangan pembaca, seperti menjawab cek stok, mengisi harga, mentransfer dana, mengonfirmasi transfer, mencatat ke accounting, dan memilah tiket. Tiap baris menyebut dengan kalimat biasa **apa yang harus dilakukan**, nomor dokumen, nominal, dan sudah berapa lama menunggu. Yang paling lama menunggu tampil paling atas. Klik baris membuka panel di samping berisi rincian dokumen dan tombol yang tepat untuk langkah itu.

**Kenapa.** Diukur di produksi 2026-10-15: dari seluruh antrean pengajuan barang, tiket, dan setoran live yang berjalan, **hanya 2 dari ±380 dokumen** yang benar-benar menunggu keputusan. Sisanya, sekitar 99%, menunggu pekerjaan operasional. Halaman yang hanya memuat keputusan akan hampir selalu kosong, sementara orang yang paling banyak ditunggu (Gudang GA, AP, Accounting) tetap harus mencari pekerjaannya di modul masing-masing.

**Siapa yang terdampak.** Semua karyawan melihat menunya, tetapi kebanyakan staf akan melihat halaman kosong yang menjelaskan fungsinya. Yang benar-benar memakainya: SPV Finance, Staff Accounting, AP, Gudang GA, kepala divisi yang memilah tiket, dan Direktur.

**Yang tidak dijanjikan.**
- Tidak ada perubahan siapa berwenang memutus atau mengerjakan apa. Seluruh tombol tetap memanggil endpoint milik modul asalnya.
- Tidak ada tombol "Setujui lalu buka berikutnya"; sesudah satu tindakan, panel tertutup dan kembali ke daftar.
- Tidak ada penanda "terlambat" atau batas waktu (SLA) dulu, karena batas resminya belum ada. Satu pengecualian diusulkan untuk tiket yang menunggu dipilah lebih dari 7 hari.
- Pencatatan massal ke accounting tidak dibangun di sini; itu kebutuhan terpisah.

**Perkiraan besaran kerja** (kasar, belum melewati `/plan`). Irisan perbaikan bug: satu sampai dua hari. Fondasi kontrak baru di agregator dan tabel baru: tiga sampai lima hari, backend lebih dulu. Panel per kategori: satu sampai tiga hari per kategori, dimulai dari Pengajuan Barang dan Tiket. Pecahan kerjanya di [[ANALISA - Portal Persetujuan Memuat Tindakan Operasional]].

## Deskripsi

*Halaman `/portal/persetujuan` ("Persetujuan") memuat semua yang menunggu tindakan pemanggil, baik keputusan maupun tindakan operasional. Agregator employee-service mengirim kode tindakan (`aksi`) per baris; frontend hanya menerjemahkannya ke kalimat dua bahasa. Klik baris membuka Sheet berkerangka bersama yang badannya memakai komponen detail milik modul. Riwayat memuat dokumen yang pernah pemanggil proses beserta posisinya saat ini.*

- **Status**: 🟢 Diterima, kode belum ada (lihat baris status di atas)
- **Path di repo** (akan disentuh): `bip-erp/services/employee/antrean_pengajuan.go` · `bip-erp/services/procurement/pengajuan_barang_diproses_saya.go` (disambung, tidak diubah perilakunya) · `erp-frontend/src/app/(main)/portal/persetujuan/` · `erp-frontend/src/features/persetujuan/` · `erp-frontend/src/i18n/locales/{id,en}.ts`
- **Tanggal**: 2026-10-15
- **Pecahan kerja**: [[ANALISA - Portal Persetujuan Memuat Tindakan Operasional]]
- **Rujukan visual**: mockup Artifact privat https://claude.ai/artifact/8oXpNrXmmzUW11KEHm3wV2 (nama di dalamnya fiktif; mockup memakai judul "Tindakan Saya", yang kemudian ditolak, lihat § Alternatif yang Ditolak). Mockup adalah salinan rancangan bertanggal, bukan sumber kebenaran.

## Context

### Pemicu: satu dokumen cek stok yang tampil sebagai persetujuan

Pengajuan barang PB/284/10/26 berada di tahap **Cek Stok GA**. Tahap itu bukan persetujuan: backend menolak Setujui di sana (`bip-erp services/procurement/pengajuan_barang_setujui_tahap.go:38`). Tetapi ia muncul di tab **"Perlu Disetujui"** modul Pengajuan Barang, karena pembelah tab di frontend (`erp-frontend src/features/pengajuan-barang/lib/tab-kerja.ts`) hanya mengenal dua kelompok: transfer, dan sisanya.

Dokumen yang sama juga tampil di `/portal/persetujuan`, karena adapter `pengajuan_barang` di agregator (`bip-erp services/employee/antrean_pengajuan.go`) memungut antrean tanpa menyaring tahap. Tautan tetapnya `/persetujuan/pengajuan-barang` lalu membuang tahap cek stok, karena layar itu hanya mengenal lima tahap persetujuan (`antrean-persetujuan.tsx:45-107`). Hasilnya jalan buntu: baris terlihat di portal, diklik, lalu dokumennya tidak ada di layar tujuan.

Dua jalan keluar terbuka: menyaring tahap non-keputusan keluar dari portal (sesuai ADR 0114 apa adanya), atau mengakui bahwa yang dibutuhkan pemakai adalah daftar **pekerjaan yang menunggu dirinya**, bukan daftar keputusan saja. Pengukuran di bawah menentukan pilihannya.

### Isi antrean nyata: hampir seluruhnya tindakan operasional

Diukur prod 2026-10-15 sekitar 10.38 WIB, agregat seluruh perusahaan, baca-saja:

| Sumber | Berjalan | Rincian tahap / keadaan |
|---|---|---|
| Pengajuan Barang | 322 | `pb_accounting_catat` 288 (median 6,1 hari, maks 14) · `pb_ap_transfer` 16 · `pb_spv_transfer` 13 · `pb_procurement_beli` 2 · `pb_cek_stok_ga` 1 · tahap keputusan hanya **2**: `pb_spv_finance` 1, `pb_finance_setujui_bayar` 1 |
| Tiket (status Request) | 56 | median 13 hari, maks 77,8 hari, 48 tiket menunggu lebih dari 7 hari |
| Live Support | 3 | 9 hari |
| Offer rekrutmen | 5 | **palsu**: berstatus Draft padahal sudah Approved; agregator tidak menyaring status |
| Karyawan (absensi) | 0 menunggu | volume ±540 per bulan, diputus ±2-3 jam; sisanya otomatis Diabaikan setelah ±24 jam |
| Permintaan ERP, Pelatihan, Payroll, Permintaan GA, Requisition | 0 | |

Jadi sekitar **99%** isi antrean adalah tindakan operasional.

### Masalah tampilan hari ini

Diukur di `origin/main` 2026-10-15:

- Perihal mentah (mis. `UMUM`), tahap mentah (`pb_*`, `request`, `draft`).
- Pemohon Pelatihan dan Payroll tampil sebagai `employee_id`, bukan nama.
- Tidak ada nomor dokumen dan tidak ada nominal; kolom Nilai [[ADR - 0114 Antrean Persetujuan Terpusat di Web, Satu Tabel Seragam dari Agregator Employee-Service]] butir 1 belum dibangun.
- Urutan terbaru dulu (`antrean_pengajuan.go:1546-1555`), menyimpang dari butir 1 ADR 0114 (paling lama dulu).
- Klik baris hanya benar untuk Karyawan dan Tiket. Dua kategori rekrutmen bertautan kosong. Live Support bertahap kosong sehingga tampil "Tidak menunggu keputusan".

### Yang sudah ada dan dipakai ulang

| Kebutuhan | Sudah ada |
|---|---|
| Agregator baris lintas modul, `{data, degraded}`, 401/403 bukan degraded | `GET /pengajuan/antrean`, `bip-erp services/employee/antrean_pengajuan.go` |
| Riwayat Pengajuan Barang per pemroses, membawa `aksi_saya` | `GET /pengajuan-barang/diproses-saya`, `bip-erp services/procurement/pengajuan_barang_diproses_saya.go` |
| Detail Pengajuan Barang dalam Sheet | `SheetDetailPengajuan` (default export `erp-frontend src/features/pengajuan-barang/components/sheet-detail-pengajuan.tsx`), sudah dipakai antrean AP dan Accounting |
| Detail Permintaan GA dalam Sheet | `PermintaanDetailSheet` (`erp-frontend src/features/ga/permintaan/components/permintaan-detail-sheet.tsx:44`) |
| Detail pengajuan absensi | `RequestDetail` (`erp-frontend src/features/hris/requests/components/request-detail.tsx:76`) |
| Antrean pencatatan Accounting (tahap `pb_accounting_catat`), urut terlama | `antrean-pencatatan-accounting.tsx` di tab Ringkasan (bawaan) `/finance/tim-accounting`; halaman digerbang `finance.accounting.view`, tabelnya hanya dipasang bagi pemegang `budget.accounting.pencatatan`; mencatat tetap per dokumen di `/pengajuan-barang/[id]` |
| Antrean transfer AP | `AntreanTransferAp` di `/finance/ap` |
| Menu terbuka untuk semua | entri "Persetujuan" `url: "/portal/persetujuan"`, `public: true` (`erp-frontend src/components/layout/sidebar-menus.tsx`) |

## Decision

**1. Halaman tetap bernama "Persetujuan" di rute `/portal/persetujuan`, dan isinya diperluas.** Ia memuat semua yang menunggu tindakan **pemanggil**: keputusan (setujui/tolak) maupun tindakan operasional (jawab stok, isi harga, transfer dana, konfirmasi transfer, catat accounting, triase tiket). Nama menu, judul, dan rute tidak berubah.

**2. Menu terbuka untuk SEMUA karyawan** (sudah `public: true` hari ini). Penyaringan per pemanggil tetap dikerjakan **service sumber**, tidak berubah dari ADR 0114. Ini mengesahkan penyimpangan irisan 1 atas ADR 0114 butir 10 (gerbang data) menjadi keputusan.

**3. Kode tindakan dikirim backend.** Agregator mengirim field `aksi` per baris, berupa kode enum: `putuskan`, `jawab_stok`, `isi_harga`, `transfer`, `konfirmasi_transfer`, `catat`, `serah_terima`, `periksa_qc`, `triase`, `tindak_lanjut`, `pantau`.
   - `catat` = HANYA pencatatan accounting. `serah_terima` = serah GA, barang tiba, terima GA, terima RM, dan serah GA Permintaan Barang GA. `periksa_qc` = QC dan QC GA. `tindak_lanjut` = kelebihan bayar (procurement menolak Setujui di tahap itu) dan jaring pengaman untuk tahap yang belum dikenal; tombolnya ke halaman dokumen, BUKAN Setujui. Tiga kode terakhir ditambahkan 2026-10-15 oleh irfanarfianto sesudah judge menemukan tahap operasional non-accounting terpetakan ke `catat` dan kelebihan bayar ke `putuskan`.
- Pemetaan tahap ke aksi tinggal di **adapter agregator per sumber** untuk sumber yang sudah ada, dan **disetor sendiri** oleh sumber baru (sejalan ADR 0114 butir 7).
- Frontend hanya menerjemahkan kode ke kalimat i18n `id` dan `en` ([[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]).
- Alasannya satu fakta satu tempat. Frontend yang menebak aksi dari tahap menyimpan salinan pengetahuan tahap milik modul lain, dan salinan itu basi diam-diam begitu modul menambah tahap. Backend yang mengirim kalimat jadi melanggar ADR 0010.

**4. Isi baris.**
- Kategori.
- Nomor dokumen.
- Perihal yang bisa dibaca, ditambah keterangan singkat.
- Nama pemohon asli (bukan `employee_id`), dengan posisi dan departemen.
- **Nilai**: nominal, rata kanan. `null` berbeda dari 0 dan tampil dengan catatan (mis. "harga belum diisi").
- Tahap berlabel, ditambah "langkah x dari y" bila sumbernya tahu.
- Kolom **"Yang harus Anda lakukan"**: lencana aksi dan satu kalimat.
- Urut **paling lama menunggu dulu** sebagai bawaan.

**4a. Pengguna bisa mengganti urutan** lewat kontrol "Urutkan: Terlama | Terbaru" (keputusan user 2026-10-15).
- Bawaan tab Menunggu = **Terlama** (paling lama menunggu di atas, [[ADR - 0114 Antrean Persetujuan Terpusat di Web, Satu Tabel Seragam dari Agregator Employee-Service]] butir 1); bawaan tab Riwayat = **Terbaru**.
- Urutan diterapkan atas **SELURUH** baris agregator sebelum paginasi tampilan. Agregator mengembalikan semua baris; `MainTable` tidak mengurutkan `data`, dan mengurutkan satu halaman saja menghasilkan urutan yang masuk akal dan salah tanpa galat.
- Pilihan disimpan di query param `?urut=terlama|terbaru`, supaya tombol Back peramban dan tautan yang dibagikan ikut membawanya. Nilai lain jatuh ke bawaan tab.

**5. Filter utama per jenis tindakan**, berupa pil berhitung di bawah judul "Yang perlu Anda lakukan". Saringan bawaan "Perlu tindakan" **menyembunyikan** baris `pantau` (bukan giliran pemanggil); baris itu tampil lewat pil "Pantauan".

**6. Klik baris membuka panel samping (Sheet) per kategori.**
- Kerangka bersama mengikuti Sheet berangka tiga (`ui-checklist.md` §2a): header tetap, badan menggulir, footer aksi.
- Isi badan, berurutan: kotak **"Yang harus Anda lakukan"** (label aksi, tahap, kalimat, penjelasan baku per kode aksi, dan langkah berikutnya dari data jenjang), ringkasan, item atau rincian, lampiran (thumbnail), jenjang ringkas (titik 16px bergaris, lencana Selesai / Giliran Anda / Menunggu / Bila stok kurang / Belum).
- Footer per mode:

| Aksi | Footer |
|---|---|
| `putuskan` | Tolak · Setujui |
| `konfirmasi_transfer` | Kembalikan ke AP · Konfirmasi transfer |
| tindakan operasional lain | satu tombol ke form atau halaman yang tepat **untuk dokumen itu**, bukan ke daftar |
| `pantau` | tanpa aksi |

- Semua footer memuat "Buka halaman penuh" ke dokumen itu.
- ⛔ **Badan panel memakai komponen detail milik modul** (mis. `SheetDetailPengajuan`, `PermintaanDetailSheet`, `RequestDetail`). Yang dibuat bersama hanya kerangkanya: header, kotak aksi, footer. Salinan detail tiap modul **tidak** dibangun. Kategori yang belum punya komponen detail cukup menampilkan kotak aksi dan "Buka halaman penuh".

**7. TIDAK ada "Setujui lalu buka berikutnya" maupun "Konfirmasi & berikutnya".** Dibatalkan karena membingungkan pemakai (keputusan user 2026-10-15). Ini membatalkan bagian itu di T3 [[ANALISA - Antrean Persetujuan Terpusat di Web]]. Sesudah tindakan, panel tertutup dan pemakai kembali ke daftar.

**8. Tolak dan Kembalikan mewajibkan alasan**, karena alasannya dibaca pemohon atau AP. Setujui atas dokumen bernilai uang memunculkan dialog konfirmasi yang menyebut nomor dan nominal (T4 ANALISA ADR 0114).

**9. Volume besar per tindakan** (mis. 288 dokumen menunggu dicatat): tampilkan spanduk ke layar kerja milik modul yang **sudah ada**. Untuk `catat`, tujuannya tabel antrean pencatatan di tab Ringkasan `/finance/tim-accounting` (`antrean-pencatatan-accounting.tsx`); untuk `transfer`, antrean di `/finance/ap`. Panel tetap dipakai untuk melihat satu dokumen. Layar pencatatan massal **bukan** bagian ADR ini; ia dicatat sebagai kebutuhan terpisah.

**10. Keadaan kosong total** (dialami mayoritas staf) menjelaskan fungsi halaman, lalu menautkan "Lihat status pengajuan saya" (menu Pengajuan) dan Riwayat. Kosong karena saringan dibedakan dari kosong total.

**11. Riwayat** memuat dokumen yang pernah **pemanggil** proses, terbaru dulu. Jendelanya mengikuti tiap sumber (attendance 30 hari, pengajuan barang 200 dokumen terbaru lewat `/diproses-saya`), jadi layar TIDAK menjanjikan angka jendela (dikoreksi 2026-10-15 sesudah judge menemukan klaim 30 hari tak berlaku untuk semua sumber).
- Kolom: Diproses, Dokumen, Pemohon, Nilai, **Posisi sekarang** (tahap atau status dokumen **saat ini**, bukan saat pemanggil bertindak), Tindakan Anda (lencana hasil dan alasan).
- Panel baca-saja. Filter per hasil.
- Arti "riwayat" tetap yang ketat dari ADR 0114 butir 11: keputusan atau tindakan pemanggil sendiri, bukan "sudah diproses siapa pun".
- Keadaan backend 2026-10-15: `PathRiwayat` agregator hanya terisi untuk Karyawan, Permintaan ERP, Pelatihan, dan Payroll run. Pengajuan Barang sudah punya `GET /pengajuan-barang/diproses-saya` yang mengirim `aksi_saya`, tinggal disambung. Tiket, Live Support, Permintaan GA, dan Rekrutmen belum punya endpoint riwayat (**TBD**, dibangun di service asalnya bila diputuskan, bukan direkonstruksi di agregator).

**12. Penanda SLA atau "terlalu lama" TIDAK ditampilkan dulu**, karena belum ada batas resmi. Pengecualian yang diusulkan: spanduk untuk tiket yang menunggu triase lebih dari 7 hari. Ambang 7 hari **TBD**, menunggu keputusan pemilik proses tiket.

**13. Aturan untuk fitur baru: tiap tahap yang menuntut tindakan orang tertentu WAJIB masuk portal ini** (keputusan user 2026-10-15). Berlaku untuk fitur baru maupun fitur yang berubah, bila ia menambah tahap persetujuan atau tahap yang menunggu tangan orang tertentu (setujui/tolak, cek, isi, transfer, konfirmasi, catat, triase, dan sejenisnya). Sebelum fitur itu dianggap selesai:
- **(a) Service sumber menyediakan endpoint antrean per pemanggil.** Penyaringan hak dikerjakan di service sumber, bukan di agregator. Tiap baris menyetor bentuk seragam: `id`, `nomor`, perihal, pemohon (nama asli, bukan `employee_id`), `nilai` (nullable, `null` ≠ 0), tahap (kode + kunci label), `aksi` (kode dari daftar butir 3), `langkah_ke`/`langkah_total` bila ada, dan tautan per item yang membuka **item itu**, bukan daftar. Kode `aksi` baru = tambah ke daftar butir 3 dan beri label i18n di `id.ts` dan `en.ts`.
- **(b) Terdaftar di `registriAntrean`** (`bip-erp services/employee/antrean_pengajuan.go`, atau mekanisme yang menggantikannya) lengkap dengan `PathRiwayat`: endpoint "yang pernah saya proses" beserta posisi dokumen sekarang (butir 11).
- **(c) Menyatakan di mana detailnya dibuka**: komponen detail milik modul untuk panel (butir 6), atau rute per item.
- **(d) Layar antrean milik modul boleh tetap ada sebagai layar kerja** (mis. pemrosesan massal), tetapi isinya harus bersumber sama dengan portal, bukan daftar tandingan dengan saringan sendiri. Tab "Perlu Disetujui" atau "Perlu Tindakan" di modul **bukan pengganti** setoran ke portal.
- **(e) Notifikasi inbox** untuk tahap itu mengarah ke item yang sama dengan tautan di portal.

Pengecualian hanya lewat ADR. Aturan ini lahir dari empat kegagalan yang semuanya senyap: PB/284/10/26 di tahap cek stok GA menumpang tab "Perlu Disetujui" modul Pengajuan Barang sementara di portal ia buntu (§ Context); Live Support masuk portal dengan tahap kosong sehingga berbunyi "Tidak menunggu keputusan"; 5 offer Draft palsu tampil karena sumbernya tak menyaring status; dan 288 dokumen menunggu dicatat Accounting tanpa tempat yang jelas bagi pencatatnya. Tiap kasus adalah tahap yang lahir di modul tanpa ada yang memutuskan di mana orangnya akan menemukannya.

## Consequences

**Positif.**
- Satu tempat untuk semua yang menunggu pemanggil. Gudang GA, AP, dan Accounting tidak perlu membuka dua tempat.
- Pengetahuan "tahap ini menuntut tindakan apa" tinggal satu tempat per sumber, di backend.
- Jalan buntu klik baris hilang, karena tiap baris membawa tautan per dokumen.
- Tanpa ganti nama atau rute: tidak ada pengalihan, kunci menu, atau test sidebar yang harus ditulis ulang.

**Negatif dan risiko yang diterima.**
- ⚠️ **Nama "Persetujuan" kini lebih sempit dari isinya.** Pemakai yang membaca nama saja akan mengira halaman hanya berisi hal untuk disetujui, kebingungan sekelas tab "Perlu Disetujui" yang memuat cek stok. Yang memikul kejelasan karena itu adalah kalimat penjelas: judul pil "Yang perlu Anda lakukan", kolom "Yang harus Anda lakukan", kotak aksi di panel, dan keadaan kosong. Kalimat-kalimat itu wajib, bukan hiasan.
- **Kontrak agregator berubah** (`aksi`, `nomor`, `nilai`, nama pemohon, tahap berlabel, tautan). **Deploy backend sebelum frontend**; frontend wajib aman bila field baru belum ada.
- **Adapter tahap ke aksi bisa menyimpang** saat modul menambah tahap: tahap baru jatuh ke aksi yang salah tanpa galat. Penjaganya test per sumber yang mendaftar setiap tahap modul itu dan gagal bila ada tahap tanpa pemetaan, ditambah test kontrak atas rekaman respons sungguhan (T11 ANALISA ADR 0114).
- **Mayoritas pemakai melihat halaman kosong.** Karena menunya terbuka untuk semua, keadaan kosong harus menjelaskan dirinya sendiri (butir 10), kalau tidak halaman ini terbaca rusak.
- **Volume terkonsentrasi**: 288 dari 322 dokumen Pengajuan Barang menunggu Accounting, dan tanpa pencatatan massal pekerjaan itu tetap satu per satu.

**Catatan di luar keputusan ini.** Diperiksa 2026-10-15: belum ada panduan menu untuk `/portal/persetujuan` di `erp-frontend src/features/panduan/isi/`. Aturan tim mewajibkan menu membawa panduannya, dan isi halaman yang berubah membuat panduan itu lebih dibutuhkan. Pemilik panduan menu umum TBD.

**Yang tidak berubah.** Siapa berwenang memutus atau mengerjakan apa. Agregator tetap tidak pernah menulis; semua tombol memanggil endpoint modul asalnya dengan gerbangnya sendiri.

## Alternatif yang Ditolak

- **(a) Hanya keputusan, sesuai ADR 0114 lama.** Halaman hampir selalu kosong (2 keputusan dari ±380 dokumen berjalan), dan Gudang GA, AP, serta Accounting tetap membuka dua tempat.
- **(b) Ganti nama menjadi "Tindakan Saya".** Ditolak karena [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]] §1 dan §7 melarang kata "Saya" di nama menu sebagai keputusan final, dan larangan itu sudah dikunci `sidebar-urusan.test.ts`. Nama "Perlu Tindakan" juga ditawarkan; user memilih tetap "Persetujuan" (2026-10-15). Risikonya diakui di § Consequences.
- **(c) Frontend menebak aksi dari tahap.** Salinan kedua pengetahuan tahap milik modul lain, basi diam-diam saat modul menambah tahap.
- **(d) Backend mengirim kalimat jadi.** Melanggar [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]; kalimat tidak ikut bahasa aktif.

## Belum Diputuskan (TBD)

1. Ambang 7 hari spanduk tiket, menunggu pemilik proses tiket.
2. Endpoint riwayat untuk Tiket, Live Support, Permintaan GA, dan Rekrutmen.
3. Rute per dokumen untuk Live Support, Pelatihan, Permintaan ERP, dan Offer (belum ada).
4. Pemilik panduan menu umum (bukan milik satu departemen).

## Dokumen Terkait

- [[ADR - 0114 Antrean Persetujuan Terpusat di Web, Satu Tabel Seragam dari Agregator Employee-Service]]: diubah sebagian
- [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]]: diubah sebagian (§4)
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]
- [[ANALISA - Portal Persetujuan Memuat Tindakan Operasional]] · [[ANALISA - Antrean Persetujuan Terpusat di Web]]
- [[REF - Alur Persetujuan]] · [[APP - Web ERP]] · [[Microservices - Employee Service]]
