# Rencana 4 - MyBharata Mobile (tenant-awareness)

> **Untuk pekerja agentic:** SUB-SKILL WAJIB: superpowers:subagent-driven-development atau superpowers:executing-plans. Langkah pakai checkbox (`- [ ]`).

**Goal:** Karyawan perusahaan pilot bisa memakai MyBharata (absen, jadwal, izin/cuti) dengan data ter-scope perusahaannya, tanpa asumsi single-company yang salah.

**Prasyarat:** Rencana 1 & 2 (backend company + presensi disaring). **Deploy BE dulu.**

**Architecture:** Mobile **hampir tidak berubah**. `AuthInterceptor` menambah `Authorization: Bearer <token>` ke SEMUA request (`lib/src/core/api/auth_interceptor.dart:18-28`), dan endpoint presensi tak mengirim identifier perusahaan (server tahu dari JWT). WiFi/lokasi diambil dari BE (`/api/attendance/networks`), bukan hardcoded -> verifikasi WFO otomatis ikut per-perusahaan. Yang tersisa: buang tampilan info perusahaan yang **hardcoded**, dan (opsional) simpan/ tampilkan identitas perusahaan.

**Tech Stack:** Flutter (Clean Architecture, Dio, get_it), package `my_bharata`. Repo: `c:\Data utama\Aplikasi\Office\erp\mybharata-app`. PR ke branch `dev`, **wajib naikkan versionCode** (pubspec) agar bisa publish.

## Global Constraints
- **BIP tak berubah.** Karyawan BIP di mobile berperilaku identik.
- **1 login = 1 karyawan = 1 perusahaan** (implisit dari JWT). TIDAK ada "admin pusat berpindah perusahaan" di mobile.
- PR ke `dev`, naikkan versi via `dart scripts/increment_version.dart` (atau update_version.dart). Loading pakai ShimmerBox.
- **Git**: branch mis. `feat/tenant-mobile`, commit tanpa `Co-Authored-By`.

---

### Task 0: Verifikasi "tanpa perubahan" (paling penting dulu)

Buktikan hipotesis bahwa alur inti presensi mobile sudah ter-scope otomatis oleh JWT, sebelum menyentuh kode.

- [ ] **Step 1 (dev, BE Rencana 1+2 aktif):** Login MyBharata sebagai karyawan **perusahaan pilot** (akun dibuat via web Rencana 3). Lakukan: absen masuk (`POST /api/attendance/tap?method=Mobile`), lihat jadwal, lihat riwayat, ajukan izin.
- [ ] **Step 2:** Verifikasi via web HR: data muncul di perusahaan pilot, TIDAK di BIP. Jaringan WiFi yang diizinkan sesuai perusahaan pilot (`GET /api/attendance/networks`).
- [ ] **Step 3:** Login karyawan BIP -> semua identik seperti sekarang (regresi).
- [ ] **Step 4:** Catat temuan. Jika semua lolos tanpa ubah kode -> hanya Task 1-2 (kosmetik info perusahaan) yang tersisa.

*(Bila ada endpoint yang TERNYATA bocor/gagal karena mobile mengirim sesuatu yang company-agnostic, tambahkan task perbaikan spesifik di sini berdasar temuan.)*

---

### Task 1: Ganti info perusahaan hardcoded -> data nyata

`company_info_page.dart` memakai `CompanyInfoModel.dummy()` yang berisi "PT Bharata Internasional Pharmaceutical" hardcoded -> salah untuk perusahaan lain.

**Files (Modify):** `lib/src/features/company_info/data/models/company_info_model.dart:54-73` (buang/kurangi `dummy()`), `lib/src/features/company_info/presentation/pages/company_info_page.dart:14`. Mungkin tambah datasource `GET` info perusahaan aktif.

- [ ] **Step 1:** Tentukan sumber info perusahaan aktif: endpoint ringan (mis. `/api/employee/me` atau `/api/employee/master/companies/{key}`) yang mengembalikan nama/alamat perusahaan user. (Butuh dukungan BE bila belum ada; kalau MVP cukup nama perusahaan dari profil, ambil dari situ.)
- [ ] **Step 2:** Ganti `final companyInfo = CompanyInfoModel.dummy();` -> ambil dari repository/bloc yang fetch per perusahaan aktif; tampilkan ShimmerBox saat loading.
- [ ] **Step 3:** Uji: karyawan pilot melihat info perusahaannya; karyawan BIP melihat info BIP.
- [ ] **Step 4:** Commit `feat(company-info): tampilkan perusahaan aktif, buang dummy hardcoded`.

---

### Task 2: (Opsional) simpan identitas perusahaan dari login

Hanya bila perusahaan perlu ditampilkan di profil/header mobile. Bila tidak, LEWATI (JWT sudah cukup untuk scoping).

**Files (Modify):** `lib/src/core/helper/secure_storage_helper.dart` (+key `company_id`/`company_name`), `lib/src/features/auth/data/implements/auth_implements.dart:49-80` (simpan dari response login bila BE mengirim `company_id`).

- [ ] **Step 1:** Bila response login BE memuat `company_id`/`company_name`, simpan ke storage; expose via profil.
- [ ] **Step 2:** Tampilkan label perusahaan di halaman profil (opsional).
- [ ] **Step 3:** Uji tampil benar per perusahaan.
- [ ] **Step 4:** Commit `feat(auth): simpan identitas perusahaan dari login (opsional)`.

---

### Task 3: (Opsional) label bangunan dinamis

`lib/src/core/constants/building_names.dart` berisi `'Head Office'`, `'Warehouse Tinggarjaya'` dll (khas BIP). Hanya perlu bila perusahaan lain punya lokasi berbeda yang ditampilkan.

- [ ] **Step 1:** Bila dipakai untuk tampilan lokasi presensi, jadikan bersumber dari data BE (lokasi/site per perusahaan) alih-alih konstanta. Bila hanya label kosmetik minor, tunda.
- [ ] **Step 2:** Commit bila diubah.

---

### Task 4: Rilis pilot

- [ ] **Step 1:** Naikkan versi: `dart scripts/increment_version.dart` (versionCode `pubspec.yaml`).
- [ ] **Step 2:** PR ke `dev` (cek `gh pr view` sebelum menganggap open).
- [ ] **Step 3:** Uji E2E dari HP oleh 1-2 karyawan perusahaan pilot: absen, jadwal, izin -> muncul benar di HR pilot.
- [ ] **Step 4:** Setelah lolos, siapkan rilis ke perusahaan pilot.

---

## Self-review
- Cakupan spec Bagian 3 (login mobile perusahaan baru) + tolok ukur sukses fase 1 (E2E pilot dari HP): Task 0 (verifikasi otomatis), Task 1 (info perusahaan benar), Task 4 (rilis). OK.
- Placeholder: tidak ada; file:line konkret. Task 2/3 sengaja OPSIONAL & bersyarat (YAGNI) - hanya bila perusahaan perlu ditampilkan.
- Konsistensi: mengandalkan JWT dari Rencana 1; tak menduplikasi scoping backend. Notifikasi ADA di Rencana 2 (bukan di sini).
- **Temuan kunci:** mobile minim perubahan; Task 0 (verifikasi) adalah inti - membuktikan alur presensi sudah ter-scope tanpa ubah kode, sisanya kosmetik.
