**Status**: ⚠️ Implemented (ada catatan). Kode selesai di branch `feat/oneForAll` (2026-08-06), seluruh uji hijau — **belum merge dan belum deploy**, jadi belum ada satu pun akun yang di-assign. Catatan yang belum tertutup: satu celah pada akun tanpa paket (belum terukur di produksi) dan penegakan backend yang sengaja parsial; keduanya di §Consequences.

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
- **"Sudah ada yang di-assign" adalah fakta GLOBAL**, tak bisa disimpulkan dari klaim satu orang. Employee-service menghitungnya saat token terbit (assignment dari akun **dan** dari posisi, keduanya, karena hak datang dari dua arah menurut ADR 0030) lalu menempelkan **penanda kunci** `$menulock.<kunci>` ke klaim setiap orang. Tanpa penanda itu, konsumen tak bisa membedakan "restriksi belum aktif" dari "aktif tapi saya tak di-assign", dan keduanya menuntut jawaban berbeda.
- **Prefiks penanda sengaja `$menulock.`, bukan `menu.`.** Setiap service menilai "punya izin modul X?" dengan mencocokkan prefiks `X.`; penanda ber-awalan `menu.` akan membuat orang yang justru **tidak** di-assign tampak seperti punya izin modul menu. Pola sama dengan penanda reach (`<modul>.$reach.<level>`) dan penanda akun luar (`account.$type.external`) yang lebih dulu menumpang di klaim yang sama.
- **Aturan tiga langkah**, satu sumber di `common.HasMenuAccess`, dicerminkan frontend di `utils/menu-terbatas.ts`: punya izin → boleh; punya penanda kunci → tolak; selain itu → `fallback` lama. Urutannya tak boleh dibalik, sebab akun yang di-assign juga membawa penanda kunci.
- **`fallback` adalah perilaku yang berlaku SEBELUM menu itu dibatasi**, bukan nilai baru yang dikarang. Di frontend ia cerminan `useFinanceFallback` (role `finance` atau anggota IT); di backend ia `true`, karena endpoint yang digerbangi memang sebelumnya terbuka bagi siapa pun bertoken sah.
- **Tak ada pengecualian super-akses.** IT dan pemegang `finance_admin` tidak otomatis lolos; kalau perlu, mereka di-assign seperti yang lain. Izin `menu.*` juga dijaga uji agar tak pernah bocor masuk paket atau tier finance.

Berkas: `shared-library/common/catalog_menu.go` · `services/employee/menu_terbatas.go` · `services/integration/internal/interface/http/menu_gate.go` · `erp-frontend/src/utils/menu-terbatas.ts` · `erp-frontend/src/components/menu-terbatas-guard.tsx`.

## Consequences

**Konsekuensi yang diterima:**

- **Urutan deploy tak lagi menentukan**, dan restriksinya reversibel tanpa deploy: memasang paket menyalakan, mencabut semua assignment mengembalikan. Ini seluruh alasan bentuk "default terbuka" dipilih.
- **Menyalakan fitur ≠ membatasi.** Sesudah merge, tak ada yang berubah bagi siapa pun sampai pengelola memasang paket. Enak untuk rollout, tapi berarti dokumen ini **tidak** boleh dibaca sebagai "halaman Accounting sudah terbatas".
- **Penanda ikut umur token (72 jam).** Orang yang tokennya masih hidup baru terkunci setelah login ulang, dan akun yang baru di-assign baru bisa masuk setelah login ulang. Pertukaran yang sama dengan seluruh hak di ADR 0030, plus jeda cache 60 detik di sisi penghitung.

**Ranjau yang ditemukan saat perencanaan, dan yang mengubah desain:**

Penanda hanya ditempelkan pada klaim yang **sudah tidak kosong**. Sebabnya konkret: dari empat konsumen klaim izin, tiga (payroll, monitoring, procurement) menilai fallback tier dari "klaim memuat izin **modulnya**", tetapi `effectiveTicketPermissions` di task-management menilainya dari "klaim **ada**" (`len(list) > 0`). Menempelkan penanda ke karyawan yang belum punya paket apa pun akan mengubah klaimnya dari kosong menjadi berisi, dan seluruh hak tiket mereka lenyap tanpa pesan apa pun — kelas kegagalan yang sama yang dulu sengaja dimanfaatkan `account.$type.external` untuk menutup akun vendor.

Konsekuensinya diterima sadar: **karyawan tanpa paket sama sekali tak pernah menerima penanda**, sehingga bagi mereka menu terbatas tetap dinilai dengan fallback lama. Untuk akun yang sudah punya paket — dugaan kuat atas seluruh tim Finance, sebab `finance.accounting.view` dulu terpaksa ditambahkan ke tier staff justru karena klaim mereka sudah berisi — restriksinya berlaku penuh.

**Celah sisa yang BELUM terukur.** Akun ber-`system_roles.finance` yang belum punya paket apa pun akan tetap melihat halaman ini walau restriksi sudah menyala. Ukurannya satu query — berapa akun punya `system_roles.finance` tetapi `permission_sets` kosong — dan query itu **belum dijalankan**: kredensial `erp-analyst` hanya berlaku di Integration DB (32789), sedangkan datanya ada di Employee DB (32783). Kalau hasilnya nol, celahnya kosong dan tak ada yang perlu dikerjakan; kalau tidak, jalan keluarnya memperbaiki task-management jadi per-modul lebih dulu, bukan menambal di sini. Sifat "hanya menumpang klaim tak kosong" dikunci uji, jadi melonggarkannya akan membuat CI merah lebih dulu.

**Penegakan backend sengaja parsial.** Hanya `/accounting/balance-sheet` yang digerbang — satu-satunya endpoint yang eksklusif milik halaman ini. `/accounting/profit-loss` dan `/account-balance` dibiarkan terbuka karena halaman posisi **SPV**, **Tax**, dan **Cost Control** juga memakainya; menggemboknya akan mematikan tiga halaman itu bagi orang di luar whitelist. Artinya ini **kontrol menu, bukan segel data**: angka laba rugi tetap terjangkau lewat halaman posisi bagi yang berhak ke sana. Jangan dibaca sebagai kerahasiaan angka.

Sifat turunan yang disengaja: panggilan service-to-service (worker/cron) tak membawa header izin sama sekali, sehingga selalu jatuh ke `fallback` dan tetap berjalan setelah restriksi menyala.

**Hubungannya dengan `menu_hidden`.** Vault sudah punya mekanisme lain yang menyentuh menu — `position_items[].menu_hidden`, penyembunyian **tampilan** per jabatan yang secara eksplisit bukan keamanan ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]). Keduanya berdampingan dan gampang tertukar; pembedaannya ditabelkan di [[CORE - RBAC dan Permission Set]]. Ringkasnya: `menu_hidden` mengurangi tampilan per jabatan tanpa gerbang, menu terbatas membatasi akses per akun dengan gerbang.

**Yang belum diputuskan (TBD):**

- **Apakah pola ini boleh menggantikan izin modul untuk kasus lain.** Ia sengaja sempit (satu menu, satu paket), dan kalau dipakai berlebihan katalog `menu` akan tumbuh jadi daftar halaman — persis yang ditolak ADR 0030 lewat "satu permission per keputusan akses, bukan per endpoint". Batas pemakaian yang wajar belum dirumuskan.
- **Perilaku saat pemakai membuka URL tanpa hak** masih ikut TBD ADR 0030 (403 informatif vs pengalihan); halaman ini memakai panel "Akses Ditolak" di tempat, tanpa pengalihan.
- **Menutup celah akun tanpa paket** menunggu hasil pengukuran di atas.

## Terkait

- [[CORE - RBAC dan Permission Set]] (katalog modul `menu`, paket, dan pembedaannya dari `menu_hidden`)
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] (fondasi paket & resolusi izin) · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]
- [[Microservices - Employee Service]] (penerbit penanda kunci saat token terbit) · [[Microservices - Integration Service]] (gerbang endpoint) · [[Microservices - Task Management Service]] (konsumen klaim yang memaksa penanda hanya menumpang klaim tak kosong)
- [[APP - Web ERP]] (guard halaman & penyaringan menu) · [[API - Integration Service]] (endpoint yang digerbangi)
