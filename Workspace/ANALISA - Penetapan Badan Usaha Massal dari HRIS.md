# ANALISA - Penetapan Badan Usaha Massal dari HRIS

> **Status**: ⛔ **Menunggu [[ADR - 0189 Penetapan Badan Usaha Penggaji Massal dari HRIS, Tanpa Persetujuan bila Hanya Penggaji Berganti]] Diterima: sebelum itu ANALISA ini BUKAN keputusan yang bisa ditunjuk `/brief`.**

Blueprint hasil `/analisa-kebutuhan` 2026-10-20 atas permintaan "halaman baru untuk HRD memetakan karyawan ke badan usaha, tidak lagi di Payroll". Papan kerja, berubah tiap issue selesai; keputusannya di ADR.

- **Keputusan**: [[ADR - 0189 Penetapan Badan Usaha Penggaji Massal dari HRIS, Tanpa Persetujuan bila Hanya Penggaji Berganti]] (merevisi sebagian [[ADR - 0148 Struktur Gaji Berversi per Event Personalia dan Diprorata per Hari]])
- **Dok domain**: [[HRIS - Payroll]] · [[Microservices - Payroll Service]] · [[REF - Kepemilikan Data]]
- **Desain layar**: Figma https://www.figma.com/design/RrlclRCNp1p1BcJPbbX5iO?node-id=3-2 (⚠️ frame 2 dan 3 masih menampilkan "Menunggu persetujuan"; keputusan akhirnya tanpa persetujuan, versi langsung terjadwal)
- **Pemutus**: `irfanarfianto`
- **Ukuran**: **Sedang**: dua repo, masing-masing satu PR. `bip-erp` harus berubah karena belum ada pintu massal maupun daftar lintas badan usaha (`services/payroll/routes.go:38` hanya per badan usaha; `salary_version_service.go:342` selalu menunggu persetujuan). `erp-frontend` harus berubah karena menu HRIS dirakit eksplisit (`src/components/layout/sidebar-menus.tsx:1495-1510`) dan halaman belum ada. `my-bharata` **tidak** berubah: slip membaca snapshot run.
- **Urutan**: [BE] lalu [FE]; deploy BE sebelum FE. Kategori inbox baru: payroll-service + notification-service naik bersama.

## Kebutuhan dan temuan

- **Kebutuhan sebenarnya**: penetapan badan usaha penggaji itu pekerjaan massal-administratif (62 dari 186 `employee_salary` tanpa `company_id`, ADR 0183 Context 6) yang hari ini dikerjakan per orang lewat form struktur gaji dan selalu menunggu persetujuan, sehingga slip diam-diam jatuh ke badan usaha default.
- **Yang sudah ada**: `buatVersiGaji` (jalur tunggal pembuat versi), preseden `PersetujuanDilewati`, hulu `keputusan_massal` yang belum dipakai, pola hasil per baris bulk BPJS, rencana badan usaha per karyawan, `GET /companies/:id/karyawan`, `MainTable` dengan pilihan baris, `buildCompanyOptions`, `DateStringPicker`.
- **Keputusan user 2026-10-20**: halaman HRIS untuk `payroll.salary.write`; tanpa persetujuan bila hanya penggaji berganti; pengaman notifikasi ke SPV HRD + riwayat versi; tanggal berlaku diisi HR (bawaan awal bulan depan); kontrak tidak disentuh.
- **Asumsi eksplisit**: alasan pemindahan dari menu Payroll belum dinyatakan (dipakai: penetapan massal tanpa membuka struktur gaji per orang); karyawan dengan versi menunggu persetujuan ditolak per baris; karyawan nonaktif tidak tampil.

## Langkah manusia

1. Setujui ADR 0189 (`🟢 Diterima, <tanggal>, oleh <login>`), lalu hapus baris "Menunggu ADR … Diterima" di atas.
2. Jalankan kueri **Perlu ukur prod** di issue [BE] (baca saja) dan tempel hasilnya.
3. Perbarui frame 2 dan 3 Figma (tanpa "Menunggu persetujuan") sebelum [FE] dikerjakan.
4. Pasang label `Siap Agent` pada issue yang lolos Definition of Ready.

## Issue 1: Induk, `bip-erp`: Penetapan badan usaha penggaji massal dari HRIS

- **Urutan**: induk, tanpa PR sendiri · **Issue**: [bip-erp#3323](https://github.com/bip-itteam-internal/bip-erp/issues/3323)

**Pemutus:** @irfanarfianto
**PIC:** @

### Masalah

Badan usaha penggaji (`company_id`) ditetapkan per karyawan di Payroll › Gaji Karyawan lewat form struktur gaji, dan setiap perubahan menunggu persetujuan SPV HRD (`services/payroll/salary_version_service.go:342`). Tidak ada pintu massal maupun daftar seluruh karyawan beserta penggajinya; 62 dari 186 `employee_salary` tanpa `company_id` dan jatuh ke badan usaha default (ADR 0183 Context 6).

### Keputusan

ADR "ADR - 0189 Penetapan Badan Usaha Penggaji Massal dari HRIS, Tanpa Persetujuan bila Hanya Penggaji Berganti" (vault `architecture-draft/Decisions/`), merevisi sebagian ADR 0148. Layak `Siap Agent` sesudah ADR berstatus Diterima (sekarang 🟡 Diusulkan).

Bentuk: menu HRIS › Penetapan Badan Usaha (`payroll.salary.write`), pilih-banyak → Tetapkan; bergaji = versi salinan dengan `company_id` baru langsung terjadwal tanpa persetujuan; belum bergaji = rencana; satu notifikasi per batch ke pemegang `payroll.approve.hrd`.

Issue induk tanpa PR sendiri. Dikerjakan lewat sub-issue [BE] (bip-erp) lalu [FE] (erp-frontend).

### Yang harus benar

- [ ] Sub-issue [BE] merged dan ter-deploy (payroll-service dan notification-service bersama) sebelum [FE] ter-deploy.
- [ ] Sesudah keduanya di prod, staf HR pemegang `payroll.salary.write` menetapkan badan usaha untuk banyak karyawan sekaligus dari HRIS, tanpa membuka menu Payroll.
- [ ] Pemegang `payroll.approve.hrd` menerima satu notifikasi untuk penetapan itu.

### Di luar cakupan

- Perubahan gaji, BPJS, atau PTKP (tetap di Struktur Gaji, tetap menunggu persetujuan).
- Kontrak kerja (atas nama tenant, tidak berubah).
- Menghapus form badan usaha di Struktur Gaji.

### Data / bukti pendukung

Desain: Figma https://www.figma.com/design/RrlclRCNp1p1BcJPbbX5iO?node-id=3-2. Blueprint: vault `Workspace/ANALISA - Penetapan Badan Usaha Massal dari HRIS.md`. Perlu ukur prod: lihat sub-issue [BE].

### Prasyarat

ADR 0189 Diterima.


## Issue 2: [BE] `bip-erp`: Daftar lintas badan usaha dan penetapan badan usaha massal

- **Urutan**: 1 · **Issue**: [bip-erp#3324](https://github.com/bip-itteam-internal/bip-erp/issues/3324)

**Pemutus:** @irfanarfianto
**PIC:** @

### Masalah

- `GET /companies/:id/karyawan` (`services/payroll/karyawan_badan_usaha.go`) hanya menjawab satu badan usaha; tidak ada daftar seluruh karyawan beserta penggajinya.
- Versi gaji yang hanya membawa `company_id` lahir dengan gaji nol, karena `versiDariMasukan` menyalin semua field apa adanya (`salary_version_service.go:131-146`), dan setiap versi baru menunggu persetujuan (`:342`).
- Rencana badan usaha hanya per karyawan (`badan_usaha_rencana.go:212-214`).
- Tidak ada notifikasi versi gaji (`notifikasi.go:39-51` hanya kategori run).

### Keputusan

ADR "ADR - 0189 Penetapan Badan Usaha Penggaji Massal dari HRIS, Tanpa Persetujuan bila Hanya Penggaji Berganti", butir 2-7. Layak `Siap Agent` sesudah ADR berstatus Diterima (sekarang 🟡 Diusulkan).

Bentuk: endpoint massal `{company_id, effective_date, employee_ids[]}` mode `cek`/`terapkan`, gerbang `payroll.salary.write`; bergaji = salinan versi berlaku + `company_id` baru lewat `buatVersiGaji`, `terjadwal`, `PersetujuanDilewati=true`, hulu `keputusan_massal` ber-pengenal batch; belum bergaji = rencana; satu notifikasi inbox per batch (`terapkan` saja) ke pemegang `payroll.approve.hrd`.

### Yang harus benar

- [ ] Daftar lintas badan usaha mengembalikan seluruh karyawan **aktif** dengan `badan_usaha_id`, nama badan usaha, status (`gaji_berlaku` / `rencana` / `belum_diplot`), ada-tidaknya struktur gaji, nama, posisi, departemen; tanpa field gaji. Memakai sumber yang sama dengan `karyawan_badan_usaha.go`, bukan salinan aturan gabungnya.
- [ ] Penetapan untuk karyawan bergaji menerbitkan versi yang **identik dengan versi berlaku kecuali `company_id`** (gaji pokok, komponen, dasar upah BPJS, PTKP, kepesertaan sama), status `terjadwal`, `PersetujuanDilewati=true`, lalu menjadi `berlaku` lewat rekonsiliasi yang ada.
- [ ] Penetapan untuk karyawan belum bergaji menulis rencana; karyawan yang punya proyeksi `employee_salary` tetapi belum punya versi tidak diberi rencana (celah `badan_usaha_rencana.go:182-184` yang hanya memeriksa versi).
- [ ] Hasil per baris `{diterapkan, tanpa_ubah, gagal[{employee_id, alasan}]}`, slice tak pernah nil, batas jumlah sama dengan bulk BPJS (`bulk_bpjs_base.go:27`). Mode `cek` tidak menulis apa pun dan mengembalikan pembagian dua jalur yang sama.
- [ ] Ditolak per baris dengan alasan terbaca: punya versi `menunggu_persetujuan`; karyawan tidak aktif / tak dikenal. Badan usaha yang sama dengan yang berlaku pada tanggal itu = `tanpa_ubah`. Badan usaha tidak ada / tidak beroperasi = galat batch (4xx) sebelum baris mana pun diproses.
- [ ] Endpoint tidak menerima field gaji selain `company_id` (field tambahan diabaikan atau ditolak, dikunci test).
- [ ] Satu notifikasi inbox per `terapkan` yang menerapkan ≥ 1 baris, ke tiap pemegang `payroll.approve.hrd`, kategori baru terdaftar di `InboxCategories`; test kategori yang BENAR, bukan sekadar terdaftar.
- [ ] Test handler lewat Fiber per rute: 403 tanpa `payroll.salary.write`, 400 body rusak, jalur `cek` vs `terapkan`; fungsi murni penyalin versi dengan fixture yang field-nya **berbeda-beda** (fixture seragam tak menjaga apa pun).
- [ ] Rute literal didaftarkan sebelum saudara ber-`:param`; verifikasi lewat gateway `/api/payroll/...` membandingkan bentuk respons, bukan status.

### Di luar cakupan

- Layar (sub-issue [FE]).
- Persetujuan untuk penetapan ini (diputuskan tidak ada).
- Mengubah `PUT /badan-usaha-rencana/:employeeId` per karyawan selain menutup celah proyeksi di atas.

### Data / bukti pendukung

Perlu ukur prod (baca saja, `payroll_db`):
- karyawan bergaji tanpa `company_id`: `db.employee_salary.countDocuments({$or:[{company_id:{$exists:false}},{company_id:""}]})`
- versi menunggu persetujuan (akan ditolak per baris): `db.employee_salary_version.countDocuments({status:"menunggu_persetujuan"})`
- rencana yang ada: `db.employee_badan_usaha_rencana.countDocuments({})`
- pemegang `payroll.approve.hrd` (penerima notifikasi): hitung dari paket izin jabatan di `employee_db` (kueri disusun pelaksana sesudah membaca katalog paket).

### Prasyarat

ADR 0189 Diterima.


## Issue 3: [FE] `erp-frontend`: Halaman HRIS › Penetapan Badan Usaha

- **Urutan**: 2 · **Issue**: [erp-frontend#2631](https://github.com/bip-itteam-internal/erp-frontend/issues/2631)

**Pemutus:** @irfanarfianto
**PIC:** @

### Masalah

Penetapan badan usaha hari ini hanya lewat Sheet struktur gaji per karyawan di `src/app/(main)/hris/payroll/employee-salary/page.tsx` (`salary-register-page.tsx:438`) dan pemilih rencana di Buat Karyawan (`create-employee/pilih-badan-usaha.tsx`). Tidak ada halaman daftar seluruh karyawan beserta badan usaha penggajinya, dan tidak ada pilih-banyak.

### Keputusan

ADR "ADR - 0189 Penetapan Badan Usaha Penggaji Massal dari HRIS, Tanpa Persetujuan bila Hanya Penggaji Berganti", butir 1, 5, 6. Layak `Siap Agent` sesudah ADR berstatus Diterima (sekarang 🟡 Diusulkan).

Bentuk: halaman daftar pola HRIS (satu kartu, `Banner bare` di `toolbar` `MainTable`, `useTableState`), pilih baris via `selectedKeys`/`onSelectedKeysChange`/`selectionActions`, dialog Tetapkan (badan usaha dari `buildCompanyOptions`, tanggal `DateStringPicker`), menu HRIS ber-`perm: "payroll.salary.write"`.

### Yang harus benar

- [ ] Menu **HRIS › Penetapan Badan Usaha** tampil hanya bagi pemegang `payroll.salary.write` (daun ber-`perm` + entri FALLBACK `tolak` di `utils/menu-permission.ts`), dan panduannya ditulis di `features/panduan/isi/hrga.ts` atau URL-nya dicatat di `BELUM_DITULIS_HRGA`.
- [ ] Daftar memakai pola tabel HRIS (acuan `hris/resign/page.tsx`); bawaan tersaring "Belum ditetapkan"; filter status, badan usaha, departemen; kolom Nama + ID, Posisi, Departemen, Struktur gaji (Ada / Belum ada), Badan usaha penggaji ("Default: <nama>" bila belum ditetapkan), Status. Empat kartu ringkasan: aktif, sudah ditetapkan, belum ditetapkan, rencana.
- [ ] Pilih-banyak memakai pilihan baris `MainTable` (acuan `ga/permintaan/page.tsx:385-401`), bukan kolom `Checkbox` rakitan; bilah pilihan menyebut "N dipilih · X punya struktur gaji, Y belum".
- [ ] Dialog Tetapkan memanggil mode `cek` dulu dan menampilkan dua jalur (versi baru langsung terjadwal vs rencana) beserta nama karyawan, lalu `terapkan`; badan usaha hanya yang beroperasi; tanggal bawaan tanggal 1 bulan berikutnya, dengan `DateStringPicker` (bukan `<input type="date">`).
- [ ] Hasil per baris ditampilkan: diterapkan, tanpa ubah, ditolak + alasan dari backend (tanpa menebak alasan di FE); daftar disegarkan sesudahnya.
- [ ] Lima keadaan: memuat (`Skeleton`), kosong, galat (403 dibedakan), sebagian (ada baris ditolak), terkunci (tanpa izin).
- [ ] Semua teks lewat `t()` dengan kunci di `id.ts` dan `en.ts`; tanggal diformat di render dengan `intlLocale(lang)`; uji i18n dengan instance asli + kontrol negatif `en`.
- [ ] `pnpm tsc --noEmit`, `pnpm lint`, `pnpm build` hijau; kegagalan `pnpm test` dibandingkan baseline `origin/main`.

### Di luar cakupan

- Menghapus atau mengubah form badan usaha di Struktur Gaji.
- Persetujuan (tidak ada untuk penetapan ini).

### Data / bukti pendukung

Desain: Figma https://www.figma.com/design/RrlclRCNp1p1BcJPbbX5iO?node-id=3-2 (frame 2 dan 3 perlu diperbarui: tanpa "Menunggu persetujuan").

### Prasyarat

Deploy sesudah sub-issue [BE] (bip-erp) ter-deploy. ADR 0189 Diterima.
