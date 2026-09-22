**Status**: 🟡 Daftar task dari `/analisa-kebutuhan` 2026-09-22. Keputusannya di [[ADR - 0116 Setelan Akun Marketplace Bergerbang dan Berjejak, Komponen Tak Dikenal Wajib Terlihat]], cara kerjanya di [[Finance - Pemetaan Komponen Marketplace ke Akun Accurate]]. Dok ini papan kerja, bukan arsitektur. Coret item begitu PR-nya merge, dan pindahkan keadaannya ke dok domain lewat `/sync-docs`, jangan menumpuk status di sini.

## Kebutuhan yang dijawab

Finance melaporkan biaya marketplace tercatat di akun yang salah empat kali dalam lima minggu (18 Agustus sampai 20 September 2026), dan tiap laporan diperbaiki satu per satu lewat tiket. Perbaikan 9 September tidak menghentikan keluhan sejenis 11 hari kemudian.

Pemeriksaan membantah dugaan awal bahwa masternya belum ada. Masternya ada (11 laci akun, layar Setelan Akun hidup, bisa diubah tanpa deploy). Yang keliru adalah residual memakai akun yang sama dengan Biaya Admin sehingga komponen tak dikenal menyamar jadi biaya admin, pemetaan yang berlaku tidak bisa dilihat sehingga disimpulkan keliru, dan perubahan pemetaan tidak bergerbang serta tidak berjejak.

Pembanding yang dipakai: 26 permintaan "Bantuan Data" di space yang sama berhenti total setelah alat mandiri berizin dan berlog merge 8 Juli 2026.

## Prasyarat non-kode

- **Keputusan SPV FAT**: akun tersendiri untuk `settlement-adjustment`, supaya residual berhenti berbagi akun 6112 dengan `service-fee`. T5 bisa berjalan tanpa keputusan ini (ia hanya menampilkan peringatan), tetapi manfaat penuhnya baru ada setelah akunnya dipisah.
- **Pengukuran pemakaian layar Setelan Akun** sebelum gerbang dipasang (T1). Tanpa ini, T2 berisiko menghentikan pekerjaan orang yang tidak pernah diberi tahu.
- **Penetapan peran penyetuju**: apakah SPV FAT memakai peran modul `finance` tingkat supervisor. Belum diverifikasi ke prod.
- **Daftar jenis komponen yang memang bukan biaya** (penarikan ke bank, pencairan escrow) dari Finance, supaya daftar di T6 tidak berisik sejak hari pertama.

## Urutan deploy yang mengikat

- Backend sebelum frontend.
- Tidak ada env baru, jadi `--force-recreate` tidak diperlukan.
- Bila T6 memakai kategori inbox baru: `integration-service` dan `notification-service` naik bersama (daftar-izin kategori hidup di `shared-library`), lalu picu satu notifikasi sungguhan sebagai bukti.
- Prod dijalankan manusia (skill `deploy-bip-erp` §0).

## Task

### T1. Ukur siapa yang memakai layar Setelan Akun hari ini
- **Isi**: dari log gateway atau akses rute kv-config, siapa saja yang benar-benar memanggil rute tulis dalam tiga bulan terakhir, dan dari peran apa. Hasilnya menentukan peran mana yang dipasang di T2 dan siapa yang perlu diberi tahu sebelum gerbangnya hidup.
- **Verifikasi**: daftar pemakai nyata, bukan daftar pemegang izin secara teori.
- **Dependensi**: tidak ada. **Ini prasyarat T2, jangan dilewati.**

### T2. Gerbang peran dan validasi nilai pada rute yang mengubah laci akun
- **Repo**: bip-erp `services/integration/main.go`, `internal/interface/http/accurate_handler.go`
- **Isi**: pasang gerbang peran pada `POST`, `PUT`, `DELETE` kv-config, yang hari ini hanya dijaga pemeriksaan gateway. Rute baca tetap terbuka bagi pemegang akses modul integration. Nilai laci divalidasi terhadap katalog akun Accurate, bukan sekadar dibatasi panjang.
- **Test**: kontrol negatif (peran tanpa hak ditolak) berpasangan dengan kontrol positif (peran berhak lolos), lewat Fiber bukan hanya fungsi murni. Nilai bukan akun ditolak dengan pesan yang menyebut sebabnya.
- **Verifikasi**: lewat gateway di dev dengan dua akun berbeda peran, bandingkan bentuk respons bukan hanya status.
- **Dependensi**: T1.

### T3. Jejak perubahan laci akun
- **Repo**: bip-erp `internal/domain/entity/accurate.go`, `internal/infrastructure/repository/accurate_kv_riwayat.go` (baru)
- **Isi**: tiap perubahan menyimpan nilai lama, nilai baru, pengubah, dan waktu sebagai baris riwayat tersendiri. **Bukan hanya `updated_by` pada barisnya**, sebab nilai lama akan hilang tertimpa dan justru nilai lama itu yang dicari saat menelusuri selisih.
- **Test**: dua perubahan berturut-turut menghasilkan dua baris riwayat dengan nilai lama yang benar.
- **Dependensi**: T2 (identitas pemanggil baru tersedia setelah gerbangnya ada).

### T4. Usul lalu setujui untuk perubahan laci akun
- **Repo**: bip-erp `services/integration/`; erp-frontend `features/integration/config-accurate/`
- **Isi**: staf mengusulkan dengan alasan tertulis, SPV FAT menyetujui atau menolak. **Pakai ulang pola Kotak Adopsi yang sudah hidup di modul yang sama** (draft, catatan wajib, panel sebelum dan sesudah, deteksi draf basi, jejak penyelesai), jangan membangun mesin persetujuan kedua. Tanggal cutover dan saklar sistem **tidak** ikut alur ini.
- **Test**: usul yang belum disetujui tidak mengubah nilai yang dipakai pembukuan; penyetuju yang tidak berhak ditolak di gerbang maupun di antrean, memakai fungsi yang sama.
- **Verifikasi**: satu perjalanan utuh di dev sebagai staf lalu sebagai SPV FAT.
- **Dependensi**: T2, T3.

### T5. Residual dilarang berbagi akun dengan kategori bernama
- **Repo**: bip-erp `internal/interface/http/accurate_handler.go`; erp-frontend layar Setelan Akun
- **Isi**: simpanan yang membuat `settlement-adjustment` menunjuk akun yang sama dengan laci bernama ditolak, kecuali ditandai sengaja beserta alasannya. Selama akun residual belum dipisah, layar menampilkan peringatan bahwa dua laci berbagi akun, sehingga keadaannya terlihat alih-alih diam.
- **Test**: kontrol negatif dengan dua laci berakun sama.
- **Dependensi**: T2. Manfaat penuh menunggu keputusan SPV FAT (§ Prasyarat non-kode).

### T6. Daftar komponen yang belum punya akun, per marketplace
- **Repo**: bip-erp `internal/usecase/komponen_belum_berakun.go` (baru); erp-frontend halaman baru di modul integration
- **Isi**: jenis komponen yang muncul di data tetapi belum punya laci, dengan jumlah kejadian, nilai, dan kapan pertama terlihat, per marketplace. Sumbernya data tersimpan, bukan penarikan baru. Pemberitahuan dikirim **sekali** saat sebuah jenis muncul pertama kali; jenis yang sudah diketahui tidak memberitahu lagi. Jenis yang memang bukan biaya ditandai supaya tidak berisik.
- **Test**: jenis yang sudah punya laci tidak muncul di daftar; jenis yang sudah pernah diberitahukan tidak memberitahu dua kali.
- **Verifikasi**: bandingkan jumlah jenis yang tampil dengan pengukuran langsung ke koleksi sumbernya. Nol hasil diperlakukan sebagai pertanyaan, bukan kabar baik.
- **Catatan**: tabelnya pakai `MainTable` dengan `Banner bare` di prop `toolbar`, karena halaman `/integration/master-data/*` belum memakai pola itu dan jangan menambah satu lagi yang menyimpang.
- **Dependensi**: T8 untuk teksnya.

### T7. Transaksi terdampak saat pemetaan berubah
- **Repo**: bip-erp `services/integration/`; erp-frontend `features/integration/config-accurate/`
- **Isi**: sebelum usul disetujui, tampilkan transaksi mana saja yang tercatat dengan akun lama beserta nilainya. ERP **tidak** mengirim koreksi ke Accurate dan tidak mengubah dokumen terkirim ([[ADR - 0001 Akuntansi via Accurate]]). **Pakai ulang pola modal "Faktur terdampak"** pada riwayat harga jual (pilih beserta alasan, konfirmasi, hasil per baris).
- **Test**: daftar terdampak kosong tidak dibaca sebagai "aman", melainkan dinyatakan sebagai tidak ada yang cocok.
- **Dependensi**: T4.

### T8. i18n layar Config Accurate
- **Repo**: erp-frontend `features/integration/config-accurate/`, `src/i18n/locales/id.ts` dan `en.ts`
- **Isi**: layar ini **belum memakai i18n sama sekali** (nol pemakaian `useTranslation`, diperiksa 2026-09-22), sementara T4 sampai T7 menambah teks di sana. Angkat teks yang ada beserta yang baru ke dua berkas locale sesuai [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]].
- **Test**: uji paritas kunci id dan en dengan instance i18next asli, plus kontrol negatif bahwa `en` bukan hasil jatuh balik ke `id`.
- **Catatan**: `id.ts` dan `en.ts` berkas yang paling sering disunting paralel. Sebelum merge, `git merge origin/main` lokal lalu `pnpm tsc` **dan** `pnpm build`.
- **Dependensi**: tidak ada. Kerjakan lebih dulu atau bersamaan dengan T4, jangan ditinggalkan di akhir.

### T9. Catat pemiliknya dan sinkronkan dok
- **Isi**: masukkan fakta "pemetaan komponen biaya marketplace ke akun" ke peta [[REF - Kepemilikan Data]] dengan pemilik Finance dan salinan sah di sheet COA Finance untuk Lazada. Tambahkan tautan dari [[Finance - Proses Penjualan Marketplace dan Uang Masuk]] dan [[Finance - Proses Pencatatan dan Buku Besar]] ke dok domain baru. Naikkan [[ADR - 0116 Setelan Akun Marketplace Bergerbang dan Berjejak, Komponen Tak Dikenal Wajib Terlihat]] ke status terpasang dengan catatan.
- **Dependensi**: T2 sampai T7 sesuai cakupan yang benar-benar dikerjakan.

## Di luar lingkup, tetapi ditemukan saat analisa ini

Dicatat supaya tidak hilang. Keduanya **bukan** bagian dari ADR 0116.

1. **Status [[ADR - 0097 Kompensasi Shopee Susulan Ditahan dan Dicatat AR lewat Koreksi Manual ERP]] sudah basi.** ADR menyatakan penahanan dorman karena kv-nya belum ada (diperiksa 2026-09-17). Kv itu ternyata dibuat pada tanggal yang sama dan kini berisi `2026-09-01`, jadi penahanannya **sudah berjalan**. Terukur 2026-09-22: 4 kompensasi senilai Rp787.000 tertahan menunggu dicatat AR. Perlu pembaruan status dan pengecekan apakah antreannya benar-benar ditindaklanjuti.
2. **Laci akun tidak terpisah dari saklar sistem.** Koleksi yang sama memuat laci akun, tanggal cutover, saklar on dan off, serta penanda idempotensi notifikasi. Field `type` tidak konsisten (dari 26 baris: 17 `string`, 2 `system`, 4 kosong, 3 tanpa field itu), jadi tidak bisa dipakai membedakan. Belum jadi masalah nyata, tetapi menjadikannya alasan untuk berhati-hati saat memberi Finance akses tulis yang lebih luas.

## Task pertama

`/start-task T1 Ukur siapa yang memakai layar Setelan Akun Config Accurate hari ini (ADR 0116)`
