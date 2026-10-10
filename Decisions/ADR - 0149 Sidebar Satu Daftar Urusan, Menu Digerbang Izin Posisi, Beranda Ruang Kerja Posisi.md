> **Status**: 🟢 **Diterima**, 2026-10-10, oleh irfanarfianto (diusulkan 2026-10-02). HRGA sudah berjalan (bip-erp#2488); Marketing sedang dikerjakan (bip-erp#2924); departemen lain dan penyatuan akhir belum.

## Untuk Manajemen

**Apa yang berubah di layar.** Sidebar web ERP tidak lagi dibagi per departemen dan tidak lagi punya bagian "Portal Saya". Isinya satu daftar urusan pekerjaan (mis. Pengajuan & Persetujuan, Tugas, Kehadiran & Cuti, Payroll, Piutang & Penerimaan, Toko & Penjualan), dengan nama menu yang sama untuk semua orang. Yang berbeda antar-orang hanya tiga hal: menu mana yang tampil, data mana yang terlihat di dalamnya (milik sendiri, tim, gudang yang ditugaskan, atau seluruh perusahaan), dan tombol mana yang boleh ditekan. Halaman Beranda menjadi tempat kerja harian: di atas tetap sapaan, yang menunggu tindakan, dan agenda; di bawahnya ringkasan pekerjaan sesuai jabatan. Ringkasan divisi yang dulu menjadi menu sendiri pindah ke Beranda.

**Siapa yang terdampak.** Semua pemakai web ERP. Rancangan per jabatan untuk enam departemen sudah disetujui: Marketing (percontohan), FAT, HRGA, Tech Development, Kesekretariatan, dan Manufaktur.

**Yang tidak dijanjikan.**
- Hak akses tidak bertambah karena perubahan ini. Menu yang hari ini tampil karena departemen seseorang akan tampil karena izin jabatannya. Jabatan yang izinnya belum terpasang rapi di sistem bisa kehilangan menu sampai datanya dibereskan, sehingga perbaikan data jabatan berjalan bersamaan.
- Perbaikan data hak akses di server produksi dijalankan manusia, bukan otomatis.
- Akses darurat tim IT ke modul departemen lain belum diputuskan di sini; ia menunggu keputusan pemisahan tugas yang masih diusulkan.
- Pemakai tidak bisa menyusun sidebar atau Beranda sendiri.
- Departemen di luar enam yang sudah dirancang (Procurement, Quality, Sales offline) menyusul dengan analisa sendiri.

**Perkiraan besaran kerja** (kasar, belum melewati `/plan`). Penjaga dan gerbang per menu: dua sampai tiga hari. Susunan ulang per departemen: satu sampai tiga hari tiap departemen, enam departemen. Ruang kerja Beranda baru: satu sampai dua hari per departemen yang belum punya. Penyatuan akhir sidebar: satu sampai dua hari. Perbaikan data hak akses: disiapkan per departemen, dijalankan manusia.

## Deskripsi

*Sidebar web ERP menjadi satu daftar urusan tanpa kategori departemen dan tanpa "Portal Saya". Menu sama untuk semua; yang tampil ditentukan izin posisi per menu, bukan keberadaan kategori `system_roles`; data dan aksi di dalamnya disaring server menurut cakupan posisi. Beranda (`/dashboard`) adalah tempat kerja posisi, dan ringkasan divisi pindah ke zona D [[ADR - 0105 Beranda Portal Menumpuk Zona Personal di Atas Ruang Kerja Posisi]]. Pembatas kategori baru boleh dihapus setelah setiap menu punya gerbang izin sendiri.*

- **Status**: 🟢 **Diterima**, 2026-10-10, oleh irfanarfianto. Kode HRGA sudah ada; Marketing sedang dikerjakan; sisanya belum.
- **Path di repo** (akan disentuh): `erp-frontend/src/components/layout/sidebar-menus.tsx` · `erp-frontend/src/components/layout/sidebar.tsx` · `erp-frontend/src/components/layout/sidebar-kategori.ts` · `erp-frontend/src/components/layout/portal-menu.ts` · `erp-frontend/src/components/layout/pengajuan-menu.ts` · `erp-frontend/src/utils/menu-permission.ts` · `erp-frontend/src/utils/akses-penuh.ts` · `erp-frontend/src/proxy.ts` · `erp-frontend/src/components/layout/sidebar-gerbang.test.ts` (baru) · `erp-frontend/src/features/erp/portal/lib/dashboard-posisi.ts` · `erp-frontend/src/features/erp/portal/lib/gerbang-departemen.ts` · `bip-erp/services/employee/peran_dari_jabatan.go`
- **Tanggal**: 2026-10-02

## Context

### Keadaan hari ini

Diukur ke `origin/main` erp-frontend `3b15f60d2` dan bip-erp `a5d00ada`, 2026-10-02.

**Sidebar disusun per departemen, dan departemen itulah gerbang utamanya.**
- `menus` di `sidebar-menus.tsx` adalah peta kunci kategori ke daftar menu: `erp` (Portal Saya), `finance`, `hris`, `it`, `ga`, `tools`, `manufacture`, `warehouse`, `quality`, `secretary`, `procurement`, `marketing`, `integration`, `integration_accurate`. Kira-kira 215 menu.
- Kategori yang tampil dihitung `kunciModulAktif` dari kunci `system_roles` ditambah prefiks modul paket izin, lalu ditambal tangan untuk marketing, warehouse, tools, manufacture, dan Accurate (`sidebar.tsx`). Di kategori yang bukan modul pembaca hanya menu `public` yang bertahan (`sidebar.tsx:684`).
- Hanya sekitar 89 dari 215 menu yang membawa `perm`. Sisanya tampil karena kategorinya tampil (dihitung dari `url:` dan `perm:` per rentang kategori; angka kasar). [[ADR - 0051 Pencabutan Tampilan Menu per Posisi]] sudah mencatat kelas ini: 151 menu tanpa `perm` saat itu.
- IT supervisor dan Direktur melihat semua kategori dan lolos semua `perm` kecuali yang terdaftar di `TANPA_BYPASS_SEMUA_MENU` (`aksesSemuaMenu`, `utils/akses-penuh.ts`; [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]]).
- Gerbang rute (`proxy.ts`) membaca cookie `system_roles` saja dan menganggap `it:admin` setara supervisor, sedangkan sidebar tidak. Dua definisi untuk satu pertanyaan.
- URL yang sama muncul di beberapa kategori: Form Builder di tiga, CAPA di tiga, Gudang Bahan Baku di empat, menu Accurate di dua.

**Akibatnya terlihat di layar.** Sensus prod 2026-10-01 dalam enam rancangan per departemen menemukan Security tidak melihat menu Buku Tamu karena letaknya di kategori HRIS, Corporate Secretary tidak melihat Ruang Direktur karena menunya digerbang izin keuangan, Tax Staff tidak bisa membuka Pajak, dan staf IT melihat menu KPI IT lalu dipantulkan. Orang mencari pekerjaannya menurut nama departemen, padahal yang ia cari adalah urusan.

**Hak di prod menumpuk di akun, bukan di posisi.** [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] menetapkan hak menempel di posisi, tetapi sensus yang sama menemukan banyak jabatan tanpa paket dan banyak akun dengan peran jauh di atas jabatannya. Sebagian menyangkut pemisahan tugas atas uang dan hak akses; rinciannya ada di issue privat repo kode dan sengaja tidak ditulis di vault (repo publik).

### Yang sudah ada dan dipakai ulang

| Kebutuhan | Sudah dijawab oleh |
|---|---|
| Induk dengan satu daun tampil sebagai menu tunggal | `ratakanIndukTipis`, `AMBANG_SARANG = 3`, `ambangSarang` minimum 2 (`sidebar-menu-shape.ts`) |
| Saring per menu dari izin, dengan tier sebagai cadangan | `bolehMenu` / `bolehItemSidebar`, tabel `FALLBACK`, `$menulock` (`utils/menu-permission.ts`) |
| Nama kategori tidak lagi tampil sebagai teks | pemisah tinggal garis, nama `sr-only` (`navigation.tsx`) |
| Induk menamai urusan, daun tanpa "Saya" | `ui-checklist.md` §2b di agent-kit, dijaga `sidebar-urusan.test.ts` |
| Tanpa penyembunyian menu per posisi | [[ADR - 0051 Pencabutan Tampilan Menu per Posisi]] |
| Beranda bertumpuk, ruang kerja posisi di zona D | [[ADR - 0105 Beranda Portal Menumpuk Zona Personal di Atas Ruang Kerja Posisi]]; `pilihDashboard`, `ISI_DASHBOARD`, `DASHBOARD_DEPARTEMEN` |
| Isi ruang kerja dari KPI, antrean, dan ambang; posisi tanpa data tidak diberi ruang kerja | [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] |
| Ruang kerja merender komponen asli modul kerjanya | [[ADR - 0130 Dashboard FAT Diringkas, Isi Posisi Pindah ke Modul Kerjanya]] |
| Satu antrean persetujuan | [[ADR - 0114 Antrean Persetujuan Terpusat di Web, Satu Tabel Seragam dari Agregator Employee-Service]] (`GET /pengajuan/antrean`) |
| KPI pribadi atau departemen dipilih otomatis | `/portal/kpi` lewat `useCakupanKpi` |
| Keanggotaan penerima insentif | `GET /profit-dashboard/saya/keanggotaan` (insentive-service) |
| Cakupan toko Marketing | `icc_account_mappings`, `GET /icc/mappings/me` |

### Yang belum ada (dibuktikan `git grep origin/main`, exit 1)

- Penugasan gudang per orang di manufacture/warehouse. Cakupan gudang hari ini lewat peran `admin_gudang_rm`/`admin_gudang_fg` di matriks WMS dan cakupan toko mitra Sadewa per toko.
- Jabatan Shop Quality dan Building Maintenance di `peranJabatanTabel` (`peran_dari_jabatan.go`); baris GA "leader" ada tetapi jabatannya tidak ada di master.
- Endpoint yang mengembalikan izin efektif ke FE; izin hanya ada di JWT.
- Field `SetaraDirektur` untuk FE; fungsi itu hanya dipakai di server.
- Akses darurat berjejak untuk IT; yang ada baru usulan SA-1 di [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]].

### Status dasar keputusan

ADR ini berdiri sebagian di atas dokumen yang belum menjadi kenyataan: [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] 🟡 rancangan, [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]] 🟡 diusulkan dengan nol kode, dan [[REF - Dashboard per Posisi (Indeks Cakupan)]] 🟡 rancangan. Bagian yang bergantung pada ketiganya ditandai di Decision. Sensus prod 2026-10-01 bertanggal; ukur ulang sebelum dipakai.

## Decision

### 1. Satu daftar urusan, tanpa kategori departemen dan tanpa Portal Saya

- Sidebar adalah satu daftar berurutan: Beranda, lalu urusan umum (Ruang Direktur, Kalender, KPI, Pengajuan & Persetujuan, Tugas), lalu urusan pekerjaan. Tidak ada pembatas antara urusan umum dan urusan pekerjaan, dan tidak ada label departemen.
- Induk menamai urusan, bukan jabatan dan bukan hubungan pembaca. Daun tidak memakai kata "Saya" ("Tim" boleh). Induk yang bagi pembaca hanya berisi satu daun tampil sebagai menu tunggal (`ratakanIndukTipis`); tidak ada induk berisi satu menu di definisi.
- Satu URL, satu tempat di sidebar. Menu yang dibaca beberapa departemen (Form Builder, CAPA, Gudang Bahan Baku, Accurate, Data Pemasok) tinggal di satu urusan dan tampil bagi semua pemegang izinnya.
- Susunan urusan per departemen mengikuti enam rancangan yang disetujui; daftarnya ada di § Rancangan per departemen.

### 2. Menu sama untuk semua; yang tampil ditentukan izin per menu

- **Setiap daun wajib punya gerbang sendiri**: `perm` (dengan entri `FALLBACK` tier bila modulnya masih memakai tier), atau `public: true` yang disengaja, atau gerbang khusus yang sudah ada (matriks WMS, capability Form Builder, keanggotaan insentif). Dijaga test baru yang gagal bila ada daun tanpa salah satunya.
- **Saringan kategori dicabut**: `modules.includes(mod)` dan tambalan kategori per modul di `sidebar.tsx` dihapus, sehingga paket izin bisa membuka menu di urusan mana pun dan keberadaan kunci `system_roles` tidak lagi menentukan tampil.
- ⛔ **Urutannya wajib**: saringan kategori baru dicabut setelah setiap daun bergerbang. Mencabutnya lebih dulu membuka sekitar 126 menu tanpa `perm` bagi semua orang, tanpa satu pun galat.
- **Gerbang sidebar dan gerbang rute satu definisi.** `proxy.ts` dan sidebar membaca aturan yang sama untuk rute yang sama; perbedaan `it:admin` dihapus.
- **Bypass "semua menu" untuk IT supervisor dan Direktur dicabut dari sidebar.** Direktur menerima menunya lewat paket jabatan. Jalan masuk darurat untuk IT ke modul bisnis menunggu keputusan SA-1 [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]]; sampai diputuskan, pencabutan bypass IT ditahan dan dicatat sebagai TBD, bukan dibuka diam-diam.
- Menyembunyikan menu yang boleh dibuka tetap ditolak ([[ADR - 0051 Pencabutan Tampilan Menu per Posisi]]). Menu yang tidak pantas bagi sebuah jabatan dijawab dengan mencabut izinnya.

### 3. Data dan aksi sesuai cakupan posisi, disaring di server

- Cakupan yang dipakai: **S** milik sendiri, **T** tim yang dipimpin, **G** gudang yang ditugaskan, **D** seluruh departemen atau perusahaan, dan **antrean** (yang menunggu tahap pembaca). Cakupan ditentukan server dari identitas pemanggil; frontend tidak menyaring data.
- Tombol yang mengubah data digerbang izin aksi (`work`, `approve`, `manage`), bukan sekadar izin lihat halaman.
- **Lokasi gudang Manufaktur adalah cakupan data, bukan kelompok menu.** Gudang Tinggar dan Sadewa memakai menu yang sama. Tahap ini cakupan G diturunkan dari jabatan dan peran gudang yang sudah ada; jabatan Admin Warehouse dipecah menurut gudangnya. Penugasan gudang per orang **TBD**.
- Tim Leader Marketing dibaca dari daftar Leader ICC, bukan dari atasan langsung. HRGA adalah label grup, bukan nama departemen: filter dari layar boleh memakainya, data per orang tetap `Human Resource` / `General Affair`.

### 4. Urusan umum (pengganti Portal Saya)

- **Pengajuan** hanya berisi hal yang diajukan pembaca, termasuk tugas ke tim lain. **Tidak ada menu Ajukan Tugas**; mengajukan tugas adalah kartu di Pengajuan.
- **Persetujuan** hanya berisi hal yang menunggu keputusan pembaca (ADR 0114). Kartu persetujuan yang hari ini ada di halaman Pengajuan pindah ke Persetujuan.
- **Tugas**: Daftar Tugas, Permintaan Masuk, Laporan Tugas, Laporan Tim, Kelola Space; tiga yang terakhir sesuai izin.
- **KPI satu menu** untuk semua: KPI Portal, KPI Scoring HRIS, dan menu KPI per departemen (IT, Sekretariat, Manufaktur, GA, Finance) dilebur. Rekap tim atau departemen adalah tab di halaman yang sama, bukan menu terpisah.
- **Insentif bukan urusan umum.** Ia milik FAT (pengelola) dan Marketing (penerima, hanya bagi anggota skema lewat endpoint keanggotaan).
- **Pengajuan Karyawan** (daftar kerja HR) pindah ke urusan Kehadiran & Cuti.

### 5. Beranda sebagai tempat kerja posisi

- **Ringkasan divisi bukan menu.** `/finance`, `/hris`, `/it`, `/manufacture`, dan ringkasan departemen lain keluar dari sidebar dan tampil di zona D Beranda bagi posisi yang berhak.
- Ruang kerja posisi baru dibangun mengikuti [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]]: posisi tanpa data kerja di sistem tidak mendapat ruang kerja, hanya zona personal.
- Pemilihan ruang kerja tetap satu tempat (`dashboardUntukPosisi`); jabatan yang dilebur atau diganti namanya (mis. Account Receivable) didaftarkan di sana, nama lama tetap dikenali selama peralihan.

### 6. Perbaikan data hak akses berjalan bersamaan, dijalankan manusia

- Paket dipasang ke **posisi**, bukan akun. Paket per akun hanya pengecualian bertanggal dan beralasan.
- ⛔ Memasang satu paket sempit ke posisi yang belum punya paket modul itu mencabut seluruh hak tier-nya. Tiap pemasangan wajib menyertakan paket yang menyamai hak tier lamanya.
- Agent hanya menyiapkan skrip dry-run beserta daftar sebelum/sesudah; manusia yang menjalankan di prod. Pemegang jabatan wajib login ulang.
- Temuan yang menyangkut celah keamanan dicatat di issue privat repo kode, tidak di vault.

### 7. Keputusan final yang tidak dibuka ulang

Tidak ada pembatas Portal Saya; tidak ada induk berisi satu menu; tidak ada kata "Saya" di nama menu; tidak ada menu Ajukan Tugas; KPI satu menu; ringkasan divisi masuk Beranda zona D; Insentif masuk FAT dan Marketing; menu Karyawan Terlambat untuk Cost Control dihapus (keterlambatan dicek di Payroll Run); FAT memakai satu posisi Account Receivable dan Junior Accountant dilebur ke Senior Accountant; tidak ada GA Leader (HRD Supervisor atasan GA); lokasi gudang Manufaktur jadi cakupan data.

## Rancangan per departemen

Rancangan rinci (per posisi, matriks lihat, matriks aksi, pemisahan tugas, perbaikan data, uji pakai) hidup di tujuh Artifact bertanggal 2026-10-01 sampai 2026-10-02 (enam departemen ditambah Direksi), disetujui user 2026-10-02; tautannya di § Tautan Artifact rancangan. Artifact adalah salinan rancangan, bukan sumber kebenaran; yang mengikat adalah ADR ini dan dok domain yang ditautkannya. Pokok per departemen:

| Departemen | Urusan pekerjaan | Pokok khusus |
|---|---|---|
| Marketing (percontohan) | Toko & Penjualan, Iklan & Kampanye, Live, Layanan Pelanggan, Permintaan ke Unit Lain, Tim & Penugasan, Insentif, Analisis, Kamus Metrik | Account Specialist dan Marketplace Advertiser satu menu; Rekap KPI Tim jadi tab KPI; Komplain Belum Dibalas dan SLA Chat halaman baru |
| FAT | Piutang & Penerimaan, Pengeluaran & Anggaran, Pembukuan, Payroll Run, Insentif Marketing, Sinkron Penjualan ke Accurate, Pajak, Panduan Accurate | Satu posisi Account Receivable; Junior Accountant dilebur; Kas Kecil jadi menu; Accurate satu tempat |
| HRGA | Data Karyawan, Kehadiran & Cuti, Payroll, Disiplin & Hubungan Industrial, Rekrutmen, Pelatihan & Penilaian, Budaya & Komunikasi, Form Builder, Aset & Perlengkapan, Ruang & Booking, Buku Tamu & Keamanan, Organisasi & Aturan | Pengaturan dipindah ke urusannya; buku tamu terlihat Security; tanpa GA Leader |
| Tech Development | Akun & Hak Akses, Infrastruktur, Integrasi Marketplace, Form Builder, Jejak & Akses Darurat | Helpdesk lewat Tugas; Integration dipecah; Akses Darurat menunggu ADR 0137 |
| Kesekretariatan | Ruang Direktur, Legal & Perizinan, Registrasi & Pengembangan Produk, Audit Internal | Ruang Direktur digerbang paket Persetujuan: Direksi (Corporate Secretary tanpa tab Keuangan); tim kreatif lewat space Tugas |
| Manufaktur | Perencanaan Produksi, Produksi, Gudang Bahan & Barang Jadi, Stok & Opname, Pengiriman Pesanan Online, K3 & Mutu, Master Data Produksi, Persetujuan & Riwayat | Tinggar dan Sadewa satu urusan; cakupan per gudang |
| Direksi (Direktur, Corporate Secretary) | Menu baca dan memutus dari tiap departemen, memakai nama induk departemen pemiliknya | Tidak lagi "semua menu"; Ruang Direktur jadi tab Beranda (Persetujuan, Kinerja, Keuangan, Penjualan, SDM, Produksi, Legal); antrean keputusan satu sumber (ADR 0114); "setara Direktur" untuk payroll, anggaran, kas kecil belum diputuskan |

### Tautan Artifact rancangan

Artifact dibuka dengan akun pemiliknya atau akun yang diberi akses lewat menu Share. Isinya salinan rancangan bertanggal, bukan sumber kebenaran.

| Rancangan | Artifact | Catatan berbagi |
|---|---|---|
| Marketing (percontohan) | https://claude.ai/artifact/URMnPPaVMhaCXNr2v5XeHv | sudah dibuka "anyone with link" |
| FAT | https://claude.ai/artifact/XrGexzWCCuMhoy9A2Gkwxe | privat |
| HRGA | https://claude.ai/artifact/9kNAFQjHdWJBcRX7YjsWiw | privat |
| Tech Development | https://claude.ai/artifact/RzTJJpYTJqoN4Z73xjG28R | ⛔ tetap privat: memuat temuan keamanan yang belum ditambal |
| Kesekretariatan | https://claude.ai/artifact/WEoMKBq79nE6PxVyyM8z8P | privat |
| Manufaktur | https://claude.ai/artifact/1bLgSV8cg6kwoe3EPzvSbD | ⛔ tetap privat: memuat temuan keamanan yang belum ditambal |
| Direksi | https://claude.ai/artifact/GcQNJJDdLDoem52XoescSe | privat; temuan keamanan ditulis tanpa rincian teknis |

## Consequences

**Yang didapat.**
- Nama menu dan letaknya sama untuk semua, sehingga panduan, pelatihan, dan bantuan IT bisa menyebut satu jalur.
- Paket izin posisi menjadi satu-satunya penentu menu, sesuai [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]; menu yang hari ini hilang karena salah kategori (Buku Tamu, Ruang Direktur, Pajak) kembali.
- URL ganda hilang; satu urusan, satu pintu.
- Beranda menjawab "apa pekerjaan saya hari ini" per jabatan, dan ringkasan divisi tidak lagi menghabiskan baris sidebar.

**Yang harus diterima.**
- Fase gerbang menuntut entri izin untuk sekitar 126 menu, dan setiap entri berisiko salah arah. Penjaganya test per daun plus uji pakai dengan akun nyata per jabatan, bukan hanya akun supervisor.
- Selama perbaikan data belum dijalankan, jabatan tanpa paket bisa kehilangan menu begitu saringan kategori dicabut. Karena itu penyatuan akhir menunggu perbaikan data minimal untuk keenam departemen.
- IT supervisor dan Direktur kehilangan pandangan "semua menu" di sidebar; untuk IT efektifnya menunggu ADR 0137.
- Test lama yang mengunci bentuk per kategori (`portal-menu.test.ts`, `sidebar-kategori.test.ts`, `navigation.test.tsx`, dan kawan-kawan) harus ditulis ulang, bukan dibuang.
- Label Portal Saya, label kategori, dan beberapa kunci i18n menjadi yatim; pembersihannya ikut task terkait karena berkas locale paling sering bentrok.
- Bagian "Portal Saya" di [[APP - Web ERP]] dan kalimat "item Portal Saya wajib `public: true`" berhenti berlaku saat penyatuan akhir.

**Mengubah keputusan lama.**
- [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]]: menu terbatas tetap, tetapi bypass `semuaMenu` di sidebar dicabut (§2), dan kunci `menu.finance.insentif` pindah dari Portal Saya ke urusan Insentif.
- [[ADR - 0105 Beranda Portal Menumpuk Zona Personal di Atas Ruang Kerja Posisi]] §6: daftar ruang kerja zona D bertambah dan menerima ringkasan divisi.

## Belum Diputuskan (TBD)

- Jalan masuk darurat IT ke modul bisnis (SA-1 ADR 0137), dan karena itu waktu pencabutan bypass IT.
- Penugasan gudang per orang di luar jabatan.
- Delegasi kalender Personal Assistant untuk agenda Direktur.
- Departemen yang belum dirancang: Procurement, Quality, Marketing Offline Distribution.
- Apakah gerbang rute dipindah ke definisi yang dibagikan server (tanpa endpoint izin, FE tetap membaca JWT).

## Dokumen Terkait

- [[APP - Web ERP]]: keadaan sidebar dan Beranda hari ini
- [[CORE - RBAC dan Permission Set]]: paket, tier, klaim
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]
- [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]]
- [[ADR - 0051 Pencabutan Tampilan Menu per Posisi]]
- [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]]
- [[ADR - 0105 Beranda Portal Menumpuk Zona Personal di Atas Ruang Kerja Posisi]]
- [[ADR - 0114 Antrean Persetujuan Terpusat di Web, Satu Tabel Seragam dari Agregator Employee-Service]]
- [[ADR - 0130 Dashboard FAT Diringkas, Isi Posisi Pindah ke Modul Kerjanya]]
- [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]]
- [[REF - Dashboard per Posisi (Indeks Cakupan)]]
- [[REF - Layout Dashboard erp-frontend]]
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]
