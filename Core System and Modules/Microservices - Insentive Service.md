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
- **Toko terpetakan yang belum berjualan tetap disebut** (2026-08-26, PR #1455 bip-erp + #1248 erp-frontend, merged). Ringkasan profit hanya memuat toko yang punya order, sehingga toko yang sudah dipetakan ke seorang ICC tetapi nol order **lenyap tanpa jejak**: ICC Management menyebut 15 toko untuk tim Satrio, dashboard menyebut 9. Integration kini mengirim baris bernilai nol bertanda `tanpa_penjualan`, service ini mencacahnya jadi `toko_tanpa_penjualan`, dan layar menulis "9 dari 15 toko". Terukur prod 2026-08-26: 15 = 9 berjualan + 6 belum pernah ada order. Angkanya tidak bergeser — toko tanpa order menyumbang Rp0 ke omzet, HPP, iklan, dan retur.

### Master data profit
- `GET/POST /profit/org` · `PATCH /profit/org/:id/tutup` — struktur tim, kini **hanya penambal**. Sejak 2026-08-26 Leader dan Supervisor diturunkan dari **hierarki HRIS** (`work_data.supervisor_id`), bukan dari koleksi ini — lihat §Hierarki di bawah.
- ⚠️ Seluruh rute **tulis** `/profit/*` dijaga `RequireMasterProfitWriter` (finance staff/supervisor/admin, atau it supervisor/admin). Direktur lolos lewat peran turunannya, tanpa peran `direktur` tersendiri. Peran `insentive` sengaja **tidak** ikut: boleh menyetujui hasil, tidak boleh menulis targetnya sendiri.
- `GET/POST /profit/targets` — target per entitas per periode. Ubah target setelah periode berjalan **wajib beralasan** (≥10 karakter); setelah disetujui, ditolak.
- `GET/POST /profit/opex` · `POST /profit/opex/distribusi` — biaya operasional; kini **cadangan** karena gaji ditarik dari payroll dan non-gaji dari Accurate.

### Biaya operasional terdiri dari tiga bagian (2026-08-26)

Rumus profit memakai **Biaya Operasional** sebagai pengurang terakhir. Isinya:

| Bagian | Dari mana | Contoh angka (Maftuhissaiin, Agustus 2026) |
|---|---|---|
| Gaji | payroll | Rp 6.623.500 |
| Beban marketing | Accurate, lewat [[Microservices - Integration Service]] | Rp 2.773.289 |
| Penyusutan aset | [[Microservices - Inventory Service]] | Rp 551.847 (2 aset) |
| **Total** | | **Rp 9.948.636** |

**Beban marketing menggantikan cara lama.** Sebelumnya sistem mengambil SELURUH akun beban `6000` di Accurate lalu membuang 14 akun yang sudah dihitung di tempat lain. Cara itu berbahaya: akun baru yang muncul di Accurate otomatis ikut terhitung tanpa ada yang tahu. Sekarang sistem **memilih 5 akun** yang memang beban per-orang — Software, Pelatihan, Perjalanan Dinas, Sewa, dan Server.

Cara baru juga sudah **membagi beban proyek divisi** ke tiap orang. Proyek `BIP - BH` dan `BIP - KY + GB` dulu tak pernah terbaca karena kodenya bukan employee id; kini isinya dibagi rata ke anggota divisinya.

⚠️ **Akibatnya biaya operasional turun 60–94%** (Ade dari Rp4,55 juta jadi Rp280 ribu). Turun bukan karena beban hilang, tetapi karena cara lama ikut menghitung akun yang bukan beban per-orang. Karena biaya adalah pengurang, **profit dan insentif tiap orang naik** — finance perlu tahu ini.

**Penyusutan aset dihitung per orang.** Rumusnya harga beli ÷ masa manfaat ÷ 12, dijumlahkan untuk semua aset yang dipegang orang itu.

Aturannya: **selama aset masih dipakai, penyusutannya tetap dibebankan** — walau umur bukunya sudah habis. Ini keputusan sadar dan berbeda dari akuntansi: di Accurate, aset yang habis umurnya bernilai nol dan tak disusutkan lagi. Yang diukur di sini biaya pemakaian, bukan nilai buku. Kalau suatu saat dibandingkan dengan Accurate, selisihnya akan muncul dan sebabnya ini.

Aset yang belum diisi harga atau masa manfaatnya **tidak dilewati diam-diam** — jumlahnya dilaporkan sebagai peringatan baris, supaya beban yang belum terhitung tetap terlihat. Prod 2026-08-26: 70 dari 71 aset marketing sudah lengkap.
- `GET/POST/DELETE /profit/internal-affiliates[/:username]` — daftar putih akun affiliate milik sendiri.

### Warisan skema lama (masih terdaftar)
- `GET /health` · `GET /stats` · `GET/PUT /configs/ppn`
- `GET/POST/PUT/DELETE /master-kpi[/:id]` · `/mappings[/:id]` · `GET /audit-logs`
- `/results*` (list, export Excel, approve/unapprove, override, delete)
- `GET /accurate/summary|income|invoices` · `GET /integration/shopee/item-performance`
- ⚠️ `POST /calculate` dan `POST /calculate/auto` **menolak seluruh role** dengan pesan yang menyebut SK pencabutnya. Rutenya sengaja dibiarkan supaya pemanggil lama mendapat penjelasan, bukan 404 yang membingungkan.

## Hierarki: Leader & Supervisor dari HRIS

> **Status**: ✅ live di prod sejak 2026-08-26 (PR #1431, #1432).

Sebelumnya level Leader dibangun dari koleksi `icc_leaders` dan level Supervisor dari
`incentive_org`. Keduanya gagal, dengan cara yang berbeda:

- `icc_leaders` punya indeks **UNIQUE pada `team`**, sehingga departemen ber-DUA leader —
  keadaan Beauty Hacks sejak SK-nya keluar — **ditolak database**. Ade Jaenul Farhi memimpin
  11 orang dan 3 toko di prod, dan tak akan pernah bisa masuk koleksi itu selama Satrio ada
  di tim yang sama.
- `incentive_org` level supervisor **tak pernah terisi** (0 baris) dan tak punya satu pun
  layar yang bisa mengisinya, sehingga level itu selalu kosong.

Keduanya kini diturunkan dari `work_data.supervisor_id` lewat `hierarki_hris.go`, memakai
aturan yang **sama persis** dengan [[APP - Web ERP]] (`hierarki-leader.ts`) supaya tak lahir
perbedaan halus antar-layar:

| Level | Aturan |
|---|---|
| Leader | orang yang punya bawahan langsung ber-`position_key: icc`, **dan bukan Supervisor** |
| Supervisor | atasan langsung seorang Leader |
| Anggota langsung SPV | siapa pun yang atasannya SPV tanpa perantara Leader — termasuk Affiliate, Host Live, Buzzer |

Empat hal yang menentukan benar-salahnya, dan semuanya sudah menggigit sekali:

- **"Punya bawahan ICC", bukan "berjabatan Leader"** — bila SPV memegang langsung satu
  Account Specialist, aturan berbasis jabatan membuat staf itu hilang dari penilaian.
- **Supervisor ditolak jadi Leader** (keputusan pemilik produk 2026-08-25: *"Maftuhissaiin
  hanya sebagai SPV, bukan leader"*). Tanpa ini ia muncul di dua level sekaligus dan di level
  Leader dibandingkan dengan target Leader padahal cuma memegang satu orang.
- **Batas divisi wajib** — tanpa syarat "supervisor harus sudah memimpin Leader ber-anggota
  ICC", SELURUH supervisor perusahaan ikut tertarik masuk. Terukur prod: Supervisor HRD
  muncul membawa 27 anggota berisi security, office boy, dan legal.
- **Cocokkan `position_key`, bukan label** — jabatan "ICC" di-rename jadi "Account Specialist"
  18 Agustus 2026; mencocokkan label kehilangan seluruh anggota.

Struktur lama tetap jadi **fallback**: hierarki gagal ditarik menurunkan dashboard ke perilaku
lama, bukan mengosongkannya.

Tiap baris juga membawa `divisi_id`/`divisi_nama` dan `leader_id`/`leader_nama` untuk
pengelompokan di layar. **Divisi diwakili SUPERVISORNYA**, bukan nama departemen HRIS
(keputusan 2026-08-25: *"departement = spv"*) — yang menentukan sebuah baris masuk kelompok
mana adalah siapa yang mempertanggungjawabkannya. Orang yang tak terjangkau hierarki
dibiarkan berkolom **kosong, bukan ditebak**.

Hasil terhadap 183 karyawan aktif (prod 2026-08-26): 3 Leader (Ade 11, Satrio 10, Ridho 11),
2 Supervisor (Aris → Satrio+Ade; Maftuhissaiin → Ridho + Annisa sebagai anggota langsung).

## Belum Diimplementasikan / Catatan

- **Cron harian dihapus** (`cron_worker.go`, −1.571 baris) bersama skema KPI-multiplier. Tidak ada lagi job terjadwal di service ini — lihat [[IT - Background Jobs & Schedulers]].
- **Pengecualian omzet affiliate eksternal belum terpasang di perhitungan.** Daftar putihnya sudah bisa diisi lewat Master Data, tetapi belum ada kode yang memakainya → pencapaian di layar masih lebih tinggi dari seharusnya. Terukur Juli 2026: 71,6% nilai affiliate berasal dari kreator eksternal.
- **Belum ada alur approval/freeze** untuk skema profit (yang lama punya, yang baru belum).
- **Atribusi ICC belum lengkap**: per 2026-08-01 hanya 10 dari 28 toko punya mapping ICC → 63% profit Juli tak berpemilik. Sumbernya `icc_account_mappings` di integration ([[Microservices - Integration Service]]). Membaik per 2026-08-26: 31 mapping aktif, 21 baris muncul di level ICC.
- ✅ ~~Proyek Accurate SPV belum tersambung.~~ **SELESAI 2026-08-26**, tetapi bukan lewat jalur yang direncanakan. Sempat dibuat pemetaan manual divisi→kode proyek (koleksi + endpoint + layar), lalu **dicabut** karena ternyata sudah diselesaikan lebih dulu di [[Microservices - Integration Service]]: beban proyek divisi kini dibagi ke tiap orang secara otomatis, jadi tak ada yang perlu dipetakan tangan. Dua orang mengerjakan masalah yang sama tanpa saling tahu; yang dipertahankan yang lebih lengkap.
- ✅ ~~Peringatan menggagalkan penilaian KPI secara pukul-rata.~~ **DIPERBAIKI 2026-08-26.** Sekarang hanya peringatan yang **benar-benar mengubah angka** yang menahan penilaian — gaji belum ada, opex belum ada, target belum diisi. Peringatan soal kelengkapan pembukuan dibiarkan lewat: "HPP mencakup 99,8%" meleset 0,2%, dan "N retur belum terbukukan" sama sekali tak menyentuh rumus profit (retur memang tidak dikurangkan). Maftuhissaiin sempat tak dinilai berbulan-bulan padahal realisasinya Rp486 juta sudah benar. Penjaganya sengaja dibalik — yang **boleh lewat** yang didaftar, peringatan baru yang belum dipertimbangkan tetap menahan penilaian sampai ada yang memutuskan sifatnya.
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
