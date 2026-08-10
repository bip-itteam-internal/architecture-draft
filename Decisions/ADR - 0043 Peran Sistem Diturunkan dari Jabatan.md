**Status**: ✅ Implemented (dev, 2026-08-09). Tabel `services/employee/peran_dari_jabatan.go` mengisi `system_roles` yang kosong dari (departemen, jabatan) di keempat jalur penerbitan token. Menyentuh 13 akun Manufaktur/Quality, 11 akun Beauty Hacks/Kyura, 1 akun General Affair, dan 1 akun Kesekretariatan. Sakelar `ROLE_FROM_POSITION=off`. **Jembatan sementara**, bukan pengganti [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]].

## Context

[[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] menetapkan hak menempel pada posisi lewat permission-set. Jalan itu benar, tapi menuntut modulnya berkatalog lebih dulu — dan dua modul yang paling banyak dikeluhkan justru **sudah punya pembedaan per pekerjaan yang halus dan sudah ditegakkan**, hanya saja bukan lewat katalog:

- **`manufacture`** — `MATRIKS_TAB_WMS` (`erp-frontend/src/features/manufacture/akses.ts`) dengan enam peran granular (`admin_gudang_rm`, `admin_gudang_fg`, `admin_produksi`, `ppic`, `qc`, `supervisor`), dicerminkan **per-endpoint** di `services/manufacture/rbac.go`. Keputusan pengelola 17 Juli 2026.
- **`insentive`** — nilai perannya sendiri sudah berbentuk pekerjaan: `icc`, `host_live`, `crm`, `affiliate`, `adv_meta`, `adv_marketplace`, `adv_leader`, `supervisor`.
- **`ga`** — dua nilai yang **berbeda jenis, bukan bertingkat**: `staff|supervisor|admin` membuka Asset Management (`RequireGeneralAffair`), sedangkan `security` membuka buku tamu (`RequireSecurity`, `RequireGuestbookRBAC`) dan **sengaja di luar** daftar yang pertama.

Pemeriksaan data dev 2026-08-09 menunjukkan **yang rusak bukan aturannya melainkan datanya**. Peran itu dipasang satu per satu ke akun, dan pemasangannya tak pernah tuntas:

| Departemen | Temuan |
|---|---|
| Manufaktur & Quality | Dari 22 akun hanya 9 yang memegang peran WMS — dan **kesembilannya akun uji** (`*.test`). Tak satu pun karyawan sungguhan punya akses WMS, termasuk seluruh Leader Production (4), QC Production (3), dan separuh PPIC. |
| Beauty Hacks & Kyura | 11 akun tanpa peran (4 Host Live, 3 ICC, sisanya Customer Support/Marketplace Advertiser/Meta Advertiser/SPV), plus 3 akun bernilai keliru. |
| General Affair | Paling rapi: 7 dari 8 Security sudah ber-`ga: security`, hanya 1 GA Staff yang tertinggal. Sisanya (Admin, Legal Staff, 4 Office Boy) memang tanpa peran. |
| Kesekretariatan | **Pembalikan paling tajam di seluruh data.** Direktur sungguhan (`widi`) tak punya satu pun peran, sementara seorang Personal Assistant (`okyfirman`) memegang TUJUH termasuk `group: admin` dan `it: supervisor` — super-akses ke seluruh menu. Personal Assistant yang satunya tak punya apa pun. |

Membangun katalog izin untuk kedua modul berarti **menyalin aturan yang sudah ada ke bentuk kedua** yang harus dijaga tetap sama selamanya — matriks WMS saja 400 baris, dan ia sudah punya cerminan backend yang wajib sinkron. Menambah bentuk ketiga melipatgandakan permukaan yang bisa menyimpang.

## Decision

**Peran sistem yang KOSONG diisi dari jabatan saat token diterbitkan.**

Satu tabel `departemen → jabatan → modul → nilai peran` (`services/employee/peran_dari_jabatan.go`), dipanggil di **keempat** jalur penerbitan token (login, PIN, biometrik, refresh). Karena penurunannya terjadi di titik itu, frontend maupun backend ikut benar sekaligus: keduanya membaca `system_roles` yang sama dari header yang distempel gateway. Nol gerbang disentuh.

Empat aturan yang mengikat:

**1. Tak pernah menimpa, dinilai PER MODUL.** Pengelola kadang sengaja memberi seseorang peran berbeda dari jabatannya; menimpanya berarti mencabut keputusan itu tanpa jejak. Penilaian per modul juga yang membuat kasus campuran tertangani benar — seorang Meta Advertiser Kyura yang memegang `kyura: staff` (keliru) **dan** kehilangan peran insentifnya kini menerima `adv_meta` yang hilang, sementara peran keliru itu dibiarkan untuk diputuskan manusia. Membedakan "salah isi" dari "sengaja dibedakan" bukan urusan kode.

**2. Hanya untuk peran yang menentukan AKSES, bukan perhitungan.** `insentive` lolos syarat ini karena `services/insentive` **tak membaca `system_roles` sama sekali** — keanggotaan tim insentif datang dari data tim — sehingga penurunan ini tak menyentuh perhitungan uang siapa pun. Syarat ini wajib diperiksa ulang untuk tiap modul berikutnya, dan ditulis sebagai pagar di berkas implementasinya.

**3. Jabatan yang ambigu TIDAK ditebak.** Menebak berarti melebarkan hak diam-diam: arah kesalahan yang tak punya gejala sama sekali.

**4. Bentuk kanonik yang dipakai adalah `common.KanonPosisi`** — sama dengan `positionSetKeys` dan `/me/menu-hidden`. Membuatnya lebih longgar berarti satu jabatan bisa cocok di satu tempat dan tidak di tempat lain, yaitu kelas bug yang justru sedang diperbaiki. Batas itu dikunci uji.

Sakelar `ROLE_FROM_POSITION=off` mengembalikan perilaku lama tanpa deploy kode.

### Yang sengaja tidak dipetakan

| Departemen | Jabatan | Alasan |
|---|---|---|
| Manufaktur | Operator Production, Warehouse Staff | matriks memang menetapkan mereka tanpa akses WMS |
| Manufaktur | Admin Warehouse, Warehouse Leader | gudangnya RM atau FG tak bisa disimpulkan dari nama jabatan |
| Quality | Quality Supervisor | `supervisor` di modul `manufacture` berarti SELURUH akses WMS, jauh melebihi pengawasan mutu |
| Beauty Hacks | Buzzer | bukan salah satu peran insentif yang ada; satu Buzzer hari ini memegang `icc` dan itu membuka dasbor yang bukan pekerjaannya |
| Beauty Hacks, Kyura | Video Editor, Videographer | tak punya padanan peran insentif |
| Kyura | `?` | jabatan kosong di data (3 akun) |
| General Affair | GA Supervisor | jabatan yang **ditinggalkan** setelah penggabungan HRGA; memetakannya berarti menghidupkannya kembali |
| General Affair | Admin, Legal Staff | nama jabatannya tak menyatakan kewenangan GA; `Legal Staff` lebih dekat ke modul `legal` yang belum ada di `main` |
| General Affair | Office Boy | dasbornya datang dari preset per-JABATAN (`features/hris/dashboard/lib/position-view.ts`), bukan dari peran — jadi ia memang tak perlu `system_roles` |
| General Affair | Bootcamp Content Creator | tak ada satu pun pemegangnya di data |
| Kesekretariatan | Personal Assistant | dua pemegangnya berada di dua ujung ekstrem (7 peran vs nol); menurunkan salah satunya berarti memilih tanpa dasar |
| Kesekretariatan | Administrative | pemegangnya memang ber-`secretary: staff`, tapi menurunkannya akan memunculkan kategori lalu ditolak backend — lihat di bawah |
| Kesekretariatan | Company Branding, Graphic Design, Video Editor | pekerjaan kreatif tanpa padanan modul ERP mana pun |

`integration` juga tidak diturunkan untuk atasan brand walau satu SPV Beauty Hacks hari ini memegangnya: peran itu membuka kategori Integration dengan 26 menu, jauh melebihi apa pun yang bisa disimpulkan dari nama jabatan "supervisor brand".

### `secretary: staff` sengaja tak pernah diturunkan

Kategori sidebar `secretary` hanya memuat **satu** menu (`/secretary/kpi`), dan tak ada satu pun gerbang backend yang membaca `system_roles.secretary` selain peta departemen KPI (`deptKeyToNames`). Peran itu praktis berarti satu hal: boleh melihat KPI departemen Kesekretariatan.

Cabang kedua gerbang KPI lama hanya meloloskan `supervisor`/`admin`. Karena itu `secretary: staff` akan **memunculkan kategorinya di sidebar lalu ditolak backend** saat menu satu-satunya dibuka — persis kegagalan "menu terbuka lalu halaman menolak" yang sedang diberantas di modul lain. Batas itu dikunci uji tersendiri, bukan sekadar dicatat sebagai komentar.

Pelajaran yang berlaku untuk modul berikutnya: **sebelum menurunkan sebuah nilai peran, periksa apakah nilai itu benar-benar diloloskan gerbangnya** — bukan sekadar apakah nilai itu ada di data.

### Penggabungan HRGA, dan satu baris yang menunggu master data

General Affair kini bergabung dengan HR menjadi **HRGA** (keputusan organisasi, 2026-08-09). Frontend sudah lebih dulu memperlakukan keduanya satu rumpun lewat `MODUL_HRGA = ["hris", "ga"]`, jadi penggabungan ini **tak mengubah kategori sidebar** — yang berubah daftar jabatannya: tak ada lagi supervisor di sisi GA, puncaknya kini **Leader**.

Tabel ini memetakan `Leader → ga: supervisor`. Nilai perannya tetap `supervisor` karena itulah yang dikenali `RequireGeneralAffair` dan `RequireGuestbookRBAC`; yang berubah nama jabatannya, bukan tingkat kewenangannya.

⚠️ **Baris itu belum berefek.** `master_department` General Affair masih memuat `GA Supervisor`, bukan `Leader`. Pemetaan sengaja dipasang lebih dulu supaya penggantian nama nanti tak perlu dibarengi perubahan kode. Dua langkah yang menunggu HR, dan yang kedua mudah terlewat:

1. Ganti nama jabatan **GA Supervisor → Leader**.
2. **Pindahkan paket `kpi_divisi`** yang kini menempel pada `GA Supervisor`. Tanpa itu, cakupan KPI sisi GA hilang tanpa satu pun galat — dan **KPI tetap per-departemen meski departemennya digabung** (keputusan pengelola), jadi Leader memang harus memegang cakupannya sendiri.

## Consequences

**Yang membaik.** 26 karyawan mendapat akses yang sesuai jabatannya tanpa satu gerbang pun berubah. Karyawan baru di jabatan yang terpetakan otomatis benar sejak login pertama — sebelumnya menunggu seseorang ingat memasang perannya. Dan karena tabelnya satu, "jabatan ini dapat peran apa" jadi pertanyaan yang bisa dijawab dengan membaca satu berkas.

**Yang memburuk, dan ini nyata.** Sekarang ada **dua** sumber `system_roles`: yang tersimpan di akun dan yang diturunkan dari jabatan. Dokumen `system_authentication` di database tak lagi menceritakan seluruh kebenaran, sehingga siapa pun yang memeriksa akses lewat database saja akan salah menyimpulkan. Penawarnya endpoint audit `GET /master/peran-jabatan` dan panel **Peran vs Jabatan** — keduanya membaca hasil akhir, bukan data mentah.

**Ini jembatan, dan jembatan harus dibongkar.** Begitu `manufacture` dan `insentive` berkatalog sesuai [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]], hak keduanya pindah ke permission-set yang menempel di posisi, dan tabel ini dicabut. Membiarkannya hidup berdampingan dengan katalog akan menghasilkan dua sumber hak yang bisa menyimpang — persis keadaan yang ADR 0030 hendak akhiri.

**Anomali tidak ikut tertutup.** Tiga akun marketing bernilai keliru (`Rifki` Affiliate memegang `icc`; `Annisa` dan `priyastama` ICC memegang `crm`) tetap keliru — aturan tak-menimpa memang tak menyentuhnya. Itu keputusan pengelola, bukan kode, dan tercatat di sini supaya tidak hilang.

## Terkait

- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] (arah akhirnya; ADR ini jembatan menuju ke sana)
- [[CORE - RBAC dan Permission Set]] (katalog, paket, status penegakan per modul)
- [[Microservices - Employee Service]] (pemilik jalur penerbitan token)
- [[Microservices - Manufacture Service]] (matriks WMS yang dicerminkan) · [[Microservices - Insentive Service]]
- [[HRIS - Organization Structure]] (jabatan & departemen sebagai master data)
- [[APP - Web ERP]] (sidebar membaca `system_roles` hasil akhir)
