> **Status**: ⚠️ **Berlaku sebagian** (2026-09-17). Irisan 1 merged ke `main` erp-frontend lewat PR [#1642](https://github.com/bip-itteam-internal/erp-frontend/pull/1642) (merge commit `68ff4f937`), diverifikasi di layar terhadap backend DEV sebelum merge; deploy dev/prod belum diverifikasi. Irisan 2 dan 3 belum. Membalik konsekuensi "kehilangan kartu Kehadiran dan Pengumuman" yang diterima 2026-08-26 dan 2026-09-15.

## Untuk Manajemen

**Apa yang berubah di layar.** Halaman pertama yang dibuka setiap orang di web ERP (`/dashboard`) disusun ulang jadi empat bagian, dibaca dari atas:

1. **Kepala saya**: sapaan dan status kehadiran hari ini dalam satu baris. Bila belum ada catatan kehadiran bertanggal hari ini, tertulis "Belum ada catatan kehadiran hari ini".
2. **Perlu tindakan saya**: jumlah persetujuan dan permintaan yang menunggu orang itu, masing-masing bertautan ke layarnya. Baris yang jumlahnya nol tidak tampil.
3. **Hari ini**: agenda kalender hari ini, berapa metrik KPI bulan ini yang masih menunggu laporan atau penilaian (plus skor bulan lalu bila sudah dinilai), dan pengumuman.
4. **Ruang kerja posisi**: dashboard departemen yang sudah ada hari ini (HRGA, Finance, IT, Ruang Direktur, Marketing), hanya bagi posisi yang punya.

**Siapa yang terdampak.** Semua karyawan. Bagian 1 sampai 3 tampil untuk semua orang. Staf HR, Finance, serta SPV dan Leader brand, yang sejak Agustus kehilangan kartu kehadiran dan pengumuman karena halamannya diganti dashboard departemen, mendapatkannya kembali.

**Yang tidak dijanjikan.**
- Tidak ada dashboard baru untuk posisi yang belum punya (Manufaktur, Quality, Kesekretariatan, Procurement, staf Sales). Bagian 4 untuk mereka tidak muncul.
- Isi beranda tidak bisa diatur sendiri oleh pemakai.
- Status pengajuan cuti milik sendiri, sisa kuota cuti, dan form yang wajib diisi belum masuk. Ketiganya tetap di MyBharata.
- **Tahap pertama belum menghitung cuti, izin, dan dinas yang menunggu persetujuan ATASAN.** Angka itu butuh satu sumber baru di backend dan menjadi tahap kedua.
- **Angka antrean Pengajuan Barang & Dana belum bisa ditampilkan.** Sumbernya di backend belum tersambung, dan layar menuliskannya terus terang ("Angka untuk Pengajuan Barang & Dana tak termuat") bagi yang melihat kartu itu, sampai perbaikannya dikerjakan sebagai task terpisah.
- **Skor KPI bulan berjalan tidak ditampilkan**, karena memang belum ada sebelum penilaian; yang tampil adalah metrik yang masih menunggu.

**Perkiraan besaran kerja** (kasar, belum melewati `/plan`). Tahap pertama hanya frontend, sekitar dua sampai tiga hari. Tahap kedua satu sumber baru di employee-service plus barisnya di frontend, sekitar satu sampai dua hari termasuk deploy.

## Deskripsi

*Beranda portal (`/dashboard`) berhenti memilih ANTARA bagian personal dan dashboard posisi, lalu menumpuk keduanya: tiga zona personal untuk semua orang di atas, ruang kerja posisi di bawah. Antrean "perlu tindakan" dibaca dari endpoint agregat yang sudah ada, `GET /api/employee/pengajuan/ringkasan`, bukan dirangkai di frontend dan bukan endpoint baru.*

- **Status**: ⚠️ **Berlaku sebagian**. Arah disetujui user 2026-09-17. Irisan 1 merged ke `main` erp-frontend 2026-09-17 (PR #1642), deploy belum diverifikasi; irisan 2 dan 3 belum. Lihat § Pelaksanaan Irisan 1.
- **Path di repo** (irisan 1, di branch): `erp-frontend/src/app/(main)/(erp)/dashboard/page.tsx` · `erp-frontend/src/features/erp/portal/components/` (`beranda-portal.tsx`, `kehadiran-hari-ini.tsx`, `perlu-tindakan.tsx`, `agenda-hari-ini.tsx`, `kpi-saya-ringkas.tsx`) · `erp-frontend/src/features/erp/portal/lib/` (`kehadiran-hari-ini.ts`, `baris-tindakan.ts`, `ringkasan-kpi.ts`, aturan murni beserta test) · `erp-frontend/src/features/pengajuan/use-ringkasan-pengajuan.ts` (dipakai ulang). Irisan 2 (rencana): `bip-erp/services/employee/ringkasan_pengajuan.go` (`registriRingkasan`)
- **Tanggal**: 2026-09-17

## Context

### Keadaan hari ini

Diukur ke `origin/main` erp-frontend `f1cb1fb0c` dan my-bharata `origin/dev` `341c0e0c`, 2026-09-17.

`/dashboard` adalah **pemilih** (`features/erp/portal/lib/pilih-dashboard.ts`). Pembaca mendapat SATU dari dua isi:

| Pembaca | Isi |
|---|---|
| Jabatan Direktur, posisi HRGA, posisi FAT, supervisor IT, pemimpin tim brand | dashboard departemen dari `ISI_DASHBOARD` |
| Selain itu | `BerandaPortal`: `WelcomeCard`, `AttendanceDetail`, `WorkShift`, `AnnouncementCard` |

Tiga masalah muncul dari susunan itu.

1. **Beranda tidak memuat satu pun aksi.** Keempat kartunya tanpa tombol. Isinya sapaan, kehadiran hari ini, kalender jadwal bulanan, dan pengumuman. Kehadiran dan jadwal sudah dilihat orang di MyBharata, tempat mereka absen. Pertanyaan "apa yang menunggu saya hari ini" tidak dijawab di mana pun di halaman itu.
2. **Personal dan posisi saling menggantikan.** Pembaca yang mendarat di dashboard departemen kehilangan kartu Kehadiran dan Pengumuman, dan hanya Direktur serta supervisor IT yang bisa kembali lewat dropdown. Ini diterima sadar pemilik produk 2026-08-26 dan user 2026-09-15 (lihat [[APP - Web ERP]], bagian ERP publik). ADR ini membalik keputusan itu.
3. **Data antreannya sudah ada, tetapi tidak sampai ke beranda.**
   - `GET /api/employee/pengajuan/ringkasan` ([[API - Employee Service]], bagian Ringkasan Pengajuan) sudah merangkai lima antrean dari lima service dalam satu panggilan, dan gerbang tiap angka mengikuti service sumbernya. Konsumennya hanya halaman `/portal/pengajuan`.
   - `useJumlahPersetujuan`, `useJumlahPersetujuanPesanan`, `useJumlahPersetujuanBudget` (procurement) dan `useFetchPendingReviewCount` (tukar shift) terdefinisi tanpa satu pun pemakai.
   - MyBharata sudah menjawab pertanyaan yang sama di berandanya. `PendingApprovalCard` membaca `total` dari `GET /hr/requests?as=reviewer` dengan `limit=1` ([[API - Attendance Service]], bagian HR requests terpadu) dan menyembunyikan diri saat nol. `SurveySection` dan `PendingCsatBanner` memakai pola sembunyi-saat-kosong yang sama.

## Decision

### 1. Beranda menumpuk, tidak memilih

```
A. Kepala saya                          semua orang
B. Perlu tindakan saya  |  C. Hari ini  semua orang (B dominan)
D. Ruang kerja posisi                   hanya posisi yang punya dashboard
```

Urutan baca [[REF - Layout Dashboard erp-frontend]] (aturan 6) diterjemahkan jadi urutan tindakan: yang menunggu pembaca lebih dulu, analisis posisi belakangan. Akun pihak luar tetap `VendorDashboard` sebagai cabang pertama, tidak berubah.

### 2. Zona A, B, dan C tidak boleh menuntut peran apa pun

`/dashboard` adalah tujuan pantulan setiap rute yang ditolak `src/proxy.ts`. Zona personal hanya memanggil endpoint yang cakupannya ditentukan identitas pemanggil (header gateway), sehingga halaman itu tetap berisi bagi siapa pun yang baru saja ditolak dari rute lain.

### 3. Zona A: satu baris, bukan dua kartu

Sapaan dari `WelcomeCard` dan status kehadiran hari ini dari `useAttendanceToday` (`GET /api/attendance/today`): status, jam masuk, jam pulang, dan jam kerja, sebagai chip di dalam kartu sapaan. `AttendanceDetail` dan `WorkShift` (kalender jadwal bulanan) tidak lagi dirender di beranda, dan karena beranda satu-satunya pemakainya, keduanya dihapus.

⛔ **Diubah saat implementasi (2026-09-17): kehadiran hanya ditampilkan bila catatannya bertanggal HARI INI menurut kalender WIB.** `GET /api/attendance/today` tanpa `?view` tidak menjawab "hari ini": ia mengembalikan catatan kehadiran TERBARU milik pemanggil (`FindOne` urut `date` menurun di `services/attendance/main.go`), dan 404 bila belum pernah ada satu pun (lihat [[API - Attendance Service]]). Kartu lama karena itu berjudul "Kehadiran Terakhir". Menampilkannya apa adanya di bawah janji "hari ini" membuat jam masuk kemarin terbaca sebagai kehadiran hari ini. Catatan yang bukan hari ini dan 404 sama-sama tertulis "Belum ada catatan kehadiran hari ini"; galat lain tertulis "tak bisa dimuat". Aturannya di `lib/kehadiran-hari-ini.ts`, dan arti 404 tinggal di satu tempat (`belumPernahAdaCatatan` di hook-nya), yang juga membuat 404 tak diulang tiga kali oleh React Query.

### 4. Zona B: antrean dibaca dari `pengajuan/ringkasan`, tidak dirangkai ulang

- **Sumber**: `useRingkasanPengajuan` dan `angkaKartu` di `features/pengajuan/use-ringkasan-pengajuan.ts`.
  ⚠️ Ada hook lain bernama **sama persis** di `features/hris/requests/hooks/use-requests-summary.ts`, yang membaca `/hr/requests/summary` untuk admin HR. Salah impor tidak menghasilkan galat apa pun, hanya angka dengan arti lain. Yang dipakai beranda adalah yang di `features/pengajuan/`.
- **Daftar barisnya** = kartu `/portal/pengajuan` yang tampil bagi pembaca (`KARTU_PENGAJUAN` di `components/layout/pengajuan-menu.ts`, yang tampil bila dan hanya bila menunya lolos `blokMenu`) dan punya `kunciAngka`. Beranda tidak memelihara daftar sendiri, jadi kartu berangka baru di halaman Pengajuan otomatis jadi baris beranda, dan kedua layar tidak bisa menampilkan angka berbeda untuk antrean yang sama.
- **Baris muncul hanya bila angkanya lebih dari nol.** Kunci di `degraded` tidak digambar sebagai nol, dan kunci yang absen (pemanggil tak berhak) tidak punya baris. Arti ketiga keadaan itu sudah ditetapkan di [[API - Employee Service]].
- **Kartu zona B tetap tampil** meski semua barisnya hilang, berisi satu kalimat bahwa tak ada yang menunggu. Di sini kosong adalah kabar baik; menyembunyikan seluruh zona membuat tata letak melompat dan terbaca seperti gagal memuat. Dalam keadaan kosong kartunya dirender **ringkas** (setinggi kalimatnya), bukan setinggi area dominan: staf yang tidak memegang antrean apa pun akan melihat keadaan ini hampir setiap hari, dan kotak besar yang selalu kosong mengajari mereka bahwa bagian itu tidak berguna.
- **Keadaan memuat dijaga ketat.** `useRingkasanPengajuan` memasang `placeholderData` kosong, jadi selama permintaan berjalan datanya `{}`. Kartu baru boleh berkata "tidak ada yang menunggu" setelah daftar kartu (`siap`) DAN angkanya benar-benar tiba; sebelum itu yang tampil kerangka. Galat permintaan tertulis "Antrean tak bisa dimuat sekarang. Ini bukan berarti tidak ada yang menunggu" dengan tautan ke `/portal/pengajuan`.
- **Diubah saat implementasi (2026-09-17): kunci `degraded` DISEBUT, tidak disembunyikan diam-diam** seperti di halaman Pengajuan. Di sana kartunya tetap tergambar sebagai tautan, sedangkan di beranda antrean tanpa angka tak punya baris sama sekali, sehingga diam berarti ikut berkata "tidak ada yang menunggu". Catatan kakinya menyebut judul kartu yang angkanya tak termuat, hanya untuk kartu yang TERLIHAT pembaca; bila semua baris hilang karena itu, kalimat "tidak ada yang menunggu" tidak ditampilkan.
- **Tiap baris berisi angka dan tautan ke layar sumbernya.** Beranda tidak menyalin detail antrean. Baris Booking Ruang mendarat di tab "Booking Saya" (URL kartunya); halaman itu sendiri menautkan penyetuju ke tab "Perlu Keputusan" bila antreannya berisi.
- **Ditolak**: merangkai hook per modul di frontend (tiap pembukaan beranda menembak enam endpoint atau lebih, dan gerbang tiap sumber harus disalin ke frontend), serta endpoint agregat baru (agregator kedua untuk fakta yang sama).

### 5. Zona C: hari ini

- **Agenda hari ini** dari `useCalendarRange` (`GET /api/calendar`, rentang hari ini sampai 23.59.59 seperti `weekRange` kalender) digambar `AgendaList` milik kalender apa adanya. Visibilitasnya sudah disaring di service sumber tiap feed ([[Microservices - Calendar Service]]), jadi beranda tidak menyaring ulang. Yang tidak dipakai dari kalender hanya kalimat kosongnya ("pada rentang ini"); beranda menulis "Tidak ada agenda hari ini".
- ⛔ **Diubah saat implementasi (2026-09-17): KPI menampilkan metrik yang menunggu, bukan skor bulan berjalan.** Pratinjau bulan berjalan SENGAJA tak membawa skor: metrik otomatis baru menutupi sebagian bobot template, dan total dari sebagian itu menyesatkan ke arah mana pun, jadi backend tak mengirimnya dan `normalisasiKpiSaya` mengembalikan `skor: null` (komentar `skor` di `erp-frontend/src/features/hris/kpi/lib/kpi-saya.ts`). "Skor KPI bulan berjalan" karena itu tak pernah bisa diisi. Yang tampil:
  - **jumlah metrik bulan ini yang menunggu laporan atau penilaian** dari `useKpiSaya()` (`GET /api/employee/me/kpi-score?preview=true`, field `menunggu_penilaian`);
  - **skor TERSIMPAN bulan lalu, hanya bila sudah dinilai**, dari `useKpiSayaTren()` (`?graph=true`). BUKAN `useKpiSaya({period})`, yang selalu mengirim `preview=true` sehingga tiap pembukaan beranda memicu perhitungan pratinjau untuk bulan yang sudah lewat;
  - tautan ke `/portal/kpi`. Blok tak dirender sama sekali bila pembaca tak punya template bulan ini dan tak punya skor bulan lalu. Skor tidak diberi warna ambang; ambangnya milik pemanggil lain (70 dan 80).
- **Pengumuman** lewat `AnnouncementCard` yang sudah ada.

### 6. Zona D: pemilih yang sudah ada, dipindah ke bawah

- `pilihDashboard`, `ISI_DASHBOARD`, dan `DASHBOARD_DEPARTEMEN` beserta gerbang dan test-nya dipakai apa adanya. Yang berubah hanya letaknya.
- Pilihan `beranda` di dropdown Direktur dan supervisor IT kini berarti "tanpa ruang kerja posisi", karena zona personal selalu tampil. Nilai tersimpan `beranda` di `localStorage` tetap sah dan tak perlu migrasi, tetapi label i18n `portal.dashboard.beranda` perlu disesuaikan dengan artinya yang baru.
- Posisi tanpa dashboard tidak mendapat zona D sama sekali, tanpa panel kosong ([[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] §4).
- Hanya isi terpilih yang dirender, sama dengan hari ini.

### 7. Tata letak

Mengikuti [[REF - Layout Dashboard erp-frontend]]: `grid lg:grid-cols-3`, jarak antar-zona `gap-6` dan antar-kartu `gap-4`, tanpa padding halaman sendiri, loading memakai `Skeleton`, dan seluruh teks lewat i18n dua locale ([[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]).

⛔ **Diubah saat implementasi (2026-09-17, keputusan user saat review): agenda pindah ke kolom KIRI.**

```
Kepala saya (sapaan + kehadiran hari ini)
┌ kolom kiri, lg:col-span-2 ┐┌ kolom kanan ┐
│ Perlu tindakan saya       ││ KPI saya    │
│ Agenda hari ini           ││ Pengumuman  │
└───────────────────────────┘└─────────────┘
Ruang kerja posisi (zona D)
```

Rancangan awal menaruh zona B sendirian di kolom kiri dan seluruh zona C (agenda, KPI, pengumuman) di kanan. "Perlu tindakan" hampir selalu pendek (satu baris, atau satu kalimat bagi staf tanpa antrean), sehingga di keempat akun uji DEV kolom kiri menyisakan ruang kosong setinggi tiga kartu. Di layar sempit urutannya tetap: kepala, tindakan, agenda, KPI, pengumuman, lalu zona D.

### 8. Pendekatan yang tidak diambil

| Pendekatan | Alasan |
|---|---|
| Registri widget per posisi | 272 dari 311 metrik KPI masih dinilai manual ([[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]]); kebanyakan posisi akan berisi panel menunggu data |
| Widget diatur sendiri (pin, geser, sembunyikan) | Isi beranda diturunkan dari antrean dan KPI, bukan selera. Untuk menu, `components/layout/menu-terakhir.ts` sudah menolak pola pin dan favorit |
| Menyalin beranda MyBharata utuh | Grid menu sudah dijawab sidebar web. Carousel promosi, cuaca, klub, dan visi-misi tidak menjawab "apa yang menunggu saya". Yang dipinjam hanya pola sembunyi-saat-kosong |

## Irisan Pembangunan

1. **Frontend saja, nol backend.** Susun ulang `/dashboard` jadi zona A sampai D. Zona B dari `pengajuan/ringkasan` apa adanya, zona C dari hook yang sudah ada.
2. **Pengajuan karyawan yang menunggu saya sebagai peninjau** (backend dan frontend). Kunci baru di `registriRingkasan` yang membaca `total` dari `/hr/requests?as=reviewer&limit=1` (izin, cuti, sakit, dinas, koreksi, tukar). Irisan dengan daya ungkit terbesar, karena antrean yang paling sering dimiliki atasan tidak tercakup irisan 1.
   - ⚠️ Jangan kirim `include=booking`: booking sudah punya kunci `booking` sendiri, dan menyertakannya menghitung booking yang sama dua kali.
   - ⚠️ Kunci `karyawan` yang sudah ada membaca field `menunggu` dari `/hr/requests/summary`, yaitu antrean **admin HR** (pengajuan yang sudah sampai langkah HRD). Bagi staf HRD, `as=reviewer` juga memuat langkah HRD, sehingga kedua angka bisa menghitung pengajuan yang sama. **Jangan dijumlahkan** jadi satu total. Tampil terpisah atau salah satu saja: TBD, ukur tumpang-tindihnya dulu.
3. **Pekerjaan yang ditugaskan ke saya.** Kandidat kuncinya interview dan onboarding review (`/api/recruitment/interviews/assigned`, `/api/recruitment/onboarding-reviews/assigned`) serta tiket yang ditugaskan (`tasks/filter?assigned_to_me=true`). ⚠️ Ketiganya bukan pengajuan. Bila tidak layak jadi kartu di `/portal/pengajuan`, zona B butuh daftar kedua dan aturan "beranda tidak memelihara daftar sendiri" di §4 wajib ditinjau lebih dulu, bukan diakali.

## Pelaksanaan Irisan 1

- **Branch**: erp-frontend `feat/beranda-portal-zona`, PR [#1642](https://github.com/bip-itteam-internal/erp-frontend/pull/1642) **merged 2026-09-17** (merge commit `68ff4f937`). Sebelum merge, `origin/main` digabungkan ulang karena `id.ts`/`en.ts` sempat disunting paralel, dan hook pre-push (`tsc`, `lint` seluruh repo, `build`) lolos atas hasil gabungan itu. Deploy dev/prod belum diverifikasi per tanggal itu; ukur ulang sebelum dipakai.
- **Penyimpangan sadar dari rancangan awal ADR ini**, keempatnya sudah ditulis di keputusannya masing-masing: kehadiran bersyarat tanggal hari ini (§3), catatan kaki kunci `degraded` (§4), isi blok KPI (§5), dan agenda di kolom kiri (§7).
- **Diverifikasi di layar** (Chrome headless, `next start` atas hasil build, gateway DEV, login sungguhan lewat form) dengan tiga akun uji: staf tanpa dashboard departemen, HRD Supervisor, Direktur. Angka "Perlu tindakan" sama dengan lencana `/portal/pengajuan` untuk akun yang sama; kehadiran tampil untuk catatan bertanggal hari ini dan "belum ada catatan" untuk 404; jumlah metrik KPI sama dengan `menunggu_penilaian`; ringkasan yang diblokir menghasilkan kalimat galat, bukan kalimat kosong; tema terang dan gelap, lebar 1440 dan 390 tanpa luber mendatar, bahasa id dan en.
- **Test**: aturan murni (`kehadiran-hari-ini`, `baris-tindakan`, `ringkasan-kpi`) dengan kontrol negatif untuk kasus intinya (placeholder, catatan kemarin, catatan besok); komponen `PerluTindakan` dan `AgendaHariIni`; regresi halaman `/dashboard` (gerbang lama tetap, beranda kini ikut tampil bersama dashboard departemen, dashboard di BAWAH beranda, sebelum mount tanpa zona D).

## Consequences

**Yang didapat.** Semua orang kembali memiliki bagian personal, termasuk lima kelompok yang punya dashboard departemen. Beranda menjawab "apa yang menunggu saya" dengan satu request. Halaman Pengajuan dan beranda membaca satu fakta, jadi angkanya tidak bisa menyimpang. Tidak ada gerbang, peta posisi, atau agregator baru yang harus dirawat.

**Yang harus diterima.**
- Tiap pembukaan beranda oleh siapa pun memicu employee-service memanggil lima service sumber, dengan batas waktu 8 detik per sumber. Satu sumber yang lambat menahan zona B sampai batas itu; zona lain tidak ikut tertahan karena query-nya terpisah.
- Kunci `pembelian` **terbukti selalu `degraded` di DEV** (2026-09-17: `GET /api/employee/pengajuan/ringkasan` membalas `degraded: ["pembelian"]` untuk ketiga akun uji), karena registrinya menunjuk `/pengajuan-pembelian/perlu-aksi` yang tak ada di bip-erp ([[API - Employee Service]]). Akibatnya catatan "Angka untuk Pengajuan Barang & Dana tak termuat" tampil permanen bagi siapa pun yang melihat kartu itu (terverifikasi HRD Supervisor dan Direktur). Perbaikannya task backend terpisah: antrean yang dipakai frontend, `/api/procurement/pengajuan-barang/antrean`, memuat semua tahap (cek stok, isi harga, QC), jadi kunci baru wajib hanya menghitung tahap persetujuan seperti `useAntreanDirektur`.
- `useKpiSaya` tak ber-`staleTime`, jadi pratinjau KPI bulan berjalan dihitung ulang tiap kali siapa pun membuka beranda, jauh lebih sering daripada halaman KPI. Waktu responsnya belum diukur (task terpisah).
- Kalender jadwal bulanan (`WorkShift`) keluar dari beranda.
- 13 key i18n `hris.dashboard.*` milik dua komponen yang dihapus kini tak dipakai; pembersihannya task terpisah karena berkas locale paling sering bentrok.
- Halaman lebih panjang bagi lima kelompok berdashboard departemen, karena dashboard itu kini berada di bawah zona personal. Itu harga dari tidak lagi saling menggantikan.

## Belum Diputuskan (TBD)

- **Pengajuan milik sendiri di web.** Backend sudah punya `GET /requests/mine?filter=ongoing` (dipakai "Aktivitas Saya" MyBharata), tetapi self-service HR sengaja dipindah ke MyBharata (erp-frontend #1022, lihat [[APP - Web ERP]]). Menampilkannya hanya-baca di zona C belum diputuskan.
- **Sisa kuota cuti dan form yang wajib diisi.** Keduanya dilayani MyBharata; endpoint yang dipakainya belum dipetakan untuk web.
- **Tujuan tautan "lihat jadwal"** setelah `WorkShift` keluar dari beranda.
- **Angka `karyawan` dan antrean peninjau bagi staf HRD** (irisan 2).
- **Cache hasil `pengajuan/ringkasan`** bila beban pemanggilan ke lima service terasa.
- **`staleTime` untuk pratinjau KPI di beranda**, setelah waktu respons `GET /me/kpi-score?preview=true` diukur di DEV.
- **Dua bagian "yang menunggu" bagi pengguna HRGA**: zona "Perlu tindakan" dan blok "Yang menunggu Anda" di Ringkasan Divisi HRGA (zona D) kini tampil di satu halaman dan membaca antrean yang berbeda.

## Dokumen Terkait

- [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]]: apa yang boleh tampil di ruang kerja posisi
- [[REF - Layout Dashboard erp-frontend]]: cara menyusunnya di layar
- [[APP - Web ERP]]: keadaan `/dashboard` hari ini dan keputusan yang dibalik ADR ini
- [[APP - MyBharata]]: beranda mobile, sumber pola sembunyi-saat-kosong
- [[API - Employee Service]]: `GET /pengajuan/ringkasan` dan `registriRingkasan`
- [[API - Attendance Service]]: `/hr/requests?as=reviewer` dan `/requests/mine`
- [[Microservices - Calendar Service]]: sumber agenda zona C
- [[HRIS - Key Performance Index]]: `GET /me/kpi-score` untuk zona C
- [[REF - Dashboard per Posisi (Indeks Cakupan)]]: posisi mana yang punya ruang kerja posisi
