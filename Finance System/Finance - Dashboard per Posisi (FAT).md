**Status**: ⚠️ **Implementasi (FE), sebagian besar elemen masih menunggu penyambungan data backend.** Dashboard keuangan per posisi (FAT) di `erp-frontend`, hidup dan dipakai. Marker sebelumnya `🟢` yang bukan anggota himpunan sah, sehingga dokumen ini tercatat TANPA status di `VAULT-INDEX.json`; diperbaiki 2026-09-04.

## Deskripsi

Menu **Finance** menyediakan **dashboard per posisi** (Finance/Accounting/Tax — "FAT") supaya tiap peran bisa mengambil keputusan **hanya dengan melihat layar**: kartu deviasi + grafik ringkas, bukan tabel mentah. Satu perender data-driven merender dua belas halaman dari deskripsinya, sehingga perbaikan tata letak dikerjakan sekali.

Kode: `erp-frontend/src/features/finance/posisi/`
- `components/halaman-posisi.tsx` — perender generik (kartu/bagan/tabel/peringatan) dari `data/<posisi>.ts`.
- `components/isi-<posisi>.tsx` — isi tiap posisi; yang hook-nya sudah tersambung merender kartu/grafik **nyata** lewat slot `atas`, judulnya didaftarkan ke `elemenDilewati` agar tak dobel dengan panel "menunggu penyambungan".
- `components/bagan/` — pustaka grafik lokal: `BaganBatang`, `BaganBatangHorizontal`, `BaganGaris`, `BaganPersen`, `BaganDonat` (donat komposisi, SVG + legenda). Warna dari token tema `WARNA_SERI` (`var(--fat-*)`), bukan heksa.
- Rute: `app/(main)/finance/posisi/<posisi>/page.tsx` (guard izin di pemanggil). Posisi: `spv`, `ar-staf`, `ar-leader`, `junior-accounting`, `senior-accounting`, `cost-control`, `tax`, `ap`, `cv`.

Hak akses per posisi mengikuti model RBAC yang hak-nya menempel di posisi — lihat [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]].

## Prinsip data (penting)

- **Tidak ada angka palsu.** Elemen yang hook-nya belum dipanggil dirender sebagai panel **"menunggu penyambungan data"** dengan nama hook-nya terlihat — bukan angka nol yang terbaca "tidak ada transaksi". Tiap helper grafik mengembalikan keadaan **kosong** saat datanya `undefined`.
- **Pass/fail hanya untuk target yang sudah tertulis di kode.** Indikator target‑vs‑aktual dipasang di ambang yang memang ada (AR Staf: piutang >14 hari & retur >14 hari, "maks 5%"). Ambang yang masih parameter manusia tanpa master (mis. SPV "beban non‑operasional ≤2%") **sengaja tidak** dijadikan lampu lulus/gagal.
- Sumber angka lintas modul; akuntansi via [[External - Accurate]] (laba rugi, saldo, varians anggaran).

## Grafik & indikator yang sudah hidup

Per pembaruan **2026-08-07** (FE), grafik hidup dari data yang hook‑nya sudah dimuat:

| Posisi | Elemen hidup | Sumber |
|---|---|---|
| Ringkasan Divisi | Aging piutang & Aging utang (donat komposisi); OPEX anggaran vs realisasi (batang) | `useFetchPiutangSummary`, `useAgingUtang`, `useFetchVariansEnamBulan` |
| SPV | Tren AR >60 hari (garis); Beban per kelompok (persen); **Aging piutang** (donat); kotak persetujuan | agregator persetujuan, laba rugi & piutang Accurate |
| AR Staf | Status penyelesaian retur (batang); Belum dicocokkan per kanal (persen); indikator target **Piutang >14 hari** & **Retur >14 hari** (maks 5%) | `useFetchReturnStats`, `useFetchMissingAgregat` |
| AR Leader | Uang tertagih per minggu (batang); **Komposisi piutang per umur** (persen) | `useFetchReceiptMingguan`, `useFetchPiutangSummary` |
| Cost Control | Varians per pos biaya (batang‑horizontal); **Anggaran vs Realisasi per pos** (batang 2 seri) | `useFetchVariansAnggaran` |
| Junior Acc | **Transaksi hari ini vs rata‑rata** (batang) | `useFetchJurnal` |
| AP | Aging utang (batang) | `useAgingUtang` |
| Accounting CV | Penjualan per toko (bilah, 8 teratas) | `useFetchPenjualanToko` |
| Senior Acc | Komposisi aset tetap (donat: nilai buku vs penyusutan) | `useFetchAsetTetap` |
| Tax | Beban per kelompok (donat) | `useFetchLabaRugi` |

Komponen indikator: `components/kartu-indikator-target.tsx` (pil hijau/amber/merah + bar target), status dihitung `lib/status-ambang.ts` (`statusAmbang({nilai,target,arah})` → `sehat|waspada|kritis`). Transform data grafik ada di `lib/bagan-*.ts` (murni, ber‑unit test).

## TBD (menunggu backend)

Masih panel jujur "menunggu penyambungan": AR Leader "hasil penagihan per cara hubung", Junior "koreksi per jenis transaksi", Senior "umur selisih rekonsiliasi", Cost Control "forecast kas" & "penghematan terealisasi", Tax "biaya non‑deductible per penyebab". Butuh endpoint/agregat backend baru sebelum bisa dijadikan grafik.

## Rancangan isi menurut ADR 0076

*Ditambahkan 2026-09-04. Bagian di atas merekam apa yang SUDAH tergambar; bagian ini menilai isinya terhadap [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]], sejajar dengan sembilan divisi lain. Angka KPI diukur 2026-08-28 dari [[HRIS - Matriks KPI per Departemen]]; ukur ulang sebelum dipakai mengambil keputusan.*

Divisi ini punya **61 metrik di 8 posisi**, jumlah terbanyak di perusahaan. Yang sudah menyala otomatis di produksi baru satu: `Performance Monitoring Team` milik Finance Supervisor.

### Dua penghambat memakan 30% metrik divisi ini

⛔ **Delapan belas dari 61 metrik (29,5%) adalah dua hal yang sama, berulang di hampir tiap template.**

| Penghambat | Metrik | Posisi |
|---|---:|---|
| **Tidak ada log 1-on-1** | 8 | semua kecuali Finance Supervisor dan AR Staff Piutang |
| **Ide inovasi / Kaizen** | 10 | tujuh dari delapan posisi |

Keduanya menuntut perlakuan yang **berbeda**, dan membedakannya menentukan apakah dashboardnya jujur:

- **Kaizen tidak boleh digambar sama sekali.** Ia manual **karena keputusan** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]), bukan karena sistemnya kurang. Panel "menunggu penyambungan" di sana akan berbohong tentang sebabnya, dan sepuluh panel berbohong yang tersebar di tujuh layar adalah cara tercepat membuat orang berhenti mempercayai panel jujur di tempat lain.
- **1-on-1 boleh digambar sebagai panel jujur**, sebab ia memang menunggu fitur yang belum ada. Satu fitur log 1-on-1 membuka delapan metrik sekaligus, dan itu bobot antara 0,05 sampai 0,15 di masing-masing dari tujuh posisi.

### Yang siap dijadikan visual utama

| Posisi | Kandidat visual utama | Sumber |
|---|---|---|
| AR Staff (Piutang) | umur piutang terhadap ambang 14 dan 60 hari, bobot gabungan 0,9 | `GET /accounting/receivables` |
| AR Staff (Retur) | pencatatan retur, bobot 0,5 | `accurate_daily_returns` 3.351 |
| AR Staff (Sales Admin) | pencatatan penjualan, bobot 0,5 | `kinerja_sales_admin` |
| AR Leader | piutang > 60 hari dan pengawasan ≤ 14 hari, bobot gabungan 0,6 | Accurate proxy |
| Finance Supervisor | sebaran skor KPI tim terhadap ambang | `skor_tim`, **sudah menyala** |
| Cost Control | varians OPEX terhadap ±5% | perlu master anggaran |

Empat posisi AR adalah kelompok paling siap, dan ketiganya sudah punya elemen hidup di layar sekarang (lihat tabel Grafik & indikator di atas).

### Yang harus diputuskan sebelum digambar

⚠️ **Metrik `Monitoring Team` di AR Leader (0,2) dan Senior Accountant (0,1) BUKAN skor tim murni.** Deskripsinya menggabungkan checker inputan dengan ketepatan tanggal, dua hal berbeda dalam satu metrik. Menggambarnya sebagai kartu skor tim akan menampilkan angka yang tidak menjawab separuh isi metriknya. Pisahkan lebih dulu di master data, atau jangan digambar.

⚠️ **Metrik `Pengelolaan Aset Tetap` Senior Accountant (0,15) dan `Pengelolaan asset/perlengkapan` Junior Accountant (0,15) dipetakan ke `manufacture_resi` dan `fulfillment_orders`**, yaitu data resi dan pemenuhan pesanan gudang. Aset tetap akuntansi tidak ada hubungannya dengan itu. Salah petak, sekelas dengan yang tercatat di [[GA - Dashboard per Posisi]] dan [[Manufacture - Dashboard per Posisi]].

⚠️ **Tax Staff punya tiga metrik bernama `Kepatuhan pajak 100% setiap bulan` 1, 2, dan 3** dengan sumber berbeda-beda, dua di antaranya menunggu tracker pajak yang tidak ada. Nama yang tak dapat dibedakan membuat layar detailnya mustahil dibaca; ini persoalan penamaan metrik ([[REF - Penamaan Metrik & Sumber KPI]]), bukan persoalan dashboard.

### Kebutuhan backend, terurut

1. **Fitur log 1-on-1.** Membuka 8 metrik di 7 posisi dalam satu pekerjaan. Daya ungkit tertinggi di divisi ini, dan **kemungkinan besar juga dibutuhkan Warehouse Leader** di [[Manufacture - Dashboard per Posisi]], jadi cakupannya lintas divisi.
2. **Master anggaran** untuk varians OPEX (Cost Control 0,2, Tax 0,15, Account Payable 0,25). Dipakai bersama [[GA - Dashboard per Posisi]] dan [[IT - Dashboard per Posisi]] yang membutuhkan hal yang sama untuk departemennya masing-masing.
3. **Pisahkan metrik `Monitoring Team`** di AR Leader dan Senior Accountant.
4. **Perbaiki pemetaan aset tetap** Senior dan Junior Accountant.
5. **Tracker pajak dan audit internal**, mengunci 5 metrik Tax Staff dan 1 Senior Accountant. Bersinggungan dengan modul Audit Internal yang sedang dipisah ([[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]]).
6. **Pemetaan metrik `Laporan keuangan`** yang muncul tanpa sumber di Junior Accountant (0,3), Senior Accountant (0,35 gabungan), dan Tax Staff (0,1).

## Dokumen Terkait

- [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] — prinsip penurunan isi dashboard posisi
- [[REF - Layout Dashboard erp-frontend]] — cara menyusunnya di layar
- [[HRIS - Matriks KPI per Departemen]] — sumber angka bagian rancangan
- [[Finance - Big Pictures]] — peta domain Finance System
- [[Finance - Incentive]] — dashboard insentif (menu Finance terkait)
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] — model hak akses per posisi
- [[External - Accurate]] — sumber angka akuntansi (laba rugi, varians anggaran)
