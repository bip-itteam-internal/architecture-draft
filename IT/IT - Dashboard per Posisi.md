## Deskripsi

*Rancangan isi dashboard per posisi untuk divisi **Tech Development**. Diturunkan mengikuti [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]]: KPI yang dinilai, pekerjaan yang menunggu, dan ambang yang tak boleh dilewati. Divisi ini dikerjakan lebih dulu karena satu-satunya yang punya metrik benar-benar otomatis dalam jumlah berarti, jadi rancangannya bisa diuji kebenarannya alih-alih diperdebatkan.*

- **Status**: ⚠️ **Sebagian terbangun, dan rancangan lembar per posisinya DIBATALKAN 2026-09-04** (bukan ditunda). Yang mendarat: blok uptime periode kalender dan tautan ke `/portal/kpi` di Ringkasan Divisi IT, erp-frontend [#1452](https://github.com/bip-itteam-internal/erp-frontend/pull/1452). Sebab pembatalannya di bagian tersendiri di bawah, dan itu jawaban yang sah menurut [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] §4.
- ⚠️ **Dokumen ini TIDAK usang.** Analisis per posisi di bawah tetap berlaku sebagai catatan apa yang menilai tiap orang di divisi ini, dan pelajaran pembatalannya adalah cetakan untuk sembilan divisi sisanya. Sengaja TIDAK diberi marker `⛔`, yang di vault ini berarti "sudah digantikan, jangan dipakai".
- **Angka KPI diukur 2026-08-28** (sumber: [[HRIS - Matriks KPI per Departemen]]). ⚠️ Konfigurasi template divisi ini berubah beberapa kali dalam Agustus 2026. **Ukur ulang sebelum dipakai mengambil keputusan.**
- **Path di repo**: `erp-frontend/src/features/it/ringkasan/`

## Keadaan sekarang

`/it` merender **Ringkasan Divisi**, bukan lembar per posisi: `KartuInfrastruktur`, `KartuHelpdesk`, `KartuKpiTimIt`, `KartuIndeksLayanan`, lalu petak tautan modul.

Ketiadaan tab posisi **bukan kelalaian**, dan alasannya tertulis di kodenya sendiri (`isi-ringkasan-divisi-it.tsx`): peta posisi IT belum ada di kode dan `position_key` belum mengalir ke frontend, sehingga menyusun daftar posisi di sana berarti mengarangnya.

⚠️ **Ralat 2026-09-04**: dokumen ini semula menyimpulkan dari kalimat itu bahwa rancangan di bawah "baru bisa dibangun setelah `position_key` tersedia di frontend". **Itu terlalu keras.** Dari dua alasan di kode, yang pertama sudah gugur (peta posisi IT kini ada, diturunkan dari [[HRIS - Matriks KPI per Departemen]]), dan yang kedua bukan gerbang: **17 lembar HRGA dan FAT sudah berjalan hari ini tanpa `position_key`**, dengan mencocokkan nama posisi dari `useAuth().position`. `position-view.ts` menyebutnya eksplisit sebagai satu-satunya cara selama utang [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] belum lunas.

Jadi secara teknis rancangan di bawah **bisa** dibangun. Yang membatalkannya bukan penghalang teknis, melainkan temuan di bagian berikutnya.

## ⛔ Kenapa lembar per posisi dibatalkan

Ditemukan 2026-09-04 saat lembarnya hendak dibangun: **`/portal/kpi` sudah melayani ketiga posisi berpenghuni divisi ini**, lewat kaskade persona di `erp-frontend/src/app/(main)/portal/kpi/page.tsx`.

| Posisi | Yang sudah didapat hari ini |
|---|---|
| Tech Development Leader | punya bawahan, jadi `KpiPageContent teamScope` |
| Fullstack Developer | bukan penilai, jadi `KpiSayaView` |
| IT Support | bukan penilai, jadi `KpiSayaView` |

`KpiSayaView` (359 baris) sudah lengkap dengan pemilih periode, tren, band skor, lencana sumber otomatis/semi/manual, cakupan per metrik, unggah bukti, dan dialog rincian, yaitu persis isi yang dirancang untuk dua lembar staf di bawah.

**Yang menentukan: keputusan ini sudah pernah diambil di repo dan alasannya tertulis di kode.** Komentar di `page.tsx` menyatakan kartu skor KPI di dashboard sengaja TIDAK melayani cakupan "diri" karena *"dua layar yang menjawab pertanyaan sama akan menyimpang, dan yang ini sudah lebih matang"*. Membangun tiga lembar KPI di `/it` berarti membalik keputusan itu tanpa menyebutnya.

**Yang dibangun sebagai gantinya**, erp-frontend [#1452](https://github.com/bip-itteam-internal/erp-frontend/pull/1452), keduanya benar-benar belum ada sebelumnya:

1. **Blok "Uptime Bulan Penilaian"** di Ringkasan Divisi IT, memakai `GET /api/monitoring/uptime?periode=` yang sebelumnya nol konsumen. Ia menampilkan uptime periode kalender berikut **cakupan harinya**, dan sengaja duduk tepat di bawah blok Kesehatan Infrastruktur yang memakai jendela berjalan 24 jam supaya bedanya terbaca.
2. **Tautan dari kartu KPI tim ke `/portal/kpi`**, menutup titik putus alur: kartu menyebut rata-rata tim sementara pertanyaan berikutnya yang wajar dijawab layar di modul lain, tanpa satu pun tautan.

⚠️ **Pelajaran yang berlaku untuk sembilan divisi sisanya**: sebelum merancang lembar per posisi, periksa lebih dulu apakah `/portal/kpi` sudah menjawabnya untuk posisi itu. Untuk posisi yang **bukan penilai**, kemungkinan besar sudah. Yang benar-benar menambah nilai adalah metrik yang **tidak** ada di scorecard KPI, seperti uptime periode di sini.

Konsekuensi utang `position_key` yang tetap berlaku bila suatu saat lembar per posisi dibangun di divisi mana pun: rename nama posisi di master data memutus pencocokannya secara senyap, jadi selama utang itu hidup perubahan nama posisi wajib diperlakukan sebagai perubahan yang menyentuh frontend.

## Yang menentukan lingkup: penghuni, bukan jumlah template

Divisi ini punya **7 template berisi 30 metrik**, tetapi **4 di antaranya berstatus arsip dan tidak dipegang satu akun aktif pun**.

| Posisi | Akun aktif | Template | Metrik ber-`auto` | Rancangan dashboard |
|---|---:|---|---:|---|
| Tech Development Leader | 1 | `Leader`, 5 metrik | 4 | ✅ dirancang di bawah |
| Fullstack Developer | 4 | `Fullstack`, 4 metrik | 2 | ✅ dirancang di bawah |
| IT Support | 1 | `IT Support`, 4 metrik | 3 | ✅ dirancang di bawah |
| Tech Development Supervisor | 0 | `Supervisor KPI`, 4 metrik | 0 | ⛔ tidak dirancang |
| IT Infrastructure | 0 | `Infrastruktur`, 5 metrik | 0 | ⛔ tidak dirancang |
| Backend Developer | 0 | `Backend Developer`, 4 metrik | 0 | ⛔ tidak dirancang |
| Frontend Developer | 0 | `Frontend Developer`, 4 metrik | 0 | ⛔ tidak dirancang |

**Empat posisi terakhir tidak dirancang** karena tidak dipegang siapa pun, sesuai ADR 0076 §4. Merancang layar untuk template arsip menghasilkan pekerjaan yang tidak mengubah pengalaman seorang pun. Bila salah satunya diisi lagi, rancangannya dibuat saat itu, bukan sekarang.

⚠️ Angka mentah `work_data` divisi ini **11 baris**, dan hanya 6 yang aktif. Jangan membaca jumlah baris sebagai jumlah orang tanpa menyaring `system_authentication.is_active` lebih dulu.

## Tech Development Leader

**Dinilai dari** (template `Leader`, 5 metrik):

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,4 | `Performance Monitoring Team` (KPI Team) | `skor_tim`, scope `team`, target 70 | ⏳ ber-`auto` tapi belum menghasilkan |
| 0,2 | Tiket infra & support tuntas | `kinerja_tiket_divisi` / `support_selesai_persen`, target 95 | ✅ otomatis, Agustus 90,9% → 96 |
| 0,2 | Ketepatan waktu proyek development | `kinerja_tiket_divisi` / `development_ontime`, target 60 (bertahap 30) | ✅ otomatis, Agustus 14,3% → 48 |
| 0,1 | CSAT layanan tim IT | `kinerja_tiket_divisi` / `development_csat`, target 5 | ⚠️ `semi`, cakupan 14,3% |
| 0,1 | Pengendalian anggaran IT | ⛔ sengaja manual | tak ada master anggaran IT |

**Bisa ditampilkan sekarang.** Empat dari lima metriknya punya angka, jadi ini satu-satunya posisi di seluruh perusahaan yang dashboardnya bisa hampir penuh hari ini.

- **Visual utama**: tren bulanan ketepatan waktu proyek development terhadap target bertahap. Ia yang paling menuntut tindakan (14,3% pada Agustus) dan satu-satunya yang bergerak tajam antar-bulan.
- Kartu ambang: tiket support tuntas terhadap 95, CSAT terhadap 5.
- Kartu skor tim: rata-rata skor anggota, sekaligus penanda siapa yang belum dinilai.

**Yang menunggu backend.** Pengendalian anggaran IT tidak bisa digambar sampai master anggaran memuat departemen IT. Sumber `varians_anggaran` memanggil `/accounting/anggaran/varians` **tanpa parameter departemen**, jadi memakainya apa adanya akan menilai Leader IT atas varians anggaran Marketing. Panel jujur, bukan angka.

**Pekerjaan yang menunggu.** Anggota tim yang belum dinilai periode berjalan, karena `skor_tim` membaca `kpi_score` periode yang sama dan Leader yang dinilai lebih dulu kehilangan angka otomatisnya untuk bulan itu. Urutan ini tidak bisa dibalik tanpa menimpa penilaian ([[HRIS - Otomasi Skor KPI]]).

⚠️ **Satu ketidakcocokan yang harus diputuskan sebelum angkanya dipakai**: label CSAT berbunyi "Fullstack & Support" tetapi yang terpasang `development_csat` saja, sehingga rating IT Support tidak ikut terhitung. Menyatukannya butuh sub-metrik baru di kode, bukan konfigurasi.

## Fullstack Developer

**Dinilai dari** (template `Fullstack`, 4 metrik, 4 orang):

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,5 | `System Development` | `kinerja_tiket` / `selesai_persen`, target 85 | ✅ otomatis, Agustus 80% → 94 |
| 0,2 | `Implementasi` (sinkronisasi/review dengan requester) | modul kewajiban [[Microservices - Calendar Service]] | ❌ 0 template, 0 periode, 0 pemenuhan |
| 0,2 | `Customer Satifaction` | `kinerja_tiket` / `csat`, target 5 | ⚠️ `semi`, cakupan 25% |
| 0,1 | `Kaizen` | ⛔ manual karena keputusan | [[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]] |

**Bisa ditampilkan sekarang.**

- **Visual utama**: ketuntasan tiket bulanan terhadap target 85. Ia berbobot 0,5, separuh nilai orangnya, jadi ia yang layak dominan.
- Kartu CSAT dengan **cakupan tertulis di sampingnya**. Angka 100 dari cakupan 25% dan angka 100 dari cakupan penuh berbeda arti, dan tanpa cakupan yang tertulis pembacanya tak punya cara membedakannya.
- Daftar tiket sendiri yang masih terbuka beserta tenggatnya.

**Yang menunggu backend.** `Implementasi` diarahkan ke modul kewajiban Calendar Service. Mesinnya **sudah ter-deploy dan berjalan di produksi** (rute `/obligations/templates` membalas 200, kontrol negatif 404); yang belum ada rute pemakainya. Jadi nol di sana berarti belum ada yang membuat template, bukan modulnya tak ada. Dua hal harus **diputuskan lebih dulu, bukan dikodekan**: siapa yang menandai sesi selesai, dan aturan siapa yang sah jadi lawan sesi.

**Yang TIDAK ditampilkan.** Kaizen. Ia manual karena keputusan, bukan karena kekurangan sistem, jadi panel "menunggu penyambungan" di sana akan berbohong tentang sebabnya.

## IT Support

**Dinilai dari** (template `IT Support`, 4 metrik, 1 orang):

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,4 | `Network` (uptime) | `uptime_sistem`, target 90 | ⚠️ `semi`, Agustus 99,96% |
| 0,3 | `Problem Solving` (SLA e-ticket) | `kinerja_tiket` / `ontime`, target 80 (bertahap 60) | ✅ otomatis, Agustus 80% → 100 |
| 0,15 | `Customer Satisfaction` | `kinerja_tiket` / `csat`, target 5 | ⚠️ `semi`, cakupan 60% |
| 0,15 | `Kaizen` | ⛔ manual karena keputusan | sama dengan Fullstack |

**Bisa ditampilkan sekarang.**

- **Visual utama**: tren ketepatan waktu SLA terhadap target bertahap. Ketepatan waktu bergerak 0% → 7% → 25% → 80% dalam lima bulan, jadi ini deret yang benar-benar bercerita.
- Kartu uptime, tetapi **dengan cakupan hari tertulis** (Agustus 28 dari 31 hari).
- Antrean tiket yang menunggu, diurutkan tenggat.

⚠️ **Peringatan rancangan yang paling penting di halaman ini.** Metrik `Network` berbobot 0,4 diukur terhadap target **90** sementara realisasinya 99,96%, jadi ia memberi nilai penuh setiap bulan. **Metrik berbobot 0,4 yang selalu 100 tidak mengukur apa pun**, dan menaruhnya sebagai kartu besar di dashboard justru mengabarkan hal yang salah: layar akan tampak hijau permanen di bagian yang paling berat bobotnya. Itu persis alasan metriknya dulu dipindah ke `downtime`. **Sampai bentuk metriknya ditinjau ulang, jangan jadikan ia visual dominan.**

## Kebutuhan backend, terurut

1. **Putuskan bentuk metrik `Network` IT Support.** Bukan pekerjaan kode melainkan keputusan: uptime terhadap 90 tidak membedakan bulan baik dari bulan buruk. Sampai diputuskan, kartunya tak layak dominan.
2. **Satukan atau pisahkan CSAT Leader.** Label menjanjikan Fullstack dan Support; yang terpasang development saja. Butuh sub-metrik baru di kode.
3. **Rute pemakai modul kewajiban Calendar Service.** Mesinnya sudah jalan; yang kurang cara orang menjadwalkan dan menandai selesai, plus dua keputusan yang disebut di bagian Fullstack.
4. **Master anggaran departemen IT + parameter departemen di `/accounting/anggaran/varians`.** Keduanya diperlukan bersama; salah satu saja tidak cukup.

⚠️ **Yang TIDAK masuk daftar ini**: `position_key` mengalir ke frontend. Ia utang nyata ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]) tetapi **bukan penghambat** lembar-lembar di atas, sesuai ralat di § Keadaan sekarang. Menaruhnya di sini akan membuat pekerjaan yang bisa jalan hari ini tampak menunggu.

⚠️ **Juga tidak masuk daftar ini**: menaikkan cakupan CSAT. Ia bukan pekerjaan backend melainkan kebiasaan meminta pemohon menilai tiketnya. Menaruhnya di daftar teknis akan membuatnya menunggu rilis yang tak pernah relevan.

## Dokumen Terkait

- [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] — prinsip penurunannya
- [[REF - Layout Dashboard erp-frontend]] — cara menyusunnya di layar
- [[HRIS - Matriks KPI per Departemen]] — sumber angka di dokumen ini
- [[HRIS - Otomasi Skor KPI]] — kenapa `skor_tim` menuntut urutan penilaian
- [[Microservices - Calendar Service]] — modul kewajiban untuk metrik `Implementasi`
- [[IT - Helpdesk]] — sumber tiket, SLA, dan CSAT
- [[IT - Monitoring System]] — sumber uptime
- [[RUN - Menambah Metrik KPI Otomatis]] — cara mengerjakan otomasinya
