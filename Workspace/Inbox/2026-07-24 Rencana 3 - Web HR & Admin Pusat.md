# Rencana 3 - Web HR & Admin Pusat (erp-frontend)

> **Untuk pekerja agentic:** SUB-SKILL WAJIB: superpowers:subagent-driven-development atau superpowers:executing-plans. Langkah pakai checkbox (`- [ ]`).

**Goal:** Web HR sadar-perusahaan: HR tiap perusahaan lihat datanya sendiri, admin pusat bisa memilih/berpindah perusahaan, kelola master Perusahaan, dan pilih perusahaan saat Buat Karyawan.

**Prasyarat:** Rencana 1 (backend company + `GET/POST /master/companies`) & Rencana 2 (presensi disaring per company). **Deploy BE sebelum FE.**

**Architecture:** Untuk user biasa, perusahaan diturunkan otomatis dari JWT di gateway (tanpa aksi FE). Untuk **admin pusat**, FE mengirim parameter `company=<key>` yang di-honor backend HANYA bila peran = admin pusat (override); selain itu diabaikan. Kelola Perusahaan & pemilih perusahaan meniru pola `departments-manager` + `use-companies` yang sudah ada.

**Tech Stack:** Next.js, pnpm, shadcn/ui, react-query, react-i18next (id+en), react-hook-form+zod. Test: vitest. Verifikasi: `pnpm exec tsc --noEmit` + `pnpm lint`.

## Global Constraints
- **BIP tak berubah.** Tanpa pemilihan perusahaan, tampilan HR BIP identik seperti sekarang.
- **i18n dua bahasa**: setiap teks baru ke `src/i18n/locales/id.ts` DAN `en.ts` (ADR 0010). Loading pakai ShimmerBox, bukan spinner.
- **Reuse komponen** (pola `departments-manager`, `use-companies`), jangan bikin tiruan.
- **Git**: branch `feat/tenant-web`, commit sering tanpa `Co-Authored-By`. Git via PowerShell. Finalize `pnpm lint` penuh.
- Peran **admin pusat** didefinisikan di Task 1 (backend) - interim memakai `it:admin`/role baru `group:admin`.

---

### Task 1 (backend): peran admin pusat + override perusahaan

**Files (Modify, bip-erp):** `services/attendance/company.go` (helper `effectiveCompany`), pemanggil HR/report (`hr_admin.go`, `main.go /report,/entries`). Test: `company_test.go`.

**Interfaces:** `func effectiveCompany(c *fiber.Ctx, isCentralAdmin bool) string` -> bila `isCentralAdmin && c.Query("company") != ""` kembalikan query; selain itu `common.CompanyID(c)`.

- [ ] **Step 1 (test gagal):**
```go
func TestEffectiveCompany(t *testing.T) {
	// admin pusat + query -> pakai query
	// non-admin -> selalu company sendiri (abaikan query)
}
```
(pakai fiber `app.Test` set header `BIP-Company-ID` + query `?company=`, atau ekstrak logika murni menerima `(own, query string, isAdmin bool)`.)
- [ ] **Step 2:** FAIL.
- [ ] **Step 3:** Implementasi `effectiveCompany`; peran admin pusat dicek dari `Identity.SystemRoles` (mis. `system_roles["group"]=="admin"` atau interim `it:admin`). Ganti pemakaian `common.CompanyID(c)` di HR-list/report/entries menjadi `effectiveCompany(c, isCentralAdmin(id))`.
- [ ] **Step 4:** PASS; build.
- [ ] **Step 5:** Commit (bip-erp) `feat(attendance): override perusahaan utk admin pusat via ?company=`.

---

### Task 2: Plumbing perusahaan di FE (cookie + tampil)

**Files (Modify):** `src/app/login/page.tsx:176-192` (set cookie `company_id` dari response login), `src/features/erp/auth/hooks/use-auth.ts:7-56` (expose `companyId`), `src/lib/axios.ts:26-38` (hapus cookie `company_id` saat logout).

- [ ] **Step 1:** Di `handleLoginSuccess`, tambah `setCookie("company_id", response.data.company_id)` (BE mengirimnya sejak Rencana 1). Di `redirectToLogin`/logout hapus cookie itu.
- [ ] **Step 2:** `useAuth()` kembalikan `companyId` dari cookie (untuk badge/label perusahaan aktif).
- [ ] **Step 3:** `tsc` + `lint` bersih.
- [ ] **Step 4:** Commit `feat(auth): simpan & expose company_id user`.

---

### Task 3: Halaman "Kelola Perusahaan" (master tenant)

Meniru `departments-manager.tsx` + `use-fetch-departments`/`use-upsert-department`; endpoint `GET/POST /api/employee/master/companies` (Rencana 1). Gating tulis = admin pusat.

**Files (Create):** `src/features/hris/companies/components/companies-manager.tsx`, `company-form-modal.tsx`, `src/features/hris/companies/hooks/{use-fetch-companies,use-upsert-company}.ts`, `types.ts`; halaman `src/app/(main)/hris/companies/page.tsx`. Modify: `src/components/layout/sidebar-menus.tsx` (+menu), `i18n/locales/{id,en}.ts`.

- [ ] **Step 1 (test gagal, vitest):** render `CompaniesManager` menampilkan kolom Key/Nama/Kode/Status + tombol tambah (mock hook). Assert judul & tombol.
- [ ] **Step 2:** FAIL.
- [ ] **Step 3:** Implementasi manager+modal+hook (mirror departemen), tipe `MasterCompany {key,name,code,active}`; hook `useFetchCompanies` (`GET /master/companies`), `useUpsertCompany` (`POST/PUT`). Tambah menu "Kelola Perusahaan" ke grup `it`/`hris` di `sidebar-menus.tsx`. i18n `hris.companies.*` (id+en).
- [ ] **Step 4:** vitest PASS; `tsc`+`lint`.
- [ ] **Step 5:** Commit `feat(hris): halaman Kelola Perusahaan (master tenant)`.

---

### Task 4: Pemilih perusahaan untuk admin pusat

Komponen header (bukan item menu) yang muncul HANYA untuk admin pusat; pilihannya disimpan (context/cookie) dan **diteruskan sebagai `?company=` pada request presensi/HR**.

**Files (Create):** `src/features/hris/companies/components/company-switcher.tsx`, context/provider `company-scope-context.tsx`. Modify: header layout (tempat `useAuth`), `src/lib/axios.ts:67-96` (interceptor: bila ada "selected company" utk admin pusat, tambahkan param `company`), atau tambahkan param di hook presensi.

- [ ] **Step 1:** Buat context menyimpan `selectedCompany` (default = companyId sendiri). Switcher pakai `useFetchCompanies`, hanya render bila `isCentralAdmin`.
- [ ] **Step 2:** Sisipkan `company=<selected>` pada request presensi/HR (paling bersih: di hook `use-fetch`/`use-report` tambah `params.company` bila admin pusat & terpilih). Saat ganti perusahaan, `queryClient.invalidateQueries` presensi (pola `queryClient.clear()` di login).
- [ ] **Step 3:** `tsc`+`lint`.
- [ ] **Step 4:** Commit `feat(hris): pemilih perusahaan admin pusat (?company override)`.

---

### Task 5: Field "Perusahaan" di Buat Karyawan

Admin pusat memilih perusahaan saat mendaftarkan karyawan; nilai dikirim sebagai `work_data.company_id`.

**Files (Modify):** `src/features/hris/employee/components/modals/create-employee/step1.tsx:67-118` (tambah `SelectForm`/`ComboboxForm` "Perusahaan"), skema form employee (+`company_id`). Reuse `useFetchCompanies` (Task 3).

- [ ] **Step 1:** Tambah field Perusahaan di `FormGroup` employment, sumber opsi `useFetchCompanies()`. Default = perusahaan admin (biasanya BIP). Field wajib (sesuai keputusan: prefix employee_id + perusahaan wajib).
- [ ] **Step 2:** Kirim `work_data.company_id` di payload create-employee (BE Rencana 1 Task 7 menerimanya).
- [ ] **Step 3:** `tsc`+`lint`; dev: buat karyawan di perusahaan pilot -> tersimpan dgn company benar; muncul di HR pilot, bukan BIP.
- [ ] **Step 4:** Commit `feat(hris): pilih Perusahaan saat Buat Karyawan`.

---

### Task 6: Verifikasi & regresi web

- [ ] **Step 1:** `pnpm exec tsc --noEmit` + `pnpm lint` penuh -> bersih.
- [ ] **Step 2:** vitest komponen baru -> PASS.
- [ ] **Step 3 (dev):** login HR BIP -> tampilan presensi/laporan identik seperti sekarang (regresi). Login admin pusat -> bisa lihat & berpindah perusahaan. Login HR pilot -> hanya data perusahaannya.
- [ ] **Step 4:** Commit.

---

## Catatan (prasyarat lintas-rencana)
- **Master departemen/posisi per-perusahaan**: agar dropdown departemen/posisi di web & Buat Karyawan benar per-perusahaan, `master_department` (+positions) perlu `company_id` + penyaringan (perubahan BACKEND). Ini item terpisah - masukkan ke Rencana 2 (perluasan) atau rencana backend tersendiri sebelum Task 5 dianggap penuh. Untuk pilot minimal, perusahaan baru boleh memakai set departemen sendiri yang dibuat admin pusat.
- **Reuse vs entitas payroll**: FE sudah punya `Company` (Badan Usaha payroll, `features/hris/payroll/use-companies.ts`). Tenant Company (Rencana 1) SENGAJA terpisah; jangan campur. Bila kelak disatukan, itu keputusan terpisah.

## Self-review
- Cakupan spec Bagian 3 (onboarding, peran per-perusahaan, login, web HR, admin pusat): Task 1 (peran+override), Task 3 (kelola perusahaan), Task 4 (switcher admin pusat), Task 5 (daftar karyawan pilih perusahaan), Task 2 (plumbing). OK.
- Placeholder: tak ada; file:line konkret + kode representatif + cara uji.
- Konsistensi: `company_id`/`?company` konsisten; reuse pola departemen & `use-companies`; i18n dua-locale.
