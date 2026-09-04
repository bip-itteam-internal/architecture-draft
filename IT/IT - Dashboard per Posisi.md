## Deskripsi

*Rancangan isi dashboard per posisi untuk divisi **Tech Development**. Diturunkan mengikuti [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]]: KPI yang dinilai, pekerjaan yang menunggu, dan ambang yang tak boleh dilewati. Divisi ini dikerjakan lebih dulu karena satu-satunya yang punya metrik benar-benar otomatis dalam jumlah berarti, jadi rancangannya bisa diuji kebenarannya alih-alih diperdebatkan.*

- **Status**: 🟡 **Rancangan**, belum dibangun. Yang ADA hari ini adalah Ringkasan Divisi IT tanpa tab per posisi (`erp-frontend/src/features/it/ringkasan/`).
- **Angka KPI diukur 2026-08-28** (sumber: [[HRIS - Matriks KPI per Departemen]]). ⚠️ Konfigurasi template divisi ini berubah beberapa kali dalam Agustus 2026. **Ukur ulang sebelum dipakai mengambil keputusan.**
- **Path di repo**: `erp-frontend/src/features/it/ringkasan/`

## Keadaan sekarang

`/it` merender **Ringkasan Divisi**, bukan lembar per posisi: `KartuInfrastruktur`, `KartuHelpdesk`, `KartuKpiTimIt`, `KartuIndeksLayanan`, lalu petak tautan modul.

Ketiadaan tab posisi **bukan kelalaian**, dan alasannya sudah tertulis di kodenya sendiri (`isi-ringkasan-divisi-it.tsx`): peta posisi IT belum ada di kode dan `position_key` belum mengalir ke frontend, sehingga menyusun daftar posisi di sana berarti mengarangnya. Prasyarat [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] itu belum gugur, dan **dokumen ini tidak menggugurkannya**. Rancangan di bawah baru bisa dibangun setelah `position_key` tersedia di frontend.

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

1. **`position_key` mengalir ke frontend.** Prasyarat mutlak: tanpa ini tak ada dashboard per posisi yang bisa dibangun di divisi mana pun, bukan cuma IT. Menyentuh [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]].
2. **Putuskan bentuk metrik `Network` IT Support.** Bukan pekerjaan kode melainkan keputusan: uptime terhadap 90 tidak membedakan bulan baik dari bulan buruk. Sampai diputuskan, kartunya tak layak dominan.
3. **Satukan atau pisahkan CSAT Leader.** Label menjanjikan Fullstack dan Support; yang terpasang development saja. Butuh sub-metrik baru di kode.
4. **Rute pemakai modul kewajiban Calendar Service.** Mesinnya sudah jalan; yang kurang cara orang menjadwalkan dan menandai selesai, plus dua keputusan yang disebut di bagian Fullstack.
5. **Master anggaran departemen IT + parameter departemen di `/accounting/anggaran/varians`.** Keduanya diperlukan bersama; salah satu saja tidak cukup.

⚠️ **Yang TIDAK masuk daftar ini**: menaikkan cakupan CSAT. Ia bukan pekerjaan backend melainkan kebiasaan meminta pemohon menilai tiketnya. Menaruhnya di daftar teknis akan membuatnya menunggu rilis yang tak pernah relevan.

## Dokumen Terkait

- [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] — prinsip penurunannya
- [[REF - Layout Dashboard erp-frontend]] — cara menyusunnya di layar
- [[HRIS - Matriks KPI per Departemen]] — sumber angka di dokumen ini
- [[HRIS - Otomasi Skor KPI]] — kenapa `skor_tim` menuntut urutan penilaian
- [[Microservices - Calendar Service]] — modul kewajiban untuk metrik `Implementasi`
- [[IT - Helpdesk]] — sumber tiket, SLA, dan CSAT
- [[IT - Monitoring System]] — sumber uptime
- [[RUN - Menambah Metrik KPI Otomatis]] — cara mengerjakan otomasinya
