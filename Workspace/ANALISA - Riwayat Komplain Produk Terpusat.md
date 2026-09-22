Papan kerja untuk [[ADR - 0117 Riwayat Komplain Produk Terpusat di Satu Tabel, Register Tetap Dua]].
Berubah tiap item selesai; keputusannya ada di ADR, bukan di sini.

Diukur prod 2026-09-22 sebagai titik awal: kedua register **nol dokumen**, paket izin
`marketing_akuntoko_pemegang` **dipasang ke nol orang**, dan **0 dari 36** Account Specialist
melihat menu komplain mana pun. Angka-angka itu bergerak; ukur ulang sebelum dipakai memutuskan.

## Urutan dan ketergantungan

```
T1 (izin) ──┐
T2 (kabar)  ├─► T8 (ukur ulang) ──► putuskan rekap berangka
T3 (kolom pengaju) ──► T4 (agregator) ──► T5 (halaman) ──► T6 (menu)
T7 (kepemilikan data) bebas
```

T1, T2, T3, dan T7 tidak saling menunggu dan bisa jalan paralel. T1 dan T2 yang menentukan
apakah T4 dan T5 punya isi; T4 dan T5 tetap benar secara teknis tanpa keduanya, tapi tabelnya
akan kosong bagi audiens utamanya.

## Task

### T1. Pasang paket izin pemegang akun toko ke 36 Account Specialist

Paling mendesak dan paling murah: tanpa ini seluruh fitur komplain tak terjangkau audiensnya.

⚠️ **Jalur pemasangannya belum diketahui dan wajib dibaca dari kode lebih dulu.** Di prod tidak
ada satu pun contoh pemasangan (nol dokumen di 36 koleksi `employee_db` menyebut `akuntoko`),
jadi tidak ada pola yang bisa ditiru dari data. Tim mencatat paket izin punya **dua jalur**,
lewat posisi dan lewat akun; tentukan yang mana yang berlaku, lalu baru susun skripnya.

- Tulis PROD, jadi agent menyiapkan `.ps1` + `.js` idempoten (backup, dry-run, gerbang yang
  menolak melanjutkan, rollback) dan **manusia yang menjalankan**.
- Gerbang verifikasi: bukan `docker ps` dan bukan jumlah dokumen saja. Satu akun uji pemegang
  toko membuka sidebar dan melihat ketiga menu (Ulasan, Komplain ke Gudang, Komplain ke QC),
  lalu mengajukan satu komplain sungguhan lewat gateway sampai baris pertama muncul di register.
- ⛔ Jangan memecah paketnya. ADR 0107 melarangnya, dan pemegang paket separuh justru kehilangan
  menu yang dulu dibuka perannya, sebab klaim `akuntoko.*` mematikan fallback tier seluruh modul.

### T2. Kabar inbox saat ulasan bintang rendah masuk

Memenuhi keputusan 8 [[ADR - 0099 Komplain dari Ulasan Marketplace Dirutekan per Departemen lewat Register Komplain yang Ada]], yang sampai kini belum ada kodenya: jalur ulasan integration-service nol pemanggilan notifikasi.

- Penerimanya pemegang toko yang bersangkutan, diturunkan dari kepemilikan toko, bukan dari peran.
- Kategori inbox baru berarti **notification-service naik lebih dulu**, lalu integration-service.
- Sertakan tautan langsung ke baris ulasannya, sebab kalender dan inbox di sistem ini diperlakukan
  sebagai pintu, bukan tujuan.
- Gerbang verifikasi: satu ulasan bintang rendah sungguhan memunculkan satu baris inbox pada
  pemegang tokonya, dan **tidak** pada orang lain.

### T3. Kolom pengaju dan saringan "punya saya" di tabel komplain QC

Berguna apa pun yang terjadi pada T4 dan T5, dan menjadi fondasi penanda per baris di agregator.

- Hari ini tabel QC berkolom Komplain, Kategori, Produk/SKU, Pesanan, Tingkat, Status, Catatan QC,
  Aksi. Tidak ada kolom pengaju, padahal cakupan barisnya paling luas (seluruh perusahaan).
- ⚠️ `created_by` bisa **kosong** untuk komplain yang dibuat lewat token layanan tanpa header
  `BIP-Employee-ID`. Kolomnya wajib menangani baris tanpa pengaju secara eksplisit, bukan
  menampilkan sel kosong yang terbaca seperti data hilang.
- Label lewat i18n dua bahasa, dan tanggal diformat di `render` memakai locale aktif.

### T4. Agregator `GET /komplain/riwayat` di employee-service

Inti ADR 0117. Bersaudara dengan `/pengajuan/ringkasan`, memakai ulang mekanismenya.

- Registri dua sumber: register gudang (warehouse-service) dan register QC (koleksi di DB sendiri).
- **Pemetaan dua kosakata status ke satu himpunan** (`menunggu`/`diproses`/`tuntas`/`ditolak`),
  ditulis eksplisit, bukan diturunkan dari kemiripan nama. Nilai asli tetap dikirim terpisah.
- **Penanda per baris** apakah baris itu milik pembaca. Polanya sudah ada di sistem: antrean
  Tinjau Setoran Live Support mengirim `boleh_putus` per baris.
- Kolom Perihal diisi **satu kalimat jadi dari agregator**, bukan dirakit layar.
- Balasan `{data, degraded}`: sumber gagal wajib bisa dibedakan dari nol baris.
- ⛔ **Test kontrak yang mengurai rekaman respons sungguhan kedua register**, bukan tiruan struct.
  Kelas kegagalan ini sudah menggigit di sini: uji yang memalsukan sumbernya tetap hijau sementara
  tak satu pun baris benar-benar ditarik.
- Kemungkinan butuh env base URL warehouse di blok `employee-service`, jadi container **dibuat
  ulang** dengan `--force-recreate`, bukan di-restart. Kepastiannya di `/plan`.

### T5. Halaman `/marketing/komplain`

Satu tabel untuk pengaju, leader, dan SPV. Bergantung T4.

- Struktur tabel HRIS: satu kartu, `Banner bare` di dalam prop `toolbar` milik `MainTable`,
  seluruh keadaan di `useTableState`. Jangan merakit tabel, filter, atau paginasi sendiri.
- Kolom: Unit, Perihal, Pesanan, Toko, Diajukan oleh, Status, Menunggu sejak. Urut dari yang
  paling lama menggantung. Penyaring Unit dan Status di toolbar; nomor pesanan bisa dicari.
- Detail lewat `Sheet` berangka tiga (header tetap, badan menggulir ber-padding, footer aksi).
  Baris gudang membuka sheet tindak lanjut yang ada; baris QC membuka dialog validasi yang ada.
- Halaman digerbang **cerminnya sendiri plus backend**, dan rutenya **tidak** dimasukkan ke daftar
  rute privat per departemen, sebab daftar itu akan mengunci marketing dari halamannya sendiri.
- Lima keadaan layar wajib dibedakan: memuat (kerangka, bukan spinner), kosong karena register
  memang kosong, kosong karena saringan, sebagian sumber gagal (`degraded`), dan terkunci.

### T6. Menu, sekalian membetulkan label kembar

Bergantung T5.

- Tambah satu entri ke halaman baru, lalu **putuskan** apakah dua entri lama di Marketing
  ("Komplain ke Gudang", "Komplain ke QC") tetap ada atau diganti entri baru itu.
- ⛔ Betulkan cacat yang sudah terlihat di layar hari ini: kedua judul lama berbagi awalan
  `"Komplain ke "` sepanjang 12 karakter, sementara tombol submenu sidebar memotong teks, sehingga
  dua menu bertujuan berbeda tampil identik. Usul: `"Komplain Gudang"` dan `"Komplain QC"`.
- Periksa sekalian apakah judul menu itu lewat i18n atau hardcode; pemeriksaan sebelumnya belum
  konklusif.

### T7. Daftarkan kedua register di peta kepemilikan data

[[REF - Kepemilikan Data]] belum memuat baris untuk `warehouse_komplain_gudang` maupun
`quality_complaint`. Isi fakta bisnisnya, service pemiliknya, siapa yang boleh menulis, dan
salinan yang sah beserta arah dan penjaganya. Salinan nama produk dan SKU dari `transaction_orders`
ke register juga wajib tercatat di sana saat keputusan 4 ADR 0103 diimplementasikan.

### T8. Ukur ulang 4 sampai 8 pekan setelah T1 dan T2 hidup

Ini yang memutuskan dua kegunaan yang sengaja tidak dibangun sekarang (rekap masalah berulang dan
bahan laporan ke atasan), dan sekaligus menjawab pertanyaan yang belum pernah diukur: apakah
keluhan pembeli memang tidak sampai ke sistem karena pintunya tertutup, atau karena volumenya
memang sekecil itu.

Yang diukur: jumlah komplain masuk per unit, rasio `ditolak`, berapa lama dari diajukan sampai
ditutup, dan berapa orang benar-benar membuka halamannya. Bila volumenya tetap mendekati nol
sesudah pintunya dibuka, rekap berangka **tidak** dibangun, dan itu jawaban yang berguna.

## Yang sengaja TIDAK ada di daftar ini

- **Menggabungkan kedua register jadi satu koleksi.** Ditolak dua kali dengan alasan terukur;
  lihat Context [[ADR - 0103 Satu Pintu Komplain Produk, Unit Tujuan Diturunkan dari Kategori]].
- **Perpindahan komplain antar unit.** Dibatalkan 2026-09-21; yang berlaku tolak lalu ajukan ulang.
- **Rekap berangka dan bahan laporan.** Ditunda sampai T8, bukan dibuang.
- **Memberi Quality service sendiri.** Keluhan bahwa employee-service kelebihan muatan itu sah dan
  tidak dijawab ADR 0117, tetapi pemicunya harus terukur (tim berbeda, atau deploy saling menahan),
  bukan "terasa berantakan".
