# ANALISA - Industrial Relation

Papan kerja hasil `/analisa-kebutuhan` 2026-09-10. Keputusan di [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]], cara kerja di [[HRIS - Industrial Relation]].

**Kebutuhan asal** (dari manajemen): "menu baru di HR Industrial Relation untuk budaya kepatuhan (sepatu, lanyard, dsb.); catat pelanggaran diam-diam di MyBharata saat jam kerja; penilaian muncul besok di masing-masing departemen." Wawancara menyempitkannya jadi **coaching loop non-sanksi**: sinyal pembinaan (bukan KPI/gaji/SP), dicatat petugas IR/HR khusus, dilihat supervisor + orangnya sendiri, cukup tak-real-time. Grounding: mesin rekap per-departemen & gerbang tiga-arah sudah matang dan dipinjam; entitas catatan + katalog + kanal MyBharata benar-benar baru.

**Urutan**: T1→T2→T3 (backend berantai), lalu T4 (Web) & T5 (Mobile) setelah kontrak BE turun, tutup dengan T6 (verifikasi end-to-end). ⛔ **Deploy BE sebelum FE/Mobile** (perubahan kontrak).

---

## T1. BE — Master katalog jenis pelanggaran kepatuhan

Koleksi master baru (mis. `compliance_violation_type`) + CRUD, digerbang keanggotaan modul HR. Nilai awal contoh: Sepatu, Lanyard, Atribut. **Data-driven, bukan enum** (jangan tiru `ViolationCategory` hardcoded di `warning.go`).

`/start-task buat master data jenis pelanggaran kepatuhan (compliance_violation_type) + CRUD digerbang modul HR di employee-service`

**Cara verifikasi**: `POST`/`GET` katalog lewat gateway (`/api/employee/...`), tambah satu jenis, muncul di `GET`. Bukan sekadar unit test hijau.

## T2. BE — Koleksi `compliance_note` + catat + baca tiga-arah

**Bergantung T1.** Struct `ComplianceNote` (`employee_id`, `company_id`, `category` rujuk katalog, `reason`, foto `MinIOFile`, `recorded_by`, `recorded_at`, `expires_at`). `POST` diperiksa server terhadap wewenang pencatat. Status aktif/hangus **diturunkan saat baca** (pola `WarningStatus`). Gerbang baca: HR se-perusahaan / karyawan atas dirinya / atasan via `SupervisedDepartmentsStrict`. Filter departemen via `ResolveDepartmentFilter`+`ExpandToDepartmentGroup`.

`/start-task buat koleksi compliance_note di employee-service: POST catat (gerbang pencatat) + GET baca tiga-arah (SupervisedDepartmentsStrict), status hangus diturunkan saat baca`

**Cara verifikasi**: lewat gateway — petugas HR `POST` satu catatan; karyawan target `GET /me/...` melihatnya; atasan departemen lain **tidak** melihatnya; rekan sedepartemen **tidak** melihatnya. Uji `app.Test(httptest.NewRequest(...))` untuk jalur galat, DAN satu panggilan sungguhan lewat gateway (test fungsi murni tak menangkap cacat glue).

## T3. BE — Rekap pelanggaran per-departemen (saat baca)

**Bergantung T2.** Endpoint rekap per-departemen meniru `kpi_ringkasan_departemen.go` (agregasi + pemanasan), atas `compliance_note`, **bukan** `kpi_score`. Menampilkan tanggal yang sudah lewat ("besoknya"). ⛔ Jangan menulis `kpi_score`; jangan jadikan sumber KPI ([[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]).

`/start-task tambah endpoint rekap compliance_note per-departemen di employee-service, meniru pola kpi_ringkasan_departemen, tanpa menyentuh kpi_score`

**Cara verifikasi**: `GET` rekap lewat gateway untuk satu departemen mengembalikan cacahan yang cocok dengan catatan yang di-`POST` di T2. Uji gotcha HRGA: filter label grup ("HRGA") mengembalikan anggota nyata, bukan 200 berisi nol baris.

## T4. Web ERP — Menu HR "Industrial Relation" + halaman rekap & catatan

**Bergantung T3 (kontrak BE turun).** Tiru struktur modul `surat-peringatan` (MainTable + Banner bare di toolbar, `useTableState`). Pola self-vs-team dari `kpi-departemen-atau-saya.tsx` (probe 403 → tampilan "catatan saya"). Tambah entri menu di `menus.hris` (`sidebar-menus.tsx`) + `perm`. i18n **dua bahasa** id+en + `industrial-relation-keys.test.ts`. Dropdown departemen: pertimbangkan `grouped` sesuai jebakan HRGA. Jangan `p-6` sendiri (Container sudah `p-4 sm:p-6`); tombol kembali pakai `SidebarBackButton`.

`/start-task buat menu & halaman HR Industrial Relation di erp-frontend (rekap per-departemen + catatan diri) meniru modul surat-peringatan & pola kpi-departemen-atau-saya`

**Cara verifikasi**: `pnpm tsc --noEmit`, `pnpm lint`, `pnpm test`, `pnpm build` (lokal, bandingkan baseline `origin/main`). Jalankan lewat preview: supervisor melihat rekap tim, karyawan melihat catatan dirinya. **Alur pengguna utuh** sebagai orang, bukan hanya `curl`.

## T5. MyBharata — Fitur catat pelanggaran (petugas IR/HR)

**Bergantung T2/T3.** Modul fitur baru (mis. `lib/src/features/compliance_note/`). Menu digerbang `RoleGuard` (petugas HR). Reuse `AssigneeSelectSheet` (pilih karyawan target), pola `FormData`+`MultipartFile` (foto+catatan bukti). Endpoint baru di `url.dart`. Bagian "catatan kepatuhan saya" untuk karyawan biasa. l10n baru di `app_id.arb` + `app_en.arb`.

`/start-task buat fitur catat pelanggaran kepatuhan di my-bharata untuk petugas HR (RoleGuard + AssigneeSelectSheet + upload foto) + bagian catatan saya`

**Cara verifikasi**: build app; petugas melihat menu, non-petugas tidak; `POST` satu catatan lewat gateway berhasil dan terlihat di rekap Web (T4). Rilis mobile menaikkan **version name + versionCode** (bukan restart).

## T6. Verifikasi end-to-end + tutup dok

**Bergantung T4/T5.** Satu perjalanan utuh: petugas mencatat di MyBharata → rekap muncul di menu HR keesokan tampilannya → supervisor & karyawan melihat sesuai gerbang. Perbarui status [[HRIS - Industrial Relation]] dari 🟡 ke ✅/⚠️ sesuai kenyataan, dan `/sync-docs`.

**Cara verifikasi**: bukti nyata (screenshot rekap + catatan yang cocok), bukan test hijau saja. Angka nol yang mencurigakan = pertanyaan, bukan kabar baik.

---

## Yang TIDAK jadi dikerjakan, beserta alasannya

- **Tumpang di `employee_warning`** (Opsi B): mencampur sinyal pembinaan dengan sanksi bisa-PHK; ditolak di [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]] §1.
- **Jadikan sumber KPI** (Opsi C): menulis `kpi_score` = jadi KPI resmi yang menyentuh gaji; bertentangan dengan sifat "sinyal".
- **Notifikasi/pengingat harian H+1**: ditunda sadar — coaching-only + non-real-time; rekap dibaca saat menu dibuka. Menambahkannya = kategori inbox baru (deploy 2 container) + revisi ADR.
- **Eskalasi otomatis ke SP**: naik ke SP tetap keputusan manusia; bila diputuskan perlu jalur usulan, butuh ADR tersendiri.
