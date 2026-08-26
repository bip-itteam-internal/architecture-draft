**Status**: ⚠️ Implemented (ada catatan) — **celah utamanya SUDAH DITUTUP 2026-08-26 (langkah kedua, `ee9509c5`); yang tersisa tinggal verifikasi di lingkungan nyata.** Riwayat di bawah sengaja dipertahankan karena arah keputusannya mudah dibalik lagi tanpa sadar. Catatan lama: Kode selesai di branch `feat/oneForAll` (2026-08-06), seluruh uji hijau, dan sejak itu **sudah mendarat di `main` kedua repo** (terverifikasi 2026-08-10: `services/employee/menu_terbatas.go`, `shared-library/common/catalog_menu.go`, gerbang di `services/integration/main.go`; sisi FE `utils/menu-terbatas.ts` + `components/menu-terbatas-guard.tsx`). Merge menaikkan taruhannya, bukan menurunkannya: yang menahan fitur ini kini tinggal keputusan untuk tidak memasang paketnya ke siapa pun. Aman dipasang (tak ada yang kehilangan akses), tetapi **mengaktifkannya belum benar-benar membatasi**: celah "akun tanpa paket" yang semula diduga kosong kini **terbukti tidak kosong** (bukti 2026-08-06 di §Consequences), sehingga akun finance/IT tanpa permission-set tetap bisa membuka halaman walau restriksi menyala. Prasyarat agar berfungsi: perbaiki fallback task-management lebih dulu (**langkah pertama selesai 2026-08-09, langkah kedua selesai 2026-08-26**). Penegakan backend juga sengaja parsial. **Kunci kedua `menu.finance.insentif` ditambahkan 2026-08-26** (Dashboard & Master Data Insentif, sekalian pindah ke Portal Saya).

## Context

Halaman **Laporan Keuangan** (`/finance/accounting` — Laba Rugi, Neraca, Neraca Saldo) memuat posisi keuangan **seluruh perusahaan**. Permintaannya: halaman itu hanya boleh dibuka akun tertentu, dengan mekanisme yang bisa dipakai ulang untuk menu lain nanti.

Tiga fakta dari kode yang membentuk keputusan ini:

- **Izin yang menjaganya hari ini tak bisa dipersempit.** `finance.accounting.view` juga menggerbangi dasbor divisi FAT, Jurnal & Buku Besar, dan sebelas halaman posisi — total empat belas halaman. Menyempitkannya akan menutup semuanya sekaligus.
- **Izin itu ada di ketiga paket finance bawaan** (`finance_view`, `finance_pelaksana`, `finance_admin` — `common.FinanceTierDefault`), jadi praktis seluruh divisi Finance plus anggota IT memegangnya.
- **Endpoint di baliknya tak punya gerbang sama sekali.** `/accounting/profit-loss`, `/balance-sheet`, dan `/account-balance` termasuk 241 rute telanjang integration-service yang dicatat [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]].

Bentuk yang lazim untuk kasus begini — izin baru yang **deny-by-default** — punya satu akibat operasional yang tak diinginkan: begitu frontend naik, halaman padam bagi semua orang sampai pengelola sempat memasang assignment. Urutan deploy jadi penentu, dan salah urutan berarti tim Finance kehilangan halamannya tanpa ada yang memutuskan demikian.

## Decision

**Menu terbatas: default terbuka, mengunci begitu ada yang di-assign.**

Sebuah menu terbatas berperilaku persis seperti sebelum fitur ada **sampai** paketnya dipasang ke seseorang. Sesudah itu, hanya pemegang paket yang boleh:

| Keadaan | Divisi (fallback lama) | Akun ter-assign |
|---|---|---|
| Belum ada assignment | boleh | — |
| Ada ≥1 assignment | **tak boleh** | boleh |
| Assignment dicabut semua | boleh lagi | boleh |

Keputusan turunan:

- **Modul `menu` berdiri sendiri**, terpisah dari modul yang membungkus kewenangan atas data. Izinnya tak menjawab "boleh melihat data apa", melainkan "boleh membuka menu ini". Satu izin per menu (`menu.<kunci>`), satu paket per menu (`menu_<kunci>`) — paket digabung berarti dua menu menyala bersamaan padahal yang dimaksud satu. Kunci pertama: `menu.finance.laporan`.

  **Kunci kedua: `menu.finance.insentif`** (2026-08-26, paket `menu_finance_insentif`, bip-erp [#1449](https://github.com/bip-itteam-internal/bip-erp/pull/1449) · erp-frontend [#1246](https://github.com/bip-itteam-internal/erp-frontend/pull/1246)). Menggerbangi **Dashboard Insentif** dan **Master Data Insentif** yang pada perubahan yang sama pindah dari kategori Finance ke sidebar **Portal Saya**. Alasannya sekelas Laporan Keuangan tetapi lebih tajam: tiap baris dashboard membawa `biaya_gaji`, beban perusahaan atas SATU orang, yang dengan aturan gaji-orang-itu-sendiri praktis adalah gaji orang tersebut — dan sebelum ini `GET /profit-dashboard` (insentive) serta `GET /profit/incentive/summary` (integration) sama sekali tanpa gerbang.

  **"Insentif Saya" dan "Panduan Insentif" SENGAJA di luar kunci ini.** Halaman pertama hanya memuat baris milik pemegang token; menguncinya ke whitelist akan memutus ICC, host live, affiliate, CRM, dan CS dari angkanya sendiri. Keputusan pemilik sistem 2026-08-26.
- **"Sudah ada yang di-assign" adalah fakta GLOBAL**, tak bisa disimpulkan dari klaim satu orang. Employee-service menghitungnya saat token terbit (assignment dari akun **dan** dari posisi, keduanya, karena hak datang dari dua arah menurut ADR 0030) lalu menempelkan **penanda kunci** `$menulock.<kunci>` ke klaim setiap orang. Tanpa penanda itu, konsumen tak bisa membedakan "restriksi belum aktif" dari "aktif tapi saya tak di-assign", dan keduanya menuntut jawaban berbeda.
- **Prefiks penanda sengaja `$menulock.`, bukan `menu.`.** Setiap service menilai "punya izin modul X?" dengan mencocokkan prefiks `X.`; penanda ber-awalan `menu.` akan membuat orang yang justru **tidak** di-assign tampak seperti punya izin modul menu. Pola sama dengan penanda reach (`<modul>.$reach.<level>`) dan penanda akun luar (`account.$type.external`) yang lebih dulu menumpang di klaim yang sama.
- **Aturan tiga langkah**, satu sumber di `common.HasMenuAccess`, dicerminkan frontend di `utils/menu-terbatas.ts`: punya izin → boleh; punya penanda kunci → tolak; selain itu → `fallback` lama. Urutannya tak boleh dibalik, sebab akun yang di-assign juga membawa penanda kunci.
- **`fallback` adalah perilaku yang berlaku SEBELUM menu itu dibatasi**, bukan nilai baru yang dikarang. Di frontend ia cerminan `useFinanceFallback` (role `finance` atau anggota IT); di backend ia `true`, karena endpoint yang digerbangi memang sebelumnya terbuka bagi siapa pun bertoken sah.
- **Tak ada pengecualian super-akses.** IT dan pemegang `finance_admin` tidak otomatis lolos; kalau perlu, mereka di-assign seperti yang lain. Izin `menu.*` juga dijaga uji agar tak pernah bocor masuk paket atau tier finance.

  ⛔ **KOREKSI 2026-08-26 — kalimat di atas TIDAK BENAR untuk lapisan sidebar.** Ia benar untuk gerbang halaman (`MenuTerbatasGuard`), untuk gerbang backend, dan untuk isi paket; ia **salah** untuk penyaring menu. `bolehItemSidebar` (`erp-frontend/src/utils/menu-permission.ts`) meloloskan `semuaMenu` — IT supervisor **atau jabatan Direktur** — SEBELUM menilai `perm`, kecuali izin yang terdaftar di `TANPA_BYPASS_SEMUA_MENU`. `menu.finance.laporan` **tidak** terdaftar di sana, jadi hingga hari ini keduanya tetap melihat menu Laporan Keuangan walau restriksinya menyala, lalu ditolak halamannya. Menu dan halaman berbeda pendapat, dan alurnya putus persis seperti yang [[ADR - 0047 Jejak Pengajuan Dibaca Modul IT, Digerbang Departemen Bukan Peran]] dirancang mencegah lewat `TANPA_BYPASS_SEMUA_MENU`.

  Kunci kedua (`menu.finance.insentif`, di bawah) **sudah** didaftarkan di `TANPA_BYPASS_SEMUA_MENU` sejak lahir. `menu.finance.laporan` sengaja tidak ikut diubah pada perubahan itu: mempersempit akses orang yang hari ini melihat Laporan Keuangan adalah keputusan tersendiri yang pemiliknya harus sadar mengambilnya, bukan efek samping PR tentang insentif.

Berkas: `shared-library/common/catalog_menu.go` · `services/employee/menu_terbatas.go` · `services/integration/internal/interface/http/menu_gate.go` · `erp-frontend/src/utils/menu-terbatas.ts` · `erp-frontend/src/components/menu-terbatas-guard.tsx`.

## Consequences

**Konsekuensi yang diterima:**

- **Urutan deploy tak lagi menentukan**, dan restriksinya reversibel tanpa deploy: memasang paket menyalakan, mencabut semua assignment mengembalikan. Ini seluruh alasan bentuk "default terbuka" dipilih.
- **Menyalakan fitur ≠ membatasi.** Sesudah merge, tak ada yang berubah bagi siapa pun sampai pengelola memasang paket. Enak untuk rollout, tapi berarti dokumen ini **tidak** boleh dibaca sebagai "halaman Accounting sudah terbatas".
- **Penanda ikut umur token (72 jam).** Orang yang tokennya masih hidup baru terkunci setelah login ulang, dan akun yang baru di-assign baru bisa masuk setelah login ulang. Pertukaran yang sama dengan seluruh hak di ADR 0030, plus jeda cache 60 detik di sisi penghitung.

**Ranjau yang ditemukan saat perencanaan, dan yang mengubah desain:**

Penanda hanya ditempelkan pada klaim yang **sudah tidak kosong**. Sebabnya konkret: dari empat konsumen klaim izin, tiga (payroll, monitoring, procurement) menilai fallback tier dari "klaim memuat izin **modulnya**", tetapi `effectiveTicketPermissions` di task-management menilainya dari "klaim **ada**" (`len(list) > 0`). Menempelkan penanda ke karyawan yang belum punya paket apa pun akan mengubah klaimnya dari kosong menjadi berisi, dan seluruh hak tiket mereka lenyap tanpa pesan apa pun — kelas kegagalan yang sama yang dulu sengaja dimanfaatkan `account.$type.external` untuk menutup akun vendor.

Konsekuensinya: **karyawan tanpa paket sama sekali tak pernah menerima penanda**, sehingga bagi mereka menu terbatas tetap dinilai dengan fallback lama.

⚠️ **Celah itu TERBUKTI TIDAK KOSONG (2026-08-06), dan karenanya fitur ini belum mencapai tujuannya.** Saat perencanaan, celah ini diduga kosong dengan alasan `finance.accounting.view` dulu terpaksa ditambahkan ke tier staff justru karena klaim tim Finance sudah berisi. **Dugaan itu salah** — komentar tersebut menerangkan apa yang *akan* terjadi bila klaim berisi, bukan bukti bahwa memang berisi.

Buktinya sebuah JWT yang **terbit 2026-08-06** (exp 2026-08-09; umur token 72 jam, jadi benar-benar baru) milik akun ber-`system_roles` `finance: supervisor` + `it: supervisor` + `group: admin`: klaim `permissions`-nya **tidak ada sama sekali**. Artinya akun itu tak memegang permission-set apa pun, baik dari akun maupun dari jabatannya. Akun semacam itu tak akan pernah menerima penanda kunci, jatuh ke fallback (`role finance` atau anggota IT → boleh), dan **tetap membuka halaman walau restriksi sudah menyala**.

Akibat praktisnya: memasang paket ke beberapa akun memang membuka halaman bagi mereka, tetapi **tidak menutupnya** bagi siapa pun yang belum punya paket. Menaikkan fitur ini ke produksi dalam keadaan sekarang menghasilkan halaman yang tampak terkunci padahal tidak — lebih buruk daripada belum ada fiturnya.

**Prasyarat agar berfungsi — LANGKAH PERTAMA SUDAH DIKERJAKAN (2026-08-09).** `effectiveTicketPermissions` di task-management kini menilai "klaim memuat izin **ticket**", bukan "klaim ada", sejajar payroll/monitoring/procurement/hris, dan penutupan akun vendor sudah jadi cabang **eksplisit** lewat `IsExternalAccountPermissions` alih-alih menumpang perilaku lama. Predikatnya ditaruh di `common.KlaimMemuatIzinModul` supaya konsumen berikutnya memanggil, bukan menulis ulang — divergensi aturan inilah yang jadi sumber bug menurut ADR ini. Seluruh uji keenam service konsumen klaim dijalankan ulang dan hijau.

Pendorongnya bukan fitur menu terbatas melainkan perbaikan lain: pencocokan departemen case-insensitive di employee-service (`indeksDepartemen`) membuat paket dari jabatan akhirnya ter-resolve bagi karyawan yang selama ini tak dapat apa-apa, sehingga MENAMBAH populasi berklaim-tak-kosong. Tanpa langkah ini, memperbaiki satu bug akan memicu bug lain di service tetangga — karyawan berpaket payroll/hris kehilangan seluruh akses task-management tanpa pesan apa pun.

**LANGKAH KEDUA SELESAI 2026-08-26** (bip-erp `ee9509c5`, di PR [#1449](https://github.com/bip-itteam-internal/bip-erp/pull/1449)). Penjaga "hanya menumpang klaim tak kosong" di `gabungPenandaMenu` **dicabut**, dan uji yang menguncinya dibalik: `TestPenandaTakMenyalakanKlaimKosong` menjadi `TestPenandaMenyalakanJugaKlaimKosong`. Sejak itu penanda kunci ikut ke klaim SETIAP orang, termasuk karyawan tanpa satu pun permission-set — jadi celah yang membuat fitur ini "membuka tanpa menutup" **tertutup**.

Yang membuatnya aman dicabut, diperiksa ulang lebih dulu: penjaga itu dipasang demi SATU konsumen (`effectiveTicketPermissions` di task-management) yang dulu menilai fallback dari "klaim ADA". Penyisiran `KlaimMemuatIzinModul|len(list) > 0` atas seluruh `bip-erp` menemukan **tak satu pun** konsumen klaim yang masih begitu: task-management (`identity.go`), learning, recruitment, form-builder, monitoring, payroll, hris, legal, ga, secretary, dan kpi semuanya lewat `common.KlaimMemuatIzinModul`, yang mengecualikan penanda ber-namespace. Uji **delapan** service konsumen klaim dijalankan ulang dan hijau.

Dua sifat yang menyertai pencabutan, keduanya dikunci uji sendiri:

- **Klaim kosong TETAP kosong selama belum ada satu paket menu terbatas pun yang dipasang.** Penghitungnya mengembalikan daftar kosong, jadi `append` tak menambah apa pun. Klaim orang tanpa paket baru berubah TEPAT saat restriksi pertama dinyalakan — dan pada saat itu memang itulah yang diinginkan. Tanpa sifat ini, deploy akan mengubah klaim setiap karyawan berklaim-kosong di seluruh perusahaan sekaligus.
- **Penjaga `mongodb.DB == nil` di `paketDipakai` menjadi WAJIB.** Jalur ini kini dilewati setiap penerbitan token, termasuk di uji tanpa koneksi, dan `mongodb.Count` memanik lewat `GetCollection`. Arah jawabannya `false` (restriksi dianggap belum aktif): database yang tak terjangkau tak boleh MENGUNCI menu bagi semua orang, sebab kegagalan infrastruktur bukan keputusan pengelola.

⚠️ **Yang masih tersisa sebelum benar-benar dipakai**: verifikasi di lingkungan nyata bahwa memasang paket ke beberapa akun benar-benar MENUTUP menu bagi yang lain — termasuk bagi akun bukti 2026-08-06 yang berklaim kosong. Uji membuktikan penandanya terbit; ia tak bisa membuktikan populasi mana yang menerimanya di produksi.

**Penegakan backend sengaja parsial.** Hanya `/accounting/balance-sheet` yang digerbang — satu-satunya endpoint yang eksklusif milik halaman ini. `/accounting/profit-loss` dan `/account-balance` dibiarkan terbuka karena halaman posisi **SPV**, **Tax**, dan **Cost Control** juga memakainya; menggemboknya akan mematikan tiga halaman itu bagi orang di luar whitelist. Artinya ini **kontrol menu, bukan segel data**: angka laba rugi tetap terjangkau lewat halaman posisi bagi yang berhak ke sana. Jangan dibaca sebagai kerahasiaan angka.

Sifat turunan yang disengaja: panggilan service-to-service (worker/cron) tak membawa header izin sama sekali, sehingga selalu jatuh ke `fallback` dan tetap berjalan setelah restriksi menyala.

⛔ **Sifat itu bukan kenyamanan, ia SYARAT — dan kunci kedua membuktikannya.** Saat menggerbangi rute insentif (2026-08-26) sempat dirancang fallback berupa predikat peran, supaya kebocoran tertutup sejak deploy alih-alih sejak assignment pertama. Rancangan itu akan memadamkan **tiga jalur internal** yang hanya membawa `BIP-Gateway-ID`:

- employee-service → insentive `GET /profit-dashboard` (sumber metrik KPI insentif, `kpi_sumber_insentif_profit.go`)
- pre-warm insentive → dirinya sendiri lewat `127.0.0.1` (`warmProfitDashboard`)
- insentive → integration `GET /profit/incentive/summary` dan `/opex` (`ambilInternal`)

Predikat peran menilai ketiganya sebagai tanpa-peran lalu membalas 403, sehingga **dashboard dan metrik KPI mati bersamaan**, keduanya tanpa galat yang menyebut sebabnya. Karena itu `fallback` di `common.RequireMenu` dipatok `true` di kode, bukan diserahkan ke pemanggil. Dikunci uji `TestMenuTerbatasInsentif_PanggilanInternalTetapLolos`, yang pesan galatnya menyebut akibat itu supaya siapa pun yang tergoda mengetatkannya membaca alasannya lebih dulu.

**Hubungannya dengan `menu_hidden` — sudah tidak berlaku sejak 2026-08-22.** Saat ADR ini ditulis ada mekanisme lain yang menyentuh menu, `position_items[].menu_hidden`, penyembunyian **tampilan** per jabatan yang secara eksplisit bukan keamanan ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]). Keduanya berdampingan dan gampang tertukar, sehingga pembedaannya sempat ditabelkan tiga kolom di [[CORE - RBAC dan Permission Set]].

`menu_hidden` **kini DICABUT** ([[ADR - 0051 Pencabutan Tampilan Menu per Posisi]]), jadi menu terbatas tinggal berdampingan dengan `permission_sets` biasa saja. Yang tetap perlu diingat dari perbandingan lama: menu terbatas membatasi akses **per akun dengan gerbang**, dan itu tetap membedakannya dari izin modul biasa.

**Yang belum diputuskan (TBD):**

- **Apakah pola ini boleh menggantikan izin modul untuk kasus lain.** Ia sengaja sempit (satu menu, satu paket), dan kalau dipakai berlebihan katalog `menu` akan tumbuh jadi daftar halaman — persis yang ditolak ADR 0030 lewat "satu permission per keputusan akses, bukan per endpoint". Batas pemakaian yang wajar belum dirumuskan.
- **Perilaku saat pemakai membuka URL tanpa hak** masih ikut TBD ADR 0030 (403 informatif vs pengalihan); halaman ini memakai panel "Akses Ditolak" di tempat, tanpa pengalihan.
- **Menutup celah akun tanpa paket** bukan lagi "menunggu pengukuran" melainkan **pekerjaan wajib sebelum fitur ini dipakai** — langkahnya sudah dirinci di §Consequences. Yang belum diputuskan hanya kapan dikerjakan, sebab ia menyentuh otorisasi modul lain.
- **Berapa banyak akun yang masuk celah itu** masih belum dihitung. Satu akun terbukti (2026-08-06), dan kebetulan akun ber-hak tinggi; jumlah persisnya butuh query di Employee DB (32783) yang tak terjangkau kredensial `erp-analyst` (hanya berlaku di Integration DB 32789). Angka ini tak mengubah keputusan — perbaikannya tetap wajib — tapi berguna untuk menakar dampak bila fitur sempat dinyalakan.

## Terkait

- [[CORE - RBAC dan Permission Set]] (katalog modul `menu`, paket, dan pembedaannya dari `menu_hidden`)
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] (fondasi paket & resolusi izin) · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]
- [[Microservices - Employee Service]] (penerbit penanda kunci saat token terbit) · [[Microservices - Integration Service]] (gerbang endpoint) · [[Microservices - Task Management Service]] (konsumen klaim yang memaksa penanda hanya menumpang klaim tak kosong)
- [[APP - Web ERP]] (guard halaman & penyaringan menu) · [[API - Integration Service]] (endpoint yang digerbangi)
