## Untuk Manajemen

**Apa yang berubah di layar.** Di MyBharata, halaman Slip Gaji menampilkan satu daftar bulan. Untuk tiap bulan ada dua kartu berdampingan: **Slip Gaji** dan **Insentif**. Keduanya tidak menampilkan angka. Menekan salah satu kartu meminta PIN, lalu membuka rinciannya: slip gaji seperti sekarang, atau hitungan insentif (target, realisasi, pencapaian, tarif, insentif, alasan gugur bila ada, dan peringatan bila angkanya belum final). Kartu Insentif hanya muncul bagi yang punya skema insentif profit: Account Specialist, Advertiser, Leader, dan Supervisor marketing. Halaman "Insentif Saya" di web ERP dicabut menunya setelah versi aplikasi ini terpasang luas. Dashboard Insentif dan Master Target tetap di web.

**Siapa yang terdampak.** 37 orang marketing yang hari ini punya baris insentif profit (32 Account Specialist dan Advertiser, 3 Leader, 2 Supervisor per Agustus 2026) mendapat jalan melihat insentifnya dari ponsel. Finance menerima lebih sedikit pertanyaan "kenapa insentif saya segini", karena alasannya tertulis di layar. Host Live, affiliate, dan CRM tidak mendapat kartu Insentif, karena skema mereka belum punya sumber angka di sistem.

**Yang tidak dijanjikan.** Tidak ada pemberitahuan saat periode insentif final atau saat gugur. Angka insentif tidak dijumlahkan ke slip gaji, dan aplikasi tidak menyatakan apakah insentif sudah dibayar. Tidak ada pengajuan atau koreksi insentif dari aplikasi. Insentif Host Live dan affiliate tidak ikut. Aplikasi lama tidak bisa dipaksa memperbarui diri, jadi halaman web tetap ada sampai versi barunya terpasang luas.

**Perkiraan besaran kerja.** Kecil di backend (satu endpoint tanpa angka), sedang di aplikasi (satu modul mengikuti pola KPI Saya dan penyatuan ke daftar Slip Gaji), satu rilis aplikasi ke Play Store dan App Store, satu perubahan kecil di web untuk mencabut menu. Empat task berurutan, dapat dikerjakan satu developer backend dan satu developer mobile.

## Deskripsi

*Layar Insentif Saya dipindahkan dari web ERP ke MyBharata dan ditempatkan di dalam halaman Slip Gaji sebagai kartu per bulan yang berdampingan dengan kartu slip, tanpa nominal sebelum PIN, dengan gerbang PIN di rute yang sudah dipakai slip gaji. Kelayakan kartu ditentukan server lewat satu endpoint keanggotaan tanpa angka, rinciannya membaca endpoint `/profit-dashboard/saya` yang sudah ada, dan aplikasi tidak pernah menjumlahkan atau membandingkan insentif dengan gaji. Menu web dicabut setelah rilis aplikasi terpasang luas, mengikuti preseden pemindahan layar mandiri sebelumnya.*

- **Status**: 🟡 **Diusulkan**, disetujui pemilik produk 2026-09-07 lewat percakapan `/analisa-kebutuhan`. M1 (endpoint keanggotaan) **di kode, belum merge** per 2026-09-08 (bip-erp branch `feat/insentive-keanggotaan-saya`); M2 sampai M5 belum. Daftar task: `Workspace/ANALISA - Insentif Saya di MyBharata.md` (papan kerja, bukan dok terbit).
- **Path di repo**: `bip-erp/services/insentive/func.go` (rute `/profit-dashboard/saya` yang sudah ada; `levelSkema` satu tempat) · `bip-erp/services/insentive/keanggotaan_saya.go` (endpoint keanggotaan, M1) · `mybharata-app/lib/src/features/insentif/` (baru; data, domain, presentation mengikuti `features/kpi/`) · `mybharata-app/lib/src/features/payroll/presentation/pages/payslip_page.dart` (daftar bulan menampung kartu Insentif) · `mybharata-app/lib/src/core/routes/payroll/payroll_pages.dart` dan `payroll_routes.dart` (rute rincian insentif di balik `PinGuard`) · `mybharata-app/lib/src/core/api/url.dart` · `mybharata-app/lib/l10n/app_id.arb`, `app_en.arb` · `erp-frontend/src/components/layout/sidebar-menus.tsx` dan `insentif-menu.ts` (pencabutan menu, belakangan)
- **Tanggal**: 2026-09-07

## Context

**Kebutuhannya bukan "kartu di Slip Gaji".** Kebutuhannya: orang marketing bisa melihat hitungan insentifnya sendiri beserta alasannya (belum final, gugur retur, target belum diisi) tanpa membuka komputer, di aplikasi yang sudah mereka buka tiap hari untuk absen. Kalimat "di dalam Slip Gaji" adalah keputusan letak yang diambil pemilik produk setelah menimbang alternatif menu terpisah, dengan alasan orang mencari uangnya di satu tempat. Keputusan itu diterima; konsekuensinya ditulis di bawah.

**Yang sudah ada, dan sejauh mana menjawab.**

- `GET /profit-dashboard/saya?periode=` di insentive-service memilih baris dari header `BIP-Employee-ID` yang gateway isi ulang dari klaim JWT, **tanpa gerbang role** (sengaja, komentar di `services/insentive/func.go:1405-1418`), membawa `tarif_tiers`, `batas_retur_persen`, `batas_pencapaian_bebas_retur`, `gugur`, `alasan_gugur`, `peringatan[]`, dan `layak_dibayar`. Baris milik seseorang ikut membawa `biaya_gaji`-nya sendiri, yaitu beban perusahaan (bruto ditambah BPJS pemberi kerja), bukan gaji bersih. Cache gateway 3 menit berkunci per pemakai; cache dashboard di insentive 15 menit disaring sesudahnya, jadi tak ada jalur tercampur antar-pemakai. ⚠️ Endpoint ini **belum tercatat di vault** sebelum ADR ini; [[API - Insentive Service]] diperbarui bersamanya.
- Halaman web `/finance/incentive/my-incentive` sudah memakai endpoint itu dan terbuka bagi siapa pun ber-role `insentive`, sengaja di luar kunci menu terbatas ([[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]]). Halaman itu belum dwibahasa dan belum berstruktur HRIS; itu gejala layar yang seharusnya sudah pindah, bukan hal yang perlu diperbaiki di web.
- Di MyBharata, rombakan Slip Gaji "daftar bulan tanpa nominal, PIN per slip" sudah **merged ke `dev`** (my-bharata PR [#134](https://github.com/bip-itteam-internal/my-bharata/pull/134), 2026-09-01) dengan gerbang PIN di `PayrollPages.getPage` yang dikunci `payroll_routes_guard_test.dart`, `PinSession` di memori yang dihapus saat aplikasi ke latar, dan daftar bulan yang datang dari `GET /payroll-runs/my` (hanya run `published`). ⚠️ Rilis di `main` masih 1.14.5+135 (3 Agustus 2026) sementara `dev` 1.15.2+157; rombakan itu **belum sampai ke pemakai** saat ADR ini ditulis.
- Pola fitur "milik sendiri" di aplikasi sudah baku: datasource melempar `Failure`, repository membungkus `Either`, bloc `fold`, teks lewat `context.l10n` (KPI Saya, Tugas Onboarding).
- Preseden pemindahan web ke aplikasi: erp-frontend [#1022](https://github.com/bip-itteam-internal/erp-frontend/pull/1022) mencabut item menu dari array sidebar, membiarkan halamannya hidup tanpa menu, dan meninggalkan antrean peninjau di web. Pelajarannya yang tercatat di [[APP - MyBharata]]: menu web dicabut **sebelum** rilis aplikasi mendarat, sehingga alur terputus selama enam hari.

**Data produksi (diukur 2026-09-07).** 78 akun memegang `system_roles.insentive` (icc 40, supervisor 9, host_live 11, affiliate 5, crm 5, adv_marketplace 2, adv_meta 3, adv_leader 2, kosong 1; Beauty Hacks 41, Kyura 26, sisanya IT, Kesekretariatan, Finance, HR yang diberi role untuk uji). Baris `/profit-dashboard` Agustus 2026 hanya memuat **37 orang**: 32 icc, 3 leader, 2 supervisor. Jadi role saja tidak menentukan siapa yang punya insentif profit; Host Live, affiliate, dan CRM memegang role tanpa satu pun baris. Payroll **tidak memanggil** insentive-service; komponen "Bonus" di slip adalah `InputManual`, dan arah integrasi yang ada justru sebaliknya: insentive menarik beban gaji dari payroll. Tidak ada satu pun kategori inbox atau pengiriman notifikasi di insentive-service maupun payroll-service.

**Gerbang aturan bisnis.** `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` tidak menyebut insentif, bonus, profit, PIN, maupun slip gaji; bagian payroll-nya hanya sanksi Pasal 53 sampai 56. Otoritas angka insentif adalah SK Direktur 010 dan 011/2026 ([[Finance - Incentive]]), dan seluruh angkanya dikirim server.

**Status dok yang jadi landasan.** [[APP - MyBharata]] ✅ tetapi bagian Slip Gaji ber-PIN-nya masih menyebut "belum merged" (basi, diperbaiki bersama ADR ini). [[Finance - Incentive]] dan [[Microservices - Insentive Service]] ⚠️. [[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]] 🟡 dengan T2 dan T4 sudah live di prod; ADR itu menjanjikan angka target di kartu KPI sama dengan di Insentif Saya, dan keputusan ini membawa Insentif Saya ke aplikasi yang sama dengan KPI Saya.

## Decision

### 1. Insentif Saya hidup di MyBharata, di dalam daftar Slip Gaji

Satu daftar bulan. Untuk tiap bulan yang tampil, kartu **Slip Gaji** dan kartu **Insentif** berdampingan, keduanya tanpa nominal dan tanpa status apa pun yang menyingkap angka. Tidak ada halaman perantara per bulan. Menekan kartu membuka rute rinciannya masing-masing, dan rute itu berada di balik `PinGuard` lewat `PayrollPages.getPage`, sehingga PIN diminta saat kartu ditekan, bukan saat halaman daftar dibuka. Menaruh gerbang hanya di `onTap` ditolak: rute rincian, menu developer, dan deep link harus sama-sama tertutup, dan itu pelajaran yang sudah tertulis untuk slip gaji.

`PinSession` tidak berubah: verifikasi berlaku selama aplikasi di depan, dihapus saat `paused`/`detached` dan saat logout. Membuka kartu Insentif setelah kartu Gaji pada sesi yang sama tidak meminta PIN lagi. Bila pemilik produk kelak menginginkan PIN pada tiap kartu, perubahannya satu tempat di `PinSession`, bukan desain baru.

### 2. Kelayakan kartu ditentukan server, bukan daftar role di aplikasi

Kartu Insentif tampil hanya bagi **anggota skema insentif profit**. Keanggotaan dijawab satu endpoint baru di insentive-service, `GET /profit-dashboard/saya/keanggotaan`, yang membaca hierarki dan pemetaan toko yang sudah dipakai penyusun baris dashboard untuk menjawab: apakah pemanggil adalah entitas di level `icc`, `leader`, atau `supervisor`. **Tanpa angka**, tanpa menghitung dashboard.

Sebagaimana dikodekan di M1 (2026-09-08): aturan keanggotaannya **tidak disalin**, `LevelKeanggotaan` memanggil `SusunEntitas` yang sama dengan dashboard untuk tiga level. Yang berbeda dari dashboard hanya **sumber pemetaan toko**: dashboard mendapatnya dari ringkasan profit integration (panggilan berat yang justru dihindari), sedangkan keanggotaan memakai `GET /icc/mappings/me` integration dengan meneruskan identitas pemanggil; keduanya bermuara ke `icc_account_mappings` aktif yang sama, dan aturan "punya toko" (channel terisi) meniru `petakanPemilikToko` integration. Kegagalan sumber dibalas **503** (hierarki karyawan) atau **502** (integration), bukan `levels: []`, supaya aplikasi bisa membedakan "bukan anggota" dari "server tak bisa menjawab"; itu kewajiban M2. Kontrak lengkap di [[API - Insentive Service]]. Aplikasi menampilkan kartu Insentif untuk **dua belas bulan terakhir** bila pemanggil anggota; bulan tanpa baris menampilkan kalimat "belum ada baris insentif atas nama Anda di periode ini" di rincian, persis seperti web.

Menyalin daftar role yang punya skema profit ke aplikasi ditolak: fakta "role mana yang punya skema profit" milik insentive-service, dan `system_roles.insentive` di aplikasi sengaja bertipe string karena pemetaannya pernah membocorkan gerbang. Memanggil `/profit-dashboard/saya` untuk tiap bulan sebelum PIN juga ditolak: dua belas panggilan yang membawa nominal ke memori sebelum PIN diminta.

### 3. Rincian membaca endpoint yang ada, aplikasi tidak menghitung

Rincian memanggil `GET /profit-dashboard/saya?periode=` apa adanya. Tangga tarif, batas retur, alasan gugur, peringatan, dan status layak bayar semuanya dari server. Aplikasi tidak menyalin tabel tarif, tidak menghitung pencapaian, dan tidak menyusun ulang alasan gugur. Rincian biaya operasional boleh menampilkan `biaya_gaji` karena itu gaji orang itu sendiri, dengan label yang menyebutnya **beban perusahaan** (bruto ditambah BPJS pemberi kerja), bukan gaji bersih, supaya tak dibandingkan dengan slip.

### 4. Insentif dan slip adalah dua tahap, bukan dua uang

Aplikasi **tidak pernah** menjumlahkan, mengurangkan, atau membandingkan angka insentif dengan gaji bersih, dan tidak menyatakan apakah insentif sudah dibayar. Kartu Insentif berlabel hitungan yang dibayar terpisah. Bila Finance membayar insentif lewat komponen Bonus di slip bulan berikutnya, angka itu tampil di slip sebagai uang yang diterima, dan aplikasi tidak menautkannya ke kartu Insentif. Aturan ini dikunci test.

### 5. Halaman web dicabut belakangan, mengikuti preseden

Halaman web Insentif Saya tetap hidup sampai versi aplikasi yang memuat kartu Insentif terpasang luas, diukur dari adopsi versi di Play Console, bukan dari tanggal rilis. Sesudah itu item menunya dicabut dari sidebar seperti #1022, halamannya dibiarkan dormant tanpa menu, dan test yang menurunkan kunci i18n dari judul menu disesuaikan. Dashboard Insentif, Master Target, dan Panduan tetap di web: Dashboard memuat beban gaji semua orang, Master Target adalah pekerjaan di meja Finance dan Supervisor.

### 6. Tanpa notifikasi di tahap ini

Pemberitahuan saat periode final atau saat gugur tidak dibuat. Kategori inbox baru berarti insentive-service dan notification-service naik bersama, dan deep link inbox di aplikasi belum hidup untuk kategori mana pun. Bila kelak dibuat, ia keputusan tersendiri.

### 7. Kompatibilitas dan urutan rilis

Endpoint keanggotaan bersifat aditif; aplikasi lama tidak menyentuhnya. Backend naik lebih dulu (dev, lalu prod oleh manusia), baru aplikasi dirilis dengan version name dan code yang naik bersama (dua argumen `update_version.dart`). Kartu Insentif menumpang rombakan Slip Gaji #134 dan ikut kereta rilis yang sama.

### 8. Seluruh teks lewat ARB dua bahasa

Semua teks kartu dan rincian lewat `context.l10n` dengan kunci di `app_id.arb` dan `app_en.arb`, mengikuti konvensi aplikasi; nama menu dan istilah dijaga sama dengan web ([[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]] mengatur penamaan lintas platform, mekanismenya milik tiap repo).

## Consequences

### Yang membaik

- 37 orang marketing melihat hitungan insentif dan alasannya dari ponsel, di aplikasi yang sama dengan KPI Saya yang kini membaca target yang sama (ADR 0079).
- Satu pintu untuk uang milik sendiri di aplikasi, dengan satu gerbang PIN yang sudah teruji.
- Tidak ada aturan tarif atau gugur yang disalin ke Flutter; perubahan SK cukup di server.

### Yang memburuk atau tetap terbuka

- Daftar Slip Gaji berubah dari daftar bulan slip menjadi daftar campuran; bulan yang punya insentif tetapi belum punya slip tampil dengan satu kartu saja, dan sebaliknya. Sumber daftar bulan menjadi gabungan run payroll published dan dua belas bulan terakhir bagi anggota.
- Kartu Insentif untuk bulan tanpa baris berujung rincian kosong; itu diterima sadar supaya kelayakan tetap satu fakta di server dan tak ada nominal sebelum PIN.
- Rilis aplikasi lebih lambat daripada web, dan rombakan #134 sendiri belum sampai ke pemakai; sampai versi barunya terpasang, halaman web tetap satu-satunya jalan.
- Rincian membawa beban gaji orang itu sendiri ke ponsel di balik PIN; risikonya sama dengan slip gaji dan dijaga gerbang yang sama.
- Tidak ada pemberitahuan; orang tetap harus membuka halaman untuk tahu periode sudah final.
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] tetap berlaku; tidak ada tulis lintas-DB, aplikasi hanya membaca lewat gateway.

### Yang sengaja tidak dilakukan

- **Tidak membuat menu terpisah** di Quick Access; keputusan pemilik produk, dengan alasan orang mencari uangnya di satu tempat.
- **Tidak menampilkan status "belum final" di kartu** sebelum PIN; status itu menyingkap keadaan angka, dan kartu tanpa nominal adalah syarat gerbang, bukan gaya.
- **Tidak mengikutkan Host Live, affiliate, CRM**; skema mereka belum punya sumber angka di sistem, dan kartu yang selalu kosong lebih menyesatkan daripada tak ada.
- **Tidak menyandingkan insentif dengan komponen Bonus payroll**; payroll tidak membaca insentive-service, dan penyandingan otomatis adalah salinan fakta yang belum diputuskan pemiliknya.

## Dokumen Terkait

- [[APP - MyBharata]] §Payroll dan §Pengajuan Pelatihan & Tugas Onboarding (preseden pemindahan) · [[APP - Web ERP]] §Incentive
- [[Finance - Incentive]] · [[Microservices - Insentive Service]] · [[API - Insentive Service]] · [[Microservices - Payroll Service]]
- [[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]] · [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]] · [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]] · [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]
- [[HRIS - Payroll Persona]] · [[IT - CI-CD]] (jalur rilis Codemagic)
