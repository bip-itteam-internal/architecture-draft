# ANALISA - Hak Akses Satu Pintu

> **Menunggu [[ADR - 0164 Hak Akses Satu Pintu, Peran Dibawa Paket Hak dan Dirakit saat Token Terbit]] Diterima: sebelum itu ANALISA ini BUKAN keputusan yang bisa ditunjuk `/brief`.**

- **Keputusan**: [[ADR - 0164 Hak Akses Satu Pintu, Peran Dibawa Paket Hak dan Dirakit saat Token Terbit]] (ðŸŸ¡ Diusulkan, 2026-10-10)
- **Dok domain**: [[CORE - RBAC dan Permission Set]]
- **Pemutus**: irfanarfianto
- **Ukuran**: **Besar**. Dua repo harus berubah (`bip-erp`, `erp-frontend`), dan `bip-erp` butuh empat PR. `my-bharata` TIDAK dihitung: respons login tetap membawa `system_roles` sebagai peta modul ke teks, bentuk yang sudah dibaca aplikasi (`mybharata-app` `lib/src/features/auth/data/implements/auth_implements.dart:66-72`, `origin/dev`).
- **Dibuat**: 2026-10-10 oleh `/analisa-kebutuhan`. Issue dibuat TANPA label `Siap Agent`; label dipasang manusia sesudah ADR Diterima.

## Urutan

| Urut | Issue | Repo | Judul |
|---|---|---|---|
| induk, tanpa PR sendiri | bip-erp#2933 | `bip-erp` | Hak akses satu pintu: paket hak membawa peran |
| 1 | bip-erp#2934 | `bip-erp` | [BE] Alat banding isi token per akun, baca saja (bagian 1/4) |
| 2 | bip-erp#2935 | `bip-erp` | [BE] Paket peran dan perakitannya saat token terbit, di belakang sakelar (bagian 2/4) |
| 3, deploy sesudah BE 2/4 | erp-frontend#2285 | `erp-frontend` | [FE] Hak Akses: hak efektif per orang dan pemasangan paket peran (bagian 1/2) |
| 4, lalu pemindahan data dan penyalaan sakelar oleh manusia | bip-erp#2936 | `bip-erp` | [BE] Skrip pemindahan data peran ke paket peran (bagian 3/4) |
| 5, sesudah sakelar menyala di produksi | erp-frontend#2286 | `erp-frontend` | [FE] Akun Karyawan tanpa form peran, tab Role Modul akun pihak luar ditiadakan (bagian 2/2) |
| 6, sesudah FE 2/2 terpasang di produksi | bip-erp#2937 | `bip-erp` | [BE] Tutup jalur tulis peran per akun dan bongkar tabel peran di kode (bagian 4/4) |

## Langkah manusia di antara issue

1. Sesudah BE 1/4 merged: jalankan alat banding di produksi (baca saja), tempel ringkasannya ke issue BE 3/4.
2. Sesudah BE 3/4 merged: bekukan perubahan hak, jalankan skrip pemindahan dalam mode uji coba, pastikan selisih nol, baru terapkan.
3. Nyalakan sakelar perakitan di employee-service (container dibuat ulang), periksa nilainya di container, lalu jalankan alat banding sekali lagi.
4. Putuskan butir pertama bagian Belum Diputuskan di ADR (penerima notifikasi berbasis peran) sebelum pembaca peran dari database dipindahkan; pekerjaan itu belum punya issue.

## Draf issue

### Hak akses satu pintu: paket hak membawa peran

Repo tujuan: `bip-erp` Â· Urutan: induk, tanpa PR sendiri Â· https://github.com/bip-itteam-internal/bip-erp/issues/2933

**Pemutus:** @irfanarfianto
**PIC:** belum ditetapkan

#### Masalah

Hak akses diatur di dua tempat: peran per modul diketik per akun di menu Akun Karyawan, sedangkan paket hak dipasang per jabatan di menu Hak Akses. Ada sumber ketiga yang tidak terlihat di layar mana pun: peran yang diturunkan dari jabatan saat token terbit (`services/employee/peran_dari_jabatan.go`). Akibatnya pertanyaan "orang ini boleh apa, dari mana" tidak bisa dijawab dari satu layar, dan database tidak menceritakan peran yang berlaku.

#### Keputusan

ADR "Hak Akses Satu Pintu, Peran Dibawa Paket Hak dan Dirakit saat Token Terbit" (vault `architecture-draft`, folder Decisions). Layak `Siap Agent` sesudah ADR itu berstatus Diterima (saat issue ini dibuat masih Diusulkan).

Bentuknya, ringkas:
- Peran dibawa paket berjenis peran (satu modul, satu nilai, tanpa izin), dipasang ke jabatan dengan pengecualian per akun, dan dirakit saat token terbit.
- Bentuk keluaran tidak berubah: klaim `system_roles` dan respons login tetap peta modul ke satu teks. Gerbang, sidebar, `proxy.ts`, dan MyBharata tidak disentuh.
- Isi token tiap akun sebelum dan sesudah harus sama persis; selisih ke arah mana pun adalah kegagalan.

#### Yang harus benar

- [ ] Keenam sub-issue di bawah merged.
- [ ] Di produksi, alat banding melaporkan selisih nol untuk semua akun sebelum sakelar dinyalakan (dijalankan manusia).
- [ ] Sesudah sakelar menyala, hak hanya bisa diubah dari menu Hak Akses.

#### Di luar cakupan

- Memindahkan gerbang backend dan menu web dari peran ke izin (tahap berikutnya, per modul).
- Merapikan hak yang keliru atau menyeragamkan pemegang jabatan.
- Perubahan apa pun di MyBharata.

#### Data / bukti pendukung

Sensus produksi `employee_db`, baca saja, 2026-10-10 (ukur ulang sebelum dipakai):
- 220 akun, 183 aktif; 122 menyimpan peran; 35 memegang paket per akun; 74 akun aktif tanpa peran dan tanpa paket.
- 125 jabatan di master, 38 berpaket; 130 paket di 26 modul.
- 78 jabatan punya pemegang; 14 di antaranya pemegangnya menyimpan peran tidak seragam (23 orang menyimpang dari mayoritas). Dihitung dari peran TERSIMPAN, bukan peran yang berlaku.
- Nilai peran tidak baku: `admin gudang RM` (spasi) dan `admin_gudang` (garis bawah) hidup berdampingan.

#### Prasyarat

Issue ini induk dan tidak punya PR sendiri. Urutan: BE 1/4, BE 2/4, FE 1/2, BE 3/4, pemindahan data dan penyalaan sakelar di produksi oleh manusia, FE 2/2, BE 4/4.

### [BE] Alat banding isi token per akun, baca saja (bagian 1/4)

Repo tujuan: `bip-erp` Â· Urutan: 1 Â· https://github.com/bip-itteam-internal/bip-erp/issues/2934

**Pemutus:** @irfanarfianto
**PIC:** belum ditetapkan

#### Masalah

Tidak ada cara membuktikan hak seseorang sama sebelum dan sesudah peralihan. Peran yang berlaku bukan yang tersimpan: `peranEfektif` menambahkan peran dari jabatan saat token terbit (`services/employee/peran_dari_jabatan.go:332-341`), dan izin digabung dari paket jabatan dan akun (`services/employee/permission_resolve.go`). Alat yang membaca `system_authentication.system_roles` saja akan meleset untuk setiap akun berperan turunan.

#### Keputusan

ADR "Hak Akses Satu Pintu, Peran Dibawa Paket Hak dan Dirakit saat Token Terbit" (vault `architecture-draft`, folder Decisions), Decision butir 6. Layak `Siap Agent` sesudah ADR itu berstatus Diterima (saat issue ini dibuat masih Diusulkan).

Bentuknya: perintah baca-saja yang, untuk setiap akun, mengeluarkan isi token (`system_roles` dan `permissions`) persis seperti yang diterbitkan keempat jalur login. Dijalankan manusia; tidak menulis apa pun ke database.

#### Yang harus benar

- [ ] Perhitungannya memanggil fungsi yang SAMA dengan jalur penerbitan token, bukan salinannya. Ada uji yang gagal bila jalur login dan alat ini memakai fungsi berbeda.
- [ ] Semua akun dihitung, termasuk akun nonaktif dan akun pihak luar.
- [ ] Akun yang perannya diturunkan dari jabatan menampilkan peran turunan itu (uji dengan satu jabatan dari tabel peran).
- [ ] Ringkasan memuat: jumlah akun, daftar pasangan modul dan nilai peran yang hidup dengan ejaan apa adanya, dan jumlah jabatan yang pemegangnya tidak seragam menurut peran yang BERLAKU.
- [ ] Keluaran tidak memuat kata sandi, PIN, atau data perangkat.
- [ ] Menjalankannya dua kali tanpa perubahan data menghasilkan keluaran identik.

#### Di luar cakupan

Perakitan cara baru dan perhitungan selisih (bagian 2/4).

#### Data / bukti pendukung

Sensus produksi `employee_db`, baca saja, 2026-10-10 (ukur ulang sebelum dipakai):
- 220 akun, 183 aktif; 122 menyimpan peran; 35 memegang paket per akun; 74 akun aktif tanpa peran dan tanpa paket.
- 125 jabatan di master, 38 berpaket; 130 paket di 26 modul.
- 78 jabatan punya pemegang; 14 di antaranya pemegangnya menyimpan peran tidak seragam (23 orang menyimpang dari mayoritas). Dihitung dari peran TERSIMPAN, bukan peran yang berlaku.
- Nilai peran tidak baku: `admin gudang RM` (spasi) dan `admin_gudang` (garis bawah) hidup berdampingan.

#### Prasyarat

Tidak ada. Bagian 1/4.

### [BE] Paket peran dan perakitannya saat token terbit, di belakang sakelar (bagian 2/4)

Repo tujuan: `bip-erp` Â· Urutan: 2 Â· https://github.com/bip-itteam-internal/bip-erp/issues/2935

**Pemutus:** @irfanarfianto
**PIC:** belum ditetapkan

#### Masalah

Peran per modul hanya bisa diisi dengan mengetiknya per akun, atau lewat tabel di kode Go. Tidak ada cara memasangnya ke jabatan dari layar.

#### Keputusan

ADR "Hak Akses Satu Pintu, Peran Dibawa Paket Hak dan Dirakit saat Token Terbit" (vault `architecture-draft`, folder Decisions), Decision butir 2 sampai 6. Layak `Siap Agent` sesudah ADR itu berstatus Diterima (saat issue ini dibuat masih Diusulkan).

Bentuknya:
- Paket peran: satu modul, satu nilai peran, tanpa izin, memakai key baru (bukan key bawaan).
- Saat token terbit, untuk tiap modul: pengecualian akun menang, selain itu paket peran jabatan. Pengecualian boleh berbunyi "tanpa peran".
- Semuanya di belakang sakelar yang bawaannya MATI.

#### Yang harus benar

- [ ] Sakelar mati: isi token setiap akun identik dengan sebelum perubahan ini (dibuktikan alat banding bagian 1/4).
- [ ] Sakelar menyala: peran dirakit dari paket peran di keempat jalur (login, PIN, biometrik, refresh), dengan aturan pengecualian di atas.
- [ ] Paket peran tidak menambah satu pun entri ke klaim `permissions`, dan `common.KlaimMemuatIzinModul` tetap bernilai sama untuk akun yang hanya memegang paket peran (ada ujinya).
- [ ] Dua paket peran untuk modul yang sama pada satu jabatan ditolak saat disimpan.
- [ ] Nilai peran disimpan dan dikeluarkan dengan ejaan apa adanya, tanpa normalisasi.
- [ ] Respons login tetap peta modul ke teks: tidak ada nilai bukan teks, dan kuncinya tetap ada walau kosong (uji kontrak; MyBharata versi lama gagal login bila bentuk ini berubah).
- [ ] Migrasi yang jalan saat service menyala tidak mengubah paket peran maupun pemasangannya (ada ujinya).
- [ ] Alat banding diperluas: menghitung isi token cara baru dan melaporkan selisih dua arah per akun.
- [ ] Endpoint baca hak efektif satu akun beserta asalnya (jabatan atau pengecualian), bergerbang IT.

#### Di luar cakupan

- Memindahkan data produksi (bagian 3/4).
- Menutup jalur tulis peran dan membongkar tabel peran di kode (bagian 4/4).
- Mengubah gerbang mana pun.

#### Data / bukti pendukung

Sensus produksi `employee_db`, baca saja, 2026-10-10 (ukur ulang sebelum dipakai):
- 220 akun, 183 aktif; 122 menyimpan peran; 35 memegang paket per akun; 74 akun aktif tanpa peran dan tanpa paket.
- 125 jabatan di master, 38 berpaket; 130 paket di 26 modul.
- 78 jabatan punya pemegang; 14 di antaranya pemegangnya menyimpan peran tidak seragam (23 orang menyimpang dari mayoritas). Dihitung dari peran TERSIMPAN, bukan peran yang berlaku.
- Nilai peran tidak baku: `admin gudang RM` (spasi) dan `admin_gudang` (garis bawah) hidup berdampingan.

#### Prasyarat

Bagian 1/4 merged. Bagian 2/4.

### [FE] Hak Akses: hak efektif per orang dan pemasangan paket peran (bagian 1/2)

Repo tujuan: `erp-frontend` Â· Urutan: 3, deploy sesudah BE 2/4 Â· https://github.com/bip-itteam-internal/erp-frontend/issues/2285

**Pemutus:** @irfanarfianto
**PIC:** belum ditetapkan

#### Masalah

Menu Hak Akses belum bisa menjawab "hak satu orang beserta asalnya": tab yang ada bekerja per jabatan, dan pemasangan per akun hanya menampilkan paket yang ditempel ke akun. Paket peran juga belum bisa dipasang dari layar.

#### Keputusan

ADR "Hak Akses Satu Pintu, Peran Dibawa Paket Hak dan Dirakit saat Token Terbit" (vault `architecture-draft`, folder Decisions), Decision butir 1, 2, 4, dan 11. Layak `Siap Agent` sesudah ADR itu berstatus Diterima (saat issue ini dibuat masih Diusulkan).

Bentuknya: menu Hak Akses (`/it/hak-akses`) mendapat tampilan hak efektif per orang, dan paket peran bisa dipasang di tab Hak per Posisi serta sebagai pengecualian per akun.

#### Yang harus benar

- [ ] Dari menu Hak Akses, memilih satu orang menampilkan peran dan paket izinnya, masing-masing dengan asalnya: dari jabatan, atau pengecualian akun.
- [ ] Tab Hak per Posisi bisa memasang dan melepas paket peran pada jabatan; dua paket peran untuk modul yang sama tidak bisa dipilih bersamaan.
- [ ] Pengecualian per akun bisa berbunyi "tanpa peran" untuk sebuah modul, dan tampil jelas sebagai pengecualian.
- [ ] Di daftar paket, paket peran terpisah jelas dari paket izin.
- [ ] Akun pihak luar bisa dipasangi paket peran dari layar yang sama.
- [ ] Yang boleh mengubah tetap supervisor IT; pengguna lain hanya melihat.
- [ ] Semua teks baru lewat i18n di `id.ts` dan `en.ts`.
- [ ] Lima keadaan layar tertangani (memuat, kosong, galat, sebagian, penuh), memakai komponen yang sudah ada.

#### Di luar cakupan

- Membuang form peran di Akun Karyawan (bagian 2/2).
- Mengubah sidebar, `proxy.ts`, atau gerbang menu.

#### Data / bukti pendukung

Sensus produksi `employee_db`, baca saja, 2026-10-10 (ukur ulang sebelum dipakai):
- 220 akun, 183 aktif; 122 menyimpan peran; 35 memegang paket per akun; 74 akun aktif tanpa peran dan tanpa paket.
- 125 jabatan di master, 38 berpaket; 130 paket di 26 modul.
- 78 jabatan punya pemegang; 14 di antaranya pemegangnya menyimpan peran tidak seragam (23 orang menyimpang dari mayoritas). Dihitung dari peran TERSIMPAN, bukan peran yang berlaku.
- Nilai peran tidak baku: `admin gudang RM` (spasi) dan `admin_gudang` (garis bawah) hidup berdampingan.

#### Prasyarat

Sub-issue BE bagian 2/4 merged dan terpasang di dev (menyediakan paket peran dan endpoint hak efektif). Deploy sesudah BE. Bagian 1/2.

### [BE] Skrip pemindahan data peran ke paket peran (bagian 3/4)

Repo tujuan: `bip-erp` Â· Urutan: 4, lalu pemindahan data dan penyalaan sakelar oleh manusia Â· https://github.com/bip-itteam-internal/bip-erp/issues/2936

**Pemutus:** @irfanarfianto
**PIC:** belum ditetapkan

#### Masalah

Peran yang berlaku hari ini tersebar di kolom peran tiap akun dan di tabel peran dalam kode. Agar bisa diatur dari satu pintu, semuanya harus dipindahkan menjadi paket peran tanpa mengubah hak siapa pun.

#### Keputusan

ADR "Hak Akses Satu Pintu, Peran Dibawa Paket Hak dan Dirakit saat Token Terbit" (vault `architecture-draft`, folder Decisions), Decision butir 3, 7, 8, dan 12. Layak `Siap Agent` sesudah ADR itu berstatus Diterima (saat issue ini dibuat masih Diusulkan).

Bentuknya: skrip pemindahan yang dijalankan MANUSIA, mengikuti pola `scripts/hrga-perbaikan-peran` (uji coba sebagai bawaan, cadangan, pembatalan).

#### Yang harus benar

- [ ] Bawaannya uji coba: tanpa tanda terapkan, tidak ada yang ditulis.
- [ ] Membangkitkan satu paket peran untuk tiap pasangan modul dan nilai yang hidup, dengan ejaan apa adanya.
- [ ] Isi tabel peran dari jabatan di kode menjadi paket peran yang terpasang di jabatannya.
- [ ] Tiap jabatan menerima paket peran yang dipegang mayoritas pemegangnya menurut peran yang BERLAKU; pemegang yang berbeda menjadi pengecualian per akun, termasuk pengecualian "tanpa peran".
- [ ] Akun pihak luar menerima paket peran per akun.
- [ ] Mode terapkan menolak berjalan bila alat banding melaporkan selisih yang bukan nol.
- [ ] Idempoten: dijalankan dua kali menghasilkan keadaan yang sama.
- [ ] Ada cadangan sebelum menulis dan perintah pembatalan yang mengembalikannya.
- [ ] Kolom peran tersimpan di akun tidak dihapus dan tidak diubah.

#### Di luar cakupan

- Menyalakan sakelar di lingkungan mana pun (manusia).
- Menyeragamkan pemegang jabatan atau merapikan pengecualian.

#### Data / bukti pendukung

Perlu ukur prod: keluaran alat banding bagian 1/4 di produksi, yaitu jumlah jabatan yang pemegangnya tidak seragam menurut peran yang BERLAKU dan daftar pasangan modul dan nilai yang hidup. Angka sensus di bawah dihitung dari peran tersimpan dan hanya perkiraan.

Sensus produksi `employee_db`, baca saja, 2026-10-10 (ukur ulang sebelum dipakai):
- 220 akun, 183 aktif; 122 menyimpan peran; 35 memegang paket per akun; 74 akun aktif tanpa peran dan tanpa paket.
- 125 jabatan di master, 38 berpaket; 130 paket di 26 modul.
- 78 jabatan punya pemegang; 14 di antaranya pemegangnya menyimpan peran tidak seragam (23 orang menyimpang dari mayoritas). Dihitung dari peran TERSIMPAN, bukan peran yang berlaku.
- Nilai peran tidak baku: `admin gudang RM` (spasi) dan `admin_gudang` (garis bawah) hidup berdampingan.

#### Prasyarat

Bagian 2/4 merged dan terpasang di dev. Bagian 3/4. Selama pemindahan di sebuah lingkungan, perubahan hak di lingkungan itu dibekukan.

### [FE] Akun Karyawan tanpa form peran, tab Role Modul akun pihak luar ditiadakan (bagian 2/2)

Repo tujuan: `erp-frontend` Â· Urutan: 5, sesudah sakelar menyala di produksi Â· https://github.com/bip-itteam-internal/erp-frontend/issues/2286

**Pemutus:** @irfanarfianto
**PIC:** belum ditetapkan

#### Masalah

Menu Akun Karyawan (`/it/employee`) masih memuat form peran per modul, dan dialog akses akun pihak luar masih punya tab Role Modul. Keduanya pintu kedua untuk mengatur hak.

#### Keputusan

ADR "Hak Akses Satu Pintu, Peran Dibawa Paket Hak dan Dirakit saat Token Terbit" (vault `architecture-draft`, folder Decisions), Decision butir 1 dan 9. Layak `Siap Agent` sesudah ADR itu berstatus Diterima (saat issue ini dibuat masih Diusulkan).

Bentuknya: form peran dan tab Role Modul ditiadakan. Di tempat form peran ada ringkasan baca-saja hak orang itu dengan tautan ke menu Hak Akses.

#### Yang harus benar

- [ ] Dialog akun di Akun Karyawan tidak lagi punya isian peran; aksi lain (aktif dan nonaktif, reset kata sandi, lupakan perangkat) tidak berubah.
- [ ] Di dialog itu tampil ringkasan baca-saja peran orang tersebut, dengan tautan yang membuka orang yang sama di menu Hak Akses.
- [ ] Dialog akses akun pihak luar tidak lagi punya tab Role Modul.
- [ ] Panel Peran vs Jabatan menampilkan peran yang berlaku beserta asalnya, atau ditiadakan bila tampilan hak efektif sudah menggantikannya.
- [ ] Kode yang hanya melayani form peran ikut dibuang beserta ujinya, dan kunci i18n yang tak terpakai dibuang dari `id.ts` dan `en.ts`.
- [ ] Tidak ada tempat lain di web yang menulis peran per akun (dibuktikan `git grep` atas pemanggil endpoint penulis peran).

#### Di luar cakupan

- Mengubah sidebar, `proxy.ts`, atau gerbang menu.

#### Data / bukti pendukung

Sensus produksi `employee_db`, baca saja, 2026-10-10 (ukur ulang sebelum dipakai):
- 220 akun, 183 aktif; 122 menyimpan peran; 35 memegang paket per akun; 74 akun aktif tanpa peran dan tanpa paket.
- 125 jabatan di master, 38 berpaket; 130 paket di 26 modul.
- 78 jabatan punya pemegang; 14 di antaranya pemegangnya menyimpan peran tidak seragam (23 orang menyimpang dari mayoritas). Dihitung dari peran TERSIMPAN, bukan peran yang berlaku.
- Nilai peran tidak baku: `admin gudang RM` (spasi) dan `admin_gudang` (garis bawah) hidup berdampingan.

#### Prasyarat

Sub-issue FE bagian 1/2 terpasang di produksi, dan pemindahan data serta penyalaan sakelar di produksi sudah dijalankan manusia. Tanpa itu, meniadakan form peran menghilangkan satu-satunya cara mengubah hak. Bagian 2/2.

### [BE] Tutup jalur tulis peran per akun dan bongkar tabel peran di kode (bagian 4/4)

Repo tujuan: `bip-erp` Â· Urutan: 6, sesudah FE 2/2 terpasang di produksi Â· https://github.com/bip-itteam-internal/bip-erp/issues/2937

**Pemutus:** @irfanarfianto
**PIC:** belum ditetapkan

#### Masalah

Sesudah peran dirakit dari paket, jalur lama yang menulis peran per akun masih terbuka, dan tabel peran di kode masih hidup. Keduanya membuat pintu kedua tetap ada.

#### Keputusan

ADR "Hak Akses Satu Pintu, Peran Dibawa Paket Hak dan Dirakit saat Token Terbit" (vault `architecture-draft`, folder Decisions), Decision butir 8 dan 9. Layak `Siap Agent` sesudah ADR itu berstatus Diterima (saat issue ini dibuat masih Diusulkan).

Bentuknya: ketika sakelar perakitan menyala, endpoint yang menulis peran per akun menolak dengan pesan yang mengarahkan ke menu Hak Akses. Tabel peran dari jabatan di kode dan sakelar lamanya dibongkar.

#### Yang harus benar

- [ ] Dengan sakelar menyala, penulisan peran ditolak di semua jalurnya: jalur layar Akun Karyawan (orchestrator IT), `PATCH /account/roles`, bagian peran pada pembaruan dan pembuatan akun, dan jalur peran akun pihak luar. Pesannya menyebut menu Hak Akses.
- [ ] Dengan sakelar mati, semua jalur itu berperilaku seperti sekarang.
- [ ] Reset akun tetap tidak mengubah hak.
- [ ] Tabel peran dari jabatan dan sakelar lamanya dibongkar, dan alat banding tetap melaporkan selisih nol sesudahnya.
- [ ] Kolom peran tersimpan tetap ada.

#### Di luar cakupan

- Memindahkan pembaca peran langsung dari database (penerima notifikasi, daftar admin). Itu menunggu satu keputusan yang masih terbuka di ADR, dan dibuat sebagai issue tersendiri sesudah diputuskan.
- Membuang kolom peran tersimpan.

#### Data / bukti pendukung

Sensus produksi `employee_db`, baca saja, 2026-10-10 (ukur ulang sebelum dipakai):
- 220 akun, 183 aktif; 122 menyimpan peran; 35 memegang paket per akun; 74 akun aktif tanpa peran dan tanpa paket.
- 125 jabatan di master, 38 berpaket; 130 paket di 26 modul.
- 78 jabatan punya pemegang; 14 di antaranya pemegangnya menyimpan peran tidak seragam (23 orang menyimpang dari mayoritas). Dihitung dari peran TERSIMPAN, bukan peran yang berlaku.
- Nilai peran tidak baku: `admin gudang RM` (spasi) dan `admin_gudang` (garis bawah) hidup berdampingan.

#### Prasyarat

Bagian 3/4 merged, pemindahan data dan penyalaan sakelar di produksi sudah dijalankan manusia, dan sub-issue FE bagian 2/2 sudah terpasang di produksi (form peran harus hilang dari layar sebelum backend menolaknya). Bagian 4/4.
