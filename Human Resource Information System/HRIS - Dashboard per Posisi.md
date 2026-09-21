## Deskripsi

*Rancangan isi dashboard per posisi untuk divisi **Human Resource**, lima posisi. Diturunkan mengikuti [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]]. Berbeda dari divisi lain, kelima posisi ini **sudah punya lembarnya** di `/hris`, jadi dokumen ini membandingkan yang tampil hari ini dengan yang seharusnya, bukan merancang dari nol.*

- **Status**: ⚠️ **Sebagian sudah ada**. Kelima tab hidup di `/hris` (Ringkasan Divisi HRGA); **dua** di antaranya nyaris kosong dan sebabnya bukan tata letak melainkan ketiadaan data. Recruitment & Onboarding keluar dari golongan itu 2026-09-22.
- **Angka KPI diukur 2026-08-28**, bab Recruitment disegarkan **2026-09-22**, bab Training & Performance Officer disegarkan **2026-09-15** (sumber: [[HRIS - Matriks KPI per Departemen]]). **Ukur ulang sebelum dipakai mengambil keputusan.**
- **Path di repo**: `erp-frontend/src/features/hris/dashboard/kartu/isi/`

> Divisi **General Affair** berbagi rute yang sama (`/hris`) karena keduanya satu grup supervisi HRGA, tetapi posisinya dirancang di [[GA - Dashboard per Posisi]]. Lihat § HRGA bukan nama departemen di bawah.

## Ringkasan keadaan

| Posisi | Tab | Metrik KPI | Bersumber | Yang tampil hari ini |
|---|---|---:|---:|---|
| HRD Supervisor | `hrd-supervisor` | 10 | 4 | 7 kartu, tab terkaya di divisi |
| Personalia | `personalia` | 5 | 3 | 2 antrean + 2 kartu pelengkap |
| Culture & Industrial | `org-dev` | 6 | 1 | 1 sebaran + 1 panel belum-bersumber |
| Recruitment & Onboarding | `recruitment` | 5 | **4** | 2 antrean + 2 kartu tenggat + bagan tren + panel jujur |
| Training & Performance Officer | `people-dev` | 6 | 0 | 1 antrean + 3 kartu angka umum + 1 sebaran |

Tab yang tampak kosong **bukan karena belum dirapikan**, melainkan karena metrik yang menilai orangnya tidak punya angka di sistem. Merapikan tata letaknya tidak akan mengubah apa pun.

⚠️ **Recruitment & Onboarding sudah keluar dari golongan itu** sejak sumber KPI `rekrutmen` mendarat 2026-09-21: empat dari lima metriknya kini bersumber, dan tabnya terisi. Yang tersisa kosong adalah Culture & Industrial dan Training & Performance Officer. Ini contoh langsung dari sifat yang diperingatkan [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]]: dok ini bersandar pada salinan bertanggal, jadi baris mana pun di tabel atas bisa basi tanpa ada yang berbunyi.

**Di bawah isi setiap tab posisi selalu ada matriks KPI posisinya.** `IsiTab` merender `MatriksKpi` untuk tiap tab berposisi (`kartu/isi-tab.tsx:45`), berisi label, bobot, dan status otomasi dari `GET /kpi/auto-overview` (`hooks/use-matriks-kpi-hrga.ts:100-101`) plus kolom **Kelayakan** yang disalin di frontend (`lib/kpi-hrga/kelayakan.ts`). Kolom "Yang tampil hari ini" di atas menghitung isi khusus tab di atas matriks itu, bukan matriksnya. ⚠️ Kolom Kelayakan dikunci **nama template + label** (`kunciMetrik`, `kelayakan.ts:140`), jadi template yang berganti nama tak punya entri dan barisnya tampil "belum dinilai" sampai daftar itu diperbarui.

## HRD Supervisor

**Dinilai dari** (template `KPI Supervisor HRGA`, 10 metrik):

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,2 | Seluruh karyawan berskor KPI min. 70 | `skor_tim`, reduksi **`rasio_ambang`** (ambang 70, target 100) | ✅ ada sumber |
| 0,2 | Rata-rata KPI tim HRGA min. 70 | `skor_tim`, `rata_rata`, scope `department` | ✅ mesin siap, tinggal konfigurasi |
| 0,15 | Time to recruitment < 30 hari posisi kritikal | `pemenuhan_tepat_waktu_kritikal` di `kpi_sumber_rekrutmen.go` | ✅ (sejak 2026-09-21) |
| 0,1 | Turnover 5% per tahun | `turnover_karyawan` / `turnover_persen` | ✅ ada sumber |
| 0,1 | Implementasi training | koleksi `training` kosong di prod | ❌ |
| 0,05 | Efisiensi biaya operasional GA | `GET /accounting/anggaran/varians` | ⚠️ perlu master anggaran GA |
| 0,05 | Monitoring aset 100% terdata | ⚠️ sumber tertulis data RETUR, deskripsinya ASET | ❌ salah petak |
| 0,05 | Employee productivity | koleksi `training` kosong | ❌ |
| 0,05 | Succession planning | tidak ada modul succession/talent pool | ❌ |
| 0,05 | Employee satisfaction | `GET /task-management/report/csat` | ⚠️ 17 tiket ter-rating seumur hidup |

**Bisa ditampilkan sekarang.** Tab ini sudah merender tujuh kartu (tenggat kontrak, tiga kartu angka, kartu ambang, efisiensi GA, skor KPI cakupan semua).

- **Visual utama**: sebaran skor KPI seluruh anggota HRGA terhadap ambang 70, **bukan rata-ratanya**. Metrik berbobot 0,2 itu memakai reduksi `rasio_ambang`, dan kata kuncinya "SELURUH": rata-rata 78 lolos target walau sepuluh orang di bawah 70. Dashboard yang menggambar rata-rata akan mengabarkan lulus untuk keadaan yang menurut metriknya gagal.
- Kartu turnover terhadap target, tenggat kontrak, antrean pengajuan yang menunggu persetujuannya.

**Yang menunggu backend.** Lima dari sepuluh metriknya tak punya angka. Yang paling merusak bila dipaksakan: metrik aset, karena sumber yang tertulis di template adalah data **retur**, bukan aset. Menyambungkannya apa adanya menghasilkan angka yang tampak wajar dan menjawab pertanyaan lain.

## Personalia

**Dinilai dari** (template `Personalia Team`, 5 metrik):

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,25 | Administrasi payroll & absensi akurat | `kedisiplinan_absensi` / `kelengkapan_catatan` | ✅ |
| 0,25 | Pengkinian data karyawan | belum dipetakan | ❌ |
| 0,2 | Administrasi BPJS, rekening, surat | `GET /employee/bpjs` tersedia | ⚠️ payroll baru 1 run |
| 0,2 | Administrasi kontrak baru & perpanjangan | `kontrak_karyawan` (koleksi `employee_contract`) | ✅ |
| 0,1 | Kedisiplinan sendiri | `kedisiplinan_absensi` / `ketepatan_waktu` | ✅ |

**Bisa ditampilkan sekarang.** Ini posisi paling siap di divisinya, dan tabnya sudah mendekati bentuk yang benar: dua antrean (pengajuan menunggu, absensi belum lengkap) plus tenggat kontrak dan cuti hari ini.

- **Visual utama**: kelengkapan catatan absensi bulan berjalan terhadap target. Ia berbobot 0,25 dan satu-satunya metriknya yang bergerak harian.
- Antrean tetap di tempatnya sekarang, tidak dipindah. Ia yang menjawab "apa yang harus saya kerjakan hari ini".

⚠️ **Kartu cuti hari ini jangan dijadikan antrean.** Ia menerangkan antrean absensi di sebelahnya ("12 belum absen" terbaca berbeda kalau delapan sedang cuti), bukan menyuruh mengerjakan apa pun. Menaruhnya sebagai antrean akan menyuruh orang mengerjakan cuti yang sudah disetujui. Alasan ini sudah tertulis di kodenya dan **jangan dibalik tanpa membacanya**.

**Yang menunggu backend.** Pengkinian data karyawan (0,25) belum dipetakan sama sekali. Ini metrik berbobot terbesar bersama administrasi payroll, jadi ia yang paling layak diperiksa lebih dulu.

## Culture & Industrial

**Dinilai dari** (template `Organizational Development`, 6 metrik):

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,2 | Penyusunan program culture | belum dipetakan | ❌ |
| 0,2 | Skor program culture | 🟡 sumber `program_culture` di branch `feature/workspace-position` | belum merge/prod |
| 0,2 | Keaktifan peserta training ≥ 100% | koleksi `training` kosong di prod | ❌ |
| 0,2 | Skor penilaian training > 70 | koleksi `training` kosong di prod | ❌ |
| 0,1 | Kedisiplinan karyawan | `kedisiplinan_absensi` / `ketepatan_waktu` | ✅ |
| 0,1 | Kaizen, 7 inovasi per bulan | ⛔ manual karena keputusan | [[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]] |

**Bisa ditampilkan sekarang.** Praktis hanya kedisiplinan. Tab yang ada memang cuma sebaran departemen plus satu panel belum-bersumber, dan itu **jujur**, bukan kekurangan tata letak.

**Yang menunggu backend, terurut.** Merge sumber `program_culture` (0,2, sudah ada di branch, jarak terpendek), lalu isi modul Training yang mengunci dua metrik lain berbobot total 0,4.

**Yang TIDAK ditampilkan.** Kaizen. Manual karena keputusan, jadi panel "menunggu penyambungan" akan berbohong tentang sebabnya.

## Recruitment & Onboarding

**Dinilai dari** (template `Recruitment`, 5 metrik, disegarkan **2026-09-22**):

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,25 | Time to fulfilment < 30 hari | `pemenuhan_tepat_waktu` (+ varian kritikal) di `kpi_sumber_rekrutmen.go` | ✅ |
| 0,25 | Ketersediaan dokumen jobdesk seluruh posisi | tidak ada tempat menyimpan jobdesk per posisi | ❌ |
| 0,2 | Jadwal & pelaksanaan onboarding masa percobaan | `review_evaluasi_tepat_waktu` | ✅ mesin siap, data prod masih tipis |
| 0,2 | Database buffer kebutuhan MPP | `buffer_mpp_persen` (+ varian kritikal), lewat `GET /manpower-plans/coverage` | ✅ |
| 0,1 | Turnover masa probation 0% | `retensi_masa_probation` | ✅ |

⚠️ **Catatan sebelumnya di bagian ini SUDAH USANG dan dicabut.** Ia berbunyi "0 dari 5 bersumber" dan "jangan menambah kartu di tab ini sampai minimal satu metrik punya angka", diukur 2026-09-02. Premisnya kedaluwarsa pada 2026-09-21 ketika sumber KPI `rekrutmen` mendarat: empat dari lima metrik kini punya angka, dan yang tersisa tanpa sumber cuma jobdesk.

**Yang tampil sekarang.** Baris "yang menunggu Anda" berisi empat kartu — kandidat dalam proses, interview pekan ini, **requisisi menuju tenggat**, dan offer menunggu jawaban — lalu ringkasan cakupan buffer MPP, bagan **slot requisisi dibuka vs terpenuhi**, funnel rekrutmen, dan panel jujur untuk metrik jobdesk.

- **Visual utama**: kartu tenggat requisisi, bukan bagan. Metrik terberat posisi ini adalah pemenuhan kurang dari 30 hari, jadi keputusan hariannya "requisisi mana yang akan lewat tenggat". `KartuTenggat` menaruh yang SUDAH lewat di paling atas dengan warna paling keras, dan requisisi yang menggantung berbulan-bulan memang yang paling mendesak justru karena ia tak lagi muncul di daftar "akan datang" mana pun.
- ⛔ **Kartu tenggat menarik 12 bulan, bagan menggambar 6.** Jendela yang sama untuk keduanya membuang requisisi tertua lebih dulu, dan ketiadaannya terbaca sebagai "tak ada yang terlambat".
- ⛔ **Dua hitungan pengecualian WAJIB ikut tampil** (`requisisi_tanpa_jejak_persetujuan`, `diterima_tanpa_posting`). Keduanya berarti ada requisisi atau hire yang tak terwakili, dan arah salahnya **selalu** membuat tim rekrutmen tampak lebih baik daripada kenyataan — untuk angka yang dipakai menilai orang.
- **Tenggat 30 hari dibaca dari respons**, bukan konstanta frontend. Satu-satunya tempat angka itu hidup `common.TenggatPemenuhanHari` di `shared-library`.

**Yang menunggu backend.** Tinggal jobdesk (bobot 0,25): tak ada tempat menyimpannya di sistem mana pun, jadi ia dirender sebagai panel `BelumBersumber`, bukan angka nol ([[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] §3).

**Yang TIDAK ditampilkan, dan alasannya.**

- **Aktual vs Rencana MPP per departemen.** Faktanya dimiliki [[ADR - 0113 Actual vs Planning MPP Dihitung Sistem per Bulan, Berpijak pada Jejak Keluar Bertanggal]], layarnya Manpower Planning, dan gerbangnya HRD + Direktur (§8) — lebih sempit daripada tab ini.
- **Tren headcount bulanan.** Dilarang [[ADR - 0113 Actual vs Planning MPP Dihitung Sistem per Bulan, Berpijak pada Jejak Keluar Bertanggal]] §3 selama masih ada akun non-aktif tanpa tanggal keluar. Bagan di tab ini menggambar **requisisi**, bukan headcount, sehingga tak kena larangan itu.
- **Kartu ambang per metrik KPI.** Satu-satunya sumber angka per metrik yang ber-RBAC pemakai adalah `/me/kpi-score`, dan itu skor **pembaca** — supervisor yang membuka tab ini akan melihat angkanya sendiri berlabel Recruitment. Menghitung ulang persentasenya di frontend juga ditolak: itu menyalin rumus KPI ke tempat kedua. Menghidupkannya menuntut agregat per-posisi yang belum ada.

## Training & Performance Officer

**Dinilai dari** (template `People and Development`, 6 metrik, disegarkan 2026-09-15; template 5-metrik `People Development` diarsipkan 25 Agu 2026):

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,35 | Skor penilaian training seluruh karyawan > 70 | post-test berskor ada di service `learning` tapi tanpa layar; `quiz_attempt` 0 | ❌ |
| 0,2 | Terlaksananya kegiatan training sesuai rencana | `training` 2; tak ada entitas "rencana" untuk pembanding | ❌ |
| 0,15 | Kesesuaian materi LMS dengan jobdesk | materi LMS dan jobdesk per posisi belum ada di sistem | ❌ |
| 0,1 | Training attendance rate | `training_participant` 1, belum hadir | ❌ |
| 0,1 | Employee productivity 120 juta per karyawan | pendapatan (`GET /accounting/profit-loss`) dan `work_data` ada, definisinya belum | ⚠️ perlu definisi + sumber baru |
| 0,1 | Training satisfaction score (1-10) | `trainer_evaluation` 0; skala di sistem 1-5 | ❌ |

**Bisa ditampilkan sekarang.** Tak satu pun metrik KPI posisi ini berangka. Tab yang ada (`isi-people-dev.tsx`) merender antrean pengajuan pelatihan yang menunggu tindakan (`as=reviewer`, status Menunggu SPV/HR) beserta tautan ke halamannya, tiga kartu angka umum (total karyawan, departemen, posisi), sebaran departemen, agenda, dan pengumuman. Antrean itu sumbu "pekerjaan yang menunggu" yang benar; kartu angka dan sebarannya tidak menjawab satu pun metrik posisi ini. Di bawahnya matriks KPI posisi ini tampil (lihat Ringkasan keadaan), tetapi **kolom Kelayakan masih milik template lama**: entrinya hanya ada untuk template `People Development` (`kelayakan.ts:246-250`), sehingga keenam metrik template aktif `People and Development` tampil "belum dinilai".

⛔ **Empat metrik (bobot 0,75) terkunci pada modul Training yang belum dipakai, dan mengisinya saja tidak cukup.** Per 2026-09-15 `learning_db` prod berisi 2 pelatihan, 1 peserta yang belum hadir, 0 evaluasi trainer, dan 0 post-test. Sesudah datanya terisi pun belum ada sumber KPI yang membaca `learning_db`, jadi dev tetap harus menulisnya, dan post-test belum punya layar di web maupun aplikasi. Nilai yang diketik untuk Agustus 2026 (attendance 92, skor training 83, kepuasan 77) karena itu tidak berasal dari sistem; perbandingannya di [[HRIS - Matriks KPI per Departemen]].

**Rekomendasi rancangan.** Tunda perancangan layarnya sampai modul Training terisi **dan** sumber KPI-nya ada. Merancang sekarang berarti merancang untuk data yang bentuk akhirnya belum diketahui.

## HRGA bukan nama departemen

⛔ Tak seorang pun ber-`work_data.department` = `HRGA`. Isinya selalu **`Human Resource`** atau **`General Affair`**; `HRGA` adalah `supervision_label` yang lahir dari `supervised_by`, dan pengelompokannya bisa **batal** kapan saja lewat master data.

Konsekuensinya untuk dashboard: layar yang menyaring anggota per orang wajib membandingkan dengan **label blok yang dikembalikan backend**, bukan mencocokkan `work_data.department` persis. Kekeliruan ini sudah menggigit dua kali di frontend, dan kedua kali gejalanya senyap. Layar yang **menulis** nama departemen sebaliknya tak boleh memakai daftar bergrup, karena `kpi_template.department` menyimpan nama asli.

## Kebutuhan backend, terurut

1. **Isi modul Training di produksi, lalu tulis sumber KPI yang membacanya.** Dua langkah, dua pemilik: pelatihan, peserta, kehadiran, evaluasi, dan post-test diisi HR (modulnya sudah ter-deploy), sedangkan sumber KPI atas `learning_db` pekerjaan dev (belum ada satu pun), dan post-test masih menunggu layarnya. Keduanya membuka bobot 0,75 di Training & Performance Officer (0,55 langsung, 0,2 menunggu definisi "rencana") plus 0,4 di Culture & Industrial dan 0,15 di HRD Supervisor. Tak ada pekerjaan lain di divisi ini yang sebanding daya ungkitnya.
2. **Merge sumber `program_culture`** dari branch `feature/workspace-position`. Sudah ada, tinggal mendarat.
3. **Perbaiki metrik turnover probation.** Bukan penyambungan melainkan **koreksi pertanyaan**: sumber yang terdaftar mengukur resign sukarela seluruh perusahaan.
4. **Perbaiki metrik aset HRD Supervisor.** Sumbernya data retur, deskripsinya monitoring aset. Salah petak yang menghasilkan angka masuk akal.
5. **Tempat menyimpan jobdesk per posisi.** Belum ada di sistem mana pun, mengunci metrik berbobot 0,25 di Recruitment & Onboarding dan 0,15 di Training & Performance Officer (yang juga menunggu materi LMS).
6. ~~**Koleksi `candidate`** supaya time to fulfilment punya ujung pengukuran.~~ ✅ **Selesai 2026-09-21**: `kpi_sumber_rekrutmen.go` menurunkan pemenuhan dari jejak audit persetujuan requisition dan waktu kandidat `Hired`, tanpa menunggu koleksi baru.
7. **Master anggaran departemen GA** untuk metrik efisiensi biaya.

## Dokumen Terkait

- [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] — prinsip penurunannya
- [[REF - Layout Dashboard erp-frontend]] — cara menyusunnya di layar
- [[HRIS - Matriks KPI per Departemen]] — sumber angka di dokumen ini
- [[GA - Dashboard per Posisi]] — divisi saudara yang berbagi rute `/hris`
- [[HRIS - Training Program]] — modul yang mengunci daya ungkit terbesar divisi ini
- [[Microservices - Learning Service]]: backend modul Training (pelatihan, peserta, evaluasi, post-test)
- [[HRIS - Recruitment]] — modul untuk posisi Recruitment & Onboarding
- [[HRIS - Personalia]] — modul untuk posisi Personalia
- [[HRIS - Pengembangan Organisasi (Community of Interest)]] — modul untuk Culture & Industrial
- [[HRIS - Key Performance Index]] — mekanisme scoring dan cakupan tim
