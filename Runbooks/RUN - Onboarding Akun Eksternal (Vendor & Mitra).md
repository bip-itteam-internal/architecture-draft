> **Status**: ⚠️ Implemented (ada catatan) — tahap 1–4 (terbitkan akun → serahkan kredensial → pasang hak → gerbang login) terverifikasi dari kode dan data produksi 5 Agustus 2026. **Tahap 5 (vendor benar-benar masuk ke modulnya) belum pernah terjadi**: sampai dokumen ini ditulis, satu-satunya akun luar di produksi masih `system_roles: {}` tanpa paket hak apa pun. Naikkan ke ✅ setelah pemasangan hak pertama terbukti jalan.

## Tujuan

Menerbitkan akun ERP untuk orang di **luar** perusahaan (vendor, mitra, kontraktor) dan memberinya akses ke modul tertentu — tanpa menjadikannya record karyawan.

## Kapan dipakai

- Mitra gudang, vendor maintenance, atau kontraktor butuh masuk ke sebagian kecil ERP.
- Akun luar yang sudah ada perlu diperpanjang, dicabut haknya, atau ditutup.

**Jangan** dipakai untuk karyawan baru — itu jalur onboarding karyawan ([[Microservices - Employee Service]] §Auth & Registration). Alasan pemisahannya ada di [[Microservices - Employee Service]] §Akun pihak luar: record karyawan menuntut NIK, KK, agama, golongan darah, NPWP, dua nomor BPJS, dan rekening bank — untuk orang luar sebagian besar bukan kebetulan kosong, melainkan memang tak boleh dikumpulkan.

## Prasyarat

- **Role IT supervisor atau admin.** Seluruh grup endpoint digerbang `RequireITSupervisor` — sengaja lebih ketat dari master data lain, karena menerbitkan kredensial untuk orang luar lebih dekat ke *memberi kunci* daripada ke *mengelola data HR*.
- **Nama penanggung jawab internal** yang benar-benar ada sebagai karyawan. Divalidasi ke `work_data`; nama karangan ditolak 400.
- **Tanggal akhir berlaku.** Wajib, dan wajib di masa depan.
- **Kejelasan modul tujuan** — menentukan sumbu hak akses mana yang dipakai (lihat §Memilih Sumbu Hak Akses; ini bagian yang paling sering salah).

## Langkah

Semua lewat Web ERP: **`/hris/master-data` → tab "Akun Eksternal"**. Ditaruh sebagai tab di area HRIS meski digerbang IT, mengikuti pola Kelola Perusahaan.

### 1. Terbitkan akun

Tombol **"Tambah Akun Luar"**. Isi: Nama, Organisasi, Penanggung Jawab (pilih dari daftar karyawan), Berlaku Sampai, Keperluan; Email & Telepon opsional.

ID diterbitkan server berprefiks **`EXT-`** dengan pola `EXT-NNNN-BB-TT` (mis. `EXT-0001-08-26`), mengikuti bentuk ID karyawan. Sistem menulis **dua baris**:

| Koleksi | Isi |
|---|---|
| `external_account` | identitas, organisasi, penanggung jawab, `company_id`, masa berlaku, keperluan |
| `system_authentication` | kredensial, `account_type: external`, `username` = ID akun, `is_active: true`, `has_registered: true` |

Kredensialnya sengaja **menumpang `system_authentication`**, bukan koleksi kedua — supaya login, SSO, device, dan permission-set tetap satu jalur.

> Akun luar terbit **sudah jadi** (`has_registered: true`), beda dari karyawan. Alur onboarding "password sementara lalu pilih username sendiri" cuma ada di aplikasi mobile; web membalas 409 `new_user` yang tak ditangani siapa pun. Vendor tak akan memasang MyBharata, jadi mengarahkannya ke sana berarti menerbitkan akun yang mustahil diselesaikan.

### 2. Catat kata sandi — hanya muncul sekali

Dialog **"Kredensial Akun Vendor"** menampilkan Nama Pengguna + Kata Sandi. Sistem hanya menyimpan **sidik** kata sandinya. Kalau layar ditutup sebelum dicatat, satu-satunya jalan adalah menerbitkan ulang (langkah 6).

Serahkan **langsung** ke vendor. Sistem sengaja tidak mengirimnya lewat email/WhatsApp otomatis: yang menerbitkan yang menyerahkan, sehingga jelas siapa yang bertanggung jawab bila bocor.

### 3. Pasang hak akses — tanpa ini akun tidak bisa apa-apa

Akun yang baru terbit **berhak atas nol modul**. Ini disengaja, bukan kelalaian: sebelum penutupan `izinAkun`, akun vendor tanpa paket apa pun diam-diam mendapat 6 izin ticket lewat fallback tier.

Buka kolom **"Hak Akses"** pada baris akun → dialog **"Hak Akses Vendor"**, yang punya **dua tab**:

- **Paket Hak** → menulis `permission_sets`
- **Role Modul** → menulis `system_roles`

Pilih tab yang benar (§ berikutnya), simpan.

### 4. Serahkan & minta vendor login

Vendor login di `erp.bharatainternasional.com` memakai **ID akun sebagai username**. Login menerima username atau `employee_id`, dan keduanya sengaja disamakan supaya vendor cuma perlu mengingat satu hal.

### 5. Perpanjang / ubah

Tombol **"Perpanjang / Ubah"**. `employee_id` dan `company_id` **tidak bisa** diubah — keduanya kunci identitas dan batas tenant. Field yang dikosongkan diabaikan, bukan menghapus nilai lama.

### 6. Terbitkan ulang kata sandi

Tombol **"Terbitkan Ulang Kata Sandi"**. Kata sandi lama langsung tak berlaku.

> ⚠️ **Jangan pakai `/account/reset` milik karyawan untuk akun luar.** Endpoint itu menyetel `is_active: true` sebagai efek samping, sehingga akan **menghidupkan kembali vendor yang sengaja dinonaktifkan** — persis kebalikan dari yang diinginkan orang yang menekannya. Tombol di tab ini tidak menyentuh `is_active` sama sekali.

Tidak ada "lupa kata sandi" mandiri untuk akun luar, dan memang tak seharusnya ada: pemulihan lewat email berarti mempercayai kotak masuk di luar kendali perusahaan.

### 7. Tutup akses

Tombol **"Nonaktifkan"** → `is_active: false`. **Bukan menghapus** — jejak siapa pernah punya akses harus tetap ada.

⚠️ **Satu arah dari layar ini**: tak ada tombol untuk menyalakannya kembali (lihat §Verifikasi). Kalau yang dimaksud cuma menjeda sementara, pakai **Perpanjang / Ubah** untuk memundurkan masa berlakunya. Dan ingat token yang sudah beredar tetap hidup sampai 72 jam — ini menutup pintu masuk berikutnya, bukan sesi yang sedang berjalan.

## Memilih Sumbu Hak Akses (Paket Hak vs Role Modul)

**Ini bagian yang paling sering salah.** Tiap modul menggerbang pada **salah satu** sumbu, dan mencentang di sumbu yang salah **tidak menghasilkan galat apa pun** — cuma vendor yang tetap tak bisa masuk, dan pemasangnya menyangka sudah memberi akses.

| Sumbu | Menulis ke | Dibaca modul | Isi di produksi (5 Agu 2026) |
|---|---|---|---|
| **Paket Hak** | `system_authentication.permission_sets` | RBAC permission-set ([[CORE - RBAC dan Permission Set]]) | 15 paket: `ticket_*` (3), `payroll_*` (4), `finance_*` (3), `monitoring_*` (2), `procurement_*` (3) |
| **Role Modul** | `system_authentication.system_roles` | modul yang menggerbang di `system_roles` | 9 key: `warehouse`, `insentive`, `integration`, `ticket`, `finance`, `procurement`, `marketing`, `wms_viewer`, `group` |

**Aturan praktis:**

- Butuh **warehouse / WMS** → **Role Modul**. Tidak ada satu pun paket hak yang menyentuh warehouse. Gerbangnya `warehouseGuard` yang membaca `system_roles["warehouse"]`.
- Butuh **ticket, payroll, finance, monitoring, procurement** → **Paket Hak**.
- Beberapa key muncul di **kedua** koleksi (`ticket`, `finance`, `procurement`). Untuk **akun luar**, yang berlaku pada ticket adalah **Paket Hak**: klaim izin akun luar tak pernah kosong (selalu berisi penanda `account.$type.external`), sehingga fallback tier yang berpatokan "klaim absen" tak pernah menyala. Untuk `finance`/`procurement` — **TBD**, verifikasi ke kode modulnya sebelum memasang.

**Yang divalidasi saat menyimpan Role Modul** (lebih ketat daripada jalur karyawan):

- Key modul **dan nilai role** dicocokkan ke master data. Salah ketik ditolak dengan pesan yang menyebut apa yang salah — jalur karyawan menyimpan apa pun yang dikirim, lalu role itu tak pernah cocok dengan gerbang mana pun.
- Katalog yang **gagal dibaca menolak segalanya**, bukan meloloskan segalanya.
- Role **`group`** (admin Bharata Group) dibuang paksa. Ia membuka override lintas-perusahaan, kebalikan dari maksud akun yang justru dikurung ke satu tenant.

### Contoh nyata — CV Sadewa

Akun `EXT-0001-08-26` (Laili Faidatun Nisa, CV Sadewa) dengan keperluan "Akses sistem warehouse":

- Sumbu yang benar: **Role Modul**
- Nilai: `warehouse` = **`admin_gudang_sadewa`**
- Hasilnya: sidebar menampilkan grup **"Warehouse Sadewa"** — 4 menu: Dashboard, Pengemasan, Riwayat Cetak Resi, Retur. Menu operasional gudang Tinggar **tidak** muncul, dan endpoint-nya juga ditolak backend — `admin_gudang_sadewa` harus disebut eksplisit per-rute, tidak mewarisi `admin_gudang`. Detail: [[WH - Warehouse Sadewa]].

## Verifikasi

**Di layar** — tab Akun Eksternal menampilkan status **tiga macam**, karena dua yang pertama sama-sama menutup akses tapi pemulihannya beda:

| Status | Artinya | Pemulihan |
|---|---|---|
| **Nonaktif** | `is_active: false` | ⚠️ **tak ada tombolnya di tab ini** — lihat catatan di bawah |
| **Kedaluwarsa** | `valid_until` sudah lewat, **atau kosong** | tombol **Perpanjang / Ubah** |
| **Aktif** | boleh login | — |

> ⚠️ **Menonaktifkan akun luar adalah pintu satu arah dari layar ini.** Tab Akun Eksternal hanya punya enam aksi — buat, ubah/perpanjang, pasang paket hak, setel role modul, terbitkan ulang kata sandi, nonaktifkan — dan **tak satu pun menyalakan kembali `is_active`**. `PUT` hanya menyentuh data pendamping, dan tombol Terbitkan Ulang Kata Sandi sengaja tidak menyentuh `is_active`. Menghidupkan kembali harus lewat `PATCH /account/active-status` (gate `RequireITStaff`) yang **tidak ada di layar ini**. Jadi perlakukan Nonaktifkan sebagai keputusan final; untuk akun yang cuma perlu dijeda, **mundurkan masa berlakunya** lewat Perpanjang / Ubah — itu menutup akses lewat jalur yang punya tombol pemulihan. (Mengosongkan tanggalnya tidak bisa: `PUT` mengabaikan `valid_until` kosong, jadi nilai lama bertahan. Pemeriksaan "harus di masa depan" hanya ada saat **membuat**, tidak saat mengubah.)

Kolom **"Hak Akses"** (kolomnya sekaligus tombol pembuka dialog) menampilkan paket yang terpasang.

> ⚠️ **Kolom itu hanya membaca Paket Hak, bukan Role Modul.** `ringkasHak` dirender dari `permission_sets` saja, sehingga akun yang haknya dipasang lewat tab *Role Modul* — termasuk kasus warehouse/Sadewa — **tetap tertulis "Belum ada"** meski penyimpanannya berhasil. Jangan simpulkan pemasangan gagal dari kolom ini; buka dialognya dan lihat tab **Role Modul**, atau pastikan lewat toast "Role modul vendor disimpan". **TBD**: menyatukan ringkasan kedua sumbu di kolom itu.

**Oleh vendor** — login berhasil, lalu sidebar memuat menu modul yang dimaksud, dan halamannya benar-benar terbuka (bukan 403).

**Di data** (bila perlu pembuktian keras) — baris `system_authentication` untuk ID itu punya `is_active: true`, `has_registered: true`, dan `system_roles`/`permission_sets` **tidak kosong**.

## Bila gagal / Rollback

| Gejala | Sebab | Tindakan |
|---|---|---|
| Vendor login sukses tapi **tak ada menu apa pun** | Tahap 3 belum dikerjakan, atau dipasang di sumbu yang salah | Cek kolom Hak Akses. Cocokkan modul tujuan ke tabel §Memilih Sumbu |
| Hak sudah dipasang tapi vendor **masih ditolak** | Izin dirakit **saat token terbit** | Minta vendor logout–login ulang. Token lama berlaku sampai 72 jam |
| **"masa berlaku harus di masa depan"** saat membuat akun | Tanggal diisi mundur | Isi tanggal di masa depan. Akun yang terbit dalam keadaan mati bikin orang menyangka login-nya rusak |
| **"penanggung jawab tidak ditemukan sebagai karyawan"** | Sponsor tak ada di `work_data` | Pilih karyawan dari daftar, jangan ketik manual |
| **"paket hak '<key>' tidak ditemukan"** / **"role '<x>' tidak berlaku untuk modul '<y>'"** | Key/role di luar master data | Perbaiki lewat master data ([[HRIS - Organization Structure]]), jangan paksakan |
| Kolom **Hak Akses** tetap "Belum ada" padahal Role Modul sudah disimpan | Kolom itu hanya membaca `permission_sets` | Bukan kegagalan — buka dialognya, cek tab Role Modul (lihat §Verifikasi) |
| Kata sandi hilang sebelum dicatat | Yang tersimpan cuma sidiknya | Terbitkan Ulang Kata Sandi (langkah 6) |
| Akun sudah dinonaktifkan tapi vendor **masih bisa jalan** | JWT berlaku 72 jam, **revoke masih placeholder** | Tak ada cara memutus sesi berjalan hari ini. Untuk kasus mendesak, eskalasi ke IT — lihat §Batasan yang Diketahui |

**Rollback pembuatan akun**: tidak ada tombol hapus, dan itu disengaja. Gunakan **Nonaktifkan**. Bila insert kredensial gagal di tengah jalan, sistem sudah otomatis membuang data pendampingnya supaya tak tertinggal akun setengah jadi.

## Batasan yang Diketahui

- 🔴 **Nonaktif tidak memutus sesi berjalan.** JWT TTL 72 jam dan revoke masih placeholder ([[CORE - SSO Flow]] §Catatan & Keterbatasan). Menonaktifkan menutup pintu masuk **berikutnya**, bukan yang sedang terbuka.
- ⚠️ **Vendor tak muncul di layar audit "Siapa Boleh Apa".** Layar itu berangkat dari `work_data`, yang tak dimiliki akun luar — blind spot pada layar yang justru dibuat untuk mengaudit hal ini. **TBD.**
- ⚠️ **Hak dari posisi/jabatan mati untuk vendor.** `positionSetKeys` berhenti bila `work_data.Department` kosong. Hak vendor **hanya** bisa datang dari pemasangan eksplisit per-akun lewat runbook ini.
- ⚠️ **Beranda vendor belum benar di produksi (per 5 Agustus 2026).** Frontend beranda khusus vendor sudah live, tapi backend yang menyuplainya (`/me` cabang akun luar, PR #972) **belum ikut ter-deploy** — image `Employee-Service` dibangun 14 menit sebelum commit itu masuk. Akibatnya vendor mendarat di dashboard karyawan berisi tanda hubung, dan namanya tampil sebagai ID akun. **Akses ke modulnya tidak terpengaruh** — yang rusak hanya halaman `/dashboard`. Perbaikannya rebuild + restart Employee-Service ([[RUN - Deploy Microservices bip-erp]]), tanpa perubahan kode.
- **Masa berlaku panjang = masa berlaku yang tak berarti.** `valid_until` beberapa tahun ke depan secara teknis sah, tapi menghapus gunanya fitur ini. Setel sesuai durasi kerja sama yang nyata.

## Dokumen Terkait

- [[Microservices - Employee Service]] — §Akun pihak luar (model, endpoint, keputusan desain)
- [[CORE - SSO Flow]] — §Role & Otorisasi, gerbang masa berlaku di empat jalur token
- [[CORE - RBAC dan Permission Set]] — sumbu Paket Hak
- [[HRIS - Organization Structure]] — master data department & system role
- [[WH - Warehouse Sadewa]] — kasus pemakai pertama (`admin_gudang_sadewa`)
- [[Microservices - Warehouse Service]] — `warehouseGuard`, gerbang per-rute
- [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]] — kenapa `company_id` wajib diisi
- [[APP - Web ERP]] — tempat tab Akun Eksternal berada
- [[RUN - Deploy Microservices bip-erp]] — rebuild service
