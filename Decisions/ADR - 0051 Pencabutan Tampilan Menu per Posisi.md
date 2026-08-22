**Status**: ⚠️ Implemented dan **LIVE di PROD** (2026-08-22), dengan satu sisa: **data belum di-purge**. [erp-frontend #1163](https://github.com/bip-itteam-internal/erp-frontend/pull/1163) (`7f10a099`) dan [bip-erp #1371](https://github.com/bip-itteam-internal/bip-erp/pull/1371) (`e8d94c48`) sudah merge DAN sudah naik ke prod. [erp-frontend #1171](https://github.com/bip-itteam-internal/erp-frontend/pull/1171) (`b66525f5`, pembersihan kode mati) sudah merge tapi **belum ikut naik**; isinya kode mati dan komentar, jadi tak berdampak.

> Diverifikasi di prod 2026-08-22 15:52 WIB, bukan disimpulkan dari status PR. FE: `position-menu-manager.tsx` tak ada lagi di checkout `~/apps/erp-frontend`, container naik dengan image baru. BE: probe biner `docker exec Employee-Service grep -ac 'menu-hidden' /service` = **0**, dengan kontrol positif `permission-sets` = 6 dan `positions` = 6 serta kontrol negatif string karangan = 0; image dibangun 14:11 WIB, sesudah merge.
>
> ⚠️ **`menu_hidden` masih TERSIMPAN di 10 posisi** karena purge belum dijalankan. Tak ada lagi yang membacanya (field-nya sudah lenyap dari model), jadi ia inert. Konsekuensi yang menguntungkan: keadaannya masih bisa dipulihkan seandainya pencabutan ini perlu dibatalkan. Skripnya `.task-plans/purge-menu-hidden.ps1`, dijalankan manusia.

## Context

`master_department.position_items[].menu_hidden` menyimpan url menu yang disembunyikan dari sidebar bagi pemegang sebuah jabatan. Aturannya, dari `components/layout/sidebar-menu-shape.ts`:

	tampil = (boleh menurut role/izin) DAN (tidak ada di menu_hidden)

Ia dijalankan **setelah** seluruh penyaringan izin, jadi secara desain hanya bisa mengurangi dan tak pernah bisa memperluas akses. Itu benar, dan justru itu yang jadi masalahnya.

**Keluhan yang memicu keputusan ini:** paket hak yang sudah dipasang ke sebuah jabatan tidak pernah terlihat. Sah menurut desain (gerbang AND), tetapi tak terbaca sebagai desain oleh yang mengalaminya, karena kedua setelan itu diurus di dua layar berbeda dan tak ada apa pun yang menyebut keterkaitannya.

**Pengukuran prod 2026-08-22** menunjukkan pemakaiannya jauh dari yang dibayangkan saat fitur dibuat. Dari 110 posisi, **10** memakai `menu_hidden`, tetapi kesepuluhnya memakainya sebagai **whitelist terbalik**: sembunyikan hampir semuanya, sisakan yang perlu.

| Posisi | Disembunyikan | dari 196 menu | Paket hak |
|---|---|---|---|
| Finance / Senior Accountant | 170 | 87% | kosong |
| Finance / Cost Control | 168 | 86% | kosong |
| Percetakan / ADMIN | 165 | 84% | kosong |
| Percetakan / ACCOUNTING STAFF | 163 | 83% | kosong |
| Beauty Hacks / Leader | 147 | 75% | kosong |
| HR / Training & Perfomance Officer | 136 | 69% | 10 paket |
| HR / Culture & Industrial | 132 | 67% | kosong |
| HR / Recruitment & Onboarding | 129 | 66% | 5 paket |
| HR / Personalia | 119 | 61% | 13 paket |
| HR / HRD Supervisor | 97 | 49% | 12 paket |

Tiga fakta dari data itu yang membentuk keputusan:

- **Ia dipakai sebagai pengganti RBAC, bukan sebagai kerapian tampilan.** Menyembunyikan 87% menu bukan merapikan sidebar, itu mendefinisikan akses lewat sumbu yang sengaja dirancang tidak menegakkan apa pun.
- **Sebabnya RBAC memang belum digelar.** Hanya **10 dari 110 posisi** punya `permission_sets` sama sekali, dan lima dari sepuluh posisi di atas tak punya paket satu pun. `menu_hidden` mengisi kekosongan itu.
- **Hanya 45 dari 196 menu punya tag `perm:`**, jadi permission set hari ini memang belum bisa menggantikannya sepenuhnya. Batas itu diterima sadar, lihat §Consequences.

## Decision

**`menu_hidden` dicabut seluruhnya: kode, kedua layar, kedua endpoint, field model, dan datanya di prod.**

Yang mengatur menu sesudah ini hanya **`permission_sets`** (izin per menu lewat `bolehMenu`, dan pembukaan kategori lewat `kunciModulAktif`) dan **`system_roles`** (kategori sidebar serta gerbang rute di `proxy.ts`, lihat [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]]).

Keputusan turunan:

- **Tidak ada pengganti untuk "menyembunyikan menu yang boleh dilihat".** Kalau sebuah menu tak pantas dilihat sebuah jabatan, jawabannya mencabut izinnya, bukan menyembunyikannya. Menyediakan pengganti berarti mengundang kembali pola whitelist terbalik yang justru dicabut.
- **Rute `/it/settings` dipertahankan sebagai pengalih** ke `/it/hak-akses`, mengikuti pola `rute-lama.ts`. Penanda buku dan tautan lama mendarat di tempat yang benar alih-alih 404.
- **Tab yang hilang wajib meninggalkan jalan.** `PetaNiatOrganisasi` di halaman Organisasi & Jabatan mendapat baris baru yang mengarahkan ke Kelola Permission Sets. Tab yang lenyap tanpa petunjuk adalah bentuk putus yang sudah dicatat di checklist perencanaan, jadi ditutup di perubahan yang sama, bukan di follow-up.
- **`features/hris/master-data/lib/rute-lama.ts` TIDAK ikut dicabut**, walau komentarnya menyebut `menu_hidden`. Ia menangani pengalihan rute lama dan dipakai tujuh halaman. Yang memang hanya ada demi `menu_hidden` adalah `PETA_URL_MENU_LAMA` di `sidebar-menu-shape.ts`, dan itu yang dihapus. Keduanya nyaris tertukar saat perencanaan.

Berkas: `erp-frontend/src/components/layout/{sidebar.tsx,sidebar-menu-shape.ts}` · `erp-frontend/src/features/hris/pengaturan/components/peta-niat-organisasi.tsx` · `bip-erp/services/employee/position_assign.go` · `bip-erp/shared-library/models/employee/master_data.go`.

## Consequences

**Dampak nyata jauh lebih kecil daripada 1.426 entri.** Layar Tampilan Menu melistkan seluruh 196 menu tanpa memfilter peran, jadi sebagian besar entri menyembunyikan menu yang **sudah** tak terlihat lewat `system_roles`. Yang benar-benar akan muncul: **159 kemunculan menu untuk 11 orang**.

Dari 159 itu, **115 adalah menu di modul orang itu sendiri** (HR melihat menu HRIS, Finance melihat menu Finance), dan itu justru hasil yang diinginkan. Sisanya **43 menu lintas modul untuk 2 akun**, dan sebabnya bukan pencabutan ini melainkan `system_roles` yang kelewat lebar:

- `BIP-0222-11-25` (HRD Supervisor) memegang **9 peran** termasuk `group: admin` dan `it: supervisor`
- `BIP-0031-07-23` (Senior Accountant) memegang `finance`, `integration`, `marketing`

`menu_hidden` selama ini **menambal peran yang salah diberikan**. Mencabutnya membuat tambalan itu lepas dan masalah aslinya terlihat, dan itu dianggap perbaikan, bukan kerugian. Pembenahan kedua akun itu menunggu keputusan pengelola; `integration` pada Senior Accountant **tidak** diusulkan dicabut karena Accurate memang sistem akuntansi, dan menebaknya sebagai kesalahan melanggar aturan 3 ADR 0043 (jabatan ambigu tidak ditebak).

**Yang hilang, dan diterima sadar:**

- **Tak ada lagi cara menyembunyikan menu per jabatan.** Untuk 151 menu yang belum punya tag `perm:`, visibilitasnya kini sepenuhnya ditentukan `system_roles` dan tier fallback. Jabatan yang dulu disaring halus lewat `menu_hidden` akan melihat lebih banyak menu daripada sebelumnya.
- **Pekerjaan sebenarnya belum selesai.** Agar permission set benar-benar bisa menggantikannya, cakupan tag `perm:` harus naik dari 45 ke mendekati 196, dan paket harus dipasang ke jauh lebih dari 10 posisi. Itu proyek tersendiri sebesar [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] dan sengaja tidak ditumpangkan ke sini.

⚠️ **Fitur ini masih dipakai orang saat pencabutannya dikerjakan, dan mereka TIDAK sempat diberi tahu.** `Beauty Hacks / Leader` disetel pada **2026-08-22 04:59** oleh `BIP-0205-08-25`, beberapa jam setelah pengukuran awal dan di tengah pengerjaan PR-nya. Angka terdampak bergeser 9 ke 10 selagi task berjalan, dan yang menangkapnya adalah gerbang di skrip purge, bukan orang.

Rencananya menuntut pengumuman lebih dulu; kenyataannya deploy mendahului. Jadi ini **bukan lagi tindakan pencegahan melainkan utang**: sepuluh jabatan kehilangan alat yang baru saja dipakai salah satunya, tanpa pemberitahuan, dan mereka akan melihat sidebar yang lebih ramai tanpa tahu sebabnya. Yang masih bisa dikerjakan tinggal memberi tahu setelahnya, dan menyiapkan jawaban ketika ada yang bertanya kenapa menunya bertambah. Dicatat di sini supaya urutannya tidak terulang, bukan supaya disesali.

**Urutan yang mengikat:** FE dulu, lalu BE, lalu purge data. Terbalik membuat FE lama memanggil endpoint yang sudah tiada. Purge boleh ditunda tanpa risiko karena field yang tak dibaca siapa pun bersifat inert; skripnya `.task-plans/purge-menu-hidden.ps1`, tiga fase dengan `mongodump` wajib, dan **dijalankan manusia** sesuai konvensi rilis.

**Modul `menu` (menu terbatas) tidak disentuh.** Ia mekanisme ketiga yang menyentuh sidebar dan statusnya sengaja belum dinyalakan ([[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]]). Mencampur dua keputusan berbeda dalam satu perubahan akan membuat keduanya sulit dibatalkan sendiri-sendiri.

**Yang belum diputuskan (TBD):**

- **Kapan tag `perm:` diperluas** ke sisa 151 menu, dan apakah itu dikerjakan per modul atau sekaligus.
- **Apakah 5 posisi tanpa paket** (Culture & Industrial, Senior Accountant, Cost Control, dua posisi Percetakan) mendapat paket, dan paket mana. Dua posisi Percetakan bahkan tak punya pemegang, jadi mungkin jawabannya menghapus jabatannya.
- **Pembenahan `system_roles` dua akun di atas** menunggu konfirmasi pengelola per akun.

## Terkait

- [[CORE - RBAC dan Permission Set]] (katalog, paket, dan status penegakan per modul)
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] (arah yang menggantikannya) · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] (dasar bahwa menyembunyikan menu memang bukan keamanan, sehingga pencabutan ini tak menurunkan postur keamanan apa pun)
- [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]] (`system_roles` menentukan kategori sidebar dan lolosnya rute; paket menentukan izin) · [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]] (mekanisme ketiga, tidak disentuh)
- [[Microservices - Employee Service]] (pemilik endpoint yang dicabut) · [[APP - Web ERP]] (sidebar & kedua layar yang dihapus)
