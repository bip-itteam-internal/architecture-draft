# ADR - 0145 Agen Pengelola Toko Tumbuh dari Mesin Keputusan yang Ada, Dampak Diukur Sebelum Eksekusi

> **Status**: 🟡 **Diusulkan**, 2026-10-01, kode belum ada. Disetujui pemohon lewat `/analisa-kebutuhan` (opsi C dari tiga). Diusulkan dari Tech Development; **belum ada konfirmasi bahwa manajemen marketing, Finance, atau Direktur sudah membahasnya**. Berdiri di atas grounding vault + kode `origin/main` + pengukuran prod read-only pada 2026-09-30.

%% Status ditulis di blockquote atas, alasan sama dengan ADR 0120/0127/0132/0135:
## Untuk Manajemen mendorong Deskripsi melewati baris ke-15 sehingga status tak terbaca VAULT-INDEX.json. %%

## Untuk Manajemen

**Apa yang berubah di layar.** Beberapa toko dipilih sebagai toko pilot. Untuk toko pilot, laporan keputusan yang sudah ada (hentikan, kurangi, atau naikkan iklan, dan tindakan lain dari daftar tetap) dikirim ke Leader atau SPV brand-nya untuk disetujui atau ditolak. Sekitar sebulan sesudah sebuah keputusan dijalankan, sistem menampilkan hasilnya: laba toko itu dibanding toko sejenis yang tidak mendapat keputusan tersebut. Dari situ terlihat jenis keputusan mana yang benar-benar menambah laba.

**Siapa yang terdampak.** Leader dan SPV Beauty Hacks dan Kyura (menjadi penyetuju untuk toko pilot). Account Specialist pemegang toko pilot tetap tercatat sebagai pemegang, dengan insentif dan KPI tidak berubah, selama tahap pertama. Direktur menerima ringkasan hasilnya.

**Apa yang TIDAK dijanjikan.**
- Tahap pertama **belum menggantikan siapa pun**. Tindakan tetap dijalankan orang di Seller Center; sistem hanya mengusulkan, mencatat persetujuan, dan menilai hasilnya.
- Sistem **tidak mengubah iklan, harga, promo, atau membalas pembeli sendiri** pada tahap ini.
- Hasil sebuah keputusan baru bisa dinilai **sekitar 30 sampai 50 hari** sesudah dijalankan, karena uang dari marketplace dan retur datang terlambat. Kesimpulan pertama paling cepat sekitar dua bulan sesudah pilot dimulai.
- Melepas toko dari Account Specialist menunggu keputusan manajemen dan Finance tentang insentif toko pilot. Tanpa itu, profit toko pilot hilang dari pencapaian Leader dan SPV yang justru menyetujuinya.
- Pembuatan video AI dan pengetahuan toko belum ikut tahap ini.

**Perkiraan besaran kerja.** Tahap pertama: beberapa pekan kerja backend dan satu layar tambahan, di atas fitur laporan keputusan yang sudah berjalan. Sesudah itu ada masa tunggu minimal sekitar 30 sampai 50 hari sampai data pertama matang. Tahap kedua (sistem menjalankan tindakan saat disetujui) belum diperkirakan: bergantung izin dari TikTok dan Shopee serta hasil tahap pertama.

## Deskripsi

*Gagasan "AI agent yang menggantikan Account Specialist" tidak dibangun sebagai service agent baru. Ia tumbuh dari mesin keputusan Asisten Analisa Marketing yang sudah hidup di produksi, dengan dua tambahan yang selama ini tidak ada: penyetuju Leader/SPV untuk toko pilot, dan penilaian dampak tiap keputusan terhadap laba matang dibanding toko pembanding. Eksekusi ke marketplace sengaja ditunda ke tahap kedua yang bergerbang angka, dan melepas toko dari pemegang manusia ditunda sampai aturan insentifnya diputuskan.*

- **Path di repo**: `bip-erp/services/marketing-analytics/keputusan_dampak*.go` (baru) · `bip-erp/services/marketing-analytics/keputusan_pilot*.go` (baru) · `erp-frontend/src/features/marketing-analytics/` layar hasil keputusan (baru, lokasi persis diputuskan `/plan`)
- **Tanggal**: 2026-10-01
- **Dok domain**: [[Marketing - Agen Pengelola Toko]] · daftar task: `Workspace/ANALISA - Agen Pengelola Toko`

## Context

**Permintaan awal adalah solusi, bukan kebutuhan.** Yang diminta: agent AI yang menggantikan pemegang toko (membuat konten, mengelola iklan, promo, CS, strategi), bertujuan laba maksimal dan terus belajar dari pengalaman. Wawancara 2026-09-30 menyempitkannya: sasaran pertama posisi **Account Specialist** (pemegang toko, termasuk membuat video AI), aksi agent **disetujui Leader/SPV brand**, jangka panjang menggantikan, sekarang tahap pembuktian. Kebutuhan di baliknya: pekerjaan mengelola toko berjalan dengan jauh lebih sedikit tenaga manusia tanpa laba turun, dan untuk itu manajemen butuh jawaban atas pertanyaan yang belum bisa dijawab siapa pun: **apakah keputusan mesin untuk sebuah toko sama baiknya dengan keputusan manusia?**

**Yang sudah ada menyelesaikan kira-kira separuhnya.** [[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]] (⚠️, prod sejak 2026-09-28, mode bayangan) sudah punya katalog tertutup sepuluh tindakan (`keputusan_katalog.go:27-36`), kelayakan dihitung backend, model memilih dan menjelaskan, dan jawaban `jalankan`/`tolak` per keputusan tercatat append-only di koleksi `keputusan_kiriman` (`keputusan_kiriman_store.go:143,191-194`). Copilot ([[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]]) murni baca. Ideamills ([[APP - Ideamills]]) membuat video AI dengan persetujuan manusia, tetapi terpisah dari ERP dan tidak menyimpan id video marketplace.

**Yang tidak ada, diukur 2026-09-30:**

1. **Loop belajar belum punya data.** Prod `marketing_analytics_db.keputusan_kiriman` berisi **1 kiriman** (2026-09-28 22:00 UTC, `status_model=siap`) dan **0 jawaban**. Keputusan aturan di kiriman itu: `hentikan_iklan` 19, `kurangi_belanja` 13, `naikkan_belanja` 13, `pertahankan` 11, `periksa` 1.
2. **Dampak keputusan tidak diukur di mana pun.** `git grep` pola `dampak|uplift|toko.pembanding|kelompok.kontrol|sebelum.sesudah` di `services/marketing-analytics` tidak menemukan kode yang membandingkan laba sebelum dan sesudah atau memakai pembanding; satu-satunya hit (`dampakRupiahKeputusan`, `keputusan_kirim_bayangan.go:939`) dipakai untuk mengurutkan. Loop belajar langkah 1 hanya menghitung dijawab/dijalankan per jenis tindakan dalam 90 hari (`keputusan_riwayat.go:9-47`; ADR 0127 § Realisasi butir j).
3. **"Dijalankan" hanya pengakuan orang.** Tidak ada pemeriksaan ke data marketplace bahwa tindakan benar-benar dilakukan.
4. **Nol aksi tulis pemasaran ke marketplace.** `git grep` di `services/` (tanpa test) untuk `reply_comment`, `send_message`, `add_discount`, `add_voucher`, `update_price`, `update_stock`, pola edit/budget iklan Shopee, `promotion/.../activities`, `/prices/update`, `customer_service/.../messages`, `campaign|adgroup|budget/update`, `gmv_max/.../(update|create)`: semuanya 0. Satu-satunya aksi tulis ke marketplace adalah pengiriman barang Shopee (`shopee_client.go:148`).
5. **Pemegang toko**: prod `integration_db.icc_account_mappings` **61 baris aktif, dipegang 36 orang** (20 orang memegang 1 toko, 11 orang 2, 3 orang 3, 2 orang 5), Beauty Hacks 39 dan Kyura 22, nol baris aktif tanpa `employee_id`.

**Tiga keputusan terkunci bertabrakan dengan agent otonom:**

- **Larangan eksekusi.** ADR 0127 §2 ("Sistem tidak mengeksekusi": tidak ada panggilan ke platform iklan, tidak ada perubahan anggaran otomatis) dan [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]] §5.
- **Identitas.** [[ADR - 0135 Jadwal Tugas Copilot Mengirim Pengingat, Bukan Menjalankan Tanpa Kehadiran Pemakai]] menolak eksekusi tanpa kehadiran pemakai karena JWT kedaluwarsa dan TBD di [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] tentang pemanggil tepercaya.
- **Uang dan penilaian orang.** Insentif profit membuang toko tanpa pemegang manusia (`services/insentive/func.go:2168-2170`: `continue // toko tanpa pemegang ICC — tidak masuk baris mana pun`), dan toko Leader/SPV adalah gabungan toko anggotanya (`func.go:853-861`). Pemegang dibaca dari keadaan saat ini tanpa periode (`incentive_profit_repo.go:443`, filter `is_active: true`). KPI `insentif_profit` scope team/department ikut turun (`kpi_sumber_insentif_profit.go:318-325`). Artinya melepas toko pilot dari Account Specialist **mengeluarkan profitnya dari pencapaian Leader/SPV**, padahal merekalah penyetuju aksi agent: konflik kepentingan. [[ADR - 0138 Penugasan Toko Marketplace Bertanggal Berlaku untuk KPI dan Insentif]], yang seharusnya mengatur perpindahan pemegang, masih 🟡 Diusulkan dengan nol kode. `BUSINESS_LOGIC_IMPLEMENTATION.md` (mybharata-app) tidak mengatur insentif maupun KPI; otoritasnya SK 010/011 Direksi ([[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]]). Pasal 54 dokumen itu (penyalahgunaan akses akun) relevan bila agent kelak memakai akun toko atas nama seseorang.

⚠️ **Status dasar keputusan**: ADR 0127 ⚠️ (implemented, mode bayangan, baru satu kiriman); ADR 0058 🟡 Diusulkan; ADR 0135 🟡 Diusulkan; ADR 0138 🟡 Diusulkan. Keputusan ini sebagian berdiri di atas rencana, bukan kenyataan, terutama soal insentif.

## Decision

### 1. Tidak ada service agent baru; satu mesin keputusan

Agen pengelola toko adalah **perluasan mesin keputusan ADR 0127 di `marketing-analytics`**, bukan service kedua dengan memori dan katalog tindakannya sendiri. Dua mesin keputusan untuk toko yang sama akan menyimpang diam-diam (satu fakta satu tempat). Katalog tindakan tetap satu, tumbuh dengan cara yang sudah diatur ADR 0127: satu baris katalog, satu aturan kelayakan, dan uji negatifnya.

### 2. Tahap 1: toko pilot dengan penyetuju Leader/SPV, tanpa eksekusi

- Toko pilot ditetapkan **eksplisit** (daftar toko per jadwal), bukan diturunkan dari aturan.
- Penyetuju toko pilot ditulis **eksplisit per toko**, bukan diturunkan dari peran. `RequireMarketingLeader` tidak dipakai sebagai daftar penyetuju: ia juga meloloskan supervisor integration dan staf IT.
- Keputusan untuk toko pilot yang dijawab penyetujunya memakai jalur jawaban yang sudah ada (`POST /keputusan-kiriman/:id/jawaban`), bukan jalur kedua.
- **ADR 0127 §2 tetap berlaku penuh di tahap 1**: orang yang menekan tombol di Seller Center.

### 3. Setiap keputusan yang dijalankan dinilai dampaknya

- Metrik tunggal: **`laba_matang`** jendela 30 hari sesudah tanggal jawaban `jalankan`, dibanding 30 hari sebelumnya, **dikurangi perubahan yang sama pada toko pembanding** (toko yang tidak menerima keputusan sejenis pada periode itu, dari tim dan channel yang sama). Bukan `gross_profit`: laba yang belum cair terbaca rugi besar (`keputusan_jendela_matang.go:11-12`).
- Penilaian baru dihitung **sesudah matang**; sebelum itu statusnya `belum_matang`, bukan nol.
- Keputusan tanpa pembanding yang layak berstatus **`tak_bisa_dinilai`**, bukan dampak nol.
- Tidak ada proyeksi rupiah ke depan (ADR 0127 tetap melarangnya; R² belanja iklan ke laba 0,258). Yang dilaporkan adalah hasil yang sudah terjadi.
- Hasil penilaian disimpan append-only, terpisah dari dokumen kiriman, dan menjadi masukan loop belajar langkah 2 ADR 0127 (penyesuaian keyakinan dari riwayat) yang selama ini hanya punya hitungan tolak.

### 4. "Dijalankan" diverifikasi dari data bila bisa

Untuk tindakan yang jejaknya terbaca di data (mis. `hentikan_iklan`, `kurangi_belanja`, `naikkan_belanja` terhadap `ads_cost` harian toko/level terkait), sistem menandai `terverifikasi` / `tidak_terverifikasi` / `tak_bisa_diverifikasi`. Pengakuan orang tetap disimpan apa adanya. Penilaian dampak menyebut status verifikasinya, supaya keputusan yang dicatat "dijalankan" padahal tidak dilakukan tidak dihitung sebagai bukti.

### 5. Gerbang ke tahap 2 ditulis di muka

Tahap 2 hanya boleh diusulkan bila **semua** terpenuhi, diukur dari data, bukan kesan:

- minimal **30 keputusan** toko pilot berstatus `jalankan` + `terverifikasi` dengan penilaian **matang**;
- mencakup minimal **2 jenis tindakan**;
- selisih `laba_matang` terhadap pembanding, dijumlah atas keputusan yang dinilai, **tidak negatif**.

Angka ini hanya diubah lewat revisi tertulis ADR ini.

### 6. Tahap 2 (di luar keputusan ini): eksekusi saat disetujui

Arah yang disepakati, **bukan izin**: ketika penyetuju menekan "jalankan", sistem memanggil API marketplace **pada saat itu, memakai identitas orang yang menekan**, satu jenis tindakan per langkah, dimulai dari yang berisiko rendah (balas ulasan), budget iklan paling akhir. Bentuk ini tidak membutuhkan eksekusi tanpa kehadiran pemakai, sehingga tidak bergantung pada penyelesaian ADR 0135/0031. Setiap jenis tindakan yang dieksekusi **wajib ADR sendiri** yang menggantikan ADR 0127 §2 khusus untuk tindakan itu, dan izin scope API dari marketplace harus sudah didapat.

### 7. Toko pilot tidak dilepas dari pemegang manusia sampai insentifnya diputuskan

Selama tahap 1, pemetaan pemegang di `icc_account_mappings` **tidak diubah**; insentif dan KPI Account Specialist, Leader, dan SPV tidak terdampak. Melepas toko pilot dari pemegang manusia adalah langkah terpisah yang mensyaratkan:

- aturan insentif dan KPI untuk toko tanpa pemegang manusia diputuskan manajemen marketing bersama Finance (apakah profitnya tetap masuk pencapaian Leader/SPV), mengikuti keputusan ADR 0138;
- pelepasan dimulai tanggal 1 sebuah periode, supaya skor bulan berjalan tidak rusak;
- agent tidak pernah bertindak memakai akun toko atas nama seseorang (Pasal 54).

### 8. Pengetahuan toko dan video AI di luar tahap 1

- Pengetahuan kurasi manusia (profil toko, klaim produk yang disetujui BPOM, playbook, pelajaran) tinggal di vault **privat** terpisah, bukan di vault ini (repo ini publik). Jalur bacanya dari server diputuskan saat dibutuhkan.
- Pembelajaran konten video menuntut Ideamills menyimpan id video marketplace hasil unggahan, supaya pembuatan bisa disambung ke `tt_shop_video_performances`. Diputuskan terpisah; hari ini `git grep -i ideamills` di bip-erp = 0.

## Consequences

**Yang membaik.**
- Pertanyaan "apakah keputusan mesin menambah laba" untuk pertama kali punya jawaban terukur per jenis tindakan, dan jawaban yang sama menjadi dasar penyesuaian keyakinan model.
- Tidak ada sumber keputusan kedua; semua yang sudah dibangun ADR 0127 (katalog, validator, jawaban, bayangan) dipakai ulang.
- Tidak ada perubahan pada uang siapa pun selama tahap 1.

**Yang diterima sadar.**
- Tahap 1 tidak mengurangi pekerjaan siapa pun; nilainya ada pada bukti, bukan penghematan.
- Belajar lambat: siklus penilaian ±30 sampai 50 hari, dan dengan satu kiriman per jadwal jumlah keputusan terkumpul pelan. Gerbang 30 keputusan mungkin butuh beberapa bulan.
- Toko pembanding tidak sempurna (toko berbeda produk dan audiens); hasil per keputusan berisik, jadi yang dibaca adalah jumlah atas banyak keputusan, bukan satu kasus.
- Verifikasi "dijalankan" hanya mungkin untuk tindakan yang jejaknya ada di data; tindakan lain tetap bersandar pada pengakuan.
- Leader/SPV mendapat pekerjaan baru (menjawab keputusan) tanpa kompensasi yang diputuskan.

**Konsekuensi deploy.**
- Tahap 1 hanya menyentuh `marketing-analytics` dan `erp-frontend`; koleksi baru untuk penilaian dampak dan daftar toko pilot/penyetuju.
- Memakai kategori inbox yang sudah ada (`kategoriInboxLaporanTerjadwal`), jadi tidak perlu menaikkan notification-service bersamaan.
- Bila kontrak `GET /keputusan-kiriman` bertambah field, backend dideploy sebelum frontend.
- Deploy prod dijalankan manusia.

## Terkait

[[Marketing - Agen Pengelola Toko]] · [[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]] · [[ADR - 0120 Asisten Analisa Marketing Jadi Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI]] · [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]] · [[ADR - 0135 Jadwal Tugas Copilot Mengirim Pengingat, Bukan Menjalankan Tanpa Kehadiran Pemakai]] · [[ADR - 0138 Penugasan Toko Marketplace Bertanggal Berlaku untuk KPI dan Insentif]] · [[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]] · [[ADR - 0125 Insentif Profit Dibayar lewat Slip Gaji dari Snapshot yang Disetujui Finance]] · [[ADR - 0107 Alat Kerja Pemegang Akun Toko lewat Izin Posisi akuntoko]] · [[ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak]] · [[Microservices - Marketing Analytics Service]] · [[Finance - Incentive]] · [[APP - Ideamills]]
