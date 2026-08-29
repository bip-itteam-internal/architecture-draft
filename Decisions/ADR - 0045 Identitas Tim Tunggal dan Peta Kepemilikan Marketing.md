**Status**: 🟡 Sebagian dieksekusi (2026-08-29). **Expand** dan **Migrate** live di produksi: penyemaian awal 16 pemetaan (2026-08-11) tumbuh lewat entri manual susulan jadi **58 dari 59 toko terpetakan** per 2026-08-27 (satu yatim tersisa: `Series Glowbooster`), drift ICC-vs-`department_shops` (`Menyimpang`) nol. **Contract BARU SEBAGIAN**: saringan `/divisi` di [[Microservices - Marketing Analytics Service]] sudah pindah penuh ke `department_shops` sebagai sumber (bip-erp PR [#1520](https://github.com/bip-itteam-internal/bip-erp/pull/1520) & [#1522](https://github.com/bip-itteam-internal/bip-erp/pull/1522), erp-frontend PR #1305 — merged 2026-08-29, **belum di-deploy/diverifikasi lewat gateway**), keputusan sadar (2026-08-27) yang **sengaja menunda** dua hal ke rencana terpisah: kolom penanggung jawab toko (`icc`/blok "per tim" di `/beranda`) **masih membaca `team_shops`+`marketing_teams`**, dan menu `/integration/teams` **belum dicabut**. Rincian status per-langkah: §Migrasi. Menyusul [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] dan [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]]; **tidak** menggantikan keduanya.

## Context

Pertanyaan "toko ini milik tim mana" hari ini dijawab oleh **tiga mekanisme yang tidak saling tahu**, dan tak satu pun dokumen menyatukannya. Ketiganya ditemukan saat menelusuri menu yang terasa redundan (Teams vs ICC Management).

### Tiga gagasan "tim" yang hidup bersamaan

| Kandidat | Keadaan produksi 2026-08-11 | Dipakai siapa |
|---|---|---|
| `work_data.department` (nama) | terisi penuh | `icc_account_mappings.team`, `icc_leaders.team`, `icc_affiliate_accounts.team`, header `BIP-Department`, isolasi data SPV |
| `marketing_teams` + `team_shops` | **3 tim** (`aris`, `BH`, `GB-KY`), **1 anggota**, **5 toko** (2 TikTok, 3 Shopee) | saringan divisi & penanggung jawab toko di [[Microservices - Marketing Analytics Service]] |
| `IncentiveOrg` (TIM ADE / TIM RIDO) | **koleksinya tidak ada** di `insentive_db` | rollup insentif (kode ada, data tak pernah diisi) |

Nama di `marketing_teams` membuktikan ia bukan department: `GB-KY` adalah gabungan dua brand, dan `aris` adalah nama orang yang dijadikan tim.

### Pondasi yang sudah dibangun tetapi mati suri

`integration_db.department_shops` **sudah ada** berikut entitas, endpoint (`GET/POST/DELETE /department-shops`), dan laporan kesehatan (`GET /department-shops/kesehatan` — toko yatim & pemetaan sisa). Semantiknya persis yang dibutuhkan: **satu toko milik satu departemen**, ditegakkan index unik `(channel, shop_id)`, dengan alasan yang ditulis di entitasnya — satu toko yang dimiliki dua departemen membuat omzetnya terhitung dua kali dan menaikkan skor dua supervisor sekaligus.

Kenyataannya: **0 dokumen, tanpa UI, tanpa satu pun pembaca**. Ia terbangun tetapi tak pernah tersambung — dan karena tak terdokumentasi di vault, orang berikutnya hampir pasti membangun sumber keempat.

### Empat fakta yang membentuk keputusan ini

1. **Kunci yang dipakai adalah NAMA, bukan key.** `MasterDepartment` **sudah punya** field `Key` stabil, tetapi `work_data.department` dan seluruh `icc_*.team` menyimpan namanya. Ini persis kelemahan yang [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] selesaikan untuk posisi lewat `PositionKey`: tanpa key stabil, rename memutus kaitan tanpa jejak.
2. **Kopling nama sudah terbukti membusuk di sini.** 2026-08-07 ditemukan **12 mapping aktif** tersimpan sebagai `team: "Tech Development"` — department akun IT yang meng-assign, bukan department karyawannya. Akibatnya SPV Kyura dan Beauty Hacks tidak menemukan datanya sama sekali, karena daftar mereka disaring `?team=`. Sudah diperbaiki, tetapi membuktikan kelas kegagalannya nyata.
3. **Mencabut Teams begitu saja merusak dua hal.** `team_shops` adalah **satu-satunya sumber Shopee** untuk kolom penanggung jawab toko (3 dari 5 barisnya Shopee), dan `marketing_teams` memasok **saringan divisi** yang juga dipakai halaman Affiliate. `icc_account_mappings` punya `shopee_shop_id`, tetapi **kosong di seluruh baris aktif**.
4. **Ada tiga ruang-nama string yang mudah tertukar**: nama department (`"Kyura"`), kode modul `system_roles` (`"kyura"` — bukan nama departemen, pemetaannya di `deptKeyToNames`), dan nama tim bebas (`"GB-KY"`).
5. **Sumber insentif sudah tidak dirawat** (dikonfirmasi pemilik fitur 2026-08-11). `insentive_db.employee_performance_mappings` berisi **3 dokumen**, seluruhnya dibuat **10 Juli 2026** dengan `updated_at` sama persis dengan `created_at` — tak pernah disentuh sejak dibuat. Saat fitur ICC dibangun, yang dipinjam dari modul insentif sebenarnya hanya **nama peran posisi** (`adv_leader`, `adv_marketplace`, `icc`), bukan datanya. Arah yang benar justru sebaliknya: insentif yang mengambil dari sini.

### Inventaris nyata yang harus dimigrasi (2026-08-11)

Seluruh `team_shops` ternyata milik **satu tim** — `aris`, nama SPV Beauty Hacks. Tim `BH` dan `GB-KY` **kosong** (nol toko, nol anggota), jadi keduanya tinggal dihapus tanpa migrasi.

| Toko | `shop_id` | Bukti | Divisi |
|---|---|---|---|
| TIKTOK `Beautyhack's` | `7494710464840632749` | Satrio Jatmiko — `icc_account_mappings` | **Beauty Hacks** (diturunkan) |
| TIKTOK `Beautyhacks.store` | `7495537364189547259` | tak ada bukti sah | **Beauty Hacks** (keputusan pemilik) |
| SHOPEE `Beautyhack's Original Shop` | `940147456` | tak ada bukti sah | **Beauty Hacks** (keputusan pemilik) |
| SHOPEE `Beautyhacks Official Shop` | `908963392` | tak ada bukti sah | **Beauty Hacks** (keputusan pemilik) |
| SHOPEE `Bumble beauty` | `823286268` | tak ada bukti sah; namanya bukan brand yang dikenali | **Beauty Hacks** (keputusan pemilik) |

Keempat baris terakhir **diputuskan pemilik fitur pada 2026-08-11**, bukan diturunkan dari data. Dicatat begitu supaya pembaca berikutnya tahu mana yang berbukti dan mana yang berdasar wewenang — `Bumble beauty` khususnya, karena namanya tidak menunjukkan brand mana pun dan akan terus memancing pertanyaan.

`Beautyhacks.store` sempat terbaca sebagai konflik — namanya Beauty Hacks, pemegangnya Ridho Feldiansyah yang justru **leader Kyura**. Setelah sumber insentif dinyatakan basi, konflik itu bubar: yang tersisa bukan pertentangan bukti, melainkan ketiadaan bukti — lalu diisi oleh keputusan pemilik.

### Yang ikut termigrasi dari `icc_account_mappings`

Memindahkan `team_shops` saja **tidak cukup**: kelima tokonya semua Beauty Hacks, sehingga Kyura akan berakhir tanpa satu pun toko terpetakan padahal 10 tokonya sudah punya pemegang. Karena itu penyemaian `department_shops` mengambil **dua sumber sekaligus**, memakai aturan berjenjang yang sama:

| Sumber | Toko | Hasil |
|---|---|---|
| `icc_account_mappings` (department pemegang) | 12 | Kyura 10, Beauty Hacks 2 |
| `team_shops` (keputusan di atas) | 5 | Beauty Hacks 5 |
| **Gabungan unik** | **16** | 1 tumpang tindih (`7494710464840632749`), **kedua sumber sepakat Beauty Hacks** |

16 pemetaan jauh di atas 5, sehingga penyemaian ini **menaikkan** cakupan alih-alih mengancamnya — sekaligus menutupi dua toko yang selama ini hanya ditopang sumber insentif, yang jadi syarat pencabutannya (keputusan #9).

## Decision

**Satu identitas tim untuk seluruh data marketing: DEPARTMENT, dengan `department_key` sebagai kunci.**

1. **Kunci identitas = `department_key`** (slug stabil dari `MasterDepartment.Key`). Nama department tetap disimpan **hanya untuk tampilan**, tidak pernah dipakai mencocokkan. Alasannya sama dengan `PositionKey` di [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]].
2. **Kode modul `system_roles` DILARANG dipakai sebagai kunci identitas tim.** Ia menyatakan hak akses modul, bukan unit organisasi.
3. **Kepemilikan toko = `department_shops`** (satu toko satu departemen). `marketing_teams` dan `team_shops` dipensiunkan setelah pembacanya pindah.
4. **Penugasan orang → akun toko = `icc_account_mappings`** (satu toko satu pemegang aktif). Ini pertanyaan **berbeda** dari kepemilikan divisi dan tetap terpisah.
5. **Kepemilikan akun affiliate = `icc_affiliate_accounts`**, `employee_id` opsional (kosong = belum ditugaskan, bukan akun luar). Lihat [[Sales - ICC Affiliate Mapping]].
6. **Keanggotaan tim TIDAK disimpan di mana pun** — diturunkan dari `work_data.department`. `team_members` (1 baris) dibuang.
7. **Sub-tim di dalam divisi DITOLAK untuk sekarang.** Bila kelak dibutuhkan, bentuknya wajib entitas tim ber-ID stabil **dengan induk `department_key`** — bukan nama bebas seperti `marketing_teams`. Syarat memperkenalkannya: ada lebih dari satu tim nyata dalam satu divisi yang perlu dibedakan atribusinya, dan pemiliknya bersedia merawat datanya.
8. **Migrasi wajib expand → migrate → contract**, dengan gerbang cakupan (lihat §Migrasi). Big-bang swap dilarang.
9. **Arah ketergantungan dibalik: Integration jadi sumber, Insentif jadi konsumen.** `insentive_db.employee_performance_mappings` **berhenti** dipakai sebagai sumber penanggung jawab toko; modul insentif yang mengambil dari `icc_account_mappings` + `department_shops`, bukan sebaliknya. Yang tetap dipinjam dari modul insentif hanyalah **nama peran** (`adv_leader`, `adv_marketplace`, `icc`) yang sudah menempel di `system_roles` — itu kosakata, bukan data kepemilikan.

> **Pencabutan sumber insentif punya urutannya sendiri.** Ia menyumbang 2 toko ke cakupan 51,2%, dan salah satunya (`Beautyhacks.store`) **belum punya pemegang di `icc_account_mappings`**. Melepasnya sebelum ICC menutupi kedua toko itu akan menurunkan cakupan — persis yang dilarang gerbang di §Migrasi. Urutannya: isi di ICC dulu, verifikasi, baru lepas.

### Alternatif yang ditolak: ICC sebagai satu-satunya sumber

Ditanyakan pemilik fitur 2026-08-11: kalau ICC Management sudah punya datanya, kenapa tidak cukup satu sumber dan `department_shops` dihapus saja?

Ditolak karena **ICC menjawab pertanyaan yang berbeda dan secara struktural tak dapat menampung jawabannya**: `POST /icc/mappings` menolak dengan `employee_id is required`, sehingga toko yang **belum ada pemegangnya tidak dapat dicatat di sana sama sekali**. Empat dari enam belas toko hari ini persis dalam keadaan itu — tiga Shopee dan `Beautyhacks.store`.

Menyandarkan kepemilikan divisi pada penugasan orang juga membuatnya **hilang setiap kali pemegangnya kosong** — rotasi, resign, atau cuti panjang. Omzet toko itu lepas dari atribusi sampai ada pengganti, tanpa satu pun tanda bahwa sesuatu hilang. Itu kelas kegagalan yang sama dengan yang sudah kita tolak untuk akun affiliate, dan alasannya sama: *belum ditugaskan bukan berarti bukan milik kita*.

**Penyemaian dua sumber bukan dua sumber permanen.** Ia sekali jalan; setelahnya hanya ada satu tempat mengisi — kartu team di ICC Management — dengan `department_shops` sebagai penyimpanannya, bukan sebagai menu kedua.

### Aktor dan wewenang

Tidak ada gerbang baru yang diciptakan ADR ini; semuanya memakai yang sudah ada.

| Aktor | Boleh | Gerbang | Sumber data |
|---|---|---|---|
| **Staff ICC** | melihat performa akun **miliknya sendiri** | tanpa `RequireMarketingLeader`; disaring `BIP-Employee-ID` | `GET /icc/mappings/me` |
| **Leader team** (posisi leader / `insentive: adv_leader`) | set/ganti leader, assign akun, kelola akun affiliate **teamnya** | `RequireMarketingLeader` | `/icc/*` |
| **SPV divisi** (`kyura`/`beauty_hacks`: supervisor·admin) | idem, terbatas teamnya | `RequireMarketingLeader` | `/icc/*`, disaring `?team=` |
| **Integration staff** | **melihat** kepemilikan toko + laporan kesehatan | `RequireIntegrationStaff` | `GET /department-shops`, `/kesehatan` |
| **Integration admin** | **mengubah** kepemilikan toko | `RequireIntegrationAdmin` | `POST`/`DELETE /department-shops` |
| **IT member** | super-akses lintas team | `RequireMarketingLeader` (memuat `it`) | semua di atas |
| **Pembaca Marketing Analytics** | membaca laba & performa | `bolehLihatMarketingAnalytics` = modul `integration` **atau** marketing leader | `marketing-analytics/*` |

**Gerbang tulis kepemilikan toko tetap `RequireIntegrationAdmin` walau UI-nya pindah ke ICC Management.** Memindahkan tombol tidak boleh diam-diam melebarkan hak: `RequireMarketingLeader` jauh lebih luas, dan kepemilikan toko menentukan ke divisi mana omzet dihitung.

```mermaid
flowchart TD
    A["Staff ICC"] -->|lihat akun sendiri| G1{"BIP-Employee-ID"}
    B["Leader / SPV divisi"] -->|set leader, assign akun,<br/>kelola akun affiliate| G2{"RequireMarketingLeader"}
    C["IT member"] --> G2
    D["Integration admin"] -->|ubah kepemilikan toko| G3{"RequireIntegrationAdmin"}
    E["Integration staff"] -->|lihat kepemilikan + kesehatan| G4{"RequireIntegrationStaff"}

    G1 --> M1["icc_account_mappings<br/>(milik sendiri)"]
    G2 --> M1
    G2 --> M2["icc_leaders"]
    G2 --> M3["icc_affiliate_accounts"]
    G3 --> M4["department_shops"]
    G4 --> M4

    M1 --> MA["Marketing Analytics"]
    M3 --> MA
    M4 --> MA
    MA --> F{"bolehLihatMarketingAnalytics"}
    F --> V["Halaman laba & Affiliate"]
```

### Peta data: dari toko dan akun sampai layar

Empat pertanyaan berbeda, empat koleksi, tanpa tumpang-tindih:

| Pertanyaan | Koleksi | Kardinalitas | Diisi lewat |
|---|---|---|---|
| Toko ini **milik divisi mana**? | `department_shops` | 1 toko → 1 departemen | ICC Management (kartu team) |
| Toko/iklan ini **dipegang siapa**? | `icc_account_mappings` | 1 toko → 1 pemegang aktif | ICC Management → tab Toko & Iklan |
| Divisi ini **leadernya siapa**? | `icc_leaders` | 1 team → 1 leader aktif | ICC Management → Set Leader |
| Akun affiliate ini **milik siapa**? | `icc_affiliate_accounts` | banyak ↔ banyak, pemegang opsional | ICC Management → tab Akun Affiliate |

```mermaid
flowchart LR
    subgraph SUMBER["Diisi manusia (ICC Management)"]
        DS["department_shops<br/>toko → divisi"]
        MAP["icc_account_mappings<br/>karyawan → toko/iklan"]
        LEAD["icc_leaders<br/>divisi → leader"]
        AKUN["icc_affiliate_accounts<br/>username + alias → karyawan"]
    end

    subgraph OTOMATIS["Sinkron otomatis dari marketplace"]
        ORD["transaction_orders"]
        AFF["affiliate_orders<br/>creator_username"]
    end

    HRIS["work_data.department<br/>+ MasterDepartment.Key"] -->|identitas tim| DS
    HRIS --> MAP
    HRIS --> LEAD
    HRIS --> AKUN

    DS -->|saringan divisi| MA["Marketing Analytics<br/>(baca-saja integration_db)"]
    DS -->|kepemilikan Shopee| MA
    MAP -->|penanggung jawab toko| MA
    AKUN -->|kolom Pemegang| MA
    ORD --> MA
    AFF --> MA

    MA --> H1["Laba per toko / produk / iklan<br/>kolom penanggung jawab"]
    MA --> H2["Affiliate<br/>Golongan + Pemegang"]
```

**Dua sumbu di halaman Affiliate yang sering tertukar, dan tidak boleh disatukan:**

- `collaboration_type` — sifat **order**-nya: target collaboration (kita undang) vs open collaboration (kreator datang sendiri). Datang dari TikTok.
- `kepemilikan` — siapa **karyawan** di balik username. Datang dari `icc_affiliate_accounts`.

Persilangan keduanya yang bernilai: akun kita yang ordernya masih open collab berarti belum didaftarkan target collab di toko itu; username tak terdaftar yang ordernya target collab adalah kandidat akun internal yang belum didata.

## Migrasi

Urutannya mengikat. Mencabut lebih dulu tidak menghasilkan error — hanya kolom yang diam-diam kosong.

1. ✅ **Expand** — tambahkan `department_shops` sebagai sumber **tambahan** di `penanggung_jawab.go` dan `divisi.go`, mengikuti pola `indeksICCGabungan` yang sudah berlaku: *sumber menambah, tidak menimpa*; satu sumber gagal, sumber lain tetap dipakai. Selama fase ini `team_shops` tetap hidup, sehingga mengisi koleksi baru tidak dapat merusak apa pun.
2. ✅ **Migrate** — pindahkan 5 baris `team_shops` ke `department_shops`, memakai `shop_id` + `channel` (**bukan** nama toko: nama di produksi ada yang berspasi di ujung dan ada yang beda hanya huruf besar-kecil). Tim `BH` dan `GB-KY` kosong → hapus tanpa migrasi. Tim `aris` (nama SPV Beauty Hacks) memegang kelimanya; divisinya ditentukan **per toko** lewat aturan berjenjang di bawah, bukan dari nama timnya.
   1. Ada pemegang di `icc_account_mappings` → pakai department pemegang. (1 dari 5 toko)
   2. Tidak ada → **keputusan manusia**, dan pertanyaannya bukan "siapa yang mengerjakan" melainkan **omzet toko ini dihitung sebagai capaian divisi mana**. Mengerjakan iklan sebuah toko tidak sama dengan memiliki omzetnya.
   3. Sumber insentif **tidak dipakai** sebagai bukti (keputusan #9).
   4. Toko yang benar-benar tak bisa diputuskan **dibiarkan kosong**, muncul sebagai yatim di `/kesehatan`. Pemetaan kosong yang terlihat lebih baik daripada pemetaan salah yang terlihat benar.
   5. Semai **juga** dari `icc_account_mappings` (department pemegang), bukan dari `team_shops` saja — lihat §Yang ikut termigrasi. Hasilnya 16 pemetaan, bukan 5.
   6. **Pasca-seeding, cakupan terus tumbuh lewat entri manual** (bukan penyemaian ulang): 58 dari 59 toko terpetakan per 2026-08-27 (satu yatim: `Series Glowbooster`), drift `Menyimpang` nol. Tabel inventaris §"Inventaris nyata" di atas mencerminkan keadaan awal 2026-08-11, bukan keadaan kini.
3. ✅ **Gerbang** — cakupan penanggung jawab toko **tidak boleh turun** dari **51,2% (15 toko)**. Verifikasi lewat `/department-shops/kesehatan` (toko yatim & pemetaan sisa). Gagal memenuhi ini = migrasi belum selesai, bukan alasan melanjutkan. Terpenuhi jauh di atas ambang (§6 di atas).
4. 🟡 **Contract — SEBAGIAN.** Baru **saringan `/divisi`** (`services/marketing-analytics/divisi.go`) yang pindah sepenuhnya ke `department_shops` sebagai sumber tunggal (bip-erp PR [#1520](https://github.com/bip-itteam-internal/bip-erp/pull/1520) & [#1522](https://github.com/bip-itteam-internal/bip-erp/pull/1522), erp-frontend PR #1305 — merged 2026-08-29, **belum di-deploy/diverifikasi lewat gateway**). **BELUM dikerjakan, ditunda sadar ke rencana terpisah (keputusan user 2026-08-27)**: kolom penanggung jawab toko (`icc` / blok "per tim" di `/beranda`, `penanggung_jawab.go`) **masih membaca `team_shops`+`marketing_teams`** apa adanya. Karena konsumen itu belum pindah, `marketing_teams`, `team_shops`, `team_members`, dan menu `/integration/teams` **belum bisa dicabut** — mencabutnya sekarang akan mematikan kolom penanggung jawab, persis risiko yang diperingatkan §Consequences.
5. ⛔ **Kunci stabil — belum dimulai.** Pencocokan divisi pada saringan `/divisi` masih murni **nama** (trim + huruf kecil, lihat `indeksDivisiDariDepartmentShops`), bukan `department_key`. `department_shops` sendiri belum punya kolom key. Selama ini terbuka, kelas kegagalan "Tech Development" (§2) tetap mungkin terjadi di jalur ini juga.

**Laporan ketidakcocokan wajib permanen di layar**, bukan pemeriksaan sekali jalan — entitas `department_shops` sendiri mensyaratkannya. Dua pemeriksaan yang saling menguatkan: toko terotorisasi yang belum dipetakan (`/kesehatan`), dan departemen toko yang berbeda dari department pemegangnya di `icc_account_mappings`.

## Consequences

**Diterima:**

- **Satu menu hilang (Teams).** Yang tersisa dari fungsinya — pemetaan toko → divisi — pindah ke kartu team ICC Management, yang memang sudah per-departemen.
- **Nilai saringan divisi berubah** dari nama tim bebas jadi nama departemen. Tautan atau bookmark yang menyimpan nilai lama berhenti cocok.
- **Tim lintas-brand seperti `GB-KY` tidak lagi dapat dinyatakan** sampai keputusan #7 dibuka. Ini pembatasan sadar, bukan kelalaian.
- **Kopling antar-service tetap longgar**: `department_shops` menyimpan nama/kunci departemen milik employee-service, bukan referensi keras. Itu sebabnya laporan ketidakcocokan jadi bagian wajib fitur, bukan tambahan.
- **Sinkronisasi identitas menuntut disiplin rename.** Mengganti nama departemen di HRIS harus diikuti pemeriksaan kesehatan; dengan `department_key` dampaknya hilang, tanpa itu tetap ada.

**Risiko utama:** mencabut `team_shops` sebelum pembacanya pindah akan mengosongkan saringan divisi **dan** menghapus satu-satunya kepemilikan toko Shopee. Gejalanya bukan halaman error, melainkan kolom yang berbunyi "belum ditetapkan" — terbaca seperti pekerjaan tim yang belum selesai, bukan seperti regresi yang kita sebabkan. Gerbang cakupan di §Migrasi ada khusus untuk menangkap ini.

**Yang TIDAK diputuskan di sini:**

- **Migrasi permission-set modul `integration`** — modulnya belum berkatalog dan [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] menempatkannya paling akhir karena 241 rutenya belum tergerbang. Selama itu, gerbang di tabel aktor tetap memakai `system_roles`.
- **Struktur tim untuk insentif** (`IncentiveOrg`) — ranah modul insentif; koleksinya belum pernah terisi di produksi.
- **Pengisian `shopee_shop_id` di `icc_account_mappings`** — pekerjaan data tim marketing, bukan perubahan kode.

## Dokumen Terkait

- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] — asal pelajaran "tanpa key stabil, rename memutus akses tanpa jejak"
- [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]] — jembatan sementara peran dari jabatan; tidak diubah ADR ini
- [[ADR - 0002 Database-per-Service]] — dasar pembacaan lintas-database baca-saja
- [[Microservices - Integration Service]] — pemilik `department_shops`, `icc_*`, `marketing_teams`
- [[Microservices - Marketing Analytics Service]] — konsumen; cakupan penanggung jawab & saringan divisi
- [[Sales - ICC Account Manager Mapping]] · [[Sales - ICC Affiliate Mapping]] — fitur yang memakai identitas tim ini
