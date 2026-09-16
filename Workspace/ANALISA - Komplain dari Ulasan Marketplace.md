# ANALISA - Komplain dari Ulasan Marketplace

Daftar task hasil `/analisa-kebutuhan` 2026-09-16, **direvisi hari yang sama**. Keputusannya di [[ADR - 0099 Komplain dari Ulasan Marketplace Dirutekan per Departemen lewat Register Komplain yang Ada]].

Papan kerja, bukan arsitektur. Tiap item cukup jelas untuk langsung dilempar ke `/start-task`.

⚠️ **Revisi 2026-09-16.** Daftar pertama dibuka dengan "T1. Master kategori komplain". **Task itu DIBATALKAN.** Gerbang cari-sebelum-membangun di `/plan` menemukan register komplain gudang sudah ada lengkap dengan daftar kategori tertutupnya sendiri, sehingga master ketiga hanya akan jadi sumber kedua yang menyimpang. Jangan mencarinya lagi di daftar ini.

## Menunggu keputusan orang, bukan kode

- [ ] **K1. Tujuan yang belum punya register.** Keluhan yang mengarah ke ekspedisi, vendor, atau tim brand tidak punya tempat mencatat. Pilihannya: dibuatkan nanti, dialihkan ke CS sebagai pengaju klaim ke marketplace, atau diakui di luar kendali dan cukup ditampilkan tanpa tiket. Tidak memblokir jalur gudang dan QC.
- [ ] **K2. Kewajiban regulatif untuk keluhan dugaan efek tidak diinginkan.** Vault tidak punya dasarnya dan melarang mengarangnya. Pertanyaan untuk QA/RA: wajib masuk jalur CAPA atau pelaporan BPOM atau tidak.
- [ ] **K3. Lima toko Beauty Hacks tanpa CS.** Terukur 2026-09-16. Berdiri sendiri, tetapi memengaruhi KPI penyelesaian komplain yang sudah berjalan.

## Backend

- [x] **T1. Buka rute BACA `/wms/komplain` ke marketing.** ✅ 2026-09-16, branch bip-erp `fix/warehouse-komplain-akses-marketing` (belum merge, belum PROD). Gerbangnya dikomposisikan, bukan disalin (`komplain_akses.go`), penyaringan Sadewa tetap berlaku sebagai lapisan terakhir. Ternyata lebih besar dari "kecil": cakupan toko per pembaca menuntut panggilan lintas service ke `GET /icc/mappings/me`, dan dua kelas kegagalan senyap ikut ditutup di sana (`"data": null` yang berarti nol toko, dan identitas kosong yang harus 401 bukan 500).
- [ ] **T2. Salinan ulasan di register.** Blok ringkas berisi channel, id ulasan, bintang, teks, foto, dan tanggal, disalin saat komplain dibuat. Untuk jalur gudang menumpang `keterangan` dan `bukti_foto` yang sudah ada bila cukup; untuk jalur QC menuntut field baru. Tambahkan penanda sumber supaya komplain dari ulasan terbedakan dari yang diketik manual.
- [ ] **T3. Notifikasi untuk register gudang.** Hari ini register itu tidak mengirim notifikasi sama sekali. Ikuti pola dua kategori milik jalur QC: satu ke penerima saat diajukan, satu ke pengaju saat ditindaklanjuti. ⚠️ Kategori inbox baru berarti service pengirim dan notification-service wajib naik bersama, notification-service lebih dulu.
- [ ] **T4. Pemicu notifikasi ulasan bintang rendah ke pemegang toko.** Penerimanya diturunkan dari `department_shops`. Service mana yang memicunya diputuskan di `/plan`, sebab ulasan dimiliki integration-service.

## Frontend

- [x] **T5. Layar komplain gudang.** ✅ 2026-09-16, branch erp-frontend `feat/warehouse-komplain-layar` (belum merge, belum PROD). `/warehouse/komplain`, SATU layar untuk dua audiens dengan kolom Aksi yang berbeda, dua entri menu ke URL yang sama karena marketing tak punya peran `warehouse`. ⛔ **Layar ini lahir KOSONG dan akan tetap kosong sampai T6 mendarat** — tak ada satu pun cara mengajukan komplain lewat layar mana pun. Itu syarat yang disepakati saat memilih mengerjakan T5 lebih dulu.
- [x] **T6. Tombol ajukan komplain dari baris ulasan.** ✅ 2026-09-16, branch erp-frontend `feat/ajukan-komplain-dari-ulasan` dan bip-erp `feat/komplain-dari-ulasan`. Tujuan dipilih lebih dulu (hanya Gudang yang punya register; QC dan ekspedisi tampil tak dapat dipilih berikut alasannya), lalu kategori milik gudang. `order_sn`, teks, foto, bintang, dan `comment_id` terbawa otomatis. **T2 ikut terpenuhi untuk jalur gudang**: salinan ulasan disimpan di register beserta penanda sumber yang ditimpa server. Tombolnya digerbang KEPEMILIKAN toko, bukan peran. ⚠️ Ulasan lama (sebelum WMS menarik pesanan per 1 Juli 2026) ditolak 404, dan itu keadaan normal yang dijelaskan di modalnya.
- [ ] **T7. Penanda keadaan di layar.** Hanya Shopee, dan tujuan yang belum terlayani ditampilkan apa adanya alih-alih dipaksa masuk register yang ada.

## Sesudah data terkumpul

- [ ] **T8. Rekap pola per toko dan per kategori.** Baru berguna setelah beberapa bulan. Ini juga yang kelak jadi dasar menentukan tenggat, menggantikan angka tebakan.

## Di luar lingkup

- **Master kategori komplain. DIBATALKAN**, lihat catatan revisi di atas.
- Register komplain ketiga. Dua yang ada sudah cukup untuk gudang dan QC.
- Klasifikasi otomatis atau LLM. Volumenya 3 sampai 4 per bulan.
- Membalas pembeli. Tetap milik CS di Seller Center.
- TikTok. Tidak ada teks ulasan per pembeli sama sekali.
- Tenggat dan SLA. Lihat keputusan 9 di ADR.
