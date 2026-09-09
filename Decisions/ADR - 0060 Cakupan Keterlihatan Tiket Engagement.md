## Deskripsi

*Tiket Engagement disaring per **departemen requester**, bukan dibiarkan terbuka bagi seluruh pemakai ERP. Tiket menyimpan field baru `requester_department` yang distempel server saat tiket dibuat; keterlihatannya diputuskan dari **keterkaitan pemanggil dengan tiket** (pembuat / pengerja / anggota kolam pengerja / supervisor departemen / admin), bukan dari satu aturan tunggal. Keputusan ini juga mencabut `space_id` sebagai sumber keanggotaan tim.*

- **Status**: ✅ **Berlaku, kodenya sudah di `main`** — commit `1cdd7fad` "model departemen requester + kolam pengerja lintas departemen" dan `742e0bfd` "perbaiki hasil review PR #1519 (kebocoran keterlihatan, filter mine, peta departemen)" (29 Agustus 2026), diverifikasi ulang ke kode 2026-09-09. **Belum diverifikasi lewat gateway** dev maupun prod. Keputusan diambil 2026-08-29 atas temuan audit T-10 ([[Sales - Engagement Team (Modul)]] cacat no. 4). Spesifikasi teknis lengkap ada di `Workspace/ANALISA - Model Departemen Engagement`. ⚠️ **§6 di bawah (pembersihan `space_id`/notifikasi mati) TERNYATA belum tuntas** — lihat catatan di situ dan di [[ADR - 0059 Penugasan Langsung Menggantikan Antrian Bersama]].
- **Path di repo (yang akan disentuh)**: `bip-erp/services/task-management/engagement_models.go` · `engagement_handlers.go` · `engagement_assign.go` · `engagement_repo.go` · `erp-frontend/src/features/marketing/engagement/**`
- **Tanggal**: 2026-08-29

## Context

Modul Engagement melayani **dua brand yang berbeda client**. Fakta organisasi yang memicu ADR ini (dari pemilik produk, 2026-08-29): permintaan boosting datang dari **Account Specialist yang tersebar di dua departemen — `Kyura` dan `Beauty Hacks`** — dan dikerjakan anggota **tim Engagement** (jabatan `Engagement Team`, dulu `Buzzer`).

Yang ditemukan di kode hari ini:

1. **Tak ada penyaringan sama sekali di jalur pemakai.** `antrianEngagement` (`engagement_handlers.go:216`) hanya menyaring `status`; `dashboardEngagement` (`:771`) hanya menghitung per status; `detailTiket` (`:374`) dan `riwayatTiket` (`:397`) tidak memeriksa keterkaitan pemanggil sama sekali. Gerbang rutenya `requireRoles("staff","supervisor","admin")` — yaitu **setiap pemakai ERP**. Komentar di `:209-213` menjanjikan "seluruh tiket aktif **satu departemen**"; querynya tidak melakukannya. Dokumentasi yang berbohong lebih berbahaya daripada tidak ada dokumentasi.
2. **Yang bocor bukan metadata.** `guideline`, `tone_of_voice`, `kata_terlarang`, `client`, `campaign`, dan `target_url` adalah materi kampanye. Dengan dua brand berbeda client, Kyura membaca brief Beauty Hacks dan sebaliknya — di dalam satu perusahaan yang sama, tanpa satu pun jejak.
3. **Tiket tak menyimpan departemen.** `EngagementTicket` (`engagement_models.go:51`) hanya punya `requester_id`. Penyaringan apa pun karena itu **menuntut field baru + migrasi**, dan itulah sebab keputusannya ditunda sampai sekarang.
4. **Standarnya sudah ada di modul yang sama, hanya tak diterapkan.** `daftarKandidatPengerja` menyaring departemen dan menolak memakai departemen dari query klien; muatan `/kpi/engagement` sengaja disempitkan persis untuk alasan kerahasiaan yang sama.

Asumsi diam model lama — **requester dan pengerja sedepartemen** — juga terbukti tidak dapat dijadikan pegangan. `daftarKandidatPengerja` menyaring `work_data` dengan `{department: <departemen PEMANGGIL>}`; bila kelak tim Engagement dipisahkan ke departemen sendiri, daftar kandidatnya kosong tanpa satu pun galat. Aturan keterlihatan di bawah karena itu **tidak boleh** dibangun di atas kesamaan departemen requester–pengerja.

## Decision

**Keterlihatan tiket engagement diputuskan dari KETERKAITAN pemanggil dengan tiket, dan `requester_department` adalah sumbu penyaringnya.**

### 1. Field baru `requester_department`, distempel server

`EngagementTicket` menyimpan `requester_department` (nama departemen apa adanya seperti `work_data.department`, mis. `"Kyura"` / `"Beauty Hacks"`). Diisi dari header identitas `BIP-Department` saat tiket dibuat, **tidak pernah** dari body request — nilai yang boleh dipilih klien bukan sumbu keamanan.

Disimpan sebagai **nama**, bukan key departemen: nama itulah yang tersimpan di `work_data.department` dan yang dibandingkan seluruh modul lain (`deptKeyToNames`, `insentive/hierarki_hris.go`). Perbandingannya **kanonik** (trim, lipat kapital, rapatkan spasi ganda) karena nama departemen diketik manusia di Master Data.

### 2. Lima aturan keterlihatan, digabung sebagai OR

Satu tiket terlihat oleh pemanggil bila **salah satu** benar:

| # | Aturan | Alasan |
|---|---|---|
| 1 | `requester_id == aku` | pembuatnya selalu melihat permintaannya sendiri |
| 2 | `assigned_to == aku` | tanpa ini pengerja tak bisa bekerja |
| 3 | aku **anggota kolam pengerja** → tiket dengan `requester_department` ∈ daftar departemen requester | tim Engagement melayani KEDUA brand; membatasinya ke satu departemen melumpuhkan pekerjaannya |
| 4 | aku **supervisor** → `requester_department` ∈ `scopedDivisions(aku)` | pola yang sudah dipakai modul tiket IT di service yang sama (`rbac.go:56`) |
| 5 | aku **admin** → semua | jalur pemulihan tiket macet |

Yang **tidak** ada di daftar itu, dan itu inti keputusannya: *"staff mana pun boleh melihat"*. Account Specialist Kyura tidak lagi melihat tiket Beauty Hacks, dan sebaliknya.

⚠️ **Supervisor dibatasi cakupan supervisinya, bukan diberi semuanya.** SPV Kyura membaca brief Beauty Hacks adalah kebocoran dengan kelas yang sama — jabatannya lebih tinggi, clientnya tetap bukan clientnya. Hanya `admin` yang menembus keduanya, dan itu memang perannya.

### 3. Kolam pengerja adalah DATA, bukan konstanta di handler

Siapa "anggota kolam pengerja" ditentukan `work_data.position_key` ∈ daftar kunci jabatan pengerja, dibaca dari **dokumen konfigurasi** (`engagement_settings`), bukan ditulis di handler.

Alasannya sudah terbukti mahal sekali di repo ini: rename `Buzzer` → `Engagement Team` **menerbitkan key baru** (`buzzer` → `engagement_team`, dikunci `master_data_test.go:282`) dan menghanguskan paket hak posisi itu tanpa satu pun galat. Kunci jabatan yang di-hardcode akan mengulang kegagalan yang sama: dropdown kosong, daftar kosong, nol pesan. Karena itu daftarnya berisi **kedua kunci** dan letaknya di data yang bisa diubah tanpa deploy.

Hal yang sama berlaku untuk daftar departemen requester (`Kyura`, `Beauty Hacks`): keduanya nilai default yang **di-seed**, bukan nilai yang dianyam ke dalam kode.

### 4. Kandidat pengerja diambil dari kolam pengerja, bukan dari departemen pemanggil

`daftarKandidatPengerja` berhenti memakai `{department: <departemen pemanggil>}` dan memakai `{position_key: {$in: <kunci jabatan pengerja>}}` lintas departemen. Tanpa ini, Account Specialist Kyura mendapat daftar berisi rekan-rekan Kyura dan **tak satu pun anggota tim Engagement** — ia harfiah tak bisa menugaskan orang yang seharusnya mengerjakan.

Aturan turunan yang **dipertahankan** dari [[ADR - 0059 Penugasan Langsung Menggantikan Antrian Bersama]]: departemen/kolamnya ditentukan server (bukan query klien), akun non-aktif dibuang, dan daftar kosong dijawab `200` + `catatan`, bukan galat.

Yang **berubah** dari ADR 0059 butir 3: alasan "departemen lebih stabil daripada jabatan" tetap benar sebagai peringatan, tetapi kesimpulannya — memakai departemen **pemanggil** — dibatalkan, karena asumsi diamnya (requester sedepartemen dengan pengerja) tidak berlaku. Penggantinya bukan "kembali ke nama jabatan", melainkan **kunci jabatan yang disimpan sebagai data**.

### 5. Membuat tiket dibatasi departemen requester

`POST /engagement/tickets` menolak `403` bila departemen pemanggil tidak ada di daftar departemen requester. Gerbang lama (`staff`|`supervisor`|`admin`) berarti seluruh ERP — Finance dan Warehouse pun boleh menerbitkan permintaan boosting.

Gerbangnya **departemen, bukan jabatan**: `Leader` dan supervisor brand yang sah meminta boosting tidak boleh ikut tertutup, dan label jabatan `ICC` sudah pernah di-rename jadi `Account Specialist` (`position_key_filter_test.go:21`) — mengikatnya ke label mengulang kelas kegagalan yang sama.

### 6. `space_id` dicabut sebagai sumber keanggotaan

Sejak [[ADR - 0059 Penugasan Langsung Menggantikan Antrian Bersama]], notifikasi sudah personal dan `anggotaSpaceEngagement` tak dipanggil dari mana pun. ADR ini menutupnya: **keanggotaan tim Engagement hanya punya satu sumber, yaitu `work_data`**. `space_id` tidak boleh menentukan keterlihatan, kolam pengerja, maupun penerima notifikasi.

Dua mekanisme keanggotaan yang hidup berdampingan pasti menyimpang, dan penyimpangannya muncul sebagai "orang ini tidak dapat notifikasi" — kegagalan yang tak berbunyi.

Field `space_id` **tidak dihapus dari dokumen** (data lama menyimpannya) dan tetap diteruskan ke `notifyMany` sebagai konteks tautan saja. Yang **seharusnya** dihentikan: menerimanya dari body `POST /engagement/tickets` (ini benar terjadi — `buatTiketRequest` masih punya field `SpaceID` tapi tak lagi memengaruhi keanggotaan/notifikasi), dan `anggotaSpaceEngagement` beserta dua tipe notifikasi mati (`engagement_ticket_open`, `engagement_released`) **dibuang**.

⛔ **Koreksi 2026-09-09**: bagian "dibuang" di atas TIDAK terjadi. Diverifikasi lewat Grep atas `bip-erp/services/task-management`: `anggotaSpaceEngagement` (`engagement_notify.go:55`) masih ada di kode dan memang tak dipanggil dari mana pun (dead code terbukti, bukan diasumsikan) — tapi tak dibuang. `NotifEngagementOpen`/`NotifEngagementReleased` (`engagement_notify.go:21,23`) masih terdaftar sampai `fcm.go:66`. Komentar kepala berkas `engagement_notify.go:11-16` juga masih menyatakan "modul ini menyapa SELURUH anggota space" — kalimat yang sudah salah sejak ADR-0059 berlaku. Rinciannya dipindah ke [[ADR - 0059 Penugasan Langsung Menggantikan Antrian Bersama]] (bagian ini historisnya milik keputusan itu, bukan ADR ini) supaya tak ada dua tempat mencatat fakta yang sama.

### 7. Tiket lama: dimigrasi, dan yang gagal dimigrasi TIDAK disembunyikan

Tiket yang sudah ada tak punya `requester_department`. Migrasi mengisinya dari `work_data` lewat `requester_id`.

Yang tak berhasil di-resolve (requester sudah resign, `work_data` terhapus) **tidak boleh jatuh ke keadaan tak terlihat siapa pun**. Aturannya: tiket ber-`requester_department` kosong tetap terlihat oleh pembuatnya, pengerjanya, seluruh anggota kolam pengerja, dan admin — hanya tak terlihat oleh Account Specialist lain. Menyembunyikan tiket dari semua orang adalah kehilangan data yang tampak seperti fitur.

## Consequences

**Yang diterima:**

- **Supervisor kehilangan pandangan lintas brand.** SPV Kyura tak lagi melihat tiket Beauty Hacks. Bila kelak dibutuhkan (mis. untuk melihat beban tim Engagement secara utuh), jalurnya menambah cakupan lewat `master_department.supervised_by` atau memberi peran admin — bukan melonggarkan aturan ini.
- **Satu query tambahan per permintaan daftar.** Menentukan apakah pemanggil anggota kolam pengerja menuntut pembacaan `work_data`; header gateway hanya membawa **label** posisi, bukan `position_key`. Diredam cache berumur pendek; label header dipakai sebagai cadangan bila pembacaan gagal, sehingga kegagalan employee-service menurunkan hak, bukan membuka semuanya.
- **Kontrak FE berubah**: `queue` mengembalikan lebih sedikit baris untuk sebagian orang, `/engagement/kandidat` kini memuat orang lintas departemen sehingga kolom departemen jadi perlu, dan `detailTiket`/`logs` bisa membalas `403` untuk id yang sebelumnya `200`.
- **`403`, bukan `404`, untuk tiket di luar cakupan.** `404` menyembunyikan keberadaan tiket lebih baik, tetapi membuat "tak berhak" tak dapat dibedakan dari "salah id" saat menelusuri keluhan. Yang bocor dari `403` hanyalah fakta bahwa sebuah id ada.

**TBD di atas — DIJAWAB 2026-09 (kartu `t_9fcdab8c`, komentar "JAWABAN USER ATAS TBD" di `engagementSettingsDefault`, `engagement_settings.go`):**

- ✅ **Kunci jabatan pengerja**: `position_key == 'engagement_team'` SAJA, terbukti tiga karyawan di produksi. Kunci lama `buzzer` sengaja TIDAK diikutkan di seed produksi (beda dari usulan jaring-pengaman semula) — kalau kelak masih ada `work_data` yang belum ter-rename, operator menambahkannya lewat Mongo langsung, bukan lewat kode.
- ✅ **Satu kolam lintas brand** (bukan dua kolam terpisah per brand) — ini yang berlaku di kode (`daftarKandidatPengerja` menyaring `position_key`, bukan `department`). **Nuansa penting**: ini jawaban untuk *siapa BOLEH ditugaskan/dilihat sebagai kandidat* (kolam). Untuk *siapa OTOMATIS dapat giliran* (alokasi round-robin), keputusan terpisah menyempitkannya ke sedepartemen requester secara default — lihat [[ADR - 0083 Alokasi Otomatis Round-Robin Menggantikan Penunjukan Manual AS]] §2. Dua sumbu ini gampang tertukar; jangan disatukan jadi satu kalimat "kolamnya lintas/tidak lintas departemen" tanpa menyebut yang mana.

## Terkait

- [[ADR - 0083 Alokasi Otomatis Round-Robin Menggantikan Penunjukan Manual AS]] — memakai kolam pengerja ADR ini (§4) sebagai sumber kandidat, lalu menyempitkannya ke sedepartemen requester untuk alokasi OTOMATIS
- [[Sales - Engagement Team (Modul)]] — konsep bisnis modul, daftar cacat termasuk T-10 yang jadi sebab ADR ini
- [[ADR - 0059 Penugasan Langsung Menggantikan Antrian Bersama]] — butir 3-nya diubah oleh ADR ini
- [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]] · [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]]
- [[Microservices - Task Management Service]] · [[API - Task Management Service]] · [[Microservices - Employee Service]] · [[APP - Web ERP]]
