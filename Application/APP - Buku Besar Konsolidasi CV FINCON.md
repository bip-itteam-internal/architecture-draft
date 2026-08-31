> **Status**: ⚠️ **Implemented (ada catatan)** — aplikasi berjalan penuh (jurnal → buku besar → laporan → konsolidasi), **tetapi hidup sepenuhnya di luar ERP**: repo pribadi di luar org `bip-itteam-internal`, database Supabase sendiri, login sendiri (7 akun hardcoded), dan **membangun ulang general ledger yang menurut [[ADR - 0001 Akuntansi via Accurate]] adalah ranah Accurate**. Didokumentasikan di sini supaya keberadaannya berhenti tak terlihat; keputusan arah ada di [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]] (🟡 masih Proposed).

## Deskripsi

*Aplikasi akuntansi double-entry + **konsolidasi** untuk **40 CV** grup Bharata: input jurnal (kas, piutang, utang, umum, penyesuaian), buku besar per akun per CV, laporan keuangan individual (laba rugi, neraca, arus kas metode langsung, perubahan ekuitas), daftar & penyusutan aset tetap, lalu **kertas kerja konsolidasi 40 kolom + jurnal eliminasi intercompany**. Sebagian jurnal kas juga didorong ke sebuah **Google Sheets** lewat webhook. Nama di layar: **CV FINCON**.*

- **Repo**: `consolidated-accounting-app` — **repo Git terpisah dan PRIBADI**: `github.com/Rz17-code/consolidated-accounting-app`, visibility **private**, pemilik akun perorangan (**bukan** org `bip-itteam-internal`). Branch utama `main`. 100 commit, 2026-08-05 → 2026-08-28, **satu kontributor**.
- **Stack**: Next.js **16** (App Router) + React **19** + TypeScript; komponen fitur masih **`.jsx` tanpa tipe**; linter **oxlint**; ekspor Excel `xlsx` (SheetJS); ikon `lucide-react`. CSS satu berkas global `src/index.css` (1.421 baris) — **tanpa Tailwind**, tanpa design system bersama.
- **Package manager**: repo membawa `package-lock.json` (**npm**), menyimpang dari konvensi **pnpm** yang berlaku untuk seluruh repo JS/TS di workspace ini.
- **Backend**: **tidak punya backend sendiri** — langsung ke **Supabase (PostgreSQL)** dari browser dan dari Server Component, memakai `NEXT_PUBLIC_SUPABASE_URL` + `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`. **Tidak menyentuh** [[CORE - API Master Gateway]] sama sekali.
- **Pengguna**: staf akuntansi CV (lihat § Persona). Tak ada kaitan akun dengan SSO ERP ([[CORE - SSO Flow]]).
- **README repo menyesatkan** — isinya masih templat bawaan "React + Vite" padahal seluruh aplikasi sudah Next.js App Router; `AGENTS.md`/`CLAUDE.md` di repo itu di-generate `next dev`, bukan ditulis tim.

## Arsitektur & Alur Data

```
Browser ──► Supabase (PostgreSQL)          5 tabel: transactions, eliminations,
   │         ▲        ▲                     coa, companies, assets
   │         │        └── SSR: src/app/page.tsx menarik kelima tabel paralel
   │         └────────── Client: insert/update/delete langsung dari komponen
   │
   └──────► Google Apps Script webhook (NEXT_PUBLIC_GOOGLE_SHEETS_WEBHOOK_URL)
             payload {action: ADD|UPDATE|DELETE, ...} — hanya jurnal KAS
             dan saldo awal bulanan
```

- **Sumber kebenaran = Supabase.** `page.tsx` (Server Component) menarik kelima tabel, memetakan `snake_case` → `camelCase`, lalu meneruskannya sebagai `initialData` ke `AppClient`. Bila server mengembalikan kosong, klien jatuh ke `loadData()` yang mengembalikan **COA & daftar 40 CV bawaan kode**, bukan data kosong.
- **Cache lokal sengaja dimatikan sebagian**: `saveData()` menolak menulis `accounting_transactions` dan `accounting_eliminations` ke `localStorage` ("*to prevent stale sync issues*"), tetapi **COA, daftar perusahaan, dan aset tetap tetap ditulis** ke `localStorage`.
- **Tulis bersifat optimistik & tanpa transaksi**: state React diperbarui lebih dulu, panggilan Supabase menyusul di dalam `try/catch` yang hanya `console.error`. Kegagalan simpan **tidak terlihat pemakai**.
- **Middleware Supabase ada tapi tak dipakai untuk otorisasi**: `src/proxy.ts` hanya me-refresh cookie sesi Supabase; otentikasi aplikasi sepenuhnya berjalan di `AppClient` dengan daftar kredensial di kode.

## Modul / Fitur (Sudah Diimplementasikan)

Semua modul dirender dari satu `switch (activeTab)` di `src/app/AppClient.tsx`; tidak ada routing per halaman.

**Input jurnal** (hanya untuk peran `staff`)

| Menu | Berkas | Isi |
|---|---|---|
| Jurnal Kas (Simple) | `CashJournalForm.jsx` | Dua mode: **sederhana** (BKK/BKM — pilih kas/bank + kategori + nominal, sistem menyusun dua baris jurnalnya) dan **ganda** (multi-baris, wajib seimbang). Wajib menyentuh akun kas. Impor Excel. **Satu-satunya modul yang mendorong ke Google Sheets** |
| Jurnal Piutang | `ReceivableJournalForm.jsx` | Penjualan kredit, `journalType: 'piutang'` |
| Jurnal Utang | `PayableJournalForm.jsx` | Pembelian kredit, `journalType: 'utang'` |
| Jurnal Umum | `TransactionForm.jsx` (`type="umum"`) | Multi-akun bebas, wajib seimbang, impor Excel |
| Jurnal Penyesuaian | `TransactionForm.jsx` (`type="penyesuaian"`) | Penyesuaian akhir periode |
| Saldo Awal COA | `OpeningBalanceForm.jsx` | **Satu transaksi per CV** ber-id tetap `SALDO_AWAL_<companyId>`; disunting berulang, bukan ditambah. Draft disimpan di `localStorage`; templat Excel bisa diunduh |
| Saldo Awal Bulanan | `MonthlyOpeningBalanceForm.jsx` | ⚠️ **Hanya mengirim ke Google Sheets** — sengaja **tidak** disimpan ke Supabase ("*agar tidak ganda*"), jadi angkanya tak pernah masuk buku besar aplikasi ini sendiri |

**Laporan & analisis** (peran `staff` dan `senior`)

| Menu | Berkas | Isi |
|---|---|---|
| Riwayat Jurnal | `TransactionHistoryView.jsx` | Daftar + filter + sunting + hapus per transaksi; impor Excel. Tombol aksi hanya muncul untuk `staff` |
| Buku Besar | `LedgerView.jsx` | Mutasi per akun per CV |
| Laporan Keuangan | `ReportView.jsx` | 4 tab: Laba Rugi · Neraca · Perubahan Ekuitas · Arus Kas (metode **langsung**). Ekspor Excel per tab |
| Laporan Keuangan Bulanan | `MonthlyReportView.jsx` | Keempat laporan yang sama, dipecah **12 kolom bulan** dalam satu tahun |
| Financial Analysis | `FinancialAnalysisView.jsx` | Rasio bulanan: NPM, DAR, DER, Current Ratio |
| Aset Tetap | `FixedAssetsView.jsx` | Register aset + penyusutan garis lurus per bulan. **Kelompok mengikuti masa manfaat fiskal**: kelompok 1 (4 th), 2 (8 th), 3 (16 th), 4 (20 th), bangunan permanen (20 th), semi-permanen (10 th) |
| Konsolidasi | `ConsolidationView.jsx` | Kertas kerja: satu kolom per CV → total gabungan → kolom **eliminasi (debit/kredit)** → saldo konsolidasi. Jurnal eliminasi diinput di layar yang sama |
| Dasbor | `DashboardView.jsx` | Total aset/pendapatan/beban/laba gabungan, bar laba-rugi per CV, aktivitas terakhir, penanda CV yang saldo awalnya belum diisi |

**Pengaturan**

| Menu | Berkas | Isi |
|---|---|---|
| Bagan Akun (COA) | `COAView.jsx` | CRUD akun + impor Excel. **68 akun bawaan** di `DEFAULT_COA` |
| Cadangkan & Atur Ulang | `BackupView.jsx` | Ekspor JSON/Excel seluruh basis data, restore dari JSON, muat data simulasi. **Hanya untuk username `admin3`** |

**Mesin akuntansi** — seluruh perhitungan murni ada di `src/utils/accounting.js` (800 baris): `getLedgerBalances`, `calculateTrialBalance`, `calculateIncomeStatement`, `calculateBalanceSheet`, `calculateConsolidatedData`, `calculateCashFlowDirect`, `calculateChangesInEquity`, plus helper `isCashAccount` / `isReceivableAccount` / `isPayableAccount` dan `terbilang`. **Tidak ada satu pun test** di repo.

## Persona / Pengguna

Diturunkan dari `CREDENTIALS` dan `getAllowedCompanies` di `AppClient.tsx` — bukan dari master data.

| Persona | Peran & Divisi | Akses | Device |
|---|---|---|---|
| `admin1` … `admin6` | Staf akuntansi CV — tiap akun memegang **6–7 CV tetap** (admin1 = CV01–CV07, admin2 = CV08–CV14, admin3 = CV15–CV21, admin4 = CV22–CV28, admin5 = CV29–CV34, admin6 = CV35–CV40) | peran `staff`: seluruh menu input jurnal + laporan | Desktop |
| `admin3` | Sama seperti di atas, **plus** satu-satunya pemegang menu Cadangkan & Atur Ulang | `staff` + backup/restore/reset | Desktop |
| `user` | "Super Admin / Senior" | peran `senior`: **hanya baca** — seluruh menu input jurnal disembunyikan dan diblokir; melihat semua 40 CV | Desktop |

- **Tujuan**: menutup buku bulanan per CV dan menyusun laporan konsolidasi grup.
- **Pain point yang dijawab aplikasi**: 40 entitas × 4 laporan × 12 bulan tak praktis dikerjakan di spreadsheet, dan Accurate tidak menyediakan kertas kerja konsolidasi + eliminasi intercompany (lihat § Titik Temu).
- **Aksi utama**: input jurnal kas harian → cek buku besar → tutup bulan → tarik laporan/konsolidasi → ekspor Excel.

## Model Data (Supabase)

⚠️ **Tidak ada berkas migrasi, skema SQL, maupun definisi RLS di repo.** Bentuk tabel di bawah **direkonstruksi dari kode pemanggilnya**, bukan dari skema — perlakukan sebagai perkiraan sampai diperiksa di Supabase.

| Tabel | Kolom yang disentuh kode | Catatan |
|---|---|---|
| `transactions` | `id` (string, dibuat klien), `company_id`, `date`, `description`, `journal_type`, `items` (JSON: `accountCode`/`debit`/`credit`) | Baris jurnal disimpan sebagai **JSON di satu kolom**, bukan tabel baris jurnal tersendiri — jadi tak bisa di-`JOIN`/di-agregasi di sisi database |
| `eliminations` | `id`, `date`, `description`, `items` (JSON) | Jurnal eliminasi konsolidasi. **Tanpa `company_id`** — memang milik grup, bukan satu CV |
| `coa` | `code` (kunci), `name`, `type`, `normal_balance` | |
| `companies` | `id` (`CV01`…`CV40`), `code` (3 huruf), `name` | |
| `assets` | `id`, `company_id`, `name`, `purchase_date`, `cost`, `residual`, `group_key`, `group_name`, `years`, `created_at` | |

**Identitas transaksi dibuat di klien**: `'TX' + Date.now() + acak(0..999)`. Dua entri pada milidetik yang sama dari dua browser bisa bertabrakan; tak ada penjaga keunikan yang terlihat di kode.

## Titik Temu dengan ERP Bharata

Ini bagian yang paling menentukan. **40 CV di aplikasi ini bukan entitas asing — mereka sudah hidup di ERP dan di Accurate**, dan sebagian besar yang dihitung aplikasi ini sudah punya sumber kebenaran lain.

**Bukti bahwa entitasnya sama** (dari kode, bukan dugaan):

| Entitas di `DEFAULT_COMPANIES` | Muncul di mana lagi |
|---|---|
| `CV04 Pure Glow Lux` | **Badan usaha default payroll** — `services/payroll/models_company.go`, `models_config.go`, dan golden test slip gaji Juli 2026 |
| `CV08 Global Estetika Gemilang` | **Rekening bank Accurate** `BMRI 1800020258788`, `AccurateID 129903` (`services/integration/.../wallet_withdrawal_bank_test.go`) |
| `CV40 Alvia Glow Cosmetics` | Rekening BCA pada receipt finance nyata (spec Fase 2 monitoring withdrawal) |
| `CV23 Glow Skin Radiant`, `CV07 Radiant Fresh X` | **Proyek Accurate** 2354 & 2552 (`.task-plans/2026-08-26-beban-operasional-per-individu.md`) |
| `CV25 Pure Skin Lux` | Nama berkas report TikTok di [[Finance - Delete Data Finance lama]] |
| Ke-40-nya | [[Microservices - Payroll Service]] mencatat `payroll_company` berisi **41 dokumen** di prod — "cocok dengan skala HRD (1 PT + 40 CV)" |

**Perbandingan modul terhadap yang sudah ada di ERP:**

| Yang dilakukan CV FINCON | Padanan hari ini di ERP / Accurate | Hubungan |
|---|---|---|
| Bagan Akun 68 akun, dikelola di layar | COA milik **Accurate**; ERP membacanya, tak pernah menulis | **Duplikat** — bertentangan langsung dengan [[ADR - 0001 Akuntansi via Accurate]] |
| Jurnal umum/kas/piutang/utang/penyesuaian | Jurnal Accurate **~96 ribu baris**, dibaca `GET /api/integration/accounting/journals` ([[API - Integration Service]]) | Duplikat pencatatan |
| Buku besar, neraca saldo, neraca | `/accounting/account-balance` · `/accounting/balance-sheet` | Duplikat |
| Laporan laba rugi | `/accounting/profit-loss` — **sudah jadi sumber KPI** (`admin-nonops`) dan mengisi dashboard Tax & SPV FAT | Duplikat, dan **dua angka laba yang bisa berbeda diam-diam** |
| Aset tetap + penyusutan | `/accounting/fixed-assets` — salinan Mongo `accurate_fixed_assets`, **371 aset**, disegarkan task harian; dipakai kartu Senior Accounting | Duplikat |
| Daftar 40 CV | `payroll_company` (41), rekening bank Accurate, proyek Accurate | **Master entitas ganda** — nama badan usaha kini hidup di ≥3 tempat |
| Jurnal piutang | `/accounting/receivables` (B2B + aging + DSO) dan `/orders/piutang/summary` (marketplace) | Tumpang tindih sebagian; cakupannya beda |
| Arus kas metode langsung | Tak ada di ERP; forecast kas mingguan yang ada ([[Finance - Rancangan Finance Service]] Fase 1b) itu **rencana**, bukan realisasi | Sebagian celah asli |
| **Kertas kerja konsolidasi + jurnal eliminasi intercompany** | **Tidak ada padanan** di ERP maupun di jalur Accurate mana pun yang terdokumentasi | ✅ **Celah asli — inilah nilai unik aplikasi ini** |
| Saldo awal bulanan → Google Sheets | Tak ada; Sheets tujuannya di luar kendali ERP | Celah, jalur tak terpantau |
| Login 7 akun statis, jatah CV per akun | JWT + SSO gateway, RBAC tiga sumbu ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]), tenant lewat `company_id` ([[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]) | **Tidak terhubung sama sekali** |

**Kenapa ini bukan sekadar catatan rapi.** Tiga akibat yang sudah bisa ditunjuk hari ini:

1. **Satu fakta, dua tempat.** Laba per CV kini bisa dihitung dua kali dengan hasil berbeda: dari jurnal Supabase aplikasi ini, dan dari `/accounting/profit-loss` Accurate yang **sudah dipakai menilai KPI**. Tak ada yang merekonsiliasi keduanya, dan tak ada satu pun test di sisi mana pun yang akan berbunyi bila keduanya menyimpang.
2. **Ada metrik KPI yang justru menunggu sistem ini.** [[HRIS - Matriks KPI per Departemen]] mencatat templat **`KPI Accounting CV`** (Junior Accountant, 6 metrik) dengan baris berbobot **0,30** — *"Menyusun laporan keuangan … akurat dan tepat waktu max tgl 4 bulan berikutnya"* — berstatus **"Belum dipetakan"**. Laporan itu **inilah** yang diproduksi di sini. Selama sistemnya tak dikenal ERP, metrik berbobot terbesar di templat itu tak akan pernah bisa otomatis.
3. **Posisi "Accounting CV" sudah punya layar di ERP, tapi kosong.** [[Finance - Dashboard per Posisi (FAT)]] menyediakan rute `/finance/posisi/cv`, dan satu-satunya elemen hidupnya "Penjualan per toko". Orang yang memakai layar itu adalah orang yang sehari-hari bekerja di aplikasi ini.

## Belum Diimplementasikan / Catatan

Temuan review kode 2026-08-31, seluruhnya terverifikasi ke berkas & barisnya.

**Otentikasi & otorisasi**

- ⛔ **Kredensial tertanam di bundel klien.** `CREDENTIALS` (`AppClient.tsx:54-62`) memuat tujuh pasang username/password berpola `adminNN` dalam teks polos. Karena komponennya `'use client'`, daftar itu **ikut terkirim ke setiap peramban** yang membuka halaman.
- ⛔ **Peran & jatah CV hanya ditegakkan di klien.** `getAllowedCompanies` (`:64-73`), gerbang menu (`:267-276`), dan gerbang `admin3` (`:929-931`) semuanya berjalan di React, sementara Supabase diakses langsung dari browser dengan publishable key. Pembatasan "admin1 hanya CV01–CV07" karena itu **tidak mengikat di sisi data**.
- ⛔ **Peran diambil dari `sessionStorage` tanpa diverifikasi ulang** (`:176-187`); menyuntingnya di DevTools cukup untuk berganti peran.
- 🟡 **Tidak bisa dipastikan dari repo apakah tabel Supabase dilindungi RLS** — tak ada migrasi/policy di repo. Bila tidak, URL + publishable key sudah cukup untuk membaca **dan menulis** seluruh pembukuan 40 CV. **Perlu diperiksa langsung di dashboard Supabase**; jangan diasumsikan aman maupun bocor.

**Integritas data**

- ⛔ **Impor "ganti penuh" menghapus transaksi SELURUH perusahaan**, bukan hanya yang sedang dipilih: `handleImportTransactions` dengan `isMerge=false` menjalankan `delete().not('id','like','SALDO_AWAL_%')` tanpa filter `company_id` (`:479-482`). Layar impornya sendiri berlingkup satu CV.
- ⛔ **Menyimpan COA = menghapus seluruh tabel `coa` lalu menyisipkan ulang** (`:547-552`); `handleRestoreAllData` menghapus **kelima** tabel lalu mengisi ulang (`:606-662`). Tak ada transaksi database — gagal di tengah meninggalkan pembukuan kosong sebagian.
- ⚠️ **Kegagalan simpan tidak terlihat pemakai.** Setiap panggilan Supabase dibungkus `try/catch` yang hanya `console.error`; layar tetap menampilkan data yang sebenarnya belum tersimpan.
- ⚠️ **Webhook Google Sheets dipanggil `mode: 'no-cors'`** (5 titik panggil). Respons tak terbaca, jadi penolakan Apps Script — mis. skrip diganti, izin dicabut, kuota habis — **tak terdeteksi sama sekali**; yang tertangkap hanya kegagalan jaringan.
- ⚠️ **Aset tetap dibayangi `localStorage` per peramban** (`:101-109`, `:196-206`): bila server membalas kosong, yang tampil adalah isi peramban itu, sehingga dua orang bisa melihat daftar aset berbeda tanpa tanda apa pun.
- ⚠️ **Saldo awal bulanan tidak masuk buku besar aplikasi sendiri** — hanya dikirim ke Sheets (`MonthlyOpeningBalanceForm.jsx:93-104`).

**Kebenaran akuntansi**

- ⛔ **Arus kas salah menggolongkan piutang & pajak dibayar di muka sebagai INVESTASI.** `getCashFlowCategory` (`accounting.js:433`) menandai aset ber-kode awalan `12` sebagai *investing*, dan di `DEFAULT_COA` awalan `12` justru berisi **Piutang Usaha Pelanggan (121), Piutang Karyawan (122), Piutang Usaha Lain-Lain (123), Uang Muka Pembelian (124), PPN Masukan (126), PPh 21/22/23 dibayar di Muka (127–129)** — seluruhnya pos **operasi**. Aturan itu jelas ditulis untuk skema kode lain (`1-4`, "tetap", "peralatan") yang juga masih ada di fungsi yang sama. Akibatnya arus kas operasi terlalu kecil dan arus kas investasi terlalu besar, **tanpa satu pun galat**. Fungsi tetangganya `isReceivableAccount` (`:837-844`) memakai awalan `12` untuk arti yang berlawanan — bukti bahwa awalan itu memang piutang di COA ini.
- ⚠️ **Pencarian akun kunci bertingkat dan tersebar.** Akun "Laba Tahun Berjalan" dicari lewat rantai `'3-3000' → '313' → cocok-nama → default '313'`, dan rantai yang **sama persis** ditulis ulang di tiga tempat (`calculateBalanceSheet`, `calculateConsolidatedData`, `calculateChangesInEquity`). Satu fakta di tiga tempat; menambah COA baru menuntut menyunting ketiganya.
- ⚠️ **Konsolidasi tidak mengenal kepemilikan.** `calculateConsolidatedData` menjumlahkan seluruh CV **100%** lalu menerapkan eliminasi manual. Tidak ada konsep kepemilikan sebagian maupun kepentingan non-pengendali — sah bila semua CV dimiliki penuh, tetapi asumsinya tak tertulis di mana pun.
- ⚠️ **Angka nol pada CV yang belum diisi tak dibedakan dari nol yang benar.** Dasbor menandai CV yang saldo awalnya kosong, tetapi laporan dan konsolidasi tetap menjumlahkan CV itu sebagai nol.

**Rekayasa & tata kelola**

- ⛔ **Repo berada di akun GitHub pribadi, di luar org `bip-itteam-internal`**, dengan satu kontributor dan tanpa PR. Bila akses akun itu hilang, pembukuan 40 badan usaha ikut hilang bersamanya. Bandingkan dengan aturan "semua repo kode wajib PR" yang berlaku di workspace ini.
- ⚠️ **Nol test.** Tidak ada `*.test.*` di repo, sementara `accounting.js` memuat seluruh rumus laporan.
- ⚠️ **Komponen fitur `.jsx` tanpa tipe** di proyek yang sudah TypeScript, dan `AppClient` memakai `any` untuk hampir seluruh data.
- ⚠️ **`window.alert`/`window.confirm` global ditimpa** oleh modal kustom (`:125-146`) — `confirm` yang aslinya sinkron diganti versi yang mengembalikan `Promise`, jadi pemanggil yang lupa `await` akan selalu membaca "ya".
- ⚠️ `package.json` masih memuat `vite` + `@vitejs/plugin-react` sebagai devDependency padahal build sudah `next build`.

## Dependensi & Integrasi

- **Supabase (PostgreSQL)** — satu-satunya penyimpanan. Di luar kendali infrastruktur ERP ([[IT - Server, VMs and Databases]]).
- **Google Sheets via Apps Script webhook** — penerima jurnal kas & saldo awal bulanan. Tujuan, pemilik, dan isinya **tidak terdokumentasi**; kandidat kuat sebagai sumber rekap manual yang selama ini dipakai Finance.
- **Tidak bergantung** pada [[CORE - API Master Gateway]], [[Microservices - Integration Service]], maupun [[External - Accurate]] — dan itulah masalahnya, bukan fiturnya.
- Entitas yang dibukukannya beririsan dengan [[Microservices - Payroll Service]] (badan usaha penggaji) dan [[Finance - Bridging App New Golang]] (CV yang sama dipakai sebagai penjual di marketplace).

## Dokumen Terkait

- [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]] — keputusan yang menentukan nasib sistem ini (🟡 Proposed)
- [[ADR - 0001 Akuntansi via Accurate]] — keputusan yang dilanggar keberadaan sistem ini
- [[Finance - Big Pictures]] — peta domain Finance System
- [[Finance - Dashboard per Posisi (FAT)]] — layar `/finance/posisi/cv` untuk posisi Accounting CV
- [[Finance - Rancangan Finance Service]] — modul finance yang direncanakan di ERP
- [[API - Integration Service]] — endpoint `/accounting/*` yang membaca Accurate hari ini
- [[External - Accurate]] · [[Microservices - Payroll Service]] · [[HRIS - Matriks KPI per Departemen]]
