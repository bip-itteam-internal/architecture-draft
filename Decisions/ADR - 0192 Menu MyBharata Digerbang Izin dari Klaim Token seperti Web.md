# ADR - 0192 Menu MyBharata Digerbang Izin dari Klaim Token seperti Web

> **Status**: 🟢 Diterima, 2026-10-21, oleh irfanarfianto. Pemutus: irfanarfianto. Melanjutkan [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] dan [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]] ke MyBharata. Tunduk pada batas masa transisi [[ADR - 0164 Hak Akses Satu Pintu, Peran Dibawa Paket Hak dan Dirakit saat Token Terbit]] (`system_roles` tetap dikirim) dan [[ADR - 0172 Token Login Keluar dari Cookie dan Paket Semua Izin Dimekarkan saat Token Terbit]] (bentuk klaim tidak berubah).

## Untuk Manajemen

**Apa yang berubah.**
- Menu di MyBharata yang hanya untuk orang tertentu (Buku Tamu, Cek Izin satpam, Reset Akun IT, Sesi Live untuk host, Satgas, Catatan Kepatuhan, tab Tiket Tim, layar peninjau sekretaris) ditentukan oleh **paket hak (permission set)** yang dipasang di posisi atau akun, sama seperti menu di web ERP. Mengatur siapa melihat menu apa cukup dilakukan di satu tempat, yaitu pengaturan paket hak di web.
- Menu untuk diri sendiri (Jadwal, Pengajuan, Slip Gaji, QR, KPI, Kaizen, Pelatihan, Kontrak Saya, Kuota Cuti, Bantuan, tab-tab, Profil) tetap terbuka untuk semua karyawan, tanpa izin. Ini sudah berlaku sejak ADR 0030.

**Yang tidak berubah.**
- Siapa yang boleh melakukan apa tetap dijaga server. Menu yang tampil bukan pengaman, hanya penunjuk jalan.
- HP dengan versi aplikasi lama tetap jalan seperti sekarang.

## Context

Diukur 2026-10-21 (riset read-only atas mybharata-app `origin/dev`, erp-frontend dan bip-erp `origin/main`):

- MyBharata menentukan menu dari `system_roles` yang disimpan di HP (`auth_implements.dart:65-72`), ditambah dua jawaban server per fitur: Satgas `allowed` dan Catatan Kepatuhan `can_record`. Klaim izin tidak pernah dibaca.
- Bila cache peran kosong, semua menu bergerbang **tampil** (`home_quick_access.dart:274`, `if (roles == null) return true`). Ini gagal-terbuka.
- Web menyaring menu dari klaim JWT `permissions` (`use-auth.ts:78-90`, `can()` di `utils/access.ts:126-135`, `bolehMenu()` di `utils/menu-permission.ts:684-754`), dengan cadangan per modul ke `system_roles` selama klaim belum memuat modul itu.
- Token yang diterima MyBharata dari `auth/login` dirakit oleh `rakitPayloadJWT` yang sama dengan web (`services/employee/payload_token.go`), jadi **klaim `permissions` sudah ada di HP** dan hanya belum dibaca.
- Lima menu bergerbang belum punya padanan izin di katalog `shared-library/common/catalog_*.go`: Buku Tamu (BE `RequireGuestbookRBAC`), Cek Izin satpam (`ga == security`), Reset Akun IT (`it != null`), Sesi Live host (`insentive == host_live`), dan layar peninjau sekretaris (`isSecretarySupervisor`).
- Rute Satgas yang dipanggil MyBharata (`api/form-builder/me/satgas`) sudah dihapus di backend (commit `46dc4b01`, ADR 0122). Penggantinya `/satgas-findings*` di employee-service, sehingga menu Satgas di HP kemungkinan tidak pernah muncul.

## Decision

1. **Sumber izin di MyBharata adalah klaim `permissions` di JWT**, sama dengan web. Tidak ada endpoint baru. Klaim dibaca ulang setiap kali token diperbarui (login, refresh). Bentuk klaim tidak diubah (ADR 0172).
2. **Lima menu tanpa padanan mendapat izin baru di katalog**: Buku Tamu, Cek Izin satpam, Reset Akun IT, Sesi Live host, dan peninjau sekretaris.
   - Nama kunci mengikuti konvensi katalog dan ditetapkan di issue BE. Satu izin per menu, ditaruh di berkas katalog modul pemiliknya.
   - Paket bawaan memberi izin baru itu kepada pemegang peran yang hari ini melihat menunya, sehingga **tidak ada yang kehilangan menu** saat migrasi.
   - Gerbang server yang ada (mis. `RequireGuestbookRBAC`, `RequireITStaff`) tidak dilonggarkan oleh ADR ini.
3. **Aturan cadangan sama dengan web**:
   - bila klaim memuat modul menu itu, izin yang menentukan;
   - bila tidak, `system_roles` yang menentukan (aturan peran hari ini);
   - bila keduanya tak terbaca, menu bergerbang **tidak tampil** (tertutup). Ini menutup perilaku gagal-terbuka hari ini.

   Menu self-service tidak bergerbang sama sekali.
4. **Satu tempat aturan menu di MyBharata**: satu peta menu → izin → cadangan peran. Penanda "khusus posisi" di `quick_access_menu_style.dart` diturunkan dari peta itu, bukan disalin.
5. **Menu Satgas** dipindahkan ke izin `kepatuhan.satgas.input`, dan pemanggilan rute lama yang sudah dihapus ikut dibuang.
6. **`system_roles` tetap dikirim** selama masa transisi (ADR 0164), karena HP versi lama bergantung padanya dan tidak bisa dipaksa update.

## Amandemen

### 2026-10-21: Penempatan izin, Buku Tamu, sekretaris, dan Semua Izin

Diputuskan Pemutus (irfanarfianto) sesudah riset katalog untuk bip-erp#3367:

- **Satu modul baru per menu**, mengikuti pola `catalog_engagement.go`: Buku Tamu, Cek Izin satpam, Reset Akun IT, dan Sesi Live host. Alasannya terukur: aturan cadangan butir 3 berlaku per modul. Bila izin baru ditaruh di modul yang paketnya sudah dipegang seseorang, cadangan perannya padam dan menunya hilang tanpa galat (insiden `engagement` 2026-09-09). Dengan modul baru yang belum dipegang paket siapa pun, nol orang kehilangan menu tanpa migrasi data. Nama modul tidak boleh bertabrakan dengan kategori sidebar web (`it`, `ga`, `hris`, `secretary`, `marketing`, dan seterusnya).
- **Cadangan Buku Tamu mencerminkan gerbang server** `RequireGuestbookRBAC`: `ga` security/supervisor, `hris` staff/supervisor, atau posisi Cost Control. Aturan HP lama (`hris != null || ga == security`) tidak dipakai, karena meloloskan `hris: admin` yang ditolak server dan menyembunyikan menu dari `ga: supervisor` serta Cost Control yang diterima server.
- **"Peninjau sekretaris" dikeluarkan dari cakupan.** Ia bukan menu, hanya penanda tampilan kolom pengganti, dan tidak punya gerbang server. Ia tetap memakai peran. Cakupan butir 2 menjadi **empat** menu.
- **Keempat modul dikecualikan dari paket "Semua Izin"**, seperti modul `menu`, supaya pemegangnya tidak melihat tombol yang dibalas 403 oleh server.

## Alternatif yang Ditolak

- **Endpoint `/me/permissions` baru.** Lebih segar, tetapi menambah satu panggilan dan kode backend, padahal klaimnya sudah ada di token. Pemutus memilih klaim token.
- **Lima menu tetap digerbang peran.** Hanya sebagian menu yang pindah ke paket hak, sehingga mengatur akses tetap terbelah dua tempat. Ditolak.
- **Tetap gagal-terbuka bila izin tak terbaca.** Mengurangi keluhan "menu hilang", tetapi menampilkan menu kepada yang tidak berhak. Ditolak.

## Consequences

- Mengatur akses menu MyBharata dilakukan di halaman paket hak web, tidak lagi lewat peran sistem per modul.
- Perubahan paket hak baru terasa di HP sesudah token diperbarui (login ulang atau refresh token), sama seperti web.
- Katalog izin bertambah lima kunci, dan paket bawaannya harus menjaga visibilitas hari ini.
- Pemetaan menu → izin di MyBharata menjadi fakta yang hidup di satu peta dan wajib berpenjaga test.

## Terkait

- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]] · [[ADR - 0164 Hak Akses Satu Pintu, Peran Dibawa Paket Hak dan Dirakit saat Token Terbit]] · [[ADR - 0172 Token Login Keluar dari Cookie dan Paket Semua Izin Dimekarkan saat Token Terbit]]
- [[CORE - RBAC dan Permission Set]] · [[APP - MyBharata]]
