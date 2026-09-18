> **Status**: 🟡 **Diusulkan** (2026-09-17) — tab Selisih Retur terjadwal per periode, dua tahap, akses lewat izin `returselisih.*`; T1 (izin + gerbang menu) dibuat 2026-09-18 di branch `feat/izin-selisih-retur` dan belum merge, sisanya belum ada kode.

## Untuk Manajemen

**Apa yang berubah di layar.** Halaman Auto Sync Retur mendapat tab kelima, **Selisih Retur**. Isinya daftar retur yang pembukuannya di Accurate tidak cocok dengan barang yang benar-benar diterima gudang, per bulan: retur yang lama belum terbukukan karena belum discan, paket yang isinya baru sebagian discan, barang yang discan berbeda dari yang dibeli, scan gudang yang tidak sampai ke pembukuan, scan tanpa order, dan (tahap kedua) dokumen retur yang isinya di Accurate berbeda dari catatan ERP. Di atasnya ada kartu ringkasan per jenis, keterangan kapan angka dihitung dan apakah datanya lengkap, serta tombol unduh Excel. Tiap temuan bisa ditandai **beres** dengan alasan, dan temuan yang penyebabnya sudah hilang (misalnya scan susulan masuk) tertutup sendiri.

**Siapa yang terdampak.** Finance memakainya untuk rekonsiliasi saat tutup buku dan satu-satunya yang boleh menandai beres. Gudang melihat pekerjaan scan susulan dan bisa langsung membuka WMS Retur. Manajemen membaca ringkasannya. Siapa boleh melihat dan siapa boleh menandai beres diatur HR/IT dari layar Hak Akses per jabatan, bukan dikunci di program.

**Yang tidak dijanjikan.**
- Angkanya **bukan saat itu juga**: dihitung tiap malam, jadi yang tampil adalah keadaan sampai kemarin.
- Laman ini **tidak membetulkan apa pun** di Accurate maupun di WMS. Ia menunjukkan selisih dan siapa yang harus bertindak; pembetulannya tetap lewat jalur yang sudah ada.
- Selisih **catatan ERP vs isi dokumen Accurate** baru hadir di **tahap kedua**, karena butuh membaca ribuan dokumen dari Accurate secara terjadwal.
- Perbandingan **jumlah barang** yang lengkap antara WMS dan pembukuan belum termasuk; tahap pertama memeriksa barang apa yang ada, bukan berapa banyaknya.
- Nilai yang ditampilkan adalah nilai yang **terdampak** selisih, bukan koreksi pendapatan, dan tidak boleh dijumlahkan antar jenis.

**Perkiraan besaran kerja.** Tahap pertama sekitar dua sampai tiga minggu kerja satu developer (izin baru, perhitungan terjadwal, penyajian data dari WMS, tab dan unduhan). Tahap kedua sekitar satu sampai dua minggu, termasuk mengatur beban baca ke Accurate. Keduanya menyentuh tiga bagian sistem sehingga dideploy bertahap.

## Deskripsi

*Satu tab Selisih Retur di halaman Auto Sync Retur, diisi hasil perhitungan terjadwal per periode yang disimpan per temuan beserta statusnya, menggantikan tiga cara manual yang dipakai finance untuk rekonsiliasi retur saat tutup buku. Aksesnya lewat dua izin baru di katalog finance yang dipasang ke posisi dari /it/hak-akses. Dibangun dua tahap: selisih dari data ERP dan WMS lebih dulu, selisih ERP vs isi dokumen Accurate menyusul.*

- **Status**: 🟡 **Diusulkan** — hasil `/analisa-kebutuhan` 2026-09-17, rancangan & akses disetujui user, kode belum ada.
- **Path di repo** (rencana): `bip-erp/services/integration/internal/usecase/retur_selisih*.go` (baru) · `bip-erp/services/integration/internal/worker/tasks/retur_selisih_*.go` (baru) · `bip-erp/services/integration/internal/interface/http/retur_selisih_handler.go` (baru) · repository koleksi `retur_selisih` (baru) · `bip-erp/services/manufacture/retur_scan_periode.go` (baru, endpoint internal) · `bip-erp/shared-library/common/catalog_finance.go` (dua izin) · `erp-frontend/src/features/integration/accurate/auto-sync-return/components/selisih-retur-*.tsx` (baru) · menu & gerbang akses FE
- **Tanggal**: 2026-09-17

## Context

### Kebutuhan, dipisahkan dari solusi yang diminta

Permintaan awalnya "laman untuk mengecek selisih data Auto Sync Retur dengan data scan gudang". Wawancara 2026-09-17 memperjelasnya:

| Pertanyaan | Jawaban |
|---|---|
| Keputusan yang diambil dari laman ini | **rekonsiliasi saat tutup buku**, selebihnya pemantauan |
| Cara finance sekarang | ketiganya sekaligus: Excel gabungan manual, cek dokumen Accurate satu per satu, menunggu ada yang melapor |
| Kesegaran data | tidak diketahui → **asumsi**: sampai kemarin cukup |
| Pembaca | finance, gudang, manajemen |
| Akibat angka salah | tutup buku salah, kerja sia-sia, laman ditinggalkan |
| Dokumen yang sudah dibetulkan manual di Accurate | tetap tampil, bisa ditandai beres |

Jadi kebutuhannya bukan "sebuah laman", melainkan: **saat tutup buku finance harus bisa yakin nilai dan stok retur di Accurate sama dengan barang yang benar-benar kembali, tanpa menggabungkan tiga cara manual.** Tiga sifat mengikuti langsung dari jawaban di atas: angka per periode harus **stabil** (tidak berubah tiap dibuka), **jujur soal kelengkapannya**, dan temuan harus bisa **ditandai beres** supaya daftarnya tidak tumbuh lalu ditinggalkan.

### Data nyata (diukur prod 2026-09-17, baca-saja)

- `accurate_daily_returns`: 10.299 baris; **7.261 SENT** (Juli 1.545 · Agustus **3.726** · September 1.990), 2.437 SKIPPED, 601 PENDING.
- **601 retur belum terbukukan** karena menunggu scan; umur: 135 ≤7 hari, 264 8–30 hari, **163 31–60 hari, 28 >60 hari**; per bulan tanggal retur: Juli 119, Agustus 257, September 214.
- Salinan dokumen Accurate (`accurate_mirror`) terisi **269 dari 7.261 SENT (3,7%)**; di antaranya hanya **4** yang totalnya berbeda dari `booked_total`. Pada saat yang sama, remediasi retur paket 2026-09-16/17 menemukan secara manual **17** dokumen yang catatan ERP-nya berbeda dari isi Accurate karena finance membetulkannya langsung di Accurate ([[ADR - 0040 Retur Paket Utuh via Baris Induk Faktur]] amandemen 2026-09-15). Artinya selisih ERP-vs-Accurate praktis tidak terlihat dari data yang tersimpan.
- 13 dokumen bercatatan `[KOREKSI-SCAN]`; ekspor WMS 2026-09-17 memuat **33 order** berkomponen belum discan (22 paket order batal, 8 barang satuan, 3 retur marketplace).

### Yang sudah ada — banyak, tapi tersebar

Tidak ada satu tempat yang menyandingkan dan menjumlahkan selisih per periode, dan tidak ada yang bisa ditandai beres. Potongannya:

- Auto Sync Retur: tab **Menunggu Scan Gudang** (dengan umur tunggu sejak bip-erp #1921 / erp-frontend #1610, merged 2026-09-17), **Perlu Ditindak**, **Perlu Approval Seller Center**; badge `MENUNGGU SCAN` / `SEBAGIAN` / `TANPA SCAN GUDANG` per baris; kolom Scan Gudang di detail.
- WMS Retur: badge **BELUM SAMPAI ACCURATE** (`konfirmasiTertunda`), **MENUNGGU APPROVAL SELLER CENTER**, filter scan **Belum Tertaut**.
- Kolom **Komponen Belum Discan** di Laporan Retur finance dan Ekspor Retur WMS (bip-erp #1911, erp-frontend #1598).
- Alarm pagi `check-return-anomaly` (hanya Mongo, sengaja tidak membandingkan ke Accurate).
- Perkakas baris perintah `cmd/returnrecon`, `cmd/returnorphan`, `cmd/returnscanhilang` — on-demand, hanya bisa dijalankan orang IT.

Sesi kerja lain pada 2026-09-17 sampai pada kesimpulan yang sama ("laman atau tab khusus belum pernah dibuat") dan mengusulkan tab **"Scan Beda dari Order"**. Usulan itu adalah **sebagian** dari keputusan ini dan dilebur ke dalamnya, bukan dibangun terpisah.

### Batasan teknis yang membentuk keputusan

- **Pemindai drift dokumen retur tidak pernah ada di `main`.** Diverifikasi `git grep` 2026-09-17 atas `returndriftscan|BEDA_TOTAL|DOKUMEN_HILANG` = 0 hasil, dengan kontrol positif `RefreshDailyReturnMirror` ditemukan. Salinan hanya terisi saat detail dibuka atau tombol refresh, tanpa jadwal. ⚠️ Karena itu keputusan ini **tidak bisa bersandar** pada status [[ADR - 0066 Salinan Dokumen Retur Accurate + Pemindai Drift]] — bagian pemindainya adalah rencana, bukan kenyataan.
- **Batas gateway 30 detik** untuk rute non-`/export`. Membaca Accurate untuk 3.726 dokumen sebulan pada batas 8 request/detik butuh sekitar 8 menit.
- **Feed retur WMS untuk layar dibatasi 10 halaman × 200 = 2.000 baris** (`returnFetchMaxPages`, `services/manufacture/returns.go`), sementara komentar kodenya sendiri mencatat 32.508 order retur di prod per 2026-09-05. Jalur ekspor punya batas terpisah 300 halaman.
- **Rute `/accurate/daily-returns*` di integration-service tidak memakai gerbang peran** — hanya validasi gateway dan JWT.
- integration_db dan manufacture_db berada di cluster terpisah; data lintas service lewat HTTP ([[ADR - 0002 Database-per-Service]]).
- Katalog izin: 22 modul terdaftar di `services/employee/permission_catalogs.go` per 2026-09-17; **integration tidak punya katalog**, **finance punya** dan sudah menaungi halaman di bawah Integrasi Accurate (`finance.kastoko.view` untuk Kas Toko — "kewenangan mengikuti pemakai, bukan letak berkas", `catalog_finance.go`). Mekanismenya [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] dan [[CORE - RBAC dan Permission Set]].

## Decision

### 1. Satu tab "Selisih Retur" di Auto Sync Retur

Tab kelima di halaman yang sudah dipakai finance. Tidak ada laman atau tab kedua untuk selisih retur, termasuk usulan "Scan Beda dari Order". Tab **Menunggu Scan Gudang** tetap ada dan berbeda fungsinya: ia antrean kerja harian, Selisih Retur alat rekonsiliasi per periode. Modul Audit Internal bukan tempatnya karena divisi yang diperiksa, termasuk finance, tidak punya akses ke sana ([[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]]).

### 2. Dihitung terjadwal per periode dan disimpan per temuan, bukan dihitung saat dibuka

Satu proses malam menghitung selisih per bulan tanggal retur dan menyimpan **tiap temuan** (jenis, order/resi, toko, dokumen, sisi order, sisi scan, sisi Accurate bila ada, nilai terdampak, umur, status). Tab membaca simpanan itu.

Alasannya tiga sifat di Context: angka yang dihitung saat dibuka berubah tiap kali dibuka, tidak bisa memuat pembacaan Accurate dalam 30 detik, dan bergantung pada feed WMS yang terpotong di 2.000 baris. Hasil rekonsiliasi adalah **turunan** yang boleh dihitung ulang kapan saja — bukan sumber pembukuan, dan tidak ada jalur pembukuan yang membacanya (prinsip yang sama dengan salinan di ADR-0066).

### 3. Tujuh jenis selisih, tiga kelompok, dua tahap

| Kelompok | Jenis | Sumber | Tahap |
|---|---|---|---|
| 1 · data ERP | belum terbukukan karena menunggu scan (umur >30 hari) · dibukukan tanpa bukti scan · komponen paket belum discan · barang discan berbeda dari yang dibeli | integration | 1 |
| 2 · sisi gudang | sudah discan tapi tidak sampai ke pembukuan · scan tak tertaut order | manufacture lewat HTTP | 1 |
| 3 · ERP vs Accurate | catatan ERP berbeda dari isi dokumen Accurate (termasuk edit manual) | Accurate lewat salinan terjadwal | 2 |

Detektor memakai ulang aturan yang sudah ada, bukan salinan: `komponenKurangOrder` untuk komponen belum discan, `DibukukanTanpaScan`, penilaian SKU sah order yang dipakai `koreksiBarangAsing`, dan `konfirmasiTertunda` di manufacture.

**Tahap 2** menjadwalkan penyegaran salinan dokumen Accurate per periode dengan batas kecepatan, sekaligus menuntaskan bagian pemindai ADR-0066 yang tak pernah dibuat. Ia tidak boleh berjalan bersamaan dengan perkakas yang menulis ke Accurate (batas 8 request/detik per token dipakai bersama).

### 4. Status temuan: terbuka, beres otomatis, ditandai beres

- **Tertutup otomatis** bila penyebabnya hilang pada perhitungan berikutnya (scan susulan masuk, dokumen terbukukan, salinan cocok).
- **Ditandai beres** hanya lewat izin khusus, **wajib alasan**, dengan jejak siapa, kapan, dan alasannya. Dipakai untuk yang tak akan hilang sendiri, termasuk dokumen yang sengaja dibetulkan manual finance di Accurate (keputusan user 2026-09-17: tampil, bisa ditandai beres).
- Temuan yang sudah ditandai beres **dibuka kembali** bila penyebabnya berubah bentuk (mis. nilai Accurate bergeser lagi), supaya tanda beres tidak menutupi selisih baru.

### 5. Jujur soal kelengkapan

Tiap perhitungan menyimpan kapan dijalankan, sampai tanggal berapa datanya, berapa unit diperiksa, dan berapa **gagal dibaca**. Bila ada yang gagal, tab menandai angkanya sebagai **batas bawah**, bukan total. Aturan umum ini sudah tertulis di [[ADR - 0040 Retur Paket Utuh via Baris Induk Faktur]]: audit yang bergantung pada fetch pihak ketiga wajib melaporkan fetch yang gagal.

### 6. Akses lewat katalog izin sendiri, diatur dari /it/hak-akses

Dua izin baru di modul **`returselisih`**:

| Izin | Membuka |
|---|---|
| `returselisih.view` | tab, daftar, detail, unduh Excel |
| `returselisih.tandai` | tombol Tandai beres |

- ⛔ **Prefiksnya SENDIRI, bukan `finance.`** (diputuskan 2026-09-17 setelah menelusuri kode). Klaim izin sebuah modul MENANG atas cadangan tier modul itu, bukan digabung: memasang paket sempit berprefiks `finance` kepada orang Finance yang aksesnya hari ini lahir dari tier akan memadamkan piutang, utang, dan jurnal mereka tanpa satu pun galat. Preseden yang sama: modul `akuntansicv` (ADR 0096). Menunya tetap tinggal di blok Accurate lewat alias kategori di frontend.
- **Pemegang izin tanpa peran pembuka Accurate hanya melihat menu Auto Sync Retur.** Prefiks izin ikut membuka kategori sidebar, dan kategori Accurate memuat sebelas menu yang sebagian besar tak bergerbang izin; tanpa penyaring, admin gudang yang diberi paket ikut melihat Sales, Income, dan Auto-Sync Faktur.
- **Cadangan tier**: finance, integration, integration_accurate, dan IT boleh **melihat**; hanya finance boleh **menandai**. Satu sumber di `common.ReturSelisihTierDefault`, dicerminkan tabel `FALLBACK` frontend dengan matriks uji yang identik.

- Dipasang HR/IT ke **posisi** sebagai paket lewat /it/hak-akses; menambah pembaca baru tidak butuh perubahan kode. Contoh susunan: staf/admin finance = lihat + tandai; admin gudang = lihat; Direktur = lihat.
- **Aksi di layar ditentukan izin, bukan nama peran**: Tandai beres ← `.tandai`; Buka di WMS Retur ← izin WMS retur yang sudah ada di katalog manufacture; tanpa izin aksi = baca saja.
- **Gerbang backend dan frontend wajib sinkron**: endpoint baru memeriksa izin (`common.RequirePermission`), dan frontend memakai klaim yang sama untuk menu, tab, dan tombol. **Menu Auto Sync Retur harus muncul bagi pemegang `.view`** walaupun tak punya peran finance/integration; tanpa itu admin gudang yang sudah diberi paket tetap tak melihat menunya.
- **Masa transisi**: akun ber-tier finance yang belum dipasangi paket mendapat izin setara lewat cadangan tier (`FinanceTierDefault`), supaya tak ada yang kehilangan akses saat deploy.
- Rute retur yang **sudah ada** tidak diubah gerbangnya oleh keputusan ini.

### 7. Aturan pemakaian angka

- **Nilai terdampak tidak boleh dijumlahkan antar jenis.** Satu order bisa muncul di lebih dari satu jenis (mis. komponen belum discan sekaligus catatan ERP berbeda dari Accurate). Total hanya sah **per jenis**.
- Nilai terdampak **bukan** koreksi pendapatan dan bukan nilai yang harus dibukukan; ia ukuran besarnya selisih.
- Kartu "belum terbukukan" menghitung order, bukan dokumen: satu dokumen retur bisa memuat banyak order.

## Consequences

**Yang membaik**
- Rekonsiliasi retur tutup buku punya satu tempat dengan angka yang bisa diulang per periode, menggantikan tiga cara manual.
- Selisih yang selama ini baru ketahuan dari keluhan (RTR/2026/08/11/191-KY+GB, 17 dokumen edit manual) terlihat tanpa menunggu laporan.
- Gudang mendapat daftar kerja scan susulan di layar, bukan hanya di Excel.
- Katalog finance mendapat izin yang benar-benar ditegakkan di integration-service, dan susunan akses bisa diubah tanpa deploy.

**Ongkos dan risiko**
- **Data sampai kemarin**, bukan saat itu juga — konsekuensi sadar dari Decision #2.
- **Endpoint baru di manufacture** untuk data scan per periode, karena feed layar yang ada terpotong di 2.000 baris. Kontrak lintas service baru berarti **manufacture naik lebih dulu**, lalu integration, lalu frontend.
- **Proses terjadwal baru** di integration; dinyalakan lewat saklar kv yang sudah menjadi pola job lain, sehingga tidak butuh env baru.
- **Tahap 2 membebani API Accurate** (~8 menit per bulan data pada 8 request/detik) dan harus dijauhkan dari jadwal perkakas yang menulis ke Accurate.
- **Dua gerbang akses** (backend dan frontend) adalah kelas cacat yang sudah pernah menggigit di WMS; wajib diuji bersama, termasuk kasus admin gudang yang hanya memegang `.view`.
- **Perubahan paket berlaku setelah login ulang**, karena izin terbawa di token saat login — perlu disampaikan ke HR/IT.
- Jabatan Direktur melihat semua menu di tampilan, tapi endpoint tetap menolak tanpa paket; paket lihat untuk Direktur tetap perlu dipasang.
- **Belum dicakup**: perbandingan jumlah barang yang lengkap (WMS menjumlahkan semua transaksi per order, pembukuan mengganti per order+SKU), transaksi WMS `catatanSaja` yang menambah stok tanpa masuk pembukuan, serta ubah/hapus transaksi WMS setelah dokumen terkirim. Dicatat sebagai sisa terbuka.

**Asumsi yang perlu dikonfirmasi saat dipakai**
1. Kesegaran "sampai kemarin" cukup untuk tutup buku.
2. "Manajemen" = jabatan Direktur; posisi lain ditambahkan lewat paket.
3. Periode = bulan tanggal retur, bukan bulan faktur penjualan.
4. Ambang "belum terbukukan" = menunggu scan lebih dari 30 hari.

## Dokumen Terkait
- [[Microservices - Integration Service]] — Auto-Sync Retur, tempat perhitungan dan API-nya
- [[Microservices - Manufacture Service]] — WMS Retur, sumber data scan per periode
- [[APP - Web ERP]] — halaman Auto Sync Retur
- [[CORE - RBAC dan Permission Set]] — katalog izin dan paket per posisi
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]
- [[ADR - 0066 Salinan Dokumen Retur Accurate + Pemindai Drift]] — pemindai yang dituntaskan Tahap 2
- [[ADR - 0040 Retur Paket Utuh via Baris Induk Faktur]] — asal kolom Komponen Belum Discan dan 17 dokumen edit manual
- [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] — gerbang gudang dan konfirmasi scan
- [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]] — alasan bukan di modul audit
- [[ADR - 0002 Database-per-Service]]
