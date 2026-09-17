> **Status**: 🟡 **Diusulkan** (2026-09-17). Arah disetujui user; kode belum ada. Membalik konsekuensi "kehilangan kartu Kehadiran dan Pengumuman" yang diterima 2026-08-26 dan 2026-09-15.

## Untuk Manajemen

**Apa yang berubah di layar.** Halaman pertama yang dibuka setiap orang di web ERP (`/dashboard`) disusun ulang jadi empat bagian, dibaca dari atas:

1. **Kepala saya**: sapaan dan status kehadiran hari ini dalam satu baris.
2. **Perlu tindakan saya**: jumlah persetujuan dan permintaan yang menunggu orang itu, masing-masing bertautan ke layarnya. Baris yang jumlahnya nol tidak tampil.
3. **Hari ini**: agenda kalender, skor KPI bulan berjalan, dan pengumuman.
4. **Ruang kerja posisi**: dashboard departemen yang sudah ada hari ini (HRGA, Finance, IT, Ruang Direktur, Marketing), hanya bagi posisi yang punya.

**Siapa yang terdampak.** Semua karyawan. Bagian 1 sampai 3 tampil untuk semua orang. Staf HR, Finance, serta SPV dan Leader brand, yang sejak Agustus kehilangan kartu kehadiran dan pengumuman karena halamannya diganti dashboard departemen, mendapatkannya kembali.

**Yang tidak dijanjikan.**
- Tidak ada dashboard baru untuk posisi yang belum punya (Manufaktur, Quality, Kesekretariatan, Procurement, staf Sales). Bagian 4 untuk mereka tidak muncul.
- Isi beranda tidak bisa diatur sendiri oleh pemakai.
- Status pengajuan cuti milik sendiri, sisa kuota cuti, dan form yang wajib diisi belum masuk. Ketiganya tetap di MyBharata.
- **Tahap pertama belum menghitung cuti, izin, dan dinas yang menunggu persetujuan ATASAN.** Angka itu butuh satu sumber baru di backend dan menjadi tahap kedua.

**Perkiraan besaran kerja** (kasar, belum melewati `/plan`). Tahap pertama hanya frontend, sekitar dua sampai tiga hari. Tahap kedua satu sumber baru di employee-service plus barisnya di frontend, sekitar satu sampai dua hari termasuk deploy.

## Deskripsi

*Beranda portal (`/dashboard`) berhenti memilih ANTARA bagian personal dan dashboard posisi, lalu menumpuk keduanya: tiga zona personal untuk semua orang di atas, ruang kerja posisi di bawah. Antrean "perlu tindakan" dibaca dari endpoint agregat yang sudah ada, `GET /api/employee/pengajuan/ringkasan`, bukan dirangkai di frontend dan bukan endpoint baru.*

- **Status**: 🟡 **Diusulkan**. Arah disetujui user 2026-09-17; kode belum ada.
- **Path di repo** (rencana): `erp-frontend/src/app/(main)/(erp)/dashboard/page.tsx` · `erp-frontend/src/features/erp/portal/components/` (zona beranda) · `erp-frontend/src/features/pengajuan/use-ringkasan-pengajuan.ts` (dipakai ulang) · `bip-erp/services/employee/ringkasan_pengajuan.go` (`registriRingkasan`, tahap 2)
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

Sapaan dari `WelcomeCard` dan status kehadiran hari ini dari `useAttendanceToday` (`GET /api/attendance/today`): status, jam masuk, dan shift. `AttendanceDetail` dan `WorkShift` (kalender jadwal bulanan) tidak lagi dirender penuh di beranda.

### 4. Zona B: antrean dibaca dari `pengajuan/ringkasan`, tidak dirangkai ulang

- **Sumber**: `useRingkasanPengajuan` dan `angkaKartu` di `features/pengajuan/use-ringkasan-pengajuan.ts`.
  ⚠️ Ada hook lain bernama **sama persis** di `features/hris/requests/hooks/use-requests-summary.ts`, yang membaca `/hr/requests/summary` untuk admin HR. Salah impor tidak menghasilkan galat apa pun, hanya angka dengan arti lain. Yang dipakai beranda adalah yang di `features/pengajuan/`.
- **Daftar barisnya** = kartu `/portal/pengajuan` yang tampil bagi pembaca (`KARTU_PENGAJUAN` di `components/layout/pengajuan-menu.ts`, yang tampil bila dan hanya bila menunya lolos `blokMenu`) dan punya `kunciAngka`. Beranda tidak memelihara daftar sendiri, jadi kartu berangka baru di halaman Pengajuan otomatis jadi baris beranda, dan kedua layar tidak bisa menampilkan angka berbeda untuk antrean yang sama.
- **Baris muncul hanya bila angkanya lebih dari nol.** Kunci di `degraded` tidak digambar sebagai nol, dan kunci yang absen (pemanggil tak berhak) tidak punya baris. Arti ketiga keadaan itu sudah ditetapkan di [[API - Employee Service]].
- **Kartu zona B tetap tampil** meski semua barisnya hilang, berisi satu kalimat bahwa tak ada yang menunggu. Di sini kosong adalah kabar baik; menyembunyikan seluruh zona membuat tata letak melompat dan terbaca seperti gagal memuat. Dalam keadaan kosong kartunya dirender **ringkas** (setinggi kalimatnya), bukan setinggi area dominan: staf yang tidak memegang antrean apa pun akan melihat keadaan ini hampir setiap hari, dan kotak besar yang selalu kosong mengajari mereka bahwa bagian itu tidak berguna.
- **Tiap baris berisi angka dan tautan ke layar sumbernya.** Beranda tidak menyalin detail antrean.
- **Ditolak**: merangkai hook per modul di frontend (tiap pembukaan beranda menembak enam endpoint atau lebih, dan gerbang tiap sumber harus disalin ke frontend), serta endpoint agregat baru (agregator kedua untuk fakta yang sama).

### 5. Zona C: hari ini

- **Agenda hari ini** dari `useCalendarRange` (`GET /api/calendar`). Visibilitasnya sudah disaring di service sumber tiap feed ([[Microservices - Calendar Service]]), jadi beranda tidak menyaring ulang.
- **Skor KPI bulan berjalan** dari `useKpiSaya()` (`GET /api/employee/me/kpi-score?preview=true`), bertautan ke `/portal/kpi`. Hook itu mengembalikan `null` untuk 404 (posisi tanpa template atau tanpa work data); barisnya tidak dirender, bukan ditulis nol.
- **Pengumuman** lewat `AnnouncementCard` yang sudah ada.

### 6. Zona D: pemilih yang sudah ada, dipindah ke bawah

- `pilihDashboard`, `ISI_DASHBOARD`, dan `DASHBOARD_DEPARTEMEN` beserta gerbang dan test-nya dipakai apa adanya. Yang berubah hanya letaknya.
- Pilihan `beranda` di dropdown Direktur dan supervisor IT kini berarti "tanpa ruang kerja posisi", karena zona personal selalu tampil. Nilai tersimpan `beranda` di `localStorage` tetap sah dan tak perlu migrasi, tetapi label i18n `portal.dashboard.beranda` perlu disesuaikan dengan artinya yang baru.
- Posisi tanpa dashboard tidak mendapat zona D sama sekali, tanpa panel kosong ([[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] §4).
- Hanya isi terpilih yang dirender, sama dengan hari ini.

### 7. Tata letak

Mengikuti [[REF - Layout Dashboard erp-frontend]]: `grid lg:grid-cols-3` dengan zona B `lg:col-span-2` sebagai area dominan, jarak antar-zona `gap-6` dan antar-kartu `gap-4`, tanpa padding halaman sendiri, loading memakai `Skeleton`, dan seluruh teks lewat i18n dua locale ([[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]). Di layar sempit zona bertumpuk berurutan A, B, C, D.

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

## Consequences

**Yang didapat.** Semua orang kembali memiliki bagian personal, termasuk lima kelompok yang punya dashboard departemen. Beranda menjawab "apa yang menunggu saya" dengan satu request. Halaman Pengajuan dan beranda membaca satu fakta, jadi angkanya tidak bisa menyimpang. Tidak ada gerbang, peta posisi, atau agregator baru yang harus dirawat.

**Yang harus diterima.**
- Tiap pembukaan beranda oleh siapa pun memicu employee-service memanggil lima service sumber, dengan batas waktu 8 detik per sumber. Satu sumber yang lambat menahan zona B sampai batas itu; zona lain tidak ikut tertahan karena query-nya terpisah.
- Kunci `pembelian` per 2026-09-14 kemungkinan selalu `degraded`, karena rute sumbernya tidak ditemukan di bip-erp ([[API - Employee Service]]). Barisnya praktis tak pernah muncul sampai itu dibereskan.
- Kalender jadwal bulanan (`WorkShift`) keluar dari beranda.
- Halaman lebih panjang bagi lima kelompok berdashboard departemen, karena dashboard itu kini berada di bawah zona personal. Itu harga dari tidak lagi saling menggantikan.

## Belum Diputuskan (TBD)

- **Pengajuan milik sendiri di web.** Backend sudah punya `GET /requests/mine?filter=ongoing` (dipakai "Aktivitas Saya" MyBharata), tetapi self-service HR sengaja dipindah ke MyBharata (erp-frontend #1022, lihat [[APP - Web ERP]]). Menampilkannya hanya-baca di zona C belum diputuskan.
- **Sisa kuota cuti dan form yang wajib diisi.** Keduanya dilayani MyBharata; endpoint yang dipakainya belum dipetakan untuk web.
- **Tujuan tautan "lihat jadwal"** setelah `WorkShift` keluar dari beranda.
- **Angka `karyawan` dan antrean peninjau bagi staf HRD** (irisan 2).
- **Cache hasil `pengajuan/ringkasan`** bila beban pemanggilan ke lima service terasa.

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
