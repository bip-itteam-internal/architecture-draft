# Microservices - Insentive Service

## Deskripsi

_Insentive Service adalah engine perhitungan insentif tim marketing. Sejak **2026-07-30** skemanya **profit-based untuk SELURUH jabatan** (SK 010/DIR/Rev-SK6/VII/2026 & SK 011/DIR/SK6/VII/2026): insentif = tarif × profit, dinilai bertingkat **ICC → Leader → Supervisor**. Skema lama (KPI-multiplier per-role dan ICC pay-per-video) **dicabut** — kodenya dihapus, rutenya menolak dengan pesan eksplisit. Service ini merakit dashboard dari tiga sumber: komponen profit dari [[Microservices - Integration Service]], beban karyawan dari [[Microservices - Payroll Service]], dan master data (struktur tim, target, opex) dari database sendiri._

- **Stack:** Go + Fiber v2 + MongoDB (`insentive_db`)
- **Path:** `services/insentive` (pola flat-file: handler inline di `main.go`/`func.go`)
- **Status**: ⚠️ **Implemented (ada catatan)** — perhitungan lengkap & ter-test, tetapi angkanya belum layak dipakai membayar sampai master data terisi (lihat §Belum Diimplementasikan)

## Skema yang berlaku (profit-based)

```
Profit = Uang Cair (Net Settlement) − HPP − Beban Iklan − Biaya Operasional
Insentif = tarif(%) × Profit
```

- **Tarif** naik bertingkat mengikuti % pencapaian terhadap target: `<80% → 0` · `80–90% → 2%` · `>90–100% → 3%` · `>100–110% → 4%` · `>110% → 5%`. Ditulis sebagai rantai perbandingan (bukan penelusuran tabel) supaya **celah antar-tier mustahil secara struktur** — versi tabel sebelumnya menyisakan lubang 0,01% yang diam-diam membayar 0.
- **Gerbang retur 7%**: batas hanya berlaku selama pencapaian **≤100%**; di atas itu retur tidak lagi menggugurkan. Rasio dihitung dari **jumlah order** (keputusan client 2026-07-31); rasio berbasis nilai tetap ditampilkan sebagai pembanding karena keduanya bisa berbeda jauh (Juli 2026: 4,12% vs 3,35%).
- **Target** hanya diketik di lingkup **Supervisor**, lalu dibagi rata turun ke Leader dan ICC. Baris turunan boleh ditimpa manual.
- **Satu orang bisa menempati dua level**: leader yang punya toko sendiri dinilai sebagai ICC atas tokonya **dan** sebagai Leader atas total timnya, dengan target masing-masing.

## Endpoint / Fitur (Sudah Diimplementasikan)

### Dashboard profit (inti)
- `GET /profit-dashboard?periode=YYYY-MM&level=icc|leader|supervisor` — satu tabel untuk tiga lingkup; menarik komponen profit dari integration, beban karyawan dari payroll, dan beban non-gaji dari Accurate. `&refresh=1` memaksa penarikan ulang beban non-gaji.
- Tiap baris membawa **`peringatan[]`** dan `layak_dibayar` — baris yang datanya belum lengkap **menolak** dinyatakan siap dibayar, bukan diam-diam dihitung nol.

### Master data profit
- `GET/POST /profit/org` · `PATCH /profit/org/:id/tutup` — struktur tim (ICC ↔ Leader ↔ Supervisor).
- `GET/POST /profit/targets` — target per entitas per periode. Ubah target setelah periode berjalan **wajib beralasan** (≥10 karakter); setelah disetujui, ditolak.
- `GET/POST /profit/opex` · `POST /profit/opex/distribusi` — biaya operasional; kini **cadangan** karena gaji ditarik dari payroll dan non-gaji dari Accurate.
- `GET/POST/DELETE /profit/internal-affiliates[/:username]` — daftar putih akun affiliate milik sendiri.

### Warisan skema lama (masih terdaftar)
- `GET /health` · `GET /stats` · `GET/PUT /configs/ppn`
- `GET/POST/PUT/DELETE /master-kpi[/:id]` · `/mappings[/:id]` · `GET /audit-logs`
- `/results*` (list, export Excel, approve/unapprove, override, delete)
- `GET /accurate/summary|income|invoices` · `GET /integration/shopee/item-performance`
- ⚠️ `POST /calculate` dan `POST /calculate/auto` **menolak seluruh role** dengan pesan yang menyebut SK pencabutnya. Rutenya sengaja dibiarkan supaya pemanggil lama mendapat penjelasan, bukan 404 yang membingungkan.

## Belum Diimplementasikan / Catatan

- **Cron harian dihapus** (`cron_worker.go`, −1.571 baris) bersama skema KPI-multiplier. Tidak ada lagi job terjadwal di service ini — lihat [[IT - Background Jobs & Schedulers]].
- **Pengecualian omzet affiliate eksternal belum terpasang di perhitungan.** Daftar putihnya sudah bisa diisi lewat Master Data, tetapi belum ada kode yang memakainya → pencapaian di layar masih lebih tinggi dari seharusnya. Terukur Juli 2026: 71,6% nilai affiliate berasal dari kreator eksternal.
- **Belum ada alur approval/freeze** untuk skema profit (yang lama punya, yang baru belum).
- **Atribusi ICC belum lengkap**: per 2026-08-01 hanya 10 dari 28 toko punya mapping ICC → 63% profit Juli tak berpemilik. Sumbernya `icc_account_mappings` di integration ([[Microservices - Integration Service]]).
- Menunggu dari luar: Lampiran SK (target sesungguhnya), mapping tim Beautyhacks, dan finance melengkapi HPP.
- Pertanyaan finance yang masih terbuka: PPN di dalam profit; target sebelum/sesudah opex; jadwal bayar SK (tgl 1/5) vs cutoff pencairan (tgl 25).

## Dependencies & Integrasi

- **MongoDB** (`insentive_db`) — koleksi profit: `incentive_org`, `incentive_profit_targets`, `incentive_opex`, `internal_affiliate_accounts`; warisan: `master_kpis`, `employee_performance_mappings`, `audit_logs`, `incentive_results`. Lihat [[DB - Overview and Notes]].
- **[[Microservices - Integration Service]]** — `GET /profit/incentive/summary` (komponen profit per toko + pemilik ICC) dan `GET /profit/incentive/opex` (beban non-gaji per proyek Accurate). Env `INTEGRATION_MODULE_URL`.
- **[[Microservices - Payroll Service]]** — `GET /employer-cost` (beban perusahaan per karyawan: bruto + iuran BPJS pemberi kerja). Env **`PAYROLL_MODULE_URL`** (ditambahkan ke blok `insentive-service` di `docker-compose.yml`).
- **[[External - Accurate]]** — sumber pembukuan beban operasional, dibaca lewat integration (bukan langsung).
- **[[CORE - API Master Gateway]]** — routing `/api/insentive/*`.

## Dokumen Terkait

- [[Finance - Incentive]] — skema bisnis & isi SK
- [[ADR - 0033 Beban Operasional Insentif dari Proyek Accurate]] — keputusan sumber biaya operasional
- [[API - Insentive Service]] — daftar rute
- [[Sales - Incentive]] · [[HRIS - Key Performance Index]]
