## Deskripsi

*Dashboard `/finance` (FAT — Finance, Accounting & Tax) diringkas dari sebelas tab per posisi jadi dua: Ringkasan Divisi dan Kamus & Catatan. Isi tiap tab lama pindah ke halaman modul kerja yang sudah punya pekerjaan itu; portal per posisi (`/dashboard`) tetap ada tapi kini merender komponen ASLI modul kerja, bukan salinan lokal ke `posisi/`.*

- **Status**: ✅ **Implemented** — merged ke `main` erp-frontend 2026-09-26; deploy prod **belum diverifikasi** (ukur ulang sebelum dipakai). Perbaikan terjemahan menu Tim Accounting yang hilang saat merge: erp-frontend #1753. PR 1 `feat/finance-rapikan-tab` (erp-frontend #1750, merge `cba2bf1bd`), PR 2 `feat/finance-rapikan-sidebar` (erp-frontend #1751, merge `70e7c13bf`). Linear BHA-274 (induk), BHA-275, BHA-276.
- **Path di repo**: `erp-frontend/src/features/finance/posisi/` (tab `/finance` + ruang kerja portal) · `erp-frontend/src/features/finance/ar/` (tab Penagihan/Retur/Uang Masuk, baru) · `erp-frontend/src/features/finance/tim-accounting/` (baru) · `erp-frontend/src/features/finance/ap/components/kartu-costing-hpp.tsx` (baru) · `erp-frontend/src/features/finance/pajak/components/kartu-pajak-lanjutan.tsx` (baru)
- **Tanggal**: 2026-09-26

## Context

[[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] §4 menetapkan: posisi yang isinya hampir seluruhnya penanda "menunggu penyambungan data" tidak layak punya dashboard sendiri. [[Finance - Dashboard per Posisi (FAT)]] (sebelum peringkasan ini) sudah menunjukkan gejala itu untuk beberapa posisi, dan brainstorming 2026-09-26 mengukur tumpang tindihnya terhadap halaman modul kerja yang sudah berdiri sendiri:

- Tab **Supervisor FAT** tumpang tindih ±60% dengan Ringkasan Divisi — dua layar berbeda menjawab pertanyaan yang hampir sama untuk audiens yang hampir sama.
- Tab **Accounting Payable** tumpang tindih ±80% dengan halaman `/finance/ap` yang sudah ada; satu-satunya elemen unik ("Costing HPP Valid") layak berdiri sendiri di kartu, bukan di tab tersendiri.
- Tab **Cost Control** isinya identik dengan yang sudah dirender `/finance/anggaran` (varians OPEX).
- Tab **Senior Accountant**: hanya 1 dari sekitar 9 elemen benar-benar tersambung ke data (komposisi aset tetap).
- Tab **Junior Accountant**: hanya 2 dari sekitar 8 elemen tersambung (transaksi hari ini, Skor KPI).
- Tab **Accounting CV**: satu-satunya elemen hidupnya ("Penjualan per toko") tidak punya pemegang posisi aktif yang memakainya sebagai layar kerja utama — modul kerja pemegang posisi itu sudah ada di `/finance/entitas-cv` (Entitas CV / CV Ditugaskan), berdiri sejak ADR 0096 dan T2 (transfer kas CV).

Sembilan dari sebelas tab, karena itu, adalah duplikat sebagian atau seluruhnya dari halaman yang sudah punya pekerjaan itu sebagai modul kerja mandiri — bukan sekadar dashboard ringkas. Mempertahankan keduanya berarti dua tempat yang bisa menyimpang diam-diam saat salah satunya diperbarui (kelas kegagalan yang sama dengan § SATU FAKTA SATU TEMPAT).

Rencana lengkap beserta pencarian kode yang mendasarinya: `.task-plans/2026-09-26-rapikan-finance.md`.

## Decision

### 1. `/finance` diringkas jadi dua tab

`KELOMPOK_POSISI` (`posisi/lib/daftar-posisi.ts`) — satu-satunya sumber isi tab `/finance` — kini hanya **Ringkasan Divisi** dan **Kamus & Catatan**. `saringTabPosisi` (penyaringan tab per posisi) dihapus: tak lagi bermakna karena hanya dua tab, sama untuk semua orang.

### 2. Isi tab lama pindah, bukan hilang

| Bekas tab | Tujuan |
|---|---|
| Supervisor FAT | Dilebur ke Ringkasan Divisi; bagian khusus (piutang B2B >60, utang lewat jatuh tempo, beban non-operasional, persetujuan menunggu, beban per kelompok, kotak persetujuan) tampil hanya bila `lihatSemuaFinance()` (`isAnySupervisor \|\| isItMember`) — satu fungsi di `posisi/lib/lihat-semua.ts`, dipakai `page.tsx` dan `isi-ringkasan-divisi.tsx` |
| AR Leader | Tab **Penagihan** di `/finance/ar` (`features/finance/ar/components/tab-penagihan.tsx`) |
| AR Staf | Tab **Retur** dan **Uang Masuk** di `/finance/ar`; kartu "Piutang >14 Hari" juga di ruang kerja portal AR Staff |
| Senior + Junior Accounting | Halaman baru **`/finance/tim-accounting`** (`features/finance/tim-accounting/components/isi-tim-accounting.tsx`), menu sidebar "Tim Accounting" |
| Tax Officer | Kartu "Beban pajak efektif" + "PPN Masukan" pindah ke `/finance/pajak` (`kartu-pajak-lanjutan.tsx`) |
| Account Payable | Kartu "Costing HPP Valid" pindah ke `/finance/ap` (`kartu-costing-hpp.tsx`) |
| Cost Control | **Dihapus** — menunya sendiri (`/finance/anggaran`, lihat §4) sudah merender varians OPEX |
| Accounting CV | **Dihapus** — kartu "Penjualan per toko" **dibuang, bukan dipindah** (keputusan user saat review rencana); `useFetchPenjualanToko` dan endpoint `GET /api/integration/transactions/orders/summary/shops` kini tanpa konsumen FE |
| Kamus | Tetap tab `/finance` |

Rute `/finance/posisi/*` **tidak dihapus**: semuanya jadi `redirect()` ke tujuan barunya lewat satu peta (`posisi/lib/tujuan-posisi-lama.ts`), supaya tautan dan penanda buku lama tetap mendarat di tempat yang benar.

### 3. Portal (`/dashboard`) tetap per posisi, dengan komponen asli

Sejalan [[ADR - 0105 Beranda Portal Menumpuk Zona Personal di Atas Ruang Kerja Posisi]] zona D: portal tidak ikut diringkas. `RUANG_KERJA_FAT` (`posisi/components/isi-tab.tsx`) memetakan slug posisi (`ringkasan` | `ar-leader` | `ar-staf` | `tim-accounting`) ke komponen ASLI dari modul kerjanya (`TabPenagihan`, `TabRetur`+`TabUangMasuk`, `IsiTimAccounting`) — bukan salinan lokal. `slugUntukPosisi` (`posisi/lib/tab-untuk-posisi.ts`) adalah satu-satunya peta nama-posisi-di-`work_data` → slug, dipakai portal maupun kartu Skor KPI (`skor-kpi-posisi.ts`) supaya "siapa pemegang posisi X" tak bisa berbeda pendapat antara kedua pemakai.

Posisi yang kini mendarat di Ringkasan (Finance Supervisor, Account Payable, Cost Control, Tax Staff) **tetap didaftarkan** di `PETA_POSISI`, bukan dibiarkan tak dikenal — supaya `slugUntukPosisi` tetap bisa menandai mereka sebagai "orang FAT" walau ruang kerja portalnya jadi Ringkasan.

### 4. Sidebar dirapikan mengikuti pemindahan (PR 2)

- **Pembukuan** (`/finance/accounting`) menggantikan dua menu lama, "Accounting" dan "Jurnal & Buku Besar", jadi satu halaman bertab (`?tab=jurnal|laba-rugi|neraca|neraca-saldo`). `/finance/gl` jadi pengalih ke `?tab=jurnal`.
- **Anggaran & Cost Control** (`/finance/anggaran`) menggantikan "Anggaran OPEX" dan "Cost Control" terpisah, jadi satu halaman bertab (`?tab=master|marketing|rekomendasi`). `/finance/cost-control` jadi pengalih ke `?tab=rekomendasi`, meneruskan query `periode`/`akun_no`/`akun_nama`.
- **Entitas CV disembunyikan dari sidebar.** Hanya **"CV Ditugaskan"** yang punya entri, berdiri sendiri (bukan lagi anak induk "Accounting CV"). Halaman CV Ditugaskan (`halaman-cv-saya.tsx`) menambahkan tombol **"Kelola entitas"** bagi pemegang `akuntansicv.view` (fallback `false`, sehingga tombolnya tak pernah berakhir "Akses Ditolak") — pintu satu-satunya ke `/finance/entitas-cv`, yang rutenya tetap hidup.
- **Skor KPI Tim Accounting** (`KartuSkorKpi slugPosisi="tim-accounting"`) menampilkan skor pembaca sendiri bila ia salah satu dari dua pemegang posisi (`skorUntukPosisi` parameter `pembacaId`); bagi pembaca yang bukan pemegang (mis. supervisor), berlaku aturan lama — satu pemegang tampil, lebih dari satu berbunyi "banyak pemegang".

### 5. Gerbang halaman Pembukuan: dua aturan lama dipertahankan per tab, bukan dilebur

Halaman `/finance/gl` (lama) dan `/finance/accounting` (lama) punya gerbang BERBEDA: `finance.accounting.view` vs menu terbatas Laporan Keuangan ([[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]]). Melebur ke satu gerbang selalu salah ke satu arah, jadi:

- Tab **Jurnal** digerbang `finance.accounting.view` (aturan lama `/finance/gl`).
- Tab **Laba Rugi · Neraca · Neraca Saldo** digerbang menu terbatas `menu.finance.laporan` (aturan lama `/finance/accounting`), tetap dibungkus `MenuTerbatasGuard`.
- Halaman boleh dibuka bila **SALAH SATU** gerbang lolos (`aksesPembukuan` → `bolehPembukuan`, satu fungsi di `accounting/lib/tab-pembukuan.ts`).
- Menu sidebar **"Pembukuan"** memakai penanda `$pembukuan` (`IZIN_MENU_PEMBUKUAN`, bukan izin tunggal): `bolehMenu` (`utils/menu-permission.ts`) mengenali penanda ini dan menilainya lewat fungsi yang sama, `bolehPembukuan(aksesPembukuan(...))` — satu aturan, dibaca dua tempat (halaman dan sidebar), bukan diturunkan ulang.
- Tiga hook laporan hanya dipanggil saat tab laporan aktif **dan** diizinkan (bukan tanpa syarat di tingkat halaman seperti versi lama `/finance/accounting`).

## Consequences

- **Hak akses AR kini `finance.ar.view`.** Tab Penagihan/Retur/Uang Masuk pindah ke `/finance/ar`, yang gerbangnya `finance.ar.view` (bukan `finance.accounting.view` seperti dashboard FAT lama). AR Leader dan AR Staf yang cuma memegang izin dashboard lama tanpa `finance.ar.view` bisa kehilangan akses — mitigasinya `FinanceModuleGuard` `/finance/ar` sudah lama `fallback: true` (halaman piutang lama tak berpagar sejak awal).
- **Tax Officer, Account Payable, Cost Control di portal (`/dashboard`) mendarat di ruang kerja Ringkasan**, bukan ruang kerja khusus — sejalan §2 dan §3, karena isi uniknya sudah pindah ke kartu di modul kerja masing-masing, bukan berdiri sebagai ruang kerja sendiri.
- **Kartu "Penjualan per toko" dibuang permanen.** Endpoint `GET /api/integration/transactions/orders/summary/shops` (integration-service) kini tanpa konsumen FE. Tidak dihapus dari backend pada perubahan ini — di luar cakupan (FE saja).
- **Tab "Buku Besar" TIDAK dibuat**, walau Linear BHA-59 tercatat berstatus Done. `/finance/gl` (kini tab Jurnal Pembukuan) hanya daftar journal voucher berpaginasi; tampilan buku besar **per akun** tidak pernah ada di FE. **Pertanyaan terbuka**, belum diputuskan siapa yang menutup gap Linear vs kode ini.
- **`menu.finance.laporan` pindah level: dari gerbang HALAMAN (`/finance/accounting` lama) jadi gerbang TAB** (Pembukuan). Semantiknya dipertahankan — lihat catatan di [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]].
- **Sebelas halaman posisi lama tidak lagi ada sebagai halaman terpisah** — [[Finance - Dashboard per Posisi (FAT)]] diperbarui mengikuti keadaan ini; [[Finance - FAT Persona]] **belum** diukur ulang terhadap lokasi baru (TBD).

## Terkait

- [[Finance - Dashboard per Posisi (FAT)]] — dok yang diperbarui mengikuti keputusan ini
- [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] — prinsip §4 yang dijalankan di sini
- [[ADR - 0105 Beranda Portal Menumpuk Zona Personal di Atas Ruang Kerja Posisi]] — zona D, alasan portal tetap per posisi
- [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]] — gerbang menu terbatas yang kini bekerja per tab Pembukuan
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]] — label sidebar & tab baru (Pembukuan, Anggaran & Cost Control, Tim Accounting, CV Ditugaskan) lewat kunci id/en
- [[APP - Web ERP]] — deskripsi menu Finance yang diperbarui
- [[REF - Dashboard per Posisi (Indeks Cakupan)]] — indeks lintas divisi, kolom Finance diperbarui
