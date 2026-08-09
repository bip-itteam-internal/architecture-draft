## Deskripsi

*Sistem distribusi (`Sistem-Distribusi-Offline`) berjalan di belakang **API Gateway-nya sendiri**, bukan didaftarkan sebagai modul di [[CORE - API Master Gateway]]. Penyambungannya ke ERP lewat **SSO one-time-code** yang sudah ada di kedua sisi, bukan lewat token bersama.*

- **Status**: 🟡 **Keputusan diambil, sistemnya belum di-deploy.** Repo `Sistem-Distribusi-Offline` ([github](https://github.com/bip-itteam-internal/Sistem-Distribusi-Offline)) belum berjalan di bip-vps dan belum punya dok arsitektur di vault ini (**TBD**). Keputusan diambil 2026-08-09 setelah pembacaan kode kedua gateway.
- **Berlaku untuk**: `Sistem-Distribusi-Offline` · [[CORE - API Master Gateway]] · [[CORE - SSO Flow]]

## Context

`Sistem-Distribusi-Offline` adalah port dari aplikasi .NET 8 Razor Pages + SQLite satu-proses ke pondasi arsitektur ERP Bharata: enam service Go (`master`, `warehouse`, `canvas`, `selling`, `finance`, `report`) di belakang gateway, MongoDB database-per-service ([[ADR - 0002 Database-per-Service]]), frontend Next.js. Cakupannya sales canvas, konsinyasi, gudang, dan piutang untuk bisnis distributor.

Karena pondasinya sengaja dibuat sama dengan bip-erp, muncul pertanyaan wajar: kalau polanya sudah identik, kenapa tidak sekalian memakai gateway ERP yang sudah ada dan berjalan?

Pertanyaan itu masuk akal justru karena repo distribusi **memang ditulis dengan niat itu**. Komentar di `api-gateway/sso.go` menyebut eksplisit bahwa bentuk tokennya dibuat sama persis dengan bip-erp supaya, bila kelak ditaruh di belakang gateway ERP, `redeem` di sana menghasilkan token yang langsung diterima service di repo distribusi tanpa perubahan kode. Login pun sudah didelegasikan ke `master-service` sebagai pemilik kredensial, meniru bip-erp yang mendelegasikan ke `employee-service` — dengan alasan tertulis agar penukaran sumber kredensial ke `employee-service` kelak cukup mengganti satu URL.

Pembacaan kode kedua gateway menunjukkan niat itu belum tercapai. Ada tiga selisih yang harus ditutup lebih dulu, dan yang pertama berbahaya karena gagalnya senyap.

## Decision

**Sistem distribusi memakai gateway sendiri. Penyambungan ke ERP lewat SSO handoff, bukan token bersama.**

**1. Klaim JWT kedua sistem belum sama, dan selisihnya menyangkut dasar hak akses.**

Token ERP dan token distribusi ditandatangani dengan secret dan algoritma yang sama (HS256), sehingga **token ERP akan lolos validasi di service distribusi**. Yang tidak lolos adalah isinya:

| Klaim | ERP | Distribusi |
|---|---|---|
| `employee_id`, `username`, `system_roles`, `position`, `company_id` | ada | ada |
| nama lengkap | `full_name` | **`name`** |
| `department`, `supervised_departments` | ada | tidak ada |
| `account_type` | tidak ada | ada |
| **`sales_person_id`** | **tidak ada** | ada |
| **`area`** | **tidak ada** | ada |

`sales_person_id` dan `area` bukan tambahan kosmetik. Komentar di `shared-library/auth` repo distribusi menyebutnya sebagai dasar cakupan: `sales_person_id` menentukan reach `own` (seorang sales hanya boleh melihat datanya sendiri), `area` menentukan cakupan `division`.

Menaruh sistem distribusi di belakang gateway ERP **hari ini** berarti setiap sales masuk dengan `sales_person_id` kosong. Tokennya sah, permintaannya diterima, dan cakupannya runtuh tanpa satu pun pesan galat.

Kelas kegagalan ini sudah pernah terjadi di repo ini dan tercatat di kodenya sendiri: `supervised_departments` sempat hilang seluruhnya dari token karena payload disalin field-per-field, sehingga fitur cakupan lintas departemen tak pernah aktif — **tanpa satu pun test gagal**, karena test menembak `SignJWT`, bukan jalur yang membuang field itu. Perbedaan bentuk klaim di sini persis kondisi yang melahirkan kegagalan tersebut, dengan taruhan yang lebih besar karena yang runtuh adalah pembatas data antar-sales.

**2. Gateway distribusi lebih ketat, dan itu disengaja.**

Dua perlindungan ada di gateway distribusi tetapi tidak di gateway ERP:

- `InternalURL` di distribusi adalah **allowlist**: modul yang tak terdaftar dijawab `404`. Gateway ERP memakai `api.All("/:module/*")` yang meneruskan apa adanya.
- Sub-path `/internal/*` **ditolak di tepi** oleh middleware `tolakInternal`. Di ERP prefix itu diteruskan ke service, sehingga siapa pun yang punya token login bisa memanggilnya — persis yang dicatat [[ADR - 0031 Prefix internal Bukan Batas Keamanan]].

Memindahkan distribusi ke gateway ERP berarti **membuang kedua perlindungan itu**. Repo distribusi menutupnya sejak awal justru karena dimulai dari nol dan tak perlu mewarisi kompromi yang sudah terlanjur hidup di ERP.

**3. `shared-library` kedua repo tidak bisa dipakai bersamaan.**

Keduanya memakai module path identik `github.com/bharata/shared-library` dengan isi berbeda — distribusi di Go 1.23 dan Fiber 2.52.5, ERP di Go 1.25.1. Satu build tak bisa memuat keduanya tanpa dirapikan lebih dulu.

**4. Penyambungan memakai SSO one-time-code yang sudah jadi.**

Kedua gateway sudah punya `/auth/sso/ticket` dan `/auth/sso/redeem` sesuai [[CORE - SSO Flow]]. Pemakai yang sudah punya sesi di ERP meminta `code` sekali-pakai (TTL 30 detik), diarahkan ke sistem distribusi dengan `?code=`, dan distribusi menukarnya jadi token **terbitannya sendiri** — lengkap dengan `sales_person_id` dan `area`.

Ini menyelesaikan tujuan sebenarnya (pemakai tak login dua kali) tanpa menyentuh satu pun dari tiga selisih di atas. Backend-nya agnostik aplikasi, jadi menambah konsumen SSO tidak menuntut perubahan backend di sisi mana pun.

## Consequences

- **Satu gateway lagi yang harus dijaga**, dengan limiter, CORS, dan penerbitan token sendiri. Ini biaya nyata yang diterima sadar sebagai ganti dari batas data yang tidak runtuh.
- **Port host wajib dijaga agar tidak bentrok.** Gateway distribusi memakai `7100`, frontend `3210` — 3100 sudah dipublikasikan hoppscotch di bip-vps, dan 3200 dihindari karena hoppscotch memakainya sebagai bundle server di dalam container. Nilai bawaan yang bentrok membuat `docker compose up` gagal mengikat port. Detail di `.env.example` repo distribusi.
- **Pencabutan hak tidak langsung terasa lintas sistem.** SSO menerbitkan token distribusi yang berdiri sendiri; mencabut hak di ERP tidak membatalkan token distribusi yang sudah terbit sampai kedaluwarsa. Sama dengan perilaku refresh di kedua repo, yang juga tidak mengambil ulang hak dari sumber kredensial.
- **Bila kelak benar-benar digabung, urutannya mengikat**: tambahkan `sales_person_id`, `area`, dan samakan penamaan `full_name` di `SignJWT` ERP → port `tolakInternal` ke gateway ERP → baru daftarkan keenam modul distribusi ke `InternalURL`. Membalik urutannya menghasilkan sistem yang berjalan tetapi cakupan datanya bocor tanpa gejala.
- **ADR ini tidak menyatakan penggabungan sebagai ide buruk.** Yang dinyatakan: penggabungan **hari ini** menukar kebocoran cakupan data dengan penghematan satu proses gateway. Bila ketiga selisih ditutup, keputusan ini wajib ditinjau ulang.
- **`ssoStore` masih in-memory di kedua sisi**, jadi kode SSO yang disimpan satu instance tak terlihat instance lain. Gateway distribusi belum aman dijalankan multi-replika; Redis sudah tersedia di compose-nya tetapi belum dipakai untuk ini (**TBD**).

## Alternatif yang ditolak

| Alternatif | Alasan ditolak |
|---|---|
| Daftarkan 6 modul distribusi ke `InternalURL` ERP sekarang | Token ERP tak punya `sales_person_id`/`area`; setiap sales kehilangan pembatas datanya tanpa gejala |
| Gabungkan gateway, tambal cakupan di sisi service distribusi | Memindahkan aturan cakupan ke enam tempat, padahal sumbernya satu klaim token |
| Samakan `Claims` dulu lalu gabungkan dalam satu langkah | Perubahan `SignJWT` ERP berdampak ke seluruh service bip-erp; menggabungnya dengan migrasi sistem lain membuat dua kegagalan berbeda tampak seperti satu |
| Bagikan `JWT_SECRET` saja, biarkan klaim berbeda | Justru inti masalahnya: secret yang sama membuat token lintas-sistem **lolos validasi**, sehingga selisih klaim gagal dalam diam |
| Frontend distribusi menyimpan token ERP apa adanya | Sama dengan di atas, hanya berpindah tempat |

## Dokumen Terkait

- [[CORE - API Master Gateway]] · [[CORE - SSO Flow]]
- [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[ADR - 0002 Database-per-Service]]
