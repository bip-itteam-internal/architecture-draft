> **Status**: 🟡 **Diusulkan**, 2026-10-15; keputusan 2 dan 6 diubah user 2026-10-16 dan keputusan 8 ditambahkan (lihat § Riwayat perubahan). Kode versi 2026-10-15 sudah di prod sejak 2026-10-16 (bip-erp#3169, erp-frontend#2521). Menunggu persetujuan; tulis `🟢 Diterima, <tanggal>, oleh <login/jabatan>` di baris ini bila disetujui.

## Untuk Manajemen

**Apa yang berubah.** Anggota tim IT bisa membuka web ERP *sebagai* seorang karyawan tertentu: memilih jabatan di header, lalu memilih orangnya. Selama itu, menu, Beranda, dan data yang tampil persis seperti yang dilihat orang tersebut. Gunanya memeriksa apakah menu dan halaman per jabatan ([[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]]) sudah benar, tanpa meminjam akun atau kata sandi orang lain.

**Batasnya.**
- Hanya melihat. Semua tombol yang mengubah data (menyetujui, membayar, menyimpan, menghapus) ditolak server.
- Slip gaji pribadi orang yang ditiru tetap tertutup.
- Sesi berlaku selama umur login biasa dan berakhir saat staf IT kembali ke akunnya sendiri atau logout. Alasan wajib dituliskan.
- Setiap sesi tercatat: siapa, menjadi siapa, kapan, untuk apa, dan halaman apa saja yang dibuka.
- Orang yang ditiru **tidak** diberi tahu (keputusan 2026-10-16), dan sesi tiruan tidak mengubah apa pun miliknya: tidak menandai notifikasinya terbaca, tidak mencatat bahwa ia membuka kontraknya.

**Yang perlu disadari.** Fitur ini dibuka untuk **semua anggota IT**, bukan hanya supervisor. Artinya setiap staf IT bisa membaca data kerja siapa pun yang terlihat oleh orang itu, termasuk data tim, antrean persetujuan, dan data HR yang dibuka jabatannya. Sejak 2026-10-16 pengamannya **hanya jejak sesi**, bukan larangan dan bukan pemberitahuan, dan jejak itu belum punya layar baca. Bila kelak dinilai terlalu luas, mempersempitnya cukup mengganti satu pemeriksaan pemakai.

**Yang tidak dijanjikan.**
- Bertindak atas nama orang lain (akses darurat IT) tidak termasuk; itu menunggu SA-1 [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]].
- Belum ada layar untuk membaca jejak; iterasi pertama dibaca tim IT langsung dari database.
- MyBharata tidak mendapat fitur ini; hanya web ERP.

## Deskripsi

*Anggota IT dapat memulai sesi "lihat sebagai" seorang karyawan aktif. Gateway menerbitkan token berumur sama dengan token login berisi identitas penuh target ditambah penanda peniru; gateway menolak semua permintaan tulis, slip pribadi, GET yang mengubah keadaan milik pemanggil, dan penukaran token dari sesi itu; employee-service mencatat sesinya sebelum token terbit. Target tidak diberi tahu.*

- **Status**: 🟡 Diusulkan, 2026-10-15
- **Path di repo** (akan disentuh): `bip-erp/api-gateway/main.go` · `bip-erp/api-gateway/redis.go` · `bip-erp/shared-library/auth/jwt.go` · `bip-erp/shared-library/routes/gateway_request.go` · `bip-erp/shared-library/common/header.go` · `bip-erp/shared-library/models/notification/models.go` · `bip-erp/services/employee/` (penerbit payload, kandidat, koleksi sesi) · `bip-erp/services/task-management/ws_handler.go` · `bip-erp/services/vault-mcp/erp.go` · `erp-frontend/src/components/layout/header.tsx` · `erp-frontend/src/lib/axios.ts` · `erp-frontend/src/lib/sesi-token.ts` · `my-bharata` `notification_type.dart`
- **Spec rinci**: `bip-erp/docs/superpowers/specs/2026-10-15-lihat-sebagai-design.md`
- **Tanggal**: 2026-10-15

## Context

Diukur ke `origin/main` bip-erp dan erp-frontend, 2026-10-15.

- [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]] menuntut uji pakai dengan akun nyata per jabatan. Saat ini caranya hanya meminjam akun orang, dan itu tak berjejak.
- Token diterbitkan gateway (`auth.GenerateJWT`, `shared-library/auth/jwt.go`). Izin paket posisi dihitung saat token terbit oleh employee-service (`rakitHakToken`, `services/employee/hak_token.go`).
- Gateway meneruskan identitas ke hilir sebagai header `BIP-*` (`routes.Reroute`, `shared-library/routes/gateway_request.go`), dan sekitar 433 titik di services membaca `BIP-Employee-ID` pemanggil. Data disaring per **orang**, bukan per jabatan, jadi "lihat sebagai jabatan" tanpa orang tidak punya data.
- Semua permintaan `/api` lewat satu titik `api.All("/:module/*")` di gateway. Rute di luar `/api` (`/auth/*`, SSO, onboarding) tidak.
- Gateway tidak terhubung ke Mongo. Tidak ada jejak audit terpusat; yang ada per service (finance, manufacture, recruitment).
- FE menyimpan token di `localStorage` dan identitas di lima cookie yang ditulis saat login; sidebar (`useAuth`) dan `proxy.ts` membaca keduanya.

## Decision

1. **Identitas tiruan adalah orang nyata.** Pemilih: jabatan, lalu pemegangnya. Target harus karyawan aktif, bukan akun pihak luar, bukan diri sendiri.
2. **Token tiruan diterbitkan gateway** lewat jalur payload yang sama dengan login (satu jalur, dijaga test), ditambah klaim `diperankan_oleh`, `diperankan_nama`, `sesi_tiruan_id`. Umurnya **sama dengan token login** (keputusan user 2026-10-16, menggantikan 30 menit), tanpa perpanjangan. Satu sumber angka: employee-service menetapkan `kedaluwarsa` sesi dari umur token login (`auth.UmurToken`), gateway menurunkan umur token tiruan dari `kedaluwarsa` itu.
3. **Baca-saja ditegakkan di gateway, satu tempat.** Untuk token bertanda peniru: semua metode selain GET/HEAD ditolak 403 `mode_lihat_sebagai`; slip pribadi (`payroll` `/payroll-runs/my*`, `/me`) ditolak; `/auth/refresh`, `/auth/verify-pin`, `/auth/sso/*`, dan memulai tiruan baru ditolak. Service yang mem-parse JWT sendiri (WebSocket task-management, vault-mcp) menolak token tiruan.
4. **Pemakai: siapa pun yang `system_roles`-nya memuat `it`**, keputusan user 2026-10-15. Bukan paket izin khusus.
5. **Jejak wajib.** Sesi dicatat employee-service (`sesi_lihat_sebagai`) **sebelum** token terbit; gagal mencatat berarti tidak ada sesi. Alasan wajib diisi. Daftar halaman yang dibuka dicatat best-effort, tanpa query string.
6. ~~Target diberi tahu lewat inbox saat sesi mulai.~~ **Dicabut 2026-10-16 oleh user: target tidak diberi tahu.** Kategori inbox `account-viewed-by-it` tetap terdaftar (tak dipakai) supaya notification-service tak perlu ikut di-deploy; pemetaannya di MyBharata tak berbahaya.
7. **Cache respons gateway dipisah** untuk sesi tiruan, supaya tidak berbagi atau mencemari cache milik target.
8. **GET yang mengubah keadaan milik pemanggil ditolak** untuk sesi tiruan (ditambahkan 2026-10-16 dari sapuan seluruh service): `notification` `/inbox?id=` (menandai terbaca), `employee` `/me/contracts/*/ttd/dokumen` (mencatat bukti karyawan membuka kontraknya), `warehouse` `/fulfillment/queue/export` (menandai order diekspor atas nama pemanggil), `integration` segmen `auth`, `sync`, atau `backfill` (state OAuth atas nama pemanggil, dan sinkron/backfill data channel ke DB). Umur token tiruan tak pernah melampaui umur token login, sekalipun employee membalas kedaluwarsa lebih jauh. Satu tabel aturan di `api-gateway/lihat_sebagai.go`; GET baru yang menulis atas nama pemanggil wajib ditambahkan ke tabel itu.

## Consequences

**Yang didapat.**
- Uji pakai per jabatan untuk ADR 0149 bisa dilakukan tanpa kata sandi orang lain, dan berjejak.
- Seluruh service hilir bekerja tanpa diubah, karena header yang mereka baca memang milik target.

**Yang harus diterima.**
- Setiap anggota IT bisa membaca data yang terlihat oleh siapa pun. Sejak 2026-10-16 pengamannya hanya jejak sesi; target tidak tahu, dan jejaknya belum punya layar baca.
- Daftar halaman yang dibuka bisa bolong bila pencatatan asinkron gagal; awal dan akhir sesi tidak.
- Daftar pencabutan token gateway ada di memori dan hilang saat restart. Dengan umur token 72 jam, token tiruan yang sudah "Kembali ke akun saya" bisa hidup lagi sampai 72 jam bila gateway restart sebelum ia kedaluwarsa (sebelumnya dibatasi 30 menit).
- Tab lain yang dimuat ulang selama sesi ikut memakai token tiruan (penyimpanan token dibagi antar-tab); pita peringatan tampil di sana juga.
- Daftar GET penanda (keputusan 8) hanya selengkap sapuan 2026-10-16; GET penulis baru yang tak didaftarkan akan mengubah keadaan milik target tanpa galat.

## Riwayat perubahan

- **2026-10-16, keputusan user**: target tidak diberi tahu (keputusan 6 dicabut); umur sesi sama dengan login biasa, bukan 30 menit (keputusan 2); GET yang menulis atas nama pemanggil diblokir (keputusan 8 baru). Implementasi: bip-erp#3219, erp-frontend#2532.

## Belum Diputuskan (TBD)

- Layar untuk membaca jejak sesi, dan siapa yang boleh membacanya.
- Bertindak atas nama orang lain (SA-1 ADR 0137).
- Apakah Direksi dikecualikan sebagai target. Saat ini tidak.

## Dokumen Terkait

- [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]]
- [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]]
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]
- [[CORE - RBAC dan Permission Set]]
- [[APP - Web ERP]]
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]
