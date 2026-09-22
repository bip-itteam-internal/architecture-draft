Papan kerja untuk [[ADR - 0117 Riwayat Komplain Produk Terpusat di Satu Tabel, Register Tetap Dua]].
Berubah tiap item selesai; keputusannya ada di ADR, bukan di sini.

Diukur prod 2026-09-22 sebagai titik awal: kedua register **nol dokumen**, paket izin
`marketing_akuntoko_pemegang` **dipasang ke nol orang**, dan **0 dari 36** Account Specialist
melihat menu komplain mana pun. Angka-angka itu bergerak; ukur ulang sebelum dipakai memutuskan.

## Urutan dan ketergantungan

```
T1 (izin) ──┐
T2 (kabar)  ├─► T8 (ukur ulang) ──► putuskan rekap berangka
T3 (kolom pengaju)
T3b (identitas item diisi server) ──► T4 (agregator) ──► T5 (halaman) ──► T6 (menu)
T7 (kepemilikan data) bebas
```

T1, T2, T3, dan T7 tidak saling menunggu dan bisa jalan paralel. T1 dan T2 yang menentukan
apakah T4 dan T5 punya isi; T4 dan T5 tetap benar secara teknis tanpa keduanya, tapi tabelnya
akan kosong bagi audiens utamanya.

⛔ **T3b adalah prasyarat KERAS T5, bukan perapian.** Tanpa identitas item yang berasal dari
pesanan, register QC tidak punya toko, sehingga kolom Toko kosong untuk seluruh baris QC. Bagi
pemegang toko justru kolom itu yang paling menentukan, jadi halaman gabungan yang tayang tanpa
T3b menyajikan tabel yang tidak menjawab pertanyaan pertama pembacanya.

## Task

### T1. Pasang paket izin pemegang akun toko ke 36 Account Specialist

Paling mendesak dan paling murah: tanpa ini seluruh fitur komplain tak terjangkau audiensnya.

✅ **Skripnya sudah ditulis dan sudah diuji mode baca**: `.task-plans/2026-09-22-pasang-paket-akuntoko-prod.ps1`
beserta `.js`-nya. Tulis PROD, jadi **manusia yang menjalankan**. Urutannya `-Mode cek` (tidak
menulis, keluarannya jadi berkas cadangan), lalu `-Mode terapkan`, dan `-Mode balik -Cadangan <file>`
bila perlu pulang. Mode `terapkan` menolak jalan bila cadangan belum ada.

**Dua temuan pengukuran yang menentukan bentuk skripnya**, dan keduanya tak terlihat tanpa membuka
data prod:

- ⛔ **Kedua departemen punya DUA item posisi untuk pekerjaan yang sama**: `icc` ("ICC") dan
  `account_specialist` ("Account Specialist"), keduanya kini berisi `marketing_engagement_pemohon`.
  Dari 36 Account Specialist, **33 ber-`position_key: "icc"`** dan hanya 3 ber-`account_specialist`.
  `paketPosisi` (`services/employee/permission_resolve.go`) mencocokkan `position_key` lebih dulu
  dan baru jatuh ke nama, jadi memasang paket hanya ke item "Account Specialist" akan melewatkan
  **33 orang tanpa satu pun galat**. Skrip menyentuh keempat item.
- ⛔ **Empat pemegang toko aktif berada di luar kedua item itu**: dua Leader dan dua Marketplace
  Advertiser di Beauty Hacks. Memasang paket ke item `leader`/`marketplace_advertiser` akan ikut
  memberi hak ke seluruh pemegang jabatan itu yang tidak memegang toko, jadi keempatnya ditangani
  lewat **jalur akun** (`system_authentication.permission_sets`), yang memang jalur pengecualian
  individu dan sudah dipakai 23 akun lain di prod.

Radius yang diterima sadar: 44 orang terkena jalur posisi, 29 di antaranya pemegang toko aktif.
15 sisanya tidak memegang toko, jadi mereka melihat menunya tetapi tidak dapat mengajukan apa pun
(backend menyaring lewat `icc_account_mappings`) dan daftar komplain gudangnya nol baris. Yang
benar-benar melebar hanya bacaan register QC, yang memang tidak tersempit per toko.

- ⛔ Jangan memecah paketnya. ADR 0107 melarangnya, dan pemegang paket separuh justru kehilangan
  menu yang dulu dibuka perannya. Skrip menolak jalan bila paketnya tidak utuh.
- ⚠️ Klaim izin terbit saat **login**, jadi yang sudah login belum melihat menunya sampai login
  ulang atau tokennya kedaluwarsa (TTL 72 jam).
- Gerbang verifikasi: bukan `docker ps` dan bukan jumlah dokumen saja. Satu pemegang toko login
  ulang, melihat ketiga menu (Ulasan, Komplain ke Gudang, Komplain ke QC), lalu mengajukan satu
  komplain sungguhan lewat gateway sampai baris pertama muncul di register. Kedua register nol
  dokumen sebelum ini, jadi baris pertama itulah buktinya.

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

### T3b. Identitas item komplain QC diisi SERVER dari data pesanan

Menjalankan keputusan 4 [[ADR - 0103 Satu Pintu Komplain Produk, Unit Tujuan Diturunkan dari Kategori]],
yang sudah diputuskan sejak 17 September dan belum ada kodenya. Prasyarat keras T5.

- Register QC mengambil nama produk, SKU, dan identitas toko dari data pesanan integration-service
  lalu menyalinnya; nilai serupa dari klien diabaikan. Pesanan yang tak ditemukan ditolak dengan
  pesan yang menjelaskan sebabnya.
- ⛔ Data pesanan diambil **server ke server**, tidak lewat layar pengaju, sebab responsnya memuat
  data pembeli yang tidak dibutuhkan untuk mengajukan komplain.
- Begitu register QC punya identitas toko, dua hal ikut terbuka: kolom Toko di tabel gabungan
  terisi untuk kedua unit, dan **penanda per baris** di keputusan 6 ADR 0117 bisa dicabut karena
  barisnya sudah bisa disempitkan per toko.
- Diukur prod 2026-09-17 sebagai batas yang jujur: dari 65 ulasan buruk, 61 pesanannya ada di
  `transaction_orders` dan seluruhnya ber-SKU, sedangkan 45 ada di `fulfillment_orders`. Sisanya
  tidak dapat diajukan sama sekali, dan itu konsekuensi yang sudah diterima ADR 0103.

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
- Kolom, **tujuh**: Unit, Perihal, Pesanan, Toko, Diajukan oleh, Status, Menunggu sejak. Urut dari
  yang paling lama menggantung. Penyaring Unit dan Status di toolbar; nomor pesanan bisa dicari.
  **Tiap kolom wajib terisi untuk kedua register**, dan itu diperiksa dengan membaca model, bukan
  menduga dari nama (ADR 0117 keputusan 4).
- ⛔ **Kolom Toko menuntut T3b selesai lebih dulu.** `QualityComplaint` tak punya `shop_id`, jadi
  tanpa T3b kolom itu kosong untuk seluruh baris QC. Jangan menambalnya di agregator dengan
  menebak dari `order_ref`: itu sumber kebenaran kedua soal komplain ini milik toko mana.
- ⚠️ **Produk, SKU, dan tingkat keparahan tidak jadi kolom, dan itu bukan kekurangan yang bisa
  ditambal.** Register gudang per pesanan, register QC per item; satu pesanan bisa memuat beberapa
  produk sehingga satu sel Produk untuk baris gudang akan berbohong. Ketiganya muncul di `Sheet`
  detail bersama atribusi packer.
- ⚠️ Dua kolom yang bertahan tetap bercatatan: nilai **Pesanan** sisi gudang diverifikasi ke
  `fulfillment_orders` sementara sisi QC masih teks bebas, dan **Diajukan oleh** sisi QC bisa
  kosong (token layanan tanpa header identitas) sehingga barisnya ditangani eksplisit.
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
