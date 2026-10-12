# ADR - 0172 Token Login Keluar dari Cookie dan Paket Semua Izin Dimekarkan saat Token Terbit

## Untuk Manajemen

- **Yang berubah di layar**: karyawan yang memegang banyak hak akses tidak lagi "terpental" kembali ke halaman login di Web ERP. Di halaman Hak Akses ada satu paket baru, **Semua Izin**, yang memberi seluruh izin di semua modul tanpa harus mencentangnya satu per satu.
- **Siapa terdampak**: semua pengguna Web ERP. Yang paling merasakan adalah akun berhak banyak (Direktur, tim IT, staf lintas modul) yang hari ini sudah atau akan segera melewati batas. Staf IT yang mengelola hak akses mendapat satu paket baru untuk dipasang.
- **Yang tidak dijanjikan**: paket ini membuka **izin**, bukan **peran modul** (halaman dan menu MyBharata yang digerbang peran, seperti Buku Tamu atau Live Shift, tetap butuh perannya). Larangan menyetujui pengajuan sendiri tetap berlaku. Menu terbatas tidak ikut terbuka. Paket ini tidak bisa dipasang ke akun sendiri. Ukuran token **tidak mengecil**; yang diperbaiki tempat menyimpannya.
- **Besaran kerja**: tiga PR. Satu PR Web ERP untuk penyimpanan token (kecil, ±7 berkas) dikerjakan lebih dulu karena itu yang menghentikan login terpental. Paket Semua Izin butuh satu PR backend employee-service dan satu PR Web ERP (sedang).

## Deskripsi

*Token login Web ERP berpindah dari cookie `token` ke `localStorage`, dengan cookie kecil penanda sesi untuk `proxy.ts`. Akibatnya ukuran token tak lagi dibatasi ±4 KB per cookie milik browser. Di atasnya ditambahkan paket bawaan "Semua Izin" yang dimekarkan perakit token menjadi seluruh izin katalog berjangkauan `all`. Bentuk klaim `permissions` tidak berubah, jadi tak satu pun dari ±120 konsumen izin perlu diajari penanda baru. Usulan awal "satu penanda super admin di token" ditolak.*

- **Status**: 🟡 **Diusulkan**, opsi dipilih user 2026-10-12 lewat `/analisa-kebutuhan` (A lalu C; gerbang penetapan **tidak** dinaikkan ke Supervisor IT). Per 2026-10-12: §A **merged** ke erp-frontend `main` (PR #2329, `a93e46296`; deploy dan perjalanan browser token > 4 KB belum terverifikasi); §C belum ada PR.
- **Path di repo**:
  - Opsi A (FE):
    - `erp-frontend/src/lib/sesi-token.ts` (baru)
    - `erp-frontend/src/app/login/page.tsx`
    - `erp-frontend/src/lib/axios.ts`
    - `erp-frontend/src/proxy.ts`
    - `erp-frontend/src/features/erp/auth/hooks/use-auth.ts`
    - `erp-frontend/src/features/finance/incentive/utils/download.ts`
    - `erp-frontend/src/features/integration/ads-analytics/hooks/use-fetch-advertisers.ts`
    - `erp-frontend/src/features/manufacture/components/GudangBarangJadiView.tsx`
  - Opsi C (BE):
    - `bip-erp/services/employee/permission_resolve.go`
    - `bip-erp/services/employee/hak_token.go`
    - `bip-erp/services/employee/main.go` (`PATCH /account/permission-sets`)
    - `bip-erp/services/employee/position_assign.go`
    - `bip-erp/shared-library/common/` (kunci paket bawaan)
  - Opsi C (FE): `erp-frontend/src/app/(main)/it/hak-akses/page.tsx`
- **Tanggal**: 2026-10-12

## Context

**Gejala.** Akun dengan banyak paket hak terpental ke `/login` sesaat setelah login berhasil.

**Sebab yang terbukti di kode (origin/main 2026-10-12).**
- `erp-frontend` menyimpan JWT lewat `setCookie("token", …)` (`src/app/login/page.tsx:181`, `src/lib/axios.ts:128` saat refresh).
- Browser **membuang diam-diam** cookie yang nama + isinya melewati ±4096 byte.
- Rantai sesudahnya:
  1. Login berhasil, `router.push("/dashboard")`.
  2. Request keluar tanpa `Authorization`.
  3. Backend membalas 401.
  4. Interceptor tak menemukan token (`axios.ts:196`) lalu `redirectToLogin`.
- Rute yang tercakup matcher `proxy.ts` langsung dialihkan ke `/login` (`proxy.ts:164`, `:210-212`).

**Server tidak bermasalah.** Gateway dan seluruh service sudah memakai `ReadBufferSize` 32 KB ([[CORE - API Master Gateway]]). Batas yang terlewat hanyalah batas cookie browser, dan batas itu **tidak tercatat di vault sebelum ADR ini**:
- [[ADR - 0078 Fase Satu WMS Menggabungkan Matriks dan Paket Hak, Bukan Menggantikannya]] menerima kasus terburuk ±11,4 KB gabungan dan hanya menilainya terhadap buffer server.
- Komentar `api-gateway/main.go:95-107` mencatat 51 izin ≈ 2,1 KB per salinan token.

**Usulan awal: satu penanda super admin di klaim `permissions`.** Grounding menemukan alasan menolaknya:
1. **Konsumen izin jauh lebih banyak dari helper bersama.**
   - BE: ±40 berkas lewat helper `common`, ±13 parser manual `BIP-Permissions`, ±20 titik loop izin.
   - FE: ±25 titik `permissions.includes` langsung di luar `can()`.
   - Konsumen yang terlewat menolak super admin tanpa pesan.
2. **Di sedikitnya 12 tempat, memegang izin justru membatasi atau mengubah akses.** Ini membuat "anggap punya semua" di lapisan pembaca tidak setara dengan "memegang semua":
   - Staf AP procurement dipersempit ke dokumennya sendiri (`pengajuan_barang_daftar_ap.go:31-60`).
   - Pemisahan izin asli vs efektif menjaga antrean "Perlu Aksi Saya" (`konteksPeranAsli`, bip-erp#2503).
   - Menu terkunci menolak tanpa `menu.<kunci>`.
   - KPI dan marketing jatuh ke `own` tanpa penanda reach.
   - Daftar pemegang izin mencocokkan string persis (`permission_holders.go:168`), sehingga super admin tak pernah terdaftar sebagai penyetuju atau penerima notifikasi.
3. **`system_roles` tidak bisa diwakili satu nilai.** Peran insentif (`host_live`, `icc`, …) dan `ga: security` adalah persona, bukan tingkatan (`shared-library/common/roles.go:14-31`). MyBharata membaca nilai yang tak dikenal sebagai `staff` (`system_roles.dart:13-16`).
4. **Bentrok dengan ADR yang ada.**
   - [[ADR - 0164 Hak Akses Satu Pintu, Peran Dibawa Paket Hak dan Dirakit saat Token Terbit]] §5/§6 (🟢 Diterima) mewajibkan bentuk keluaran token tidak berubah.
   - [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]] menolak super-akses untuk `menu.*`.
5. **Usulan itu tidak menolong orang yang bukan super admin.** Direktur, misalnya, memegang paket lihat-semua di jabatannya ([[CORE - RBAC dan Permission Set]] §Direktur), sehingga tetap terpental.

**Yang sudah ada dan dipakai ulang.**
- Pola paket bawaan yang disinkron ulang tiap service start (ADR 0164).
- Perakit token tunggal `rakitHakToken` (`services/employee/hak_token.go:87`), dipakai keempat jalur penerbitan token.
- Mesin reach `HigherReach` dan penanda `<modul>.$reach.<level>`.
- Pola `budget.superadmin` (`shared-library/common/catalog_budget.go:175-181`): satu paket yang dimekarkan jadi seluruh izin, dibatasi satu modul.
- Preseden token di `localStorage`: Task Manager menyimpan `erp_token` di sana ([[CORE - SSO Flow]]).

**Asumsi dan risiko yang belum terukur.**
- Belum diukur di prod akun mana yang tokennya sudah melewati 4 KB. Pengukurannya baca saja, lewat alat `banding_token` di employee-service. Tanpa angka itu, jumlah orang yang hari ini terpental adalah dugaan.
- Ukuran token pemegang Semua Izin belum dihitung. Katalog 16 modul ±150+ izin ditambah penanda reach diperkirakan 7-10 KB per salinan. Ini jauh di bawah 32 KB, tapi menjadi plafon baru yang perlu dijaga (§Consequences).

## Decision

### A. Token login Web ERP disimpan di `localStorage`, bukan cookie

1. JWT ditulis, dibaca, dan dihapus **hanya** lewat satu modul `sesi-token`. Tujuh pembaca `getCookie("token")` yang ada hari ini memanggilnya, tidak lagi membaca cookie sendiri.
2. `proxy.ts` tetap menggerbang keberadaan sesi, lewat **cookie penanda kecil** tanpa isi token. Masa berlakunya sama dengan `exp` token, dan ia ditulis, diperbarui saat refresh, dan dihapus bersama tokennya.
3. **Kenapa tidak cookie yang dipecah.** Cookie ikut **setiap** request ke server Next (halaman, aset, `/api/*`), dan server Node punya batas header bawaan sendiri (16 KB, diverifikasi di `/plan`). Memecah cookie hanya memindahkan plafon ke tempat yang sama tidak terlihatnya, dan plafon itu tumbuh mengikuti katalog izin. `localStorage` tidak ikut request mana pun.
4. **Keamanan setara dengan hari ini.** Cookie `token` sekarang ditulis JavaScript tanpa `httpOnly` (`login/page.tsx:181`), jadi skrip di halaman sudah bisa membacanya. Pindah ke `localStorage` tidak menambah permukaan XSS.
5. Cookie `system_roles` **tetap**, karena `proxy.ts` menggerbang rute darinya. Ukurannya satu kunci per modul, jauh di bawah batas. Pembaruannya saat refresh ada di luar lingkup ADR ini.
6. Pengguna yang sedang login saat rilis keluar sekali (cookie lama tak dibaca lagi). Itu diterima. Tidak dibuat jalur migrasi cookie ke `localStorage`, karena jalur semacam itu harus membaca token yang justru bisa sudah hilang.

### C. Paket bawaan "Semua Izin" dimekarkan saat token terbit

1. Satu paket **bawaan** dengan kunci tetap, didefinisikan di kode dan disinkron ulang tiap start seperti paket bawaan lain (ADR 0164). Paket ini **tidak dapat disunting isinya** dari layar, karena isinya bukan daftar melainkan aturan "seluruh katalog".
2. **Dimekarkan di perakit izin employee-service**, satu-satunya tempat izin efektif dirakit (`hitungIzinEfektif`, dipanggil `rakitHakToken`), menjadi:
   - seluruh izin dari setiap katalog terdaftar, **kecuali modul `menu`** (ADR 0039: tidak ada super-akses untuk menu terbatas);
   - penanda `<modul>.$reach.all` untuk setiap modul yang dimekarkan.
3. **Bentuk klaim `permissions` tidak berubah**: tetap daftar izin katalog + penanda. Karena itu tak ada konsumen BE/FE/mobile yang perlu diajari apa pun, dan logika "memegang izin membatasi" (staf AP, antrean asli vs efektif) berperilaku persis seperti pada orang yang memegang izin itu secara nyata. Perilaku itu sudah diuji.
4. **Peran modul (`system_roles`) tidak disentuh** paket ini. Peran tetap lewat jalurnya sendiri (peran tersimpan, turunan jabatan, atau paket peran ADR 0164).
5. **Gerbang penetapan mengikuti gerbang yang ada.** Penetapan ke akun memakai `RequireITStaff`, penetapan ke posisi memakai gerbang interim posisi. Keduanya **tidak** dinaikkan ke Supervisor IT. Alasannya: per 2026-10-12 perusahaan belum punya Supervisor IT, dan seluruh personel IT berperan staf (keputusan user).
6. **Pengaman pengganti: paket ini tidak bisa dipasang ke diri sendiri.** `PATCH /account/permission-sets` hari ini menerima `employee_id` siapa pun, termasuk pemanggil (`services/employee/main.go:6696-6740`), sehingga staf IT mana pun bisa memberi dirinya akses penuh. Karena itu, penetapan paket Semua Izin ditolak bila:
   - `employee_id` sasaran = pemanggil, **atau**
   - posisi sasaran = posisi yang sedang dipegang pemanggil.
   Rekan IT lain tetap bisa memasangkannya. Penolakan ini hanya berlaku untuk paket Semua Izin. Paket lain tidak berubah.
7. **Guard non-izin tetap menang.** Contohnya: larangan menyetujui pengajuan sendiri (`pengajuan_budget_approval_logic.go:27-29`, `pengajuan_barang_gate.go:290-295`, payroll `run_jenjang.go:142-145`), dan penolakan akun pihak luar (paket ini tidak dapat dipasang ke akun luar, mengikuti `gerbangJalurKaryawan`).

### Ditolak

- **B. Satu penanda super admin di token yang dipahami helper bersama.** Ditolak karena butir 1-5 di §Context. Satu-satunya keuntungannya (token kecil) hilang begitu A berlaku.
- **Pemekaran penanda di gateway.** Ditolak user sejak awal. Gateway juga tidak memegang katalog (katalog didaftarkan per service saat start).

## Consequences

- **Urutan rilis**: A mendahului C. C memperbesar token pemegangnya, jadi tanpa A paket Semua Izin justru membuat pemegangnya terpental lebih pasti. **C tidak boleh naik ke prod sebelum A live.**
- **Plafon baru = buffer server 32 KB**, dan token dikirim lewat `Authorization` saja (tidak lagi dua kali lewat cookie + Bearer). Pemegang Semua Izin adalah kasus terburuk mutlak, jadi ukurannya wajib diukur saat C diverifikasi dan dicatat di [[CORE - RBAC dan Permission Set]]. Katalog yang tumbuh menambah ukuran ini.
- **ADR 0164 §5/§6 tidak dilanggar.** Bentuk keluaran tidak berubah. Pemegang Semua Izin sengaja menghasilkan klaim yang berbeda dari sebelumnya, tapi itu karena paketnya baru dipasang, bukan karena perakitan berubah. Alat banding token tetap berlaku untuk akun lain.
- **Daftar pemegang izin** (`permission_holders.go`) membaca izin efektif dari perakit yang sama, sehingga pemegang Semua Izin **akan** muncul sebagai pemegang setiap izin. Mereka bisa terpilih sebagai penyetuju dan menerima notifikasi setiap modul. Ini bisa mengejutkan dan perlu ditinjau di `/plan`: apakah pemekaran diberlakukan juga di daftar pemegang, atau hanya di token.
- **Lintas perusahaan ikut terbuka.** `BolehLintasPerusahaan` (`shared-library/common/company_scope.go:55-60`) menerima pemegang izin `*.cross_company`, jadi pemegang Semua Izin bisa membaca data tenant lain. Itu konsekuensi sadar dari "semua izin".
- **Berlawanan arah dengan [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]]** (🟡 Diusulkan), yang mengusulkan agar super-akses tidak lolos gerbang persetujuan. Bila ADR 0137 diterima kelak, paket Semua Izin harus ikut ditinjau (misalnya izin persetujuan dikecualikan dari pemekaran).
- **Deploy**:
  - A: erp-frontend saja, tanpa perubahan kontrak.
  - C: employee-service lebih dulu (paket bawaan tersinkron saat start), baru erp-frontend untuk layar paket.
  - Tidak ada env baru. Prod dijalankan manusia (skill `deploy-bip-erp` §0).
- **Hak berlaku saat token terbit.** Memasang atau mencabut Semua Izin baru berlaku pada login atau refresh berikutnya, sama seperti paket lain (ADR 0030).
- Dok domain: [[CORE - RBAC dan Permission Set]] (paket Semua Izin) dan [[APP - Web ERP]] (penyimpanan token). Papan kerja: `Workspace/ANALISA - Token Login dan Paket Semua Izin.md` (privat, tidak terbit).
